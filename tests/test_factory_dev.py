import hashlib
import importlib.machinery
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import types
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMMAND = ROOT / "bin" / "factory-dev"


class FactoryDevTests(unittest.TestCase):
    def load_command_module(self):
        module = types.ModuleType("factory_dev_test_module")
        importlib.machinery.SourceFileLoader(module.__name__, str(COMMAND)).exec_module(module)
        return module

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
            "if [ \"$1\" = --version ]; then if [ -n \"$NODE_OPTIONS\" ]; then exit 98; fi; if [ -n \"${OPENAI_API_KEY+x}\" ]; then exit 99; fi; echo 1.18.19; "
            "else printf '{\"target\":\"%s\",\"config\":\"%s\",\"github\":\"%s\",\"factory_gh\":\"%s\",\"factory_node\":\"%s\",\"path\":\"%s\",\"gh_host\":\"%s\",\"gh_token\":\"%s\",\"github_token\":\"%s\",\"enterprise_token\":\"%s\",\"http_socket\":\"%s\",\"node_options\":\"%s\",\"openai_key_present\":\"%s\",\"custom\":\"%s\",\"directory\":\"%s\",\"content\":\"%s\",\"permission\":\"%s\",\"pure\":\"%s\",\"future\":\"%s\",\"autoupdate\":\"%s\",\"models_fetch\":\"%s\"}\\n' "
            "\"$1\" \"$XDG_CONFIG_HOME\" \"$GH_CONFIG_DIR\" \"$FACTORY_DEV_GH\" \"$FACTORY_DEV_NODE\" \"$PATH\" \"$GH_HOST\" \"$GH_TOKEN\" \"$GITHUB_TOKEN\" \"$GH_ENTERPRISE_TOKEN\" \"$GH_HTTP_UNIX_SOCKET\" \"$NODE_OPTIONS\" \"${OPENAI_API_KEY+yes}\" \"$OPENCODE_CONFIG\" \"$OPENCODE_CONFIG_DIR\" \"$OPENCODE_CONFIG_CONTENT\" \"$OPENCODE_PERMISSION\" \"$OPENCODE_PURE\" \"$OPENCODE_FUTURE_FLAG\" \"$OPENCODE_DISABLE_AUTOUPDATE\" \"$OPENCODE_DISABLE_MODELS_FETCH\"; fi\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        return temporary, fake

    def update_manifest(self, root, relative):
        source = root / "development" / "opencode"
        manifest_path = source / "policy-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"][relative] = hashlib.sha256((source / relative).read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    def test_tracked_policy_manifest_matches_sources(self):
        source = ROOT / "development" / "opencode"
        manifest = json.loads((source / "policy-manifest.json").read_text())
        for relative, expected in manifest["files"].items():
            actual = hashlib.sha256((source / relative).read_bytes()).hexdigest()
            self.assertEqual(expected, actual, relative)

    def test_active_controls_match_baseline_when_installed(self):
        source = ROOT / "development" / "opencode"
        active = Path.home() / ".config" / "opencode"
        baseline = json.loads((source / "active-baseline.json").read_text())
        installed = [
            relative
            for relative in baseline["files"]
            if (active / relative).is_file()
        ]
        if not installed:
            self.skipTest("Factory OpenCode controls are not installed")
        self.assertEqual(set(installed), set(baseline["files"]))
        for relative, expected in baseline["files"].items():
            actual = hashlib.sha256((active / relative).read_bytes()).hexdigest()
            self.assertEqual(expected, actual, relative)

    def make_benchmarks_ready(self, root):
        path = root / "development" / "opencode" / "model-routing" / "benchmarks.json"
        value = json.loads(path.read_text())
        value["results"][0]["measured_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        path.write_text(json.dumps(value, indent=2) + "\n")
        self.update_manifest(root, "model-routing/benchmarks.json")

    def make_launch_ready(self, root):
        self.make_benchmarks_ready(root)
        path = root / "development" / "opencode" / "model-routing" / "catalog.json"
        value = json.loads(path.read_text())
        value["refreshed_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        path.write_text(json.dumps(value, indent=2) + "\n")
        self.update_manifest(root, "model-routing/catalog.json")

    def test_doctor_receipt_fields_and_stable_policy_digest(self):
        root, fake = self.fixture()
        self.make_launch_ready(root)
        first, receipt = self.run_dev("doctor", root=root, opencode=fake)
        second, repeated = self.run_dev("doctor", root=root, opencode=fake)
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        for field in ("factory_version", "git_revision", "dirty", "opencode_version", "policy_digest", "active_installation", "config_override", "canonical_repo"):
            self.assertIn(field, receipt)
        self.assertEqual(receipt["canonical_repo"], "edoworks/factory")
        self.assertEqual(receipt["policy_digest"], repeated["policy_digest"])
        self.assertEqual(receipt["policy_status"], "valid")
        self.assertEqual(receipt["routing_contradictions"], [])
        self.assertTrue(receipt["launch_ready"])

    def test_github_cli_provenance_rejects_escape_and_writable_binary(self):
        module = self.load_command_module()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "Cellar" / "gh"
            binary = package / "1.0" / "bin" / "gh"
            binary.parent.mkdir(parents=True)
            binary.write_text("#!/bin/sh\nexit 0\n")
            binary.chmod(0o755)
            link = root / "bin" / "gh"
            link.parent.mkdir()
            link.symlink_to(binary)
            module.TRUSTED_GITHUB_CLI_PATHS = (link,)
            module.TRUSTED_GITHUB_CLI_ROOTS = {package}
            self.assertEqual(module.trusted_github_cli(), binary.resolve())

            binary.chmod(0o775)
            self.assertIsNone(module.trusted_github_cli())
            binary.chmod(0o755)
            outside = root / "outside-gh"
            outside.write_text("#!/bin/sh\nexit 0\n")
            outside.chmod(0o755)
            link.unlink()
            link.symlink_to(outside)
            self.assertIsNone(module.trusted_github_cli())

    def test_node_provenance_rejects_broken_and_writable_binaries(self):
        module = self.load_command_module()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "Cellar" / "node"
            broken = package / "1.0" / "bin" / "node"
            malformed = package / "1.5" / "bin" / "node"
            working = package / "2.0" / "bin" / "node"
            broken.parent.mkdir(parents=True)
            malformed.parent.mkdir(parents=True)
            working.parent.mkdir(parents=True)
            broken.write_text("#!/bin/sh\nexit 1\n")
            malformed.write_text("#!/bin/sh\nprintf 'not-node\\n'\n")
            working.write_text("#!/bin/sh\nprintf 'v22.0.0\\n'\n")
            broken.chmod(0o755)
            malformed.chmod(0o755)
            working.chmod(0o755)
            module.TRUSTED_NODE_PATHS = (broken, malformed, working)
            module.TRUSTED_NODE_ROOTS = {package}
            self.assertEqual(module.trusted_node(), working.resolve())

            working.chmod(0o775)
            self.assertIsNone(module.trusted_node())

            working.chmod(0o755)
            working.parent.chmod(0o775)
            self.assertIsNone(module.trusted_node())

            working.parent.chmod(0o755)
            package.chmod(0o775)
            self.assertIsNone(module.trusted_node())

    def test_trusted_node_runs_repository_policy_suite(self):
        module = self.load_command_module()
        node = module.trusted_node()
        self.assertIsNotNone(node)
        source = ROOT / "development" / "opencode"
        result = subprocess.run(
            [
                node,
                "--test",
                source / "scripts" / "continuation-command.test.mjs",
                source / "scripts" / "git-push.test.mjs",
                source / "scripts" / "import-routing-catalog.test.mjs",
                source / "scripts" / "issue-closeout.test.mjs",
                source / "plugins" / "cost-router.test.mjs",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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

    def test_router_readiness_requires_expected_receipt(self):
        root, fake = self.fixture()
        self.make_launch_ready(root)
        script = root / "development" / "opencode" / "scripts" / "routing-ready.mjs"
        script.write_text("process.stdout.write('unexpected\\n');\n")
        self.update_manifest(root, "scripts/routing-ready.mjs")
        result, receipt = self.run_dev("doctor", root=root, opencode=fake)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("unexpected" in error for error in receipt["routing_contradictions"]))

    def test_launch_execs_with_local_config_isolation(self):
        root, fake = self.fixture()
        self.make_launch_ready(root)
        fake_gh = root / "gh"
        fake_gh.write_text("#!/bin/sh\nexit 0\n")
        fake_gh.chmod(fake_gh.stat().st_mode | stat.S_IXUSR)
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
                "XDG_CONFIG_HOME": "/tmp/user-config",
                "GH_CONFIG_DIR": "",
                "GH_HOST": "enterprise.invalid",
                "GH_TOKEN": "untrusted-gh-token",
                "GITHUB_TOKEN": "untrusted-github-token",
                "GH_ENTERPRISE_TOKEN": "untrusted-enterprise-token",
                "GH_HTTP_UNIX_SOCKET": "/tmp/untrusted.sock",
                "NODE_OPTIONS": "--require=/tmp/untrusted.js",
                "OPENAI_API_KEY": "test-only-stale-key",
                "PATH": f"{root}:{os.environ['PATH']}",
            },
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        launched = json.loads(result.stdout.splitlines()[1])
        self.assertEqual(launched["target"], str(root))
        self.assertEqual(launched["config"], str(root / "development"))
        self.assertEqual(launched["github"], "/tmp/user-config/gh")
        trusted_gh = next(path.resolve() for path in (Path("/opt/homebrew/bin/gh"), Path("/usr/local/bin/gh"), Path("/usr/bin/gh"), Path("/home/linuxbrew/.linuxbrew/bin/gh")) if path.is_file())
        self.assertEqual(launched["factory_gh"], str(trusted_gh))
        self.assertNotEqual(launched["factory_gh"], str(fake_gh.resolve()))
        self.assertEqual(launched["factory_node"], receipt["node_cli"])
        self.assertEqual(launched["path"], "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/home/linuxbrew/.linuxbrew/bin")
        self.assertEqual(launched["gh_host"], "")
        self.assertEqual(launched["gh_token"], "")
        self.assertEqual(launched["github_token"], "")
        self.assertEqual(launched["enterprise_token"], "")
        self.assertEqual(launched["http_socket"], "")
        self.assertEqual(launched["node_options"], "")
        self.assertEqual(launched["openai_key_present"], "")
        self.assertNotIn("test-only-stale-key", result.stdout)
        self.assertNotIn("test-only-stale-key", result.stderr)
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

    def test_refresh_catalog_imports_generated_evidence_and_restores_readiness(self):
        root, fake = self.fixture()
        self.make_benchmarks_ready(root)
        catalog = root / "development" / "opencode" / "model-routing" / "catalog.json"
        generated = json.loads(catalog.read_text())
        generated["generation"] = "1790335243580-66796"
        generated["refreshed_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        home = root / "home"
        source = home / ".config" / "opencode" / "model-routing" / "catalog.json"
        source.parent.mkdir(parents=True)
        source.write_text(json.dumps(generated, indent=2) + "\n")

        stale = dict(generated)
        stale["generation"] = "1-1"
        stale["refreshed_at"] = "2000-01-01T00:00:00Z"
        catalog.write_text(json.dumps(stale, indent=2) + "\n")
        self.update_manifest(root, "model-routing/catalog.json")

        result, receipt = self.run_dev(
            "refresh-catalog",
            root=root,
            opencode=fake,
            overrides={"HOME": str(home)},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(receipt["command"], "factory-dev refresh-catalog")
        self.assertEqual(receipt["catalog_import"]["generation"], generated["generation"])
        self.assertTrue(receipt["launch_ready"])
        self.assertEqual(json.loads(catalog.read_text())["generation"], generated["generation"])
        manifest = json.loads((root / "development" / "opencode" / "policy-manifest.json").read_text())
        self.assertEqual(manifest["files"]["model-routing/catalog.json"], hashlib.sha256(catalog.read_bytes()).hexdigest())

    def test_tracked_catalog_matches_available_generated_user_evidence(self):
        generated = Path.home() / ".config" / "opencode" / "model-routing" / "catalog.json"
        if not generated.is_file():
            self.skipTest("generated user catalog is unavailable")
        root, fake = self.fixture()
        self.make_benchmarks_ready(root)
        result, receipt = self.run_dev("refresh-catalog", root=root, opencode=fake)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(receipt["launch_ready"])
        imported = root / "development" / "opencode" / "model-routing" / "catalog.json"
        tracked = ROOT / "development" / "opencode" / "model-routing" / "catalog.json"
        self.assertEqual(imported.read_bytes(), tracked.read_bytes())

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
