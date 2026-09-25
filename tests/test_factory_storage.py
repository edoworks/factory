import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts.factory_storage import ReservationStore, admission


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "factory_storage.py"
GIB = 1024**3


class AdmissionTests(unittest.TestCase):
    def test_green_when_reservation_fits_above_recovery_floor(self):
        result = admission(
            total_bytes=100 * GIB,
            available_bytes=40 * GIB,
            active_reserved_bytes=2 * GIB,
            requested_bytes=8 * GIB,
            recovery_floor_bytes=10 * GIB,
        )
        self.assertEqual(result["decision"], "AUTHORIZED")
        self.assertEqual(result["pressure"], "GREEN")

    def test_yellow_preserves_floor_with_limited_headroom(self):
        result = admission(
            total_bytes=100 * GIB,
            available_bytes=25 * GIB,
            active_reserved_bytes=0,
            requested_bytes=8 * GIB,
            recovery_floor_bytes=10 * GIB,
        )
        self.assertEqual(result["decision"], "AUTHORIZED")
        self.assertEqual(result["pressure"], "YELLOW")

    def test_red_blocks_when_unreserved_capacity_is_insufficient(self):
        result = admission(
            total_bytes=100 * GIB,
            available_bytes=17 * GIB,
            active_reserved_bytes=0,
            requested_bytes=8 * GIB,
            recovery_floor_bytes=10 * GIB,
        )
        self.assertEqual(result["decision"], "BLOCKED")
        self.assertEqual(result["pressure"], "RED")


class ReservationStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary.name) / "reservations.sqlite"
        self.store = ReservationStore(self.database)

    def tearDown(self):
        self.temporary.cleanup()

    @mock.patch("scripts.factory_storage.filesystem_usage")
    def test_live_reservation_reduces_concurrent_capacity(self, usage):
        usage.return_value = mock.Mock(total=40 * GIB, free=25 * GIB)
        with mock.patch("scripts.factory_storage.process_is_same", return_value=True):
            first = self.store.reserve(
                path=Path("/"), owner="first", requested_bytes=8 * GIB,
                recovery_floor_bytes=10 * GIB, ttl_seconds=60, owned_roots=[".factory/runs/first"]
            )
            second = self.store.reserve(
                path=Path("/"), owner="second", requested_bytes=8 * GIB,
                recovery_floor_bytes=10 * GIB, ttl_seconds=60, owned_roots=[".factory/runs/second"]
            )
        self.assertEqual(first["decision"], "AUTHORIZED")
        self.assertEqual(second["decision"], "BLOCKED")

    @mock.patch("scripts.factory_storage.filesystem_usage")
    def test_stale_reservation_is_reconciled(self, usage):
        usage.return_value = mock.Mock(total=40 * GIB, free=25 * GIB)
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "INSERT INTO reservations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("stale", "job", 999999, "gone", "old-boot", 8 * GIB, 10 * GIB, "[]", 0, 1, 25 * GIB, 25 * GIB),
            )
        result = self.store.inspect(path=Path("/"), requested_bytes=8 * GIB, recovery_floor_bytes=10 * GIB)
        self.assertEqual(result["reconciled_leases"], 1)
        self.assertEqual(result["decision"], "AUTHORIZED")

    @mock.patch("scripts.factory_storage.filesystem_usage")
    def test_finish_is_scoped_and_reports_growth(self, usage):
        usage.return_value = mock.Mock(total=100 * GIB, free=40 * GIB)
        with mock.patch("scripts.factory_storage.process_is_same", return_value=True):
            reserved = self.store.reserve(
                path=Path("/"), owner="verify", requested_bytes=8 * GIB,
                recovery_floor_bytes=10 * GIB, ttl_seconds=60,
                owned_roots=[".factory/runs/known"],
            )
        usage.return_value = mock.Mock(total=100 * GIB, free=38 * GIB)
        result = self.store.finish(
            reserved["reservation_id"], path=Path("/"), outcome="FAILED",
            retained_artifacts=[".factory/runs/known"],
        )
        self.assertEqual(result["persistent_growth_bytes"], 2 * GIB)
        self.assertEqual(result["owned_roots"], [".factory/runs/known"])
        self.assertEqual(result["retained_artifacts"], [".factory/runs/known"])
        self.assertEqual(result["storage_policy_status"], "VIOLATION")

    @mock.patch("scripts.factory_storage.filesystem_usage")
    def test_small_measurement_drift_can_be_explicitly_tolerated(self, usage):
        usage.return_value = mock.Mock(total=100 * GIB, free=40 * GIB)
        with mock.patch("scripts.factory_storage.process_is_same", return_value=True):
            reserved = self.store.reserve(
                path=Path("/"), owner="verify", requested_bytes=8 * GIB,
                recovery_floor_bytes=10 * GIB, ttl_seconds=60, owned_roots=["run"],
            )
        usage.return_value = mock.Mock(total=100 * GIB, free=40 * GIB - 32 * 1024**2)
        result = self.store.finish(
            reserved["reservation_id"], path=Path("/"), outcome="PASSED",
            growth_tolerance_bytes=64 * 1024**2,
        )
        self.assertEqual(result["storage_policy_status"], "PASS")

    @mock.patch("scripts.factory_storage.filesystem_usage")
    def test_finish_is_idempotent(self, usage):
        usage.return_value = mock.Mock(total=100 * GIB, free=40 * GIB)
        with mock.patch("scripts.factory_storage.process_is_same", return_value=True):
            reserved = self.store.reserve(
                path=Path("/"), owner="verify", requested_bytes=8 * GIB,
                recovery_floor_bytes=10 * GIB, ttl_seconds=60, owned_roots=["run"],
            )
        first = self.store.finish(
            reserved["reservation_id"], path=Path("/"), outcome="PASSED"
        )
        usage.return_value = mock.Mock(total=100 * GIB, free=20 * GIB)
        second = self.store.finish(
            reserved["reservation_id"], path=Path("/"), outcome="FAILED"
        )
        self.assertEqual(second, first)

    def test_unknown_reservation_fails_closed(self):
        with self.assertRaises(KeyError):
            self.store.finish("missing", path=Path("/"), outcome="FAILED")

    @mock.patch("scripts.factory_storage.time.sleep")
    @mock.patch("scripts.factory_storage.filesystem_usage")
    def test_settle_waits_for_asynchronous_reclamation(self, usage, sleep):
        usage.side_effect = [
            mock.Mock(total=100 * GIB, free=40 * GIB),
            mock.Mock(total=100 * GIB, free=38 * GIB),
            mock.Mock(total=100 * GIB, free=39 * GIB),
            mock.Mock(total=100 * GIB, free=40 * GIB),
            mock.Mock(total=100 * GIB, free=40 * GIB),
            mock.Mock(total=100 * GIB, free=40 * GIB),
            mock.Mock(total=100 * GIB, free=40 * GIB),
        ]
        with mock.patch("scripts.factory_storage.process_is_same", return_value=True):
            reserved = self.store.reserve(
                path=Path("/"), owner="verify", requested_bytes=8 * GIB,
                recovery_floor_bytes=10 * GIB, ttl_seconds=60, owned_roots=["run"],
            )
        result = self.store.settle(
            reserved["reservation_id"], path=Path("/"), timeout_seconds=60,
            interval_seconds=1, stable_samples=3, delta_bytes=4 * 1024**2,
        )
        self.assertTrue(result["settled"])
        self.assertEqual(result["minimum_available_bytes"], 38 * GIB)
        self.assertGreaterEqual(sleep.call_count, 3)

    @mock.patch("scripts.factory_storage.time.sleep")
    @mock.patch("scripts.factory_storage.time.monotonic")
    @mock.patch("scripts.factory_storage.filesystem_usage")
    def test_settle_does_not_accept_an_early_stable_plateau(self, usage, monotonic, sleep):
        usage.return_value = mock.Mock(total=100 * GIB, free=40 * GIB)
        monotonic.side_effect = [0, 1, 2, 3, 15]
        with mock.patch("scripts.factory_storage.process_is_same", return_value=True):
            reserved = self.store.reserve(
                path=Path("/"), owner="verify", requested_bytes=8 * GIB,
                recovery_floor_bytes=10 * GIB, ttl_seconds=60, owned_roots=["run"],
            )
        result = self.store.settle(
            reserved["reservation_id"], path=Path("/"), timeout_seconds=60,
            interval_seconds=1, stable_samples=3, delta_bytes=4 * 1024**2,
            minimum_wait_seconds=15,
        )
        self.assertTrue(result["settled"])
        self.assertEqual(sleep.call_count, 3)

    @mock.patch("scripts.factory_storage.time.sleep")
    @mock.patch("scripts.factory_storage.time.monotonic")
    @mock.patch("scripts.factory_storage.filesystem_usage")
    def test_settle_rejects_stability_below_recovery_target(self, usage, monotonic, sleep):
        usage.side_effect = [
            mock.Mock(total=100 * GIB, free=40 * GIB),
            mock.Mock(total=100 * GIB, free=39 * GIB),
            mock.Mock(total=100 * GIB, free=39 * GIB),
            mock.Mock(total=100 * GIB, free=39 * GIB),
            mock.Mock(total=100 * GIB, free=39 * GIB),
            mock.Mock(total=100 * GIB, free=40 * GIB),
            mock.Mock(total=100 * GIB, free=40 * GIB),
            mock.Mock(total=100 * GIB, free=40 * GIB),
            mock.Mock(total=100 * GIB, free=40 * GIB),
        ]
        monotonic.side_effect = [0, 1, 2, 3, 4, 5, 6, 7]
        with mock.patch("scripts.factory_storage.process_is_same", return_value=True):
            reserved = self.store.reserve(
                path=Path("/"), owner="verify", requested_bytes=8 * GIB,
                recovery_floor_bytes=10 * GIB, ttl_seconds=60, owned_roots=["run"],
            )
        result = self.store.settle(
            reserved["reservation_id"], path=Path("/"), timeout_seconds=60,
            interval_seconds=1, stable_samples=3, delta_bytes=4 * 1024**2,
            minimum_available_bytes=40 * GIB,
        )
        self.assertTrue(result["target_met"])
        self.assertEqual(sleep.call_count, 6)


class CommandTests(unittest.TestCase):
    def test_invalid_negative_budget_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--database",
                    str(Path(directory) / "state.sqlite"),
                    "inspect",
                    "--reserve-bytes",
                    "-1",
                    "--recovery-floor-bytes",
                    "1",
                ],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)


class LifecycleContractTests(unittest.TestCase):
    def test_verify_reserves_before_xcode_and_scopes_derived_data(self):
        script = (ROOT / "bin" / "factory-verify").read_text()
        self.assertLess(script.index("storage.py\" reserve"), script.index("xcodebuild build"))
        self.assertIn('-derivedDataPath "$DERIVED_DATA_PATH"', script)
        self.assertIn('RUN_ROOT=".factory/runs/$RUN_ID"', script)
        self.assertIn('xcrun simctl create "Factory-$RUN_ID-iPhone"', script)
        self.assertIn('xcrun simctl delete "$FACTORY_IPHONE_SIM"', script)
        self.assertIn('factory_storage.py" settle', script)
        self.assertIn("--minimum-wait-seconds 15", script)
        self.assertIn('--minimum-available-bytes "$SETTLEMENT_TARGET_BYTES"', script)
        self.assertIn('write_result "$STORAGE_RECEIPT"', script)

    def test_verify_cleanup_is_limited_to_owned_paths(self):
        script = (ROOT / "bin" / "factory-verify").read_text()
        self.assertIn('rm -rf "$RUN_ROOT"', script)
        self.assertIn("FINISH_ARGUMENTS=(--path /)", script)
        self.assertNotIn('RETAINED_ARGUMENTS=()', script)
        self.assertIn('echo "$STORAGE_RESERVATION" | python3 -m json.tool', script)
        self.assertNotIn("Library/Developer", script)
        self.assertNotIn("XCTestDevices", script)
        self.assertIn('coresimulator-device:$FACTORY_IPHONE_SIM', script)

    def test_doctor_uses_workload_reservation_and_recovery_floor(self):
        script = (ROOT / "bin" / "factory-doctor").read_text()
        self.assertIn("FACTORY_VERIFY_MAX_GIB", script)
        self.assertIn("FACTORY_RECOVERY_FLOOR_GIB", script)
        self.assertIn("storage_admission", script)

    def test_hosted_ci_bounds_storage_and_form_factor_checks(self):
        workflow = (ROOT / ".github" / "workflows" / "checks.yml").read_text()
        self.assertIn("FACTORY_STORAGE_GROWTH_TOLERANCE_MIB: 768", workflow)
        self.assertIn("Do not raise this bound again", workflow)
        self.assertRegex(workflow, r"(?m)^  policy:\n    name: Factory policy gate\n    runs-on: macos-15\n    timeout-minutes: 25$")
        self.assertIn("Run 36117730389 reached the former 8-minute bound", workflow)
        self.assertRegex(
            workflow,
            r"(?m)^      - name: Verify template builds\n(?:        #.*\n){2}        timeout-minutes: 15$",
        )
        job_timeout = int(re.search(r"(?m)^  policy:\n(?:.*\n){2}    timeout-minutes: (\d+)$", workflow).group(1))
        step_timeout = int(re.search(r"(?m)^      - name: Verify template builds\n(?:        #.*\n){2}        timeout-minutes: (\d+)$", workflow).group(1))
        self.assertLess(step_timeout, job_timeout)
        self.assertRegex(workflow, r"(?m)^  reference-app:\n    name: Mews & Woofs \(\$\{\{ matrix\.form_factor \}\}\)\n    runs-on: macos-15\n    timeout-minutes: 20$")
        self.assertIn("fail-fast: false", workflow)
        self.assertIn("simulator_key: IPHONE", workflow)
        self.assertIn("simulator_key: IPAD", workflow)
        self.assertRegex(workflow, r"(?m)^      - name: Verify reference app\n        timeout-minutes: 15$")
        self.assertIn('form_factor: iPhone', workflow)
        self.assertIn('form_factor: iPad', workflow)
        self.assertIn('MewsAndWoofs-${{ matrix.form_factor }}.xcresult', workflow)
        self.assertIn('mews-and-woofs-${{ matrix.form_factor }}-evidence', workflow)

    def test_simulator_creation_failure_writes_combined_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            app = Path(directory) / "Probe"
            project = app / "Probe.xcodeproj"
            fake_bin = Path(directory) / "bin"
            project.mkdir(parents=True)
            fake_bin.mkdir()
            (app / "project.yml").write_text("name: Probe\n")
            (project / "project.pbxproj").write_text("")
            xcrun = fake_bin / "xcrun"
            xcrun.write_text(
                "#!/usr/bin/env bash\n"
                "if [[ \"$*\" == *\"list devices available --json\"* ]]; then\n"
                "  printf '%s\\n' '{\"devices\":{\"com.apple.CoreSimulator.SimRuntime.iOS-26-0\":[{\"name\":\"iPhone 18\",\"udid\":\"phone\",\"state\":\"Shutdown\",\"isAvailable\":true,\"deviceTypeIdentifier\":\"phone-type\"},{\"name\":\"iPad Pro\",\"udid\":\"tablet\",\"state\":\"Shutdown\",\"isAvailable\":true,\"deviceTypeIdentifier\":\"tablet-type\"}]}}'\n"
                "  exit 0\n"
                "fi\n"
                "exit 1\n"
            )
            xcrun.chmod(0o755)
            environment = {
                **os.environ,
                "PATH": f"{fake_bin}:{os.environ['PATH']}",
                "FACTORY_STORAGE_STATE": str(Path(directory) / "storage"),
                "FACTORY_VERIFY_MAX_GIB": "0",
                "FACTORY_RECOVERY_FLOOR_GIB": "0",
            }
            result = subprocess.run(
                [str(ROOT / "bin" / "factory-verify")],
                cwd=app,
                env=environment,
                capture_output=True,
                text=True,
            )
            receipt = json.loads((app / ".factory-verify-result.json").read_text())
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(receipt["command"], "factory verify")
        self.assertEqual(receipt["storage"]["outcome"], "INTERRUPTED")
        self.assertIn("interrupted", [step["step"] for step in receipt["steps"]])


if __name__ == "__main__":
    unittest.main()
