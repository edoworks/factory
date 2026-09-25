import copy
import contextlib
import datetime
import importlib.util
import io
import json
import pathlib
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "docs" / "product-portfolio-index.json"
SCRIPT_PATH = ROOT / "scripts" / "check_product_portfolio.py"
SPEC = importlib.util.spec_from_file_location("check_product_portfolio", SCRIPT_PATH)
PORTFOLIO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PORTFOLIO)


class ProductPortfolioTests(unittest.TestCase):
    def setUp(self):
        self.index = json.loads(INDEX_PATH.read_text())
        self.now = datetime.datetime(2026, 9, 26, tzinfo=datetime.timezone.utc)

    def test_canonical_index_is_valid_and_complete(self):
        self.assertEqual(PORTFOLIO.validate(self.index, now=self.now), [])
        self.assertEqual(
            {record["id"] for record in self.index["records"]},
            PORTFOLIO.EXPECTED_RECORD_IDS,
        )
        self.assertNotIn("public_repository_observations", self.index)

    def test_index_rejects_stale_or_future_evidence(self):
        stale = PORTFOLIO.validate(
            self.index,
            now=datetime.datetime(2026, 10, 27, tzinfo=datetime.timezone.utc),
        )
        self.assertIn("portfolio evidence is stale", stale)
        future = copy.deepcopy(self.index)
        future["observed_at"] = "2026-09-27T00:00:00Z"
        self.assertIn("observed_at cannot be in the future", PORTFOLIO.validate(future, now=self.now))

    def test_index_rejects_duplicate_product_and_repository_ownership(self):
        duplicate_id = copy.deepcopy(self.index)
        duplicate_id["records"][1]["id"] = duplicate_id["records"][0]["id"]
        errors = PORTFOLIO.validate(duplicate_id, now=self.now)
        self.assertIn("portfolio record IDs must be unique", errors)

        duplicate_repository = copy.deepcopy(self.index)
        duplicate_repository["records"][1]["canonical_repository"] = "edoworks/nownest"
        errors = PORTFOLIO.validate(duplicate_repository, now=self.now)
        self.assertIn("canonical repository ownership must be unique", errors)

    def test_index_rejects_unsupported_mapping_lifecycle_and_tracker_claims(self):
        changed_repository = copy.deepcopy(self.index)
        changed_repository["records"][0]["canonical_repository"] = "edoworks/artifacts"
        errors = PORTFOLIO.validate(changed_repository, now=self.now)
        self.assertTrue(any("approved canonical binding" in error for error in errors))

        promoted = copy.deepcopy(self.index)
        promoted["records"][0]["lifecycle_state"] = "RELEASED"
        promoted["records"][0]["public_claim"] = "released"
        errors = PORTFOLIO.validate(promoted, now=self.now)
        self.assertTrue(any("approved canonical binding" in error for error in errors))

        reassigned = copy.deepcopy(self.index)
        reassigned["records"][0]["owning_tracker"] = "edoworks/factory#13"
        errors = PORTFOLIO.validate(reassigned, now=self.now)
        self.assertTrue(any("approved canonical binding" in error for error in errors))

    def test_private_and_unknown_records_fail_closed(self):
        private_path = copy.deepcopy(self.index)
        private_path["records"][3]["canonical_repository"] = "/Users/private/repository"
        errors = PORTFOLIO.validate(private_path, now=self.now)
        self.assertTrue(any("private repository must use an opaque reference" in error for error in errors))
        self.assertTrue(any("absolute local path" in error for error in errors))

        promoted_unknown = copy.deepcopy(self.index)
        promoted_unknown["records"][4]["public_claim"] = "released"
        errors = PORTFOLIO.validate(promoted_unknown, now=self.now)
        self.assertTrue(any("approved canonical binding" in error for error in errors))

        private_identity = copy.deepcopy(self.index)
        private_identity["records"][4]["evidence_source"] = "git@github.com:private/repo.git"
        errors = PORTFOLIO.validate(private_identity, now=self.now)
        self.assertTrue(any("SSH repository identity" in error for error in errors))

    def test_unhashable_schema_values_return_errors(self):
        malformed = copy.deepcopy(self.index)
        malformed["records"][0]["id"] = ["nownest"]
        malformed["records"][0]["record_kind"] = ["product"]
        malformed["records"][0]["lifecycle_state"] = ["VALIDATING"]
        malformed["records"][1]["product_prd_reference"] = ["private"]
        errors = PORTFOLIO.validate(malformed, now=self.now)
        self.assertTrue(errors)

    def test_public_prd_reference_binds_exact_revision_and_path(self):
        wrong_revision = copy.deepcopy(self.index)
        wrong_revision["records"][0]["product_prd_reference"] = (
            "edoworks/nownest@0000000000000000000000000000000000000000:docs/customer-zero-prd.md"
        )
        errors = PORTFOLIO.validate(wrong_revision, now=self.now)
        self.assertTrue(any("approved canonical binding" in error for error in errors))
        self.assertTrue(any("bind the evidence revision" in error for error in errors))

    def test_duplicate_json_keys_are_rejected_without_echoing_key(self):
        with self.assertRaises(ValueError) as context:
            PORTFOLIO.reject_duplicate_keys(
                [("/Users/private/path", "one"), ("/Users/private/path", "two")]
            )
        self.assertEqual(str(context.exception), "duplicate JSON key")

    def test_cli_malformed_input_failure_is_path_safe(self):
        malformed = copy.deepcopy(self.index)
        malformed["records"][0]["product_prd_reference"] = ["/Users/private/path"]
        with tempfile.TemporaryDirectory() as temporary:
            source = pathlib.Path(temporary) / "private-input.json"
            source.write_text(json.dumps(malformed))
            stderr = io.StringIO()
            with mock.patch.object(PORTFOLIO, "INDEX_PATH", source):
                with contextlib.redirect_stderr(stderr):
                    result = PORTFOLIO.main([])
        self.assertEqual(result, 1)
        self.assertNotIn(temporary, stderr.getvalue())
        self.assertNotIn("/Users/private/path", stderr.getvalue())

    def test_workflow_and_prd_pin_the_portfolio_contract(self):
        workflow = (ROOT / ".github" / "workflows" / "checks.yml").read_text()
        prd = (ROOT / "docs" / "FactoryDevelopment-PRD.md").read_text()
        cutover = (ROOT / "docs" / "single-factory-cutover.md").read_text()
        self.assertIn("python3 scripts/check_product_portfolio.py", workflow)
        self.assertIn("## Canonical Portfolio Index", prd)
        self.assertIn("Tracker: issue #78", cutover)
        self.assertIn("does not establish preservation or deletion readiness", cutover)


if __name__ == "__main__":
    unittest.main()
