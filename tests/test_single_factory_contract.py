import hashlib
import importlib.machinery
import json
import os
import pathlib
import stat
import subprocess
import tempfile
import types
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def working_node():
    module = types.ModuleType("factory_dev_contract_module")
    importlib.machinery.SourceFileLoader(module.__name__, str(ROOT / "bin" / "factory-dev")).exec_module(module)
    node = module.trusted_node()
    if not node:
        raise RuntimeError("a trusted working Node.js executable is required")
    return str(node)


NODE = working_node()


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
        self.assertEqual(permissions["python3 -m unittest*"], "deny")
        self.assertEqual(permissions["node --test*"], "deny")
        self.assertEqual(permissions["{env:FACTORY_DEV_NODE} --test*"], "deny")
        self.assertEqual(permissions["python3 -m unittest discover -s {env:FACTORY_DEV_OPENCODE_ROOT}/../../tests"], "allow")
        self.assertEqual(
            permissions["{env:FACTORY_DEV_NODE} --test {env:FACTORY_DEV_OPENCODE_ROOT}/scripts/continuation-command.test.mjs {env:FACTORY_DEV_OPENCODE_ROOT}/scripts/git-push.test.mjs {env:FACTORY_DEV_OPENCODE_ROOT}/plugins/cost-router.test.mjs"],
            "allow",
        )
        for mutation in ("gh issue create*", "gh issue comment*", "gh issue close*"):
            self.assertEqual(permissions[mutation], "deny")
        interactive = {
            "{env:FACTORY_DEV_NODE} {env:FACTORY_DEV_OPENCODE_ROOT}/scripts/issue-intent.mjs create *",
            "{env:FACTORY_DEV_NODE} {env:FACTORY_DEV_OPENCODE_ROOT}/scripts/issue-intent.mjs comment *",
            "{env:FACTORY_DEV_NODE} {env:FACTORY_DEV_OPENCODE_ROOT}/scripts/issue-intent.mjs close *",
            "{env:FACTORY_DEV_NODE} {env:FACTORY_DEV_OPENCODE_ROOT}/scripts/git-push.mjs feature/* *",
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
                permissions[f"{{env:FACTORY_DEV_NODE}} {{env:FACTORY_DEV_OPENCODE_ROOT}}/scripts/issue-intent.mjs {command}"],
                "allow",
            )
        self.assertNotIn(
            "node development/opencode/scripts/issue-intent.mjs validate *",
            permissions,
        )
        self.assertNotIn("./bin/factory-dev doctor*", permissions)
        self.assertEqual(
            permissions["{env:FACTORY_DEV_OPENCODE_ROOT}/../../bin/factory-dev doctor*"],
            "allow",
        )
        self.assertFalse(any(pattern.startswith("gh ") and action in {"allow", "ask"} for pattern, action in permissions.items()))
        self.assertTrue(all("{env:FACTORY_DEV_GH}" in pattern for pattern, action in permissions.items() if action == "allow" and (" issue " in pattern or " pr " in pattern or " api " in pattern)))
        self.assertFalse(any("credential.helper" in pattern and action == "allow" for pattern, action in permissions.items()))
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
            permissions["{env:FACTORY_DEV_GH} pr * --repo edoworks/factory *--repo*"], "deny"
        )
        self.assertEqual(
            permissions["{env:FACTORY_DEV_GH} pr * --repo edoworks/factory *-R*"], "deny"
        )
        self.assertEqual(permissions["{env:FACTORY_DEV_GH} pr *https://*"], "deny")
        self.assertEqual(permissions["{env:FACTORY_DEV_GH} pr *http://*"], "deny")
        self.assertEqual(permissions["{env:FACTORY_DEV_GH} issue * --repo edoworks/factory *--repo*"], "deny")
        self.assertEqual(permissions["{env:FACTORY_DEV_GH} issue * --repo edoworks/factory *-R*"], "deny")
        self.assertEqual(permissions["{env:FACTORY_DEV_GH} issue *https://*"], "deny")
        self.assertEqual(permissions["{env:FACTORY_DEV_GH} issue *http://*"], "deny")
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
                NODE,
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
                NODE,
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

    def test_issue_intent_validation_creation_and_readback_are_bound(self):
        script = ROOT / "development" / "opencode" / "scripts" / "issue-intent.mjs"
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary)
            body = "".join(
                f"# {section}\n\nEvidence for {section}.\n\n"
                for section in (
                    "Outcome", "Scope", "Out of scope", "Acceptance criteria",
                    "Verification", "Dependencies", "Authority and privacy",
                    "Source provenance", "Classification", "Priority", "Triage review",
                )
            )
            (directory / "body.md").write_text(body)
            intent = {
                "schema_version": 1,
                "repo": "edoworks/factory",
                "title": "Bound intent",
                "body_file": "body.md",
                "body_sha256": hashlib.sha256(body.encode()).hexdigest(),
                "classification": "enhancement",
                "priority": "P1",
                "labels": ["enhancement"],
                "dependencies": ["none"],
                "authority_constraints": ["owner approval"],
                "source_provenance": ["test fixture"],
                "duplicate_review": ["none found"],
                "reprioritization_review": ["bounded test"],
            }
            intent_path = directory / "intent.json"
            intent_path.write_text(json.dumps(intent))
            remote = directory / "remote.json"
            remote.write_text(json.dumps({"title": intent["title"], "body": body, "labels": [{"name": "enhancement"}]}))
            capture = directory / "captured.json"
            fake_gh = directory / "gh"
            fake_gh.write_text(
                "#!/bin/sh\n"
                "if [ \"$1 $2 $3 $4 $5 $6\" = \"api --hostname github.com user --jq .login\" ]; then printf 'hellofoculoom\\n'; exit 0; fi\n"
                "if [ \"$1\" = issue ] && [ \"$2\" = view ]; then cat \"$FAKE_REMOTE\"; exit 0; fi\n"
                "python3 -c 'import json, os, sys; open(os.environ[\"FAKE_CAPTURE\"], \"w\").write(json.dumps(sys.argv[1:]))' \"$@\"\n"
                "printf 'https://github.com/edoworks/factory/issues/999\\n'\n"
            )
            fake_gh.chmod(fake_gh.stat().st_mode | stat.S_IXUSR)
            environment = os.environ | {
                "PATH": f"{directory}:{os.environ['PATH']}",
                "FACTORY_DEV_GH": str(fake_gh),
                "FAKE_REMOTE": str(remote),
                "FAKE_CAPTURE": str(capture),
            }

            validated = subprocess.run([NODE, str(script), "validate", str(intent_path)], text=True, capture_output=True, env=environment, check=False)
            self.assertEqual(validated.returncode, 0, validated.stderr)
            self.assertEqual(validated.stdout, "VALID\n")
            created = subprocess.run([NODE, str(script), "create", str(intent_path)], text=True, capture_output=True, env=environment, check=False)
            self.assertEqual(created.returncode, 0, created.stderr)
            args = json.loads(capture.read_text())
            self.assertEqual(args[:4], ["issue", "create", "--repo", "github.com/edoworks/factory"])
            self.assertEqual(args[args.index("--title") + 1], intent["title"])
            self.assertEqual(args[args.index("--body") + 1], body)
            hostile = directory / "hostile" / "gh"
            hostile.parent.mkdir()
            hostile.write_text("#!/bin/sh\nexit 99\n")
            hostile.chmod(hostile.stat().st_mode | stat.S_IXUSR)
            environment["PATH"] = f"{hostile.parent}:{environment['PATH']}"
            readback = subprocess.run([NODE, str(script), "verify-remote", str(intent_path), "999"], text=True, capture_output=True, env=environment, check=False)
            self.assertEqual(readback.returncode, 0, readback.stderr)
            self.assertEqual(readback.stdout, "MATCH\n")

            comment_body = directory / "comment.md"
            comment_body.write_text("Verified evidence.\n")
            commented = subprocess.run([NODE, str(script), "comment", "999", str(comment_body)], text=True, capture_output=True, env=environment, check=False)
            self.assertEqual(commented.returncode, 0, commented.stderr)
            self.assertEqual(json.loads(capture.read_text()), ["issue", "comment", "--repo", "github.com/edoworks/factory", "999", "--body-file", str(comment_body.resolve())])
            closed = subprocess.run([NODE, str(script), "close", "999"], text=True, capture_output=True, env=environment, check=False)
            self.assertEqual(closed.returncode, 0, closed.stderr)
            self.assertEqual(json.loads(capture.read_text()), ["issue", "close", "--repo", "github.com/edoworks/factory", "999"])

            fake_gh.write_text("#!/bin/sh\nif [ \"$1\" = api ]; then printf 'wrong-user\\n'; exit 0; fi\nexit 99\n")
            rejected_identity = subprocess.run([NODE, str(script), "create", str(intent_path)], text=True, capture_output=True, env=environment, check=False)
            self.assertNotEqual(rejected_identity.returncode, 0)
            self.assertIn("GitHub identity must be hellofoculoom", rejected_identity.stderr)

            intent["body_sha256"] = "0" * 64
            intent_path.write_text(json.dumps(intent))
            rejected = subprocess.run([NODE, str(script), "validate", str(intent_path)], text=True, capture_output=True, env=environment, check=False)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("body_sha256 does not match", rejected.stderr)

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
