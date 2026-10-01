import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "bin" / "factory-verify"
BASELINE_REVISION = "0ff8117a75882a656aa20451e5c21244a3910b28"


class FactoryVerifyAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "factory"
        (self.root / "bin").mkdir(parents=True)
        (self.root / "scripts").mkdir()
        shutil.copy2(VERIFIER, self.root / "bin" / "factory-verify")
        self._write_helper(
            self.root / "bin" / "find-simulators.py",
            """#!/usr/bin/env python3
print('IPHONE=known-phone')
print('IPAD=known-pad')
print('IPHONE_NAME=Fixture iPhone')
print('IPHONE_TYPE=iPhone')
print('IPHONE_RUNTIME=iOS')
print('IPAD_NAME=Fixture iPad')
print('IPAD_TYPE=iPad')
print('IPAD_RUNTIME=iOS')
""",
        )
        self._write_helper(
            self.root / "scripts" / "factory_storage.py",
            """#!/usr/bin/env python3
import json
import os
import sys

operation = sys.argv[1]
log = os.environ['FIXTURE_STORAGE_LOG']
with open(log, 'a', encoding='utf-8') as stream:
    stream.write(json.dumps(sys.argv[1:]) + '\\n')
if operation == 'reserve':
    print(json.dumps({'reservation_id': 'fixture', 'available_bytes': 100000000000}))
elif operation == 'finish':
    print(json.dumps({'schema_version': 1, 'storage_policy_status': 'PASS',
                      'outcome': sys.argv[sys.argv.index('--outcome') + 1]}))
elif operation in ('observe', 'settle'):
    pass
else:
    raise SystemExit('unknown storage operation: ' + operation)
""",
        )
        self.bin = self.root / "controlled-bin"
        self.bin.mkdir()
        self._write_helper(
            self.bin / "xcrun",
            """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$FIXTURE_XCRUN_LOG"
if [[ "$1" != simctl ]]; then
  printf 'unknown xcrun operation\\n' >&2
  exit 97
fi
case "$2" in
  create) printf 'fixture-simulator\\n' ;;
  shutdown|delete) exit 0 ;;
  *) printf 'unknown simctl operation\\n' >&2; exit 97 ;;
esac
""",
        )
        self._write_helper(
            self.bin / "xcodebuild",
            """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$FIXTURE_XCODEBUILD_LOG"
case "$1" in
  analyze)
    printf '%s' "${FIXTURE_ANALYZE_OUTPUT-}"
    printf '%s' "${FIXTURE_ANALYZE_STDERR-}" >&2
    if [[ "${FIXTURE_REMOVE_ANALYZE_LOG-0}" == 1 ]]; then
      for run_root in .factory/runs/*; do rm -f "$run_root/static-analysis.log"; done
    fi
    exit "${FIXTURE_ANALYZE_STATUS-0}" ;;
  build)
    if [[ "${FIXTURE_BLOCK_ANALYZE_LOG-0}" == 1 ]]; then
      for run_root in .factory/runs/*; do mkdir -p "$run_root/static-analysis.log"; done
    fi
    exit 0 ;;
  test|archive) exit 0 ;;
  *) printf 'unknown xcodebuild operation\\n' >&2; exit 97 ;;
esac
""",
        )
        (self.root / "TestApp.xcodeproj").mkdir()
        (self.root / "TestApp.xcodeproj" / "project.pbxproj").write_text("fixture\n")
        (self.root / "project.yml").write_text("name: TestApp\n")
        self.home = Path(self.temporary.name) / "home"
        self.home.mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    def _write_helper(self, path, contents):
        path.write_text(contents)
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def run_verifier(self, status, output, stderr="stderr: companion\n", block_log=False, remove_log=False):
        storage_log = self.root / "storage.log"
        xcodebuild_log = self.root / "xcodebuild.log"
        xcrun_log = self.root / "xcrun.log"
        for log in (storage_log, xcodebuild_log, xcrun_log):
            log.write_text("")
        shutil.rmtree(self.root / ".factory", ignore_errors=True)
        environment = {
            "PATH": f"{self.bin}:/usr/bin:/bin",
            "HOME": str(self.home),
            "FACTORY_VERIFY_MAX_GIB": "1",
            "FACTORY_RECOVERY_FLOOR_GIB": "1",
            "FACTORY_STORAGE_GROWTH_TOLERANCE_MIB": "64",
            "FIXTURE_ANALYZE_STATUS": str(status),
            "FIXTURE_ANALYZE_OUTPUT": output,
            "FIXTURE_ANALYZE_STDERR": stderr,
            "FIXTURE_BLOCK_ANALYZE_LOG": "1" if block_log else "0",
            "FIXTURE_REMOVE_ANALYZE_LOG": "1" if remove_log else "0",
            "FIXTURE_STORAGE_LOG": str(storage_log),
            "FIXTURE_XCODEBUILD_LOG": str(xcodebuild_log),
            "FIXTURE_XCRUN_LOG": str(xcrun_log),
        }
        completed = subprocess.run(
            [str(self.root / "bin" / "factory-verify")],
            cwd=self.root,
            env=environment,
            text=True,
            capture_output=True,
            timeout=15,
        )
        receipt = json.loads((self.root / ".factory-verify-result.json").read_text())
        if not any(step["step"] == "static_analysis" for step in receipt["steps"]):
            self.fail(
                f"verifier did not reach analysis: stdout={completed.stdout!r} "
                f"stderr={completed.stderr!r} xcodebuild={xcodebuild_log.read_text() if xcodebuild_log.exists() else None!r} "
                f"xcrun={(self.root / 'xcrun.log').read_text() if (self.root / 'xcrun.log').exists() else None!r}"
            )
        analysis = next(step for step in receipt["steps"] if step["step"] == "static_analysis")
        run_logs = sorted((self.root / ".factory" / "runs").glob("*/static-analysis.log"))
        self.assertEqual(
            [line.split()[0] for line in xcodebuild_log.read_text().splitlines()],
            ["build", "test", "build", "archive"] if block_log else ["build", "test", "build", "analyze", "archive"],
        )
        return completed, receipt, analysis, run_logs, [json.loads(line) for line in storage_log.read_text().splitlines()]

    def test_analyzer_outcomes_and_owned_diagnostics(self):
        cases = (
            (0, "", "pass", "No warnings"),
            (0, "warning: first\nwarning: second\n", "pass", "2 warnings"),
            (65, 'error: bad\nraw \\ "quote"\n', "fail", "exit status 65"),
            (65, "warning: despite failure\n", "fail", "exit status 65"),
            (65, "", "fail", "exit status 65"),
            (124, "timeout\n", "fail", "exit status 124"),
            (137, "killed\n", "fail", "exit status 137"),
            (143, "terminated\n", "fail", "exit status 143"),
        )
        for status, output, expected_status, detail in cases:
            with self.subTest(status=status, output=output):
                stderr = "" if status and not output else "stderr: companion\n"
                completed, receipt, analysis, run_logs, storage = self.run_verifier(status, output, stderr)
                self.assertEqual(
                    completed.returncode,
                    0 if expected_status == "pass" else 1,
                    receipt["steps"],
                )
                self.assertEqual(analysis["status"], expected_status)
                self.assertIn(detail, analysis["detail"])
                self.assertEqual([call[0] for call in storage].count("reserve"), 1)
                finish = [call for call in storage if call[0] == "finish"]
                self.assertEqual(len(finish), 1)
                expected_outcome = "PASSED" if expected_status == "pass" else "FAILED"
                self.assertEqual(finish[0][finish[0].index("--outcome") + 1], expected_outcome)
                self.assertEqual(receipt["storage"]["outcome"], expected_outcome)
                if expected_status == "fail":
                    self.assertEqual(receipt["failed"], 1, receipt["steps"])
                    self.assertEqual(len(run_logs), 1)
                    self.assertEqual(run_logs[0].read_text(), output + stderr)
                    self.assertIn(str(run_logs[0].parent.relative_to(self.root)), finish[0])
                    self.assertIn("--retained-artifact", finish[0])
                    if "raw" in output:
                        self.assertIn('raw \\ "quote"', run_logs[0].read_text())
                        self.assertNotIn("raw", analysis["detail"])
                else:
                    self.assertEqual(receipt["failed"], 0)
                    self.assertEqual(run_logs, [])

    def test_historical_false_pass_with_the_same_controlled_tools(self):
        baseline = subprocess.run(
            ["/usr/bin/git", "--no-pager", "show", f"{BASELINE_REVISION}:bin/factory-verify"],
            cwd=ROOT,
            env={"PATH": "/usr/bin:/bin", "HOME": str(self.home),
                 "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
                 "GIT_NO_REPLACE_OBJECTS": "1"},
            capture_output=True,
            timeout=10,
        )
        if baseline.returncode:
            self.skipTest("historical reproduction requires the retained baseline Git object; current regression cases still run")
        (self.root / "bin" / "factory-verify").write_bytes(baseline.stdout)
        for status in (65, 124, 137, 143):
            with self.subTest(status=status):
                completed, receipt, analysis, run_logs, storage = self.run_verifier(status, "error: baseline probe\n")
                self.assertEqual(completed.returncode, 0)
                self.assertEqual(receipt["failed"], 0)
                self.assertEqual(analysis["status"], "pass")
                self.assertEqual(receipt["storage"]["outcome"], "PASSED")
                self.assertEqual(run_logs, [])

    def test_log_creation_failure_cannot_be_reported_as_analysis_success(self):
        completed, receipt, analysis, run_logs, storage = self.run_verifier(0, "", block_log=True)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(receipt["failed"], 1)
        self.assertEqual(analysis["status"], "fail")
        self.assertIn("diagnostics log could not be created", analysis["detail"])
        self.assertEqual(receipt["storage"]["outcome"], "FAILED")
        self.assertEqual(len(run_logs), 1)
        self.assertTrue(run_logs[0].is_dir())
        finish = next(call for call in storage if call[0] == "finish")
        self.assertIn(str(run_logs[0].parent.relative_to(self.root)), finish)

    def test_successful_analyzer_with_missing_diagnostics_fails_verification(self):
        completed, receipt, analysis, run_logs, storage = self.run_verifier(
            0, "warning: evidence must be readable\n", remove_log=True,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(receipt["failed"], 1)
        self.assertEqual(analysis["status"], "fail")
        self.assertIn("diagnostics could not be read", analysis["detail"])
        self.assertNotIn("No warnings", analysis["detail"])
        self.assertEqual(receipt["storage"]["outcome"], "FAILED")
        self.assertEqual(run_logs, [])
        roots = list((self.root / ".factory" / "runs").iterdir())
        self.assertEqual(len(roots), 1)
        finish = next(call for call in storage if call[0] == "finish")
        self.assertIn(str(roots[0].relative_to(self.root)), finish)


if __name__ == "__main__":
    unittest.main()
