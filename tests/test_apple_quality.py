#!/usr/bin/env python3
"""Tests for the ported apple-quality validator."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "apple-quality.py"


def valid_record():
    return {
        "design_intent": {
            "who": "A person who wants to track something locally",
            "feel": "Calm and focused",
            "notice_first": "The content, not the chrome",
            "primary_experience": "Quick capture and retrieval",
            "can_disappear": "Yes, the app respects focus",
            "motion": "Minimal, purposeful",
            "sound": "None",
            "physicality": "Direct touch",
            "magic": "It remembers what I needed without asking",
            "zero_explanation": "Open and use immediately",
            "distinctive": "Local-only, no accounts, no friction",
            "current_apple_capabilities": ["SwiftUI", "UserDefaults", "ShareLink"]
        },
        "apple_capability_review": {
            "capabilities": [
                {
                    "name": "SwiftUI",
                    "source": "Apple framework",
                    "maturity": "STABLE",
                    "deployment_target": "iOS 18.0",
                    "disposition": "USE_NOW",
                    "reason": "Core UI framework",
                    "fallback": ""
                }
            ]
        },
        "experience_evidence": {
            "rendered": "Simulator screenshot showing the primary view",
            "verification": "SIMULATOR_VERIFIED",
            "attention_first": "The content list",
            "generic_or_distinctive": "Distinctive due to local-only constraint",
            "remove_next": "Nothing yet",
            "critic_findings": "No critical issues found"
        },
        "design_debt": [],
        "apple_platform_debt": []
    }


class AppleQualityValidatorTests(unittest.TestCase):
    def test_valid_record_passes(self):
        record = valid_record()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(record, f)
            f.flush()
            result = subprocess.run(
                [sys.executable, str(SCRIPT), f.name],
                capture_output=True, text=True
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("passed", result.stdout)

    def test_missing_design_intent_field_fails(self):
        record = valid_record()
        del record["design_intent"]["who"]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(record, f)
            f.flush()
            result = subprocess.run(
                [sys.executable, str(SCRIPT), f.name],
                capture_output=True, text=True
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing design-intent field: who", result.stdout)

    def test_invalid_maturity_fails(self):
        record = valid_record()
        record["apple_capability_review"]["capabilities"][0]["maturity"] = "BOGUS"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(record, f)
            f.flush()
            result = subprocess.run(
                [sys.executable, str(SCRIPT), f.name],
                capture_output=True, text=True
            )
        self.assertEqual(result.returncode, 1)

    def test_missing_evidence_rendered_fails(self):
        record = valid_record()
        del record["experience_evidence"]["rendered"]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(record, f)
            f.flush()
            result = subprocess.run(
                [sys.executable, str(SCRIPT), f.name],
                capture_output=True, text=True
            )
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()