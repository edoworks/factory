import importlib.util
import json
import pathlib
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "external_storage_attribution.py"
SPEC = importlib.util.spec_from_file_location("external_storage_attribution", SCRIPT)
ATTRIBUTION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ATTRIBUTION)


def snapshot(values):
    return {
        "schema_version": 1,
        "command": "external storage snapshot",
        "measurements": {
            identifier: {
                "state": "present" if value else "absent",
                "allocated_bytes": value,
            }
            for identifier, value in values.items()
        },
    }


class ExternalStorageAttributionTests(unittest.TestCase):
    def test_snapshot_uses_fixed_identifiers_without_paths(self):
        with mock.patch.object(
            ATTRIBUTION,
            "measure_root",
            side_effect=lambda identifier, path: {
                "state": "present",
                "allocated_bytes": len(identifier),
            },
        ):
            value = ATTRIBUTION.snapshot()
        self.assertEqual(set(value["measurements"]), set(ATTRIBUTION.ROOTS))
        serialized = json.dumps(value)
        self.assertNotIn(str(pathlib.Path.home()), serialized)
        self.assertNotIn("/Library/Developer", serialized)
        self.assertEqual(
            ATTRIBUTION.ROOTS,
            {
                "coresimulator_system": pathlib.Path("/Library/Developer/CoreSimulator"),
                "coresimulator_user": pathlib.Path.home() / "Library/Developer/CoreSimulator",
                "xcode_user": pathlib.Path.home() / "Library/Developer/Xcode",
            },
        )

    def test_compare_reports_signed_and_positive_growth(self):
        identifiers = list(ATTRIBUTION.ROOTS)
        before = snapshot(dict(zip(identifiers, (100, 200, 300))))
        after = snapshot(dict(zip(identifiers, (150, 120, 300))))
        value = ATTRIBUTION.compare(before, after)
        self.assertEqual(value["measurements"][identifiers[0]]["delta_bytes"], 50)
        self.assertEqual(value["measurements"][identifiers[1]]["delta_bytes"], -80)
        self.assertEqual(value["aggregate_signed_delta_bytes"], -30)
        self.assertEqual(value["aggregate_positive_growth_bytes"], 50)
        self.assertEqual(
            value["claim"],
            "bounded_external_owner_measurement_not_full_apfs_attribution",
        )

    def test_snapshot_rejects_unknown_classes_and_duplicate_keys(self):
        value = snapshot({identifier: 0 for identifier in ATTRIBUTION.ROOTS})
        value["measurements"]["private_path"] = {
            "state": "present",
            "allocated_bytes": 1,
        }
        with self.assertRaisesRegex(ValueError, "fixed allowlist"):
            ATTRIBUTION.validate_snapshot(value)
        with self.assertRaises(ValueError) as context:
            ATTRIBUTION.reject_duplicate_keys(
                [("/private/path", "absent"), ("/private/path", "present")]
            )
        self.assertEqual(str(context.exception), "duplicate JSON key")

    def test_snapshot_rejects_boolean_schema_version(self):
        value = snapshot({identifier: 0 for identifier in ATTRIBUTION.ROOTS})
        value["schema_version"] = True
        with self.assertRaisesRegex(ValueError, "identity is invalid"):
            ATTRIBUTION.validate_snapshot(value)

    def test_measurement_rejects_symlinked_ancestor(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary).resolve()
            real = directory / "real"
            real.mkdir()
            child = real / "child"
            child.mkdir()
            alias = directory / "alias"
            alias.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "cannot be opened safely"):
                ATTRIBUTION.measure_root("test_root", alias / "child")

    def test_measurement_counts_allocated_blocks_without_following_symlinks(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary).resolve()
            (directory / "file").write_bytes(b"data")
            (directory / "link").symlink_to("file")
            value = ATTRIBUTION.measure_root("test_root", directory)
        self.assertEqual(value["state"], "present")
        self.assertGreaterEqual(value["allocated_bytes"], 0)

    def test_wide_tree_holds_descriptors_by_depth_not_width(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary).resolve()
            for index in range(100):
                (directory / f"child-{index}").mkdir()
            real_open = ATTRIBUTION.os.open
            real_close = ATTRIBUTION.os.close
            active = 0
            maximum = 0

            def tracked_open(*args, **kwargs):
                nonlocal active, maximum
                descriptor = real_open(*args, **kwargs)
                active += 1
                maximum = max(maximum, active)
                return descriptor

            def tracked_close(descriptor):
                nonlocal active
                active -= 1
                return real_close(descriptor)

            with mock.patch.object(ATTRIBUTION.os, "open", side_effect=tracked_open):
                with mock.patch.object(ATTRIBUTION.os, "close", side_effect=tracked_close):
                    ATTRIBUTION.measure_root("test_root", directory)
        self.assertEqual(active, 0)
        self.assertLessEqual(maximum, 2)

    def test_measurement_redacts_root_open_and_traversal_errors(self):
        private_path = pathlib.Path("/private/runner/path")
        with mock.patch.object(
            ATTRIBUTION,
            "open_root",
            side_effect=ValueError(f"cannot inspect {private_path}"),
        ):
            with self.assertRaises(ValueError) as context:
                ATTRIBUTION.measure_root("test_root", private_path)
        self.assertEqual(str(context.exception), "test_root: root cannot be opened safely")
        with mock.patch.object(ATTRIBUTION, "open_root", return_value=10):
            with mock.patch.object(
                ATTRIBUTION,
                "allocated_bytes",
                side_effect=OSError(f"cannot inspect {private_path}"),
            ):
                with self.assertRaises(ValueError) as context:
                    ATTRIBUTION.measure_root("test_root", private_path)
        self.assertEqual(str(context.exception), "test_root: allocated-byte measurement failed")

    def test_cli_comparison_contains_no_source_paths(self):
        values = {identifier: 0 for identifier in ATTRIBUTION.ROOTS}
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary)
            before = directory / "before.json"
            after = directory / "after.json"
            output = directory / "comparison.json"
            before.write_text(json.dumps(snapshot(values)))
            after.write_text(json.dumps(snapshot(values)))
            result = ATTRIBUTION.main(
                [
                    "compare",
                    "--before",
                    str(before),
                    "--after",
                    str(after),
                    "--output",
                    str(output),
                ]
            )
            rendered = output.read_text()
        self.assertEqual(result, 0)
        self.assertNotIn(temporary, rendered)
        self.assertEqual(json.loads(rendered)["aggregate_positive_growth_bytes"], 0)

    def test_workflow_captures_and_uploads_attribution_without_changing_tolerance(self):
        workflow = (ROOT / ".github" / "workflows" / "checks.yml").read_text()
        baseline = workflow.index("Capture external storage baseline")
        verification = workflow.index("Verify template builds")
        comparison = workflow.index("Capture external storage attribution")
        required_upload = workflow.index("Upload external storage attribution")
        general_upload = workflow.index("Upload evidence")
        self.assertLess(baseline, verification)
        self.assertLess(verification, comparison)
        self.assertLess(comparison, required_upload)
        self.assertLess(required_upload, general_upload)
        self.assertIn("if: always()", workflow[comparison:required_upload])
        self.assertIn("external-storage-attribution.json", workflow[required_upload:general_upload])
        self.assertIn("if-no-files-found: error", workflow[required_upload:general_upload])
        self.assertIn("FACTORY_STORAGE_GROWTH_TOLERANCE_MIB: 768", workflow)


if __name__ == "__main__":
    unittest.main()
