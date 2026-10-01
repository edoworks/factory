import hashlib
import contextlib
import io
import json
import pathlib
import tempfile
import unittest

import scripts.check_release_consumption as validator


REVISION = "a" * 40
DIGEST = "b" * 64


def fixture():
    lock = {
        "schema_version": 1,
        "release": {"repository": "edoworks/factory", "tag": "v1.2.3-rc1", "source_revision": REVISION},
        "manifest": {"sha256": ""},
        "payload": {"asset_name": "factory-bundle.tar.gz", "sha256": DIGEST},
        "workflow": {"path": ".github/workflows/release.yml", "commit": REVISION},
    }
    manifest = {
        "schema_version": 1,
        "release": dict(lock["release"]),
        "payload": dict(lock["payload"]),
        "workflow": dict(lock["workflow"]),
        "files": [
            {"path": "skills/demo/SKILL.md", "sha256": DIGEST, "origin": "canonical:skills/demo", "license": "MIT", "notices": "LICENSE"},
            {"path": "LICENSE", "sha256": DIGEST, "origin": "canonical:LICENSE", "license": "MIT", "notices": "LICENSE"},
        ],
        "skills": {"demo": {"instructions": "skills/demo/SKILL.md", "files": ["skills/demo/SKILL.md"], "dependencies": []}},
    }
    return lock, manifest


class ReleaseConsumptionTests(unittest.TestCase):
    def invoke(self, lock_text, manifest_text):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            lock_path, manifest_path = root / "lock.json", root / "manifest.json"
            lock_path.write_text(lock_text)
            manifest_path.write_text(manifest_text)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = validator.main([str(lock_path), str(manifest_path)])
            return status, json.loads(output.getvalue())

    def assert_rejected(self, lock, manifest):
        manifest_text = json.dumps(manifest, sort_keys=True)
        lock["manifest"]["sha256"] = hashlib.sha256(manifest_text.encode()).hexdigest()
        status, receipt = self.invoke(json.dumps(lock), manifest_text)
        self.assertEqual(status, 1)
        self.assertFalse(receipt["contract_valid"])
        self.assertFalse(receipt["release_verified"])
        self.assertFalse(receipt["consumption_authorized"])
        self.assertTrue(receipt["errors"])
        return receipt["errors"]

    def test_top_level_null_fails_with_receipt(self):
        lock, manifest = fixture()
        for lock_text, manifest_text in (("null", "null"), ("null", json.dumps(manifest)), (json.dumps(lock), "null")):
            with self.subTest(lock=lock_text[:8], manifest=manifest_text[:8]):
                status, receipt = self.invoke(lock_text, manifest_text)
                self.assertEqual(status, 1)
                self.assertFalse(receipt["contract_valid"])

    def test_malformed_nested_fields_fail_with_receipt(self):
        cases = [
            ("path", []), ("path", {}), ("instructions", []), ("instructions", {}),
            ("dependencies", None), ("dependencies", 7), ("dependencies", {"demo": True}),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                lock, manifest = fixture()
                target = manifest["files"][0] if field == "path" else manifest["skills"]["demo"]
                target[field] = value
                self.assert_rejected(lock, manifest)

    def test_schema_type_confusion_fails(self):
        for version in (True, 1.0, "1", None):
            for document in ("lock", "manifest"):
                with self.subTest(version=version, document=document):
                    lock, manifest = fixture()
                    (lock if document == "lock" else manifest)["schema_version"] = version
                    self.assert_rejected(lock, manifest)

    def test_uncovered_notices_and_duplicate_declarations_fail(self):
        for field in ("files", "dependencies", "notices"):
            with self.subTest(field=field):
                lock, manifest = fixture()
                if field == "notices":
                    manifest["files"][0][field] = "missing-license.txt"
                elif field == "files":
                    manifest["skills"]["demo"][field] *= 2
                else:
                    manifest["skills"]["helper"] = {"instructions": "LICENSE", "files": ["LICENSE"], "dependencies": []}
                    manifest["skills"]["demo"][field] = ["helper", "helper"]
                self.assert_rejected(lock, manifest)

    def test_asset_name_boundaries(self):
        for name in (".", "..", "bad name", "bad\nname", "../payload", "https://example.test/asset"):
            with self.subTest(name=name):
                lock, manifest = fixture()
                lock["payload"]["asset_name"] = manifest["payload"]["asset_name"] = name
                self.assert_rejected(lock, manifest)

    def test_valid_semver_prerelease_boundaries(self):
        for tag in ("v0.1.0", "v1.2.3-0alpha", "v1.2.3-alpha.0", "v1.2.3-rc.12"):
            with self.subTest(tag=tag):
                lock, manifest = fixture()
                lock["release"]["tag"] = manifest["release"]["tag"] = tag
                paths = self.write_pair(lock, manifest)
                raw, loaded_manifest = validator.load_json(paths[1])
                self.assertEqual(validator.validate(lock, loaded_manifest, raw), [])

    def test_self_consistent_invalid_identities_fail(self):
        cases = [
            ("release", "repository", "other/factory"),
            ("release", "tag", "latest"), ("release", "tag", "main"),
            ("release", "tag", "v1.2.3-01"), ("release", "tag", "v1.2.3+build"),
            ("release", "source_revision", "a" * 39),
            ("release", "source_revision", "A" * 40),
            ("workflow", "commit", "main"), ("workflow", "path", "../release.yml"),
            ("payload", "sha256", "B" * 64),
        ]
        for section, field, value in cases:
            with self.subTest(section=section, field=field, value=value):
                lock, manifest = fixture()
                lock[section][field] = manifest[section][field] = value
                self.assert_rejected(lock, manifest)

    def test_invalid_json_and_size_limits_return_receipts(self):
        invalid_documents = [
            '{"schema_version":1,"schema_version":1}',
            '{"value":NaN}', '{"value":Infinity}', '{"value":-Infinity}',
            '{invalid', '[' * 2000 + '0' + ']' * 2000,
            ' ' * (validator.MAX_JSON_BYTES + 1),
        ]
        for invalid in invalid_documents:
            with self.subTest(prefix=invalid[:32]):
                status, receipt = self.invoke(invalid, "null")
                self.assertEqual(status, 1)
                self.assertFalse(receipt["contract_valid"])
                self.assertFalse(receipt["consumption_authorized"])
                self.assertLessEqual(len(receipt["errors"]), 64)
                self.assertTrue(all(len(error) <= 512 for error in receipt["errors"]))

    def test_unknown_authority_fields_and_missing_inputs_fail(self):
        lock, manifest = fixture()
        lock["consumption_authorized"] = True
        self.assert_rejected(lock, manifest)
        for args in ([], ["missing.json", "missing-manifest.json"]):
            with self.subTest(args=args):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(validator.main(args), 1)
                self.assertFalse(json.loads(output.getvalue())["contract_valid"])

    def write_pair(self, lock, manifest, lock_text=None, manifest_text=None):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = pathlib.Path(directory.name)
        manifest_text = manifest_text or json.dumps(manifest, sort_keys=True)
        lock["manifest"]["sha256"] = hashlib.sha256(manifest_text.encode()).hexdigest()
        lock_text = lock_text or json.dumps(lock, sort_keys=True)
        lock_path, manifest_path = root / "lock.json", root / "manifest.json"
        lock_path.write_text(lock_text)
        manifest_path.write_text(manifest_text)
        return lock_path, manifest_path

    def test_valid_illustrative_fixture(self):
        lock, manifest = fixture()
        lock_path, manifest_path = self.write_pair(lock, manifest)
        raw, loaded_lock = validator.load_json(lock_path)
        manifest_bytes, loaded_manifest = validator.load_json(manifest_path)
        self.assertEqual(validator.validate(loaded_lock, loaded_manifest, manifest_bytes), [])
        self.assertEqual(raw[:1], b"{")

    def test_manifest_byte_mismatch_and_identity_mismatches(self):
        lock, manifest = fixture()
        lock_path, manifest_path = self.write_pair(lock, manifest)
        manifest_path.write_text(manifest_path.read_text() + "\n")
        _, loaded_lock = validator.load_json(lock_path)
        manifest_bytes, loaded_manifest = validator.load_json(manifest_path)
        errors = validator.validate(loaded_lock, loaded_manifest, manifest_bytes)
        self.assertTrue(any("exact manifest file bytes" in error for error in errors))
        for section, field, value in (("release", "repository", "other/repo"), ("release", "tag", "latest"), ("release", "source_revision", "c" * 40), ("workflow", "path", "other.yml"), ("workflow", "commit", "c" * 40), ("payload", "sha256", "c" * 64)):
            changed_lock, changed_manifest = fixture()
            changed_manifest[section][field] = value
            path_lock, path_manifest = self.write_pair(changed_lock, changed_manifest)
            _, loaded_lock = validator.load_json(path_lock)
            manifest_bytes, loaded_manifest = validator.load_json(path_manifest)
            self.assertTrue(validator.validate(loaded_lock, loaded_manifest, manifest_bytes))

    def test_bad_selectors_paths_and_hashes(self):
        lock, manifest = fixture()
        manifest["release"]["tag"] = "v1.2.3+build"
        manifest["files"][0]["path"] = "../escape"
        manifest["files"][1]["sha256"] = "B" * 64
        lock_path, manifest_path = self.write_pair(lock, manifest)
        _, loaded_lock = validator.load_json(lock_path)
        manifest_bytes, loaded_manifest = validator.load_json(manifest_path)
        errors = validator.validate(loaded_lock, loaded_manifest, manifest_bytes)
        self.assertGreaterEqual(len(errors), 3)
        for path in ("/absolute", "a\\b", "a//b", "a/./b"):
            lock, manifest = fixture()
            manifest["files"][0]["path"] = path
            errors = self.assert_rejected(lock, manifest)
            self.assertTrue(any("POSIX" in error or "traversal" in error for error in errors))

    def test_duplicate_keys_and_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as directory:
            duplicate = pathlib.Path(directory) / "duplicate.json"
            duplicate.write_text('{"schema_version": 1, "schema_version": 1}')
            with self.assertRaises(ValueError):
                validator.load_json(duplicate)
            nonfinite = pathlib.Path(directory) / "nonfinite.json"
            nonfinite.write_text('{"value": NaN}')
            with self.assertRaises(ValueError):
                validator.load_json(nonfinite)

    def test_transitive_resources_missing_dependency_and_cycle(self):
        lock, manifest = fixture()
        manifest["skills"]["demo"]["files"] = ["missing.md"]
        manifest["skills"]["demo"]["dependencies"] = ["missing"]
        errors = self.assert_rejected(lock, manifest)
        self.assertTrue(any("missing inventoried file" in error for error in errors))
        self.assertTrue(any("missing bundled skill" in error for error in errors))
        lock, manifest = fixture()
        manifest["skills"]["other"] = {"instructions": "LICENSE", "files": ["LICENSE"], "dependencies": ["demo"]}
        manifest["skills"]["demo"]["dependencies"] = ["other"]
        self.assertTrue(any("cyclic" in error for error in self.assert_rejected(lock, manifest)))

    def test_missing_license_and_malformed_types(self):
        lock, manifest = fixture()
        manifest["files"][0]["license"] = ""
        manifest["files"][1]["notices"] = 7
        manifest["skills"] = []
        errors = self.assert_rejected(lock, manifest)
        self.assertTrue(any("license" in error for error in errors))
        self.assertTrue(any("notices" in error for error in errors))
        self.assertTrue(any("skills" in error for error in errors))

    def test_receipt_never_authorizes(self):
        lock, manifest = fixture()
        lock_path, manifest_path = self.write_pair(lock, manifest)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(validator.main([str(lock_path), str(manifest_path)]), 0)
        receipt = json.loads(output.getvalue())
        self.assertTrue(receipt["contract_valid"])
        self.assertFalse(receipt["release_verified"])
        self.assertFalse(receipt["consumption_authorized"])


if __name__ == "__main__":
    unittest.main()
