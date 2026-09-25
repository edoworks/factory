import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_consolidation_evidence.py"
SPEC = importlib.util.spec_from_file_location("check_consolidation_evidence", SCRIPT)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ConsolidationPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(VALIDATOR.CONTRACT_PATH.read_text())

    def public_record(self, **changes):
        item = {
            "evidence_class": "repository_history",
            "disposition": "public_safe_reference",
            "provenance_reference": "edoworks/factory#68",
            "inventory_reference": VALIDATOR.EXPECTED_INVENTORY_REFERENCES[
                "repository_history"
            ],
        }
        item.update(changes)
        return {"schema_version": 1, "records": [item]}

    def test_contract_classifies_all_required_evidence_private_by_default(self):
        self.assertEqual(VALIDATOR.validate_contract(self.contract), [])
        self.assertEqual(self.contract["default_disposition"], "private")
        inventory = self.contract["evidence_inventory"]
        self.assertEqual(
            {item["evidence_class"] for item in inventory},
            VALIDATOR.REQUIRED_EVIDENCE_CLASSES,
        )
        self.assertTrue(all(item["source_disposition"] == "private" for item in inventory))
        self.assertTrue(
            all(item["storage_class"] == "owner_controlled_private" for item in inventory)
        )
        self.assertEqual(
            self.contract["storage_classes"]["owner_controlled_private"]["status"],
            "REQUIRED_NOT_PROVISIONED",
        )

    def test_prd_separates_classification_from_private_instance_inventory(self):
        prd = (ROOT / "docs" / "FactoryDevelopment-PRD.md").read_text()
        cutover = (ROOT / "docs" / "single-factory-cutover.md").read_text()
        normalized_prd = " ".join(prd.split())
        normalized_cutover = " ".join(cutover.split())
        self.assertIn("The issue #77 privacy contract", normalized_prd)
        self.assertIn(
            "classifies the required evidence classes, not concrete",
            normalized_prd,
        )
        self.assertIn("The sole public classification record", normalized_prd)
        self.assertIn(
            "Issue #81 owns the separate private instance inventory",
            normalized_prd,
        )
        self.assertIn("Tracker: issue #77", normalized_cutover)
        self.assertIn(
            "does not replace the private instance inventory",
            normalized_cutover,
        )

    def test_contract_policy_cannot_authorize_new_public_fields(self):
        contract = copy.deepcopy(self.contract)
        contract["public_record_contract"]["prohibited_fields"].remove("credentials")
        contract["public_record_contract"]["allowed_fields"].append("credentials")
        errors = VALIDATOR.validate_contract(contract)
        self.assertTrue(any("allowed fields are invalid" in error for error in errors))
        self.assertTrue(any("prohibited fields are invalid" in error for error in errors))

    def test_contract_cannot_redirect_the_public_inventory(self):
        contract = copy.deepcopy(self.contract)
        contract["public_record_files"] = ["docs/replacement.json"]
        errors = VALIDATOR.validate_contract(contract)
        self.assertTrue(any("pinned canonical manifest" in error for error in errors))

    def test_contract_rejects_unknown_fields_at_every_level(self):
        mutations = []
        root = copy.deepcopy(self.contract)
        root["payload"] = "private"
        mutations.append(root)
        public_contract = copy.deepcopy(self.contract)
        public_contract["public_record_contract"]["payload"] = "private"
        mutations.append(public_contract)
        inventory = copy.deepcopy(self.contract)
        inventory["evidence_inventory"][0]["payload"] = "private"
        mutations.append(inventory)
        storage = copy.deepcopy(self.contract)
        storage["storage_classes"]["owner_controlled_private"]["payload"] = "private"
        mutations.append(storage)
        for contract in mutations:
            with self.subTest(contract=contract):
                self.assertTrue(VALIDATOR.validate_contract(contract))

    def test_reference_only_public_record_passes(self):
        self.assertEqual(
            VALIDATOR.validate_public_record(self.contract, self.public_record()), []
        )

    def test_unknown_and_prohibited_public_fields_fail_closed(self):
        record = self.public_record(
            credentials="not-even-a-real-secret",
            unexpected="ambiguous",
        )
        errors = VALIDATOR.validate_public_record(self.contract, record)
        self.assertTrue(any("credentials" in error for error in errors))
        self.assertTrue(any("unexpected" in error for error in errors))

    def test_private_values_fail_even_in_allowlisted_fields(self):
        private_values = (
            "/Users/example/private-overlay",
            "person@example.com",
            "s3://private-preservation/location",
            "https://operator:password@example.com/receipt",
            "github_pat_abcdefghijklmnopqrstuvwxyz1234567890",
            "/var/private-evidence",
            "/home/operator/private-evidence",
            "C:\\private-evidence",
            "-----BEGIN PRIVATE KEY-----",
            "AKIAIOSFODNN7EXAMPLE",
        )
        for value in private_values:
            with self.subTest(value=value):
                record = self.public_record(provenance_reference=value)
                self.assertTrue(
                    VALIDATOR.validate_public_record(self.contract, record),
                    value,
                )

    def test_unknown_class_and_invalid_checksum_fail(self):
        record = self.public_record(
            evidence_class="unknown_material",
            checksum_sha256="ABC123",
        )
        errors = VALIDATOR.validate_public_record(self.contract, record)
        self.assertTrue(any("unknown evidence_class" in error for error in errors))
        self.assertTrue(any("lowercase SHA-256" in error for error in errors))

    def test_unapproved_checksum_and_recovery_reference_fail_closed(self):
        self.assertEqual(VALIDATOR.APPROVED_PUBLIC_CHECKSUMS, set())
        self.assertEqual(VALIDATOR.APPROVED_PUBLIC_RECOVERY_RECEIPTS, set())
        record = self.public_record(
            checksum_sha256="0" * 64,
            recovery_receipt_reference="RECOVERY-20260925-01",
        )
        errors = VALIDATOR.validate_public_record(self.contract, record)
        self.assertTrue(
            any("checksum_sha256 is not approved" in error for error in errors)
        )
        self.assertTrue(
            any(
                "recovery_receipt_reference is not approved" in error
                for error in errors
            )
        )

        checksum = "0" * 64
        receipt = "RECOVERY-20260925-01"
        checksum_record = self.public_record(
            evidence_class="checksums",
            inventory_reference=VALIDATOR.EXPECTED_INVENTORY_REFERENCES["checksums"],
            checksum_sha256=checksum,
        )
        receipt_record = self.public_record(
            evidence_class="recovery_receipts",
            inventory_reference=VALIDATOR.EXPECTED_INVENTORY_REFERENCES[
                "recovery_receipts"
            ],
            recovery_receipt_reference=receipt,
        )
        with mock.patch.object(
            VALIDATOR,
            "APPROVED_PUBLIC_CHECKSUMS",
            {("checksums", checksum)},
        ), mock.patch.object(
            VALIDATOR,
            "APPROVED_PUBLIC_RECOVERY_RECEIPTS",
            {("recovery_receipts", receipt)},
        ):
            self.assertEqual(
                VALIDATOR.validate_public_record(self.contract, checksum_record), []
            )
            self.assertEqual(
                VALIDATOR.validate_public_record(self.contract, receipt_record), []
            )
            wrong_class = self.public_record(
                checksum_sha256=checksum,
                recovery_receipt_reference=receipt,
            )
            errors = VALIDATOR.validate_public_record(self.contract, wrong_class)
            self.assertTrue(
                any("checksum_sha256 is not approved" in error for error in errors)
            )
            self.assertTrue(
                any(
                    "recovery_receipt_reference is not approved" in error
                    for error in errors
                )
            )

    def test_cli_validates_contract_and_public_records(self):
        with tempfile.TemporaryDirectory() as temporary:
            record_path = pathlib.Path(temporary) / "public-record.json"
            record_path.write_text(json.dumps(self.public_record()))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(record_path)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "VALID\n")

    def test_cli_always_validates_complete_tracked_public_inventory(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "VALID\n")
        public_record = json.loads(
            (ROOT / VALIDATOR.CANONICAL_PUBLIC_RECORD_FILES[0]).read_text()
        )
        self.assertEqual(
            {record["evidence_class"] for record in public_record["records"]},
            VALIDATOR.REQUIRED_EVIDENCE_CLASSES,
        )
        workflow = (ROOT / ".github" / "workflows" / "checks.yml").read_text()
        self.assertIn("python3 scripts/check_consolidation_evidence.py", workflow)

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "duplicate.json"
            path.write_text(
                '{"schema_version":1,"records":[{'
                '"evidence_class":"repository_history",'
                '"disposition":"public_safe_reference",'
                '"provenance_reference":"github_pat_abcdefghijklmnopqrstuvwxyz1234567890",'
                '"provenance_reference":"edoworks/factory#68"}]}'
            )
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                VALIDATOR.load_json(path)


if __name__ == "__main__":
    unittest.main()
