#!/usr/bin/env python3
"""Local storage admission, reservation, and receipt support."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time
import uuid


GIB = 1024**3
RESERVATION_SCHEMA = """
CREATE TABLE IF NOT EXISTS reservations (
    id TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    pid INTEGER NOT NULL,
    process_started TEXT NOT NULL,
    boot_id TEXT NOT NULL,
    reserved_bytes INTEGER NOT NULL,
    recovery_floor_bytes INTEGER NOT NULL,
    owned_roots TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL,
    starting_available_bytes INTEGER NOT NULL,
    minimum_available_bytes INTEGER NOT NULL
)
"""
COMPLETED_SCHEMA = """
CREATE TABLE IF NOT EXISTS completed_reservations (
    id TEXT PRIMARY KEY,
    receipt TEXT NOT NULL,
    completed_at INTEGER NOT NULL
)
"""


def state_root() -> Path:
    configured = os.environ.get("FACTORY_STORAGE_STATE")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / "Library" / "Application Support" / "EdoworksFactory" / "storage"


def process_started(pid: int) -> str:
    result = subprocess.run(
        ["ps", "-o", "lstart=", "-p", str(pid)],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def boot_id() -> str:
    result = subprocess.run(
        ["sysctl", "-n", "kern.boottime"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or "unknown"


def process_is_same(pid: int, expected_start: str) -> bool:
    return bool(expected_start) and process_started(pid) == expected_start


def filesystem_usage(path: Path) -> shutil._ntuple_diskusage:
    candidate = path.resolve()
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return shutil.disk_usage(candidate)


def admission(
    *, total_bytes: int, available_bytes: int, active_reserved_bytes: int,
    requested_bytes: int, recovery_floor_bytes: int
) -> dict:
    required = active_reserved_bytes + requested_bytes + recovery_floor_bytes
    headroom = available_bytes - active_reserved_bytes - requested_bytes
    if available_bytes < required:
        pressure = "RED"
        decision = "BLOCKED"
        reason = "insufficient_unreserved_capacity"
    elif headroom < recovery_floor_bytes * 2:
        pressure = "YELLOW"
        decision = "AUTHORIZED"
        reason = "authorized_with_limited_headroom"
    else:
        pressure = "GREEN"
        decision = "AUTHORIZED"
        reason = "capacity_reserved_above_recovery_floor"
    return {
        "total_bytes": total_bytes,
        "available_bytes": available_bytes,
        "active_reserved_bytes": active_reserved_bytes,
        "reservation_bytes": requested_bytes,
        "recovery_floor_bytes": recovery_floor_bytes,
        "required_available_bytes": required,
        "headroom_after_reservation_bytes": headroom,
        "percent_free": round((available_bytes / total_bytes) * 100, 2) if total_bytes else 0,
        "pressure": pressure,
        "decision": decision,
        "reason": reason,
    }


class ReservationStore:
    def __init__(self, database: Path | None = None):
        root = state_root() if database is None else database.parent
        root.mkdir(parents=True, exist_ok=True)
        self.database = database or root / "reservations.sqlite"
        with self.connect() as connection:
            connection.execute(RESERVATION_SCHEMA)
            connection.execute(COMPLETED_SCHEMA)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _reconcile(connection: sqlite3.Connection, *, now: int, current_boot: str) -> int:
        rows = connection.execute(
            "SELECT id, pid, process_started, boot_id, expires_at FROM reservations"
        ).fetchall()
        stale = [
            row["id"]
            for row in rows
            if row["expires_at"] <= now
            or row["boot_id"] != current_boot
            or not process_is_same(row["pid"], row["process_started"])
        ]
        connection.executemany("DELETE FROM reservations WHERE id = ?", ((item,) for item in stale))
        return len(stale)

    def inspect(self, *, path: Path, requested_bytes: int, recovery_floor_bytes: int) -> dict:
        usage = filesystem_usage(path)
        now = int(time.time())
        current_boot = boot_id()
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            reconciled = self._reconcile(connection, now=now, current_boot=current_boot)
            active = connection.execute(
                "SELECT COALESCE(SUM(reserved_bytes), 0) FROM reservations"
            ).fetchone()[0]
            result = admission(
                total_bytes=usage.total,
                available_bytes=usage.free,
                active_reserved_bytes=active,
                requested_bytes=requested_bytes,
                recovery_floor_bytes=recovery_floor_bytes,
            )
        return {
            "schema_version": 1,
            "command": "storage inspect",
            "reconciled_leases": reconciled,
            "starting_available_bytes": usage.free,
            "minimum_available_bytes": usage.free,
            "ending_available_bytes": usage.free,
            "peak_consumption_bytes": 0,
            "persistent_growth_bytes": 0,
            "cleanup_reclaimed_bytes": 0,
            "retained_artifacts": [],
            "unknown_persistent_growth_bytes": 0,
            **result,
        }

    def reserve(
        self, *, path: Path, owner: str, requested_bytes: int,
        recovery_floor_bytes: int, ttl_seconds: int, owned_roots: list[str],
        holder_pid: int | None = None,
    ) -> dict:
        usage = filesystem_usage(path)
        now = int(time.time())
        current_boot = boot_id()
        pid = holder_pid or os.getppid()
        started = process_started(pid)
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            reconciled = self._reconcile(connection, now=now, current_boot=current_boot)
            active = connection.execute(
                "SELECT COALESCE(SUM(reserved_bytes), 0) FROM reservations"
            ).fetchone()[0]
            result = admission(
                total_bytes=usage.total,
                available_bytes=usage.free,
                active_reserved_bytes=active,
                requested_bytes=requested_bytes,
                recovery_floor_bytes=recovery_floor_bytes,
            )
            reservation_id = None
            if result["decision"] == "AUTHORIZED":
                reservation_id = str(uuid.uuid4())
                connection.execute(
                    """INSERT INTO reservations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        reservation_id,
                        owner,
                        pid,
                        started,
                        current_boot,
                        requested_bytes,
                        recovery_floor_bytes,
                        json.dumps(owned_roots, separators=(",", ":")),
                        now,
                        now + ttl_seconds,
                        usage.free,
                        usage.free,
                    ),
                )
        return {
            "schema_version": 1,
            "command": "storage reserve",
            "reservation_id": reservation_id,
            "owner": owner,
            "owned_roots": owned_roots,
            "lease_expires_at": now + ttl_seconds if reservation_id else None,
            "reconciled_leases": reconciled,
            **result,
        }

    def observe(self, reservation_id: str, *, path: Path) -> dict:
        available = filesystem_usage(path).free
        with self.connect() as connection:
            row = connection.execute(
                "SELECT minimum_available_bytes FROM reservations WHERE id = ?", (reservation_id,)
            ).fetchone()
            if row is None:
                raise KeyError("reservation_not_found")
            minimum = min(row["minimum_available_bytes"], available)
            connection.execute(
                "UPDATE reservations SET minimum_available_bytes = ? WHERE id = ?",
                (minimum, reservation_id),
            )
        return {"schema_version": 1, "reservation_id": reservation_id, "available_bytes": available, "minimum_available_bytes": minimum}

    def settle(
        self, reservation_id: str, *, path: Path, timeout_seconds: int,
        interval_seconds: float, stable_samples: int, delta_bytes: int,
        minimum_wait_seconds: int = 0, minimum_available_bytes: int = 0,
    ) -> dict:
        started = time.monotonic()
        deadline = started + timeout_seconds
        available = filesystem_usage(path).free
        previous = available
        stable = 0
        minimum = available
        samples = 1
        while True:
            available = filesystem_usage(path).free
            minimum = min(minimum, available)
            samples += 1
            if abs(available - previous) <= delta_bytes:
                stable += 1
            else:
                stable = 0
            now = time.monotonic()
            target_met = available >= minimum_available_bytes
            if (stable >= stable_samples and now - started >= minimum_wait_seconds and target_met) or now >= deadline:
                break
            previous = available
            time.sleep(interval_seconds)
        with self.connect() as connection:
            row = connection.execute(
                "SELECT minimum_available_bytes FROM reservations WHERE id = ?", (reservation_id,)
            ).fetchone()
            if row is None:
                raise KeyError("reservation_not_found")
            minimum = min(row["minimum_available_bytes"], minimum)
            connection.execute(
                "UPDATE reservations SET minimum_available_bytes = ? WHERE id = ?",
                (minimum, reservation_id),
            )
        return {
            "schema_version": 1,
            "reservation_id": reservation_id,
            "available_bytes": available,
            "minimum_available_bytes": minimum,
            "samples": samples,
            "settled": stable >= stable_samples,
            "minimum_available_target_bytes": minimum_available_bytes,
            "target_met": available >= minimum_available_bytes,
        }

    def finish(
        self, reservation_id: str, *, path: Path, outcome: str,
        cleanup_reclaimed_bytes: int = 0, retained_artifacts: list[str] | None = None,
        attributed_persistent_bytes: int = 0, growth_tolerance_bytes: int = 0,
    ) -> dict:
        ending = filesystem_usage(path).free
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM reservations WHERE id = ?", (reservation_id,)
            ).fetchone()
            if row is None:
                completed = connection.execute(
                    "SELECT receipt FROM completed_reservations WHERE id = ?", (reservation_id,)
                ).fetchone()
                if completed is None:
                    raise KeyError("reservation_not_found")
                return json.loads(completed["receipt"])
            starting = row["starting_available_bytes"]
            minimum = min(row["minimum_available_bytes"], ending)
            persistent_growth = max(0, starting - ending)
            unknown_growth = max(0, persistent_growth - attributed_persistent_bytes)
            receipt = {
                "schema_version": 1,
                "command": "storage finish",
                "reservation_id": reservation_id,
                "owner": row["owner"],
                "outcome": outcome,
                "starting_available_bytes": starting,
                "minimum_available_bytes": minimum,
                "ending_available_bytes": ending,
                "peak_consumption_bytes": max(0, starting - minimum),
                "persistent_growth_bytes": persistent_growth,
                "reservation_bytes": row["reserved_bytes"],
                "recovery_floor_bytes": row["recovery_floor_bytes"],
                "cleanup_reclaimed_bytes": max(0, cleanup_reclaimed_bytes),
                "owned_roots": json.loads(row["owned_roots"]),
                "retained_artifacts": retained_artifacts or [],
                "attributed_persistent_bytes": max(0, attributed_persistent_bytes),
                "unknown_persistent_growth_bytes": unknown_growth,
                "growth_tolerance_bytes": max(0, growth_tolerance_bytes),
                "storage_policy_status": "PASS" if unknown_growth <= growth_tolerance_bytes else "VIOLATION",
            }
            connection.execute(
                "INSERT INTO completed_reservations VALUES (?, ?, ?)",
                (reservation_id, json.dumps(receipt, sort_keys=True), int(time.time())),
            )
            connection.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
        return receipt


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return parsed


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--database", type=Path)
    subparsers = result.add_subparsers(dest="command", required=True)

    inspect = subparsers.add_parser("inspect")
    inspect.add_argument("--path", type=Path, default=Path("/"))
    inspect.add_argument("--reserve-bytes", type=positive_int, required=True)
    inspect.add_argument("--recovery-floor-bytes", type=positive_int, required=True)

    reserve = subparsers.add_parser("reserve")
    reserve.add_argument("--path", type=Path, default=Path("/"))
    reserve.add_argument("--owner", required=True)
    reserve.add_argument("--reserve-bytes", type=positive_int, required=True)
    reserve.add_argument("--recovery-floor-bytes", type=positive_int, required=True)
    reserve.add_argument("--ttl-seconds", type=positive_int, default=14400)
    reserve.add_argument("--holder-pid", type=positive_int)
    reserve.add_argument("--owned-root", action="append", default=[])

    observe = subparsers.add_parser("observe")
    observe.add_argument("reservation_id")
    observe.add_argument("--path", type=Path, default=Path("/"))

    settle = subparsers.add_parser("settle")
    settle.add_argument("reservation_id")
    settle.add_argument("--path", type=Path, default=Path("/"))
    settle.add_argument("--timeout-seconds", type=positive_int, default=60)
    settle.add_argument("--interval-seconds", type=float, default=1.0)
    settle.add_argument("--stable-samples", type=positive_int, default=3)
    settle.add_argument("--delta-bytes", type=positive_int, default=4 * 1024**2)
    settle.add_argument("--minimum-wait-seconds", type=positive_int, default=0)
    settle.add_argument("--minimum-available-bytes", type=positive_int, default=0)

    finish = subparsers.add_parser("finish")
    finish.add_argument("reservation_id")
    finish.add_argument("--path", type=Path, default=Path("/"))
    finish.add_argument("--outcome", required=True)
    finish.add_argument("--cleanup-reclaimed-bytes", type=positive_int, default=0)
    finish.add_argument("--attributed-persistent-bytes", type=positive_int, default=0)
    finish.add_argument("--growth-tolerance-bytes", type=positive_int, default=0)
    finish.add_argument("--retained-artifact", action="append", default=[])
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        store = ReservationStore(args.database)
        if args.command == "inspect":
            receipt = store.inspect(
                path=args.path,
                requested_bytes=args.reserve_bytes,
                recovery_floor_bytes=args.recovery_floor_bytes,
            )
        elif args.command == "reserve":
            receipt = store.reserve(
                path=args.path,
                owner=args.owner,
                requested_bytes=args.reserve_bytes,
                recovery_floor_bytes=args.recovery_floor_bytes,
                ttl_seconds=args.ttl_seconds,
                owned_roots=args.owned_root,
                holder_pid=args.holder_pid,
            )
        elif args.command == "observe":
            receipt = store.observe(args.reservation_id, path=args.path)
        elif args.command == "settle":
            receipt = store.settle(
                args.reservation_id,
                path=args.path,
                timeout_seconds=args.timeout_seconds,
                interval_seconds=args.interval_seconds,
                stable_samples=args.stable_samples,
                delta_bytes=args.delta_bytes,
                minimum_wait_seconds=args.minimum_wait_seconds,
                minimum_available_bytes=args.minimum_available_bytes,
            )
        else:
            receipt = store.finish(
                args.reservation_id,
                path=args.path,
                outcome=args.outcome,
                cleanup_reclaimed_bytes=args.cleanup_reclaimed_bytes,
                retained_artifacts=args.retained_artifact,
                attributed_persistent_bytes=args.attributed_persistent_bytes,
                growth_tolerance_bytes=args.growth_tolerance_bytes,
            )
    except (OSError, sqlite3.Error, KeyError, ValueError) as error:
        print(json.dumps({"schema_version": 1, "decision": "BLOCKED", "error": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt.get("decision") != "BLOCKED" else 2


if __name__ == "__main__":
    sys.exit(main())
