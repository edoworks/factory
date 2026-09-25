import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMMAND = ROOT / "bin" / "factory-dev"


class FactoryDevTests(unittest.TestCase):
    def run_dev(self, *args, root=None, opencode=None, overrides=None):
        environment = os.environ.copy()
        if opencode:
            environment["FACTORY_DEV_OPENCODE"] = str(opencode)
        environment.update(overrides or {})
        command = root / "bin" / "factory-dev" if root else COMMAND
        result = subprocess.run([str(command), *map(str, args)], text=True, capture_output=True, env=environment, check=False)
        return result, json.loads(result.stdout.splitlines()[0])

    def fixture(self):
        temporary = Path(tempfile.mkdtemp(prefix="factory-dev-test-")).resolve()
        self.addCleanup(shutil.rmtree, temporary)
        shutil.copytree(
            ROOT / "development",
            temporary / "development",
            ignore=shutil.ignore_patterns("node_modules"),
        )
        (temporary / "bin").mkdir()
        shutil.copy2(COMMAND, temporary / "bin" / "factory-dev")
        (temporary / "VERSION").write_text("test-version\n")
        fake = temporary / "opencode"
        fake.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = --version ]; then echo 1.18.19; "
            "else printf '{\"target\":\"%s\",\"config\":\"%s\",\"custom\":\"%s\",\"directory\":\"%s\",\"content\":\"%s\",\"permission\":\"%s\",\"pure\":\"%s\",\"future\":\"%s\",\"autoupdate\":\"%s\",\"models_fetch\":\"%s\"}\\n' "
            "\"$1\" \"$XDG_CONFIG_HOME\" \"$OPENCODE_CONFIG\" \"$OPENCODE_CONFIG_DIR\" \"$OPENCODE_CONFIG_CONTENT\" \"$OPENCODE_PERMISSION\" \"$OPENCODE_PURE\" \"$OPENCODE_FUTURE_FLAG\" \"$OPENCODE_DISABLE_AUTOUPDATE\" \"$OPENCODE_DISABLE_MODELS_FETCH\"; fi\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        return temporary, fake

    def update_manifest(self, root, relative):
        source = root / "development" / "opencode"
        manifest_path = source / "policy-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"][relative] = hashlib.sha256((source / relative).read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    def make_launch_ready(self, root):
        path = root / "development" / "opencode" / "model-routing" / "benchmarks.json"
        value = json.loads(path.read_text())
        value["results"][0]["measured_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        path.write_text(json.dumps(value, indent=2) + "\n")
        self.update_manifest(root, "model-routing/benchmarks.json")

    def test_doctor_receipt_fields_and_stable_policy_digest(self):
        first, receipt = self.run_dev("doctor")
        second, repeated = self.run_dev("doctor")
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        for field in ("factory_version", "git_revision", "dirty", "opencode_version", "policy_digest", "active_installation", "config_override", "canonical_repo"):
            self.assertIn(field, receipt)
        self.assertEqual(receipt["canonical_repo"], "edoworks/factory")
        self.assertEqual(receipt["policy_digest"], repeated["policy_digest"])
        self.assertEqual(receipt["policy_status"], "valid")
        self.assertEqual(receipt["routing_contradictions"], [])
        self.assertTrue(receipt["launch_ready"])

    def test_missing_or_mismatched_required_config_fails_closed(self):
        root, fake = self.fixture()
        config = root / "development" / "opencode" / "opencode.jsonc"
        config.write_text(config.read_text() + "\n")
        result, receipt = self.run_dev("doctor", root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(receipt["policy_status"], "invalid")
        self.assertTrue(any("digest mismatch" in error for error in receipt["errors"]))

        config.unlink()
        result, receipt = self.run_dev("doctor", root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("missing" in error for error in receipt["errors"]))

    def test_predecessor_and_symlink_targets_are_rejected(self):
        root, fake = self.fixture()
        predecessor = root / "sf0.8"
        predecessor.mkdir()
        result, receipt = self.run_dev("doctor", predecessor, root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertIn("predecessor", receipt["errors"][0])

        target = root / "product"
        target.mkdir()
        link = root / "linked-product"
        link.symlink_to(target, target_is_directory=True)
        result, receipt = self.run_dev("doctor", link, root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertIn("symlink", receipt["errors"][0])

        (target / "opencode.json").write_text("{}\n")
        result, receipt = self.run_dev("doctor", target, root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("project override" in error for error in receipt["errors"]))

        policy = root / "development" / "opencode" / "policies" / "factory-progress.md"
        policy.write_text(policy.read_text() + "\nFallback: /Users/hello/sf0.8\n")
        self.update_manifest(root, "policies/factory-progress.md")
        result, receipt = self.run_dev("doctor", root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("predecessor references" in error for error in receipt["errors"]))

    def test_ancestor_override_and_unlisted_policy_files_fail_closed(self):
        root, fake = self.fixture()
        self.make_launch_ready(root)
        parent = root / "product"
        target = parent / "nested"
        target.mkdir(parents=True)
        (parent / "opencode.jsonc").write_text("{}\n")
        result, receipt = self.run_dev("doctor", target, root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("ancestor" in error for error in receipt["errors"]))

        (parent / "opencode.jsonc").unlink()
        plugin = root / "development" / "opencode" / "plugins" / "unlisted.mjs"
        plugin.write_text("export default {};\n")
        result, receipt = self.run_dev("doctor", target, root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("unlisted policy files" in error for error in receipt["errors"]))

    def test_symlinked_policy_subtree_fails_closed(self):
        root, fake = self.fixture()
        policies = root / "development" / "opencode" / "policies"
        external = root / "external-policies"
        policies.rename(external)
        policies.symlink_to(external, target_is_directory=True)
        result, receipt = self.run_dev("doctor", root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("policy source contains a symlink" in error for error in receipt["errors"]))

    def test_symlinked_policy_root_fails_before_router_execution(self):
        root, fake = self.fixture()
        source = root / "development" / "opencode"
        external = root / "external-opencode"
        source.rename(external)
        source.symlink_to(external, target_is_directory=True)
        marker = root / "router-executed"
        router = external / "scripts" / "routing-ready.mjs"
        router.write_text(f'import {{ writeFileSync }} from "node:fs"; writeFileSync("{marker}", "executed");\n')
        result, receipt = self.run_dev("doctor", root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("source path contains a symlink" in error for error in receipt["errors"]))
        self.assertFalse(marker.exists())

    def test_symlinked_policy_parent_fails_closed(self):
        root, fake = self.fixture()
        development = root / "development"
        external = root / "external-development"
        development.rename(external)
        development.symlink_to(external, target_is_directory=True)
        result, receipt = self.run_dev("doctor", root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("development" in error and "symlink" in error for error in receipt["errors"]))

    def test_router_readiness_matches_plugin_validation(self):
        root, fake = self.fixture()
        self.make_launch_ready(root)
        benchmarks = root / "development" / "opencode" / "model-routing" / "benchmarks.json"
        value = json.loads(benchmarks.read_text())
        standard = next(item for item in value["results"] if item["provider"] == "openai" and item["tier"] == "standard")
        standard["fixture_set_sha256"] = "0" * 64
        benchmarks.write_text(json.dumps(value, indent=2) + "\n")
        self.update_manifest(root, "model-routing/benchmarks.json")
        result, receipt = self.run_dev("doctor", root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("cost-router is not launch-ready" in error for error in receipt["routing_contradictions"]))

    def test_launch_execs_with_local_config_isolation(self):
        root, fake = self.fixture()
        self.make_launch_ready(root)
        result, receipt = self.run_dev(
            "launch",
            root=root,
            opencode=fake,
            overrides={
                "OPENCODE_CONFIG": "/tmp/untrusted.json",
                "OPENCODE_CONFIG_DIR": "/tmp/untrusted",
                "OPENCODE_CONFIG_CONTENT": '{"plugin":["untrusted"]}',
                "OPENCODE_PERMISSION": '{"bash":"allow"}',
                "OPENCODE_PURE": "1",
                "OPENCODE_FUTURE_FLAG": "untrusted",
            },
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        launched = json.loads(result.stdout.splitlines()[1])
        self.assertEqual(launched["target"], str(root))
        self.assertEqual(launched["config"], str(root / "development"))
        self.assertEqual(launched["custom"], "")
        self.assertEqual(launched["directory"], "")
        self.assertEqual(launched["content"], "")
        self.assertEqual(launched["permission"], "")
        self.assertEqual(launched["pure"], "")
        self.assertEqual(launched["future"], "")
        self.assertEqual(launched["autoupdate"], "1")
        self.assertEqual(launched["models_fetch"], "1")
        self.assertTrue(
            {
                "OPENCODE_CONFIG",
                "OPENCODE_CONFIG_CONTENT",
                "OPENCODE_CONFIG_DIR",
                "OPENCODE_FUTURE_FLAG",
                "OPENCODE_PERMISSION",
                "OPENCODE_PURE",
            }.issubset(receipt["ignored_environment_overrides"]),
        )
        self.assertTrue(receipt["launch_ready"])

    def test_product_runtime_has_no_development_dependency(self):
        runtime = [ROOT / "bin" / name for name in ("factory-doctor", "factory-init", "factory-storage", "factory-verify", "factory-uninstall")]
        runtime += list((ROOT / "scripts").glob("*.py"))
        for path in runtime:
            content = path.read_text().lower()
            self.assertNotIn("opencode", content, path)
            self.assertNotIn("development/", content, path)
            self.assertNotIn(".opencode", content, path)


if __name__ == "__main__":
    unittest.main()
