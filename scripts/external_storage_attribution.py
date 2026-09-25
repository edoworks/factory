#!/usr/bin/env python3
"""Measure allowlisted external-owner storage without exposing local paths."""

import argparse
import json
import os
import pathlib
import stat
import sys


ROOTS = {
    "coresimulator_system": pathlib.Path("/Library/Developer/CoreSimulator"),
    "coresimulator_user": pathlib.Path.home() / "Library/Developer/CoreSimulator",
    "xcode_user": pathlib.Path.home() / "Library/Developer/Xcode",
}
MEASUREMENT_FIELDS = {"state", "allocated_bytes", "reason"}
UNAVAILABLE_REASONS = {"root_open_failed", "traversal_failed"}


def reject_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def open_root(path):
    if not path.is_absolute():
        raise ValueError("allowlisted root must be absolute")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptor = os.open("/", flags)
    try:
        for component in path.parts[1:]:
            next_descriptor = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
    except FileNotFoundError:
        os.close(descriptor)
        return None
    except OSError as error:
        os.close(descriptor)
        raise ValueError("allowlisted root cannot be opened safely") from None
    return descriptor


def allocated_bytes(root_descriptor):
    total = 0
    seen = set()
    stack = []

    def count(metadata):
        nonlocal total
        identity = (metadata.st_dev, metadata.st_ino)
        if identity not in seen:
            seen.add(identity)
            total += metadata.st_blocks * 512

    def push(descriptor):
        count(os.fstat(descriptor))
        try:
            entries = os.scandir(descriptor)
        except OSError:
            os.close(descriptor)
            raise
        stack.append((descriptor, entries))

    push(root_descriptor)
    try:
        while stack:
            descriptor, entries = stack[-1]
            try:
                entry = next(entries)
            except StopIteration:
                entries.close()
                os.close(descriptor)
                stack.pop()
                continue
            metadata = entry.stat(follow_symlinks=False)
            count(metadata)
            if stat.S_ISDIR(metadata.st_mode):
                child = os.open(
                    entry.name,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                    dir_fd=descriptor,
                )
                try:
                    child_metadata = os.fstat(child)
                    if (child_metadata.st_dev, child_metadata.st_ino) != (
                        metadata.st_dev,
                        metadata.st_ino,
                    ):
                        raise OSError("directory identity changed")
                except OSError:
                    os.close(child)
                    raise
                push(child)
    finally:
        for descriptor, entries in stack:
            entries.close()
            os.close(descriptor)
    return total


def measure_root(identifier, path):
    try:
        descriptor = open_root(path)
    except ValueError:
        return {
            "state": "unavailable",
            "allocated_bytes": None,
            "reason": "root_open_failed",
        }
    if descriptor is None:
        return {"state": "absent", "allocated_bytes": 0, "reason": None}
    try:
        allocated = allocated_bytes(descriptor)
    except OSError:
        return {
            "state": "unavailable",
            "allocated_bytes": None,
            "reason": "traversal_failed",
        }
    return {"state": "present", "allocated_bytes": allocated, "reason": None}


def snapshot():
    return {
        "schema_version": 1,
        "command": "external storage snapshot",
        "measurements": {
            identifier: measure_root(identifier, path)
            for identifier, path in ROOTS.items()
        },
    }


def validate_snapshot(value):
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "command",
        "measurements",
    }:
        raise ValueError("snapshot fields must match the fixed schema")
    if (
        type(value["schema_version"]) is not int
        or value["schema_version"] != 1
        or value["command"] != "external storage snapshot"
    ):
        raise ValueError("snapshot identity is invalid")
    measurements = value["measurements"]
    if not isinstance(measurements, dict) or set(measurements) != set(ROOTS):
        raise ValueError("snapshot classes must match the fixed allowlist")
    for identifier, measurement in measurements.items():
        if not isinstance(measurement, dict) or set(measurement) != MEASUREMENT_FIELDS:
            raise ValueError(f"{identifier}: measurement fields are invalid")
        state = measurement["state"]
        if not isinstance(state, str) or state not in {"absent", "present", "unavailable"}:
            raise ValueError(f"{identifier}: measurement state is invalid")
        allocated = measurement["allocated_bytes"]
        reason = measurement["reason"]
        if state == "unavailable":
            if (
                allocated is not None
                or not isinstance(reason, str)
                or reason not in UNAVAILABLE_REASONS
            ):
                raise ValueError(f"{identifier}: unavailable measurement is invalid")
            continue
        if reason is not None:
            raise ValueError(f"{identifier}: measured roots cannot report a reason")
        if not isinstance(allocated, int) or isinstance(allocated, bool) or allocated < 0:
            raise ValueError(f"{identifier}: allocated_bytes is invalid")
        if state == "absent" and allocated != 0:
            raise ValueError(f"{identifier}: absent roots must report zero bytes")


def compare(before, after):
    validate_snapshot(before)
    validate_snapshot(after)
    measurements = {}
    signed_total = 0
    positive_total = 0
    measured_class_count = 0
    for identifier in ROOTS:
        before_measurement = before["measurements"][identifier]
        after_measurement = after["measurements"][identifier]
        before_allocated = before_measurement["allocated_bytes"]
        after_allocated = after_measurement["allocated_bytes"]
        if before_allocated is None or after_allocated is None:
            delta = None
        else:
            delta = after_allocated - before_allocated
            signed_total += delta
            positive_total += max(0, delta)
            measured_class_count += 1
        measurements[identifier] = {
            "before_state": before_measurement["state"],
            "after_state": after_measurement["state"],
            "before_allocated_bytes": before_allocated,
            "after_allocated_bytes": after_allocated,
            "before_reason": before_measurement["reason"],
            "after_reason": after_measurement["reason"],
            "delta_bytes": delta,
        }
    return {
        "schema_version": 1,
        "command": "external storage compare",
        "measurements": measurements,
        "aggregate_signed_delta_bytes": signed_total,
        "aggregate_positive_growth_bytes": positive_total,
        "measured_class_count": measured_class_count,
        "claim": "bounded_external_owner_measurement_not_full_apfs_attribution",
    }


def load_snapshot(path):
    try:
        value = json.loads(path.read_text(), object_pairs_hook=reject_duplicate_keys)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("snapshot input is unavailable or invalid") from error
    validate_snapshot(value)
    return value


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main(argv):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--output", type=pathlib.Path, required=True)
    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--before", type=pathlib.Path, required=True)
    compare_parser.add_argument("--after", type=pathlib.Path, required=True)
    compare_parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "snapshot":
            value = snapshot()
        else:
            value = compare(load_snapshot(args.before), load_snapshot(args.after))
        write_json(args.output, value)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
