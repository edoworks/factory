import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("rubberduck_validator", ROOT / "development" / "opencode" / "scripts" / "validate-rubberduck.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RubberduckValidatorTests(unittest.TestCase):
    def setUp(self):
        self.ledger = json.loads((ROOT / "docs" / "rubberduck-research-2026-09-26.json").read_text())
        self.report = (ROOT / "docs" / "rubberduck-research-2026-09-26.md").read_text()

    def fixture(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["receipts"]["post"] = {
            "available": True,
            "command": "bin/factory-dev doctor",
            "captured_at": "2026-09-26",
            "git_revision": self.ledger["receipts"]["pre"]["git_revision"],
            "dirty": True,
            "doctor_ready": True,
            "write_ready": False,
            "launch_ready": False,
            "policy_status": "valid",
            "routing_contradictions": [],
            "errors": [],
            "source": "docs/issue-intents/113/rubberduck-gates-progress.md",
        }
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name)
        self.addCleanup(directory.cleanup)
        ledger_path = path / "ledger.json"
        report_path = path / "report.md"
        ledger_path.write_text(json.dumps(ledger))
        report_path.write_text(self.report)
        self.approved_post = copy.deepcopy(ledger["receipts"]["post"])
        return ledger, ledger_path, report_path

    def validate(self, ledger_path, report_path):
        original = MODULE.APPROVED_RECEIPTS["post"]
        MODULE.APPROVED_RECEIPTS["post"] = copy.deepcopy(self.approved_post)
        self.addCleanup(MODULE.APPROVED_RECEIPTS.__setitem__, "post", original)
        return MODULE.validate(ledger_path, report_path)

    def assert_invalid(self, ledger, report=None, message=""):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            ledger_path = path / "ledger.json"
            report_path = path / "report.md"
            ledger_path.write_text(json.dumps(ledger))
            report_path.write_text(self.report if report is None else report)
            with self.assertRaisesRegex(ValueError, message or ".+"):
                self.validate(ledger_path, report_path)

    def test_valid_temporary_ledger_accepts_dirty_post_without_write_or_launch(self):
        ledger, ledger_path, report_path = self.fixture()
        self.assertTrue(self.validate(ledger_path, report_path))
        self.assertEqual(ledger["receipts"]["post"]["write_ready"], False)

    def test_receipt_phase_semantics_are_distinct(self):
        ledger, _, _ = self.fixture()
        ledger["receipts"]["pre"]["dirty"] = True
        self.assert_invalid(ledger, message="pre receipt")
        ledger, _, _ = self.fixture()
        ledger["receipts"]["post"]["dirty"] = False
        self.assert_invalid(ledger, message="post receipt")
        ledger, ledger_path, report_path = self.fixture()
        ledger["receipts"]["post"]["write_ready"] = True
        ledger["receipts"]["post"]["launch_ready"] = True
        ledger_path.write_text(json.dumps(ledger))
        self.assert_invalid(ledger, message="validator-approved")

        ledger, _, _ = self.fixture()
        ledger["receipts"]["post"]["git_revision"] = "not-a-revision"
        self.assert_invalid(ledger, message="revision")

        ledger, _, _ = self.fixture()
        ledger["receipts"]["post"]["dirty"] = 1
        self.assert_invalid(ledger, message="boolean")

    def test_canonical_ledger_passes_with_approved_post_receipt(self):
        self.assertTrue(MODULE.validate())

    def test_each_disposition_invariant(self):
        ledger, _, _ = self.fixture()
        ledger["candidates"][0]["disposition"] = "INVESTIGATE NOW"
        self.assert_invalid(ledger, message="investigate-now")
        ledger, _, _ = self.fixture()
        approved = copy.deepcopy(MODULE.APPROVED_PASS_ASSERTIONS)
        for gate_id, gate in ledger["candidates"][0]["gates"].items():
            gate["state"] = "PASS"
            gate["evidence"] = [f"wcag-22: {gate_id}: dated fixture assertion"]
            MODULE.APPROVED_PASS_ASSERTIONS[(ledger["candidates"][0]["id"], gate_id)] = frozenset(
                {("wcag-22", f"{gate_id}: dated fixture assertion")}
            )
        try:
            self.assert_invalid(ledger, message="watch candidate")
        finally:
            MODULE.APPROVED_PASS_ASSERTIONS.clear()
            MODULE.APPROVED_PASS_ASSERTIONS.update(approved)
        ledger, _, _ = self.fixture()
        ledger["candidates"][3]["disposition"] = "WATCH"
        self.assert_invalid(ledger, message="watch candidate")
        ledger, _, _ = self.fixture()
        for gate in ledger["candidates"][3]["gates"].values():
            gate["state"] = "MISSING"
            gate["evidence"] = ["UNKNOWN: missing"]
        self.assert_invalid(ledger, message="reject candidate")

    def test_pass_cannot_cite_unknown(self):
        ledger, _, _ = self.fixture()
        gate = ledger["candidates"][0]["gates"]["ai_essential"]
        gate["state"] = "PASS"
        gate["evidence"] = ["UNKNOWN: not proven"]
        self.assert_invalid(ledger, message="PASS cannot")

    def test_pass_requires_validator_owned_gate_assertion(self):
        ledger, _, _ = self.fixture()
        gate = ledger["candidates"][0]["gates"]["risk"]
        gate["state"] = "PASS"
        gate["evidence"] = ["wcag-22: risk: plausible but unapproved assertion"]
        self.assert_invalid(ledger, message="validator-approved")

    def test_unknown_fields_are_rejected_at_each_nested_level(self):
        mutations = [
            lambda x: x.update(extra=True),
            lambda x: x["sources"][0].update(extra=True),
            lambda x: x["candidates"][0].update(extra=True),
            lambda x: x["candidates"][0]["gates"]["risk"].update(extra=True),
            lambda x: x["candidates"][0]["unit_economics"].update(extra=True),
            lambda x: x["receipts"]["pre"].update(extra=True),
        ]
        for mutate in mutations:
            ledger, _, _ = self.fixture()
            mutate(ledger)
            self.assert_invalid(ledger, message=".")

    def test_duplicate_keys_source_dates_and_evidence_binding_fail(self):
        duplicate_documents = [
            '{"schema_version":1,"schema_version":1}',
            '{"sources":[{"id":"a","id":"b"}]}',
            '{"candidates":[{"id":"a","id":"b"}]}',
            '{"gates":{"risk":{"state":"MISSING","state":"PASS"}}}',
            '{"receipts":{"pre":{"available":true,"available":false}}}',
            '{"unit_economics":{"cost_range":"a","cost_range":"b"}}',
        ]
        for document in duplicate_documents:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "duplicate.json"
                path.write_text(document + "\n")
                with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                    MODULE.load_json(path)
        ledger, _, _ = self.fixture()
        ledger["sources"][0]["accessed_at"] = "2026-09-25"
        self.assert_invalid(ledger, message="accessed date")
        ledger, _, _ = self.fixture()
        ledger["candidates"][0]["gates"]["ai_essential"]["evidence"] = ["not-a-source"]
        self.assert_invalid(ledger, message="source-bound")

        ledger, _, _ = self.fixture()
        gate = ledger["candidates"][0]["gates"]["ai_essential"]
        gate["state"] = "PASS"
        gate["evidence"] = ["w3c-evaluation: ai_essential: undated evidence"]
        self.assert_invalid(ledger, message="published")

    def test_report_sections_order_duplicates_and_no_candidate_sentence_fail(self):
        ledger, _, _ = self.fixture()
        self.assert_invalid(ledger, self.report.replace("## WATCH", "## REJECT", 1), "headings")
        self.assert_invalid(ledger, self.report.replace("### Candidate: generic-browser-agent-automation", "### Candidate: accessibility-regression-review", 1), "candidates")
        self.assert_invalid(ledger, self.report.replace("No candidate is INVESTIGATE NOW.", "No candidate is ready."), "no-candidate")
        self.assert_invalid(ledger, self.report.replace("Disposition: WATCH", "Disposition: REJECT", 1), "disposition text")

    def test_cli_accepts_canonical_approved_receipts(self):
        _, ledger_path, report_path = self.fixture()
        script = ROOT / "development" / "opencode" / "scripts" / "validate-rubberduck.py"
        self.assertTrue(self.validate(ledger_path, report_path))
        result = subprocess.run([sys.executable, script], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "VALID\n")

if __name__ == "__main__":
    unittest.main()
