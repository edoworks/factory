import hashlib
import json
import pathlib
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SingleFactoryContractTests(unittest.TestCase):
    def test_charter_names_one_factory_and_separates_states(self):
        charter = (ROOT / "CHARTER.md").read_text()

        self.assertIn("### Single Factory Law", charter)
        self.assertIn("`edoworks/factory` is the sole canonical software factory", charter)
        for state in (
            "CANONICAL_FOR_NEW_WORK",
            "OPERATIONALLY_CUT_OVER",
            "PRESERVATION_VERIFIED",
            "READY_FOR_OWNER_DELETION_APPROVAL",
            "REMOTE_DELETION_COMPLETED",
            "LOCAL_CLEANUP_COMPLETED",
        ):
            self.assertIn(state, charter)

    def test_cutover_is_not_gated_by_product_qualification(self):
        charter = (ROOT / "CHARTER.md").read_text()
        predecessor_section = charter.split("## Predecessor Disposition", 1)[1]

        self.assertIn(
            "Choosing the sole active factory does not complete product qualification",
            predecessor_section,
        )
        self.assertNotIn("Two Apple-accepted reference apps", predecessor_section)
        self.assertNotIn("never deleted", predecessor_section.lower())

    def test_development_runtime_boundary_is_explicit(self):
        charter = (ROOT / "CHARTER.md").read_text()
        prd = (ROOT / "docs" / "FactoryDevelopment-PRD.md").read_text()
        normalized_charter = " ".join(charter.split())
        normalized_prd = " ".join(prd.split())

        self.assertIn("Product runtime", charter)
        self.assertIn("Factory development", charter)
        self.assertIn("must not become a runtime dependency", normalized_charter)
        self.assertIn(
            "Runtime commands and generated products must not import",
            normalized_prd,
        )
        self.assertIn("bin/factory-dev", prd)

    def test_product_prds_do_not_infer_qualification(self):
        focusgate = (ROOT / "docs" / "FocusGate-PRD.md").read_text()
        mews = (ROOT / "docs" / "MewsAndWoofs-PRD.md").read_text()

        self.assertIn("does not alter or complete", focusgate)
        self.assertIn("does not qualify this product", mews)

    def test_development_policy_is_fail_closed_for_shell_and_plugins(self):
        config = json.loads(
            (ROOT / "development" / "opencode" / "opencode.jsonc").read_text()
        )
        plugins = config["plugin"]
        permissions = config["permission"]["bash"]

        self.assertNotIn("@frankhommers/opencode-yolo", plugins)
        self.assertEqual(permissions["*"], "deny")
        for mutation in ("gh issue create*", "gh issue comment*", "gh issue close*"):
            self.assertEqual(permissions[mutation], "deny")
        interactive = {
            "gh issue create --repo edoworks/factory *",
            "gh issue comment --repo edoworks/factory *",
            "gh issue close --repo edoworks/factory *",
            "open https://github.com/edoworks/factory/*",
        }
        self.assertEqual(
            {pattern for pattern, action in permissions.items() if action == "ask"},
            interactive,
        )
        self.assertEqual(
            permissions["python3 ~/.agents/skills/macos-screenshot/scripts/screenshot.py *"],
            "allow",
        )
        for command in ("hash *", "validate *", "verify-remote *"):
            self.assertEqual(
                permissions[f"node development/opencode/scripts/issue-intent.mjs {command}"],
                "allow",
            )
        self.assertNotIn(
            "python3 */.agents/skills/macos-screenshot/scripts/screenshot.py *",
            permissions,
        )
        for command in ("create", "comment", "close"):
            self.assertEqual(
                permissions[f"gh issue {command} --repo edoworks/factory *--repo*"],
                "deny",
            )
            self.assertEqual(
                permissions[f"gh issue {command} --repo edoworks/factory *-R*"],
                "deny",
            )
        self.assertEqual(
            permissions["gh pr * --repo edoworks/factory *--repo*"], "deny"
        )
        self.assertEqual(
            permissions["gh pr * --repo edoworks/factory *-R*"], "deny"
        )
        self.assertEqual(
            permissions["open https://github.com/edoworks/factory/* *"], "deny"
        )

        prd = (ROOT / "docs" / "FactoryDevelopment-PRD.md").read_text()
        self.assertIn("interactive `ask` operations", prd)
        self.assertIn("auto mode", prd)
        self.assertIn("fixed home-directory installation", prd)

    def test_issue_intent_hash_command_is_deterministic(self):
        body = ROOT / "docs" / "FactoryDevelopment-PRD.md"
        result = subprocess.run(
            [
                "node",
                str(
                    ROOT
                    / "development"
                    / "opencode"
                    / "scripts"
                    / "issue-intent.mjs"
                ),
                "hash",
                str(body),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), hashlib.sha256(body.read_bytes()).hexdigest())
        rejected = subprocess.run(
            [
                "node",
                str(
                    ROOT
                    / "development"
                    / "opencode"
                    / "scripts"
                    / "issue-intent.mjs"
                ),
                "hash",
                str(body),
                "extra",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("usage: issue-intent.mjs hash BODY.md", rejected.stderr)

    def test_later_cutover_states_remain_unclaimed(self):
        record = (ROOT / "docs" / "single-factory-cutover.md").read_text()

        self.assertIn(
            "| `CANONICAL_FOR_NEW_WORK` | VERIFIED by merged PR #71 and the matching installed continuation |",
            record,
        )
        expected = {
            "OPERATIONALLY_CUT_OVER": "NOT VERIFIED",
            "PRESERVATION_VERIFIED": "NOT VERIFIED",
            "READY_FOR_OWNER_DELETION_APPROVAL": "NOT VERIFIED",
            "REMOTE_DELETION_COMPLETED": "NOT PERFORMED",
            "LOCAL_CLEANUP_COMPLETED": "NOT PERFORMED",
        }
        for state, result in expected.items():
            matching = [line for line in record.splitlines() if f"`{state}`" in line]
            self.assertEqual(matching, [f"| `{state}` | {result} |"])


if __name__ == "__main__":
    unittest.main()
