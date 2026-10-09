import copy
import contextlib
import io
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import benchmark
from requirements import HEADING, validate_prd

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'tests/fixtures/safe-share-prd.md'


class RequirementsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='factory-requirements-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.prd = self.root / 'PRD.md'
        self.value = json.loads(EXAMPLE.read_text().split('```json\n')[1].split('\n```')[0])

    def write(self, value=None):
        self.prd.write_text(HEADING + '\n\n```json\n' + json.dumps(value or self.value) + '\n```\n')

    def receipt(self, result='passed'):
        item = self.value['capabilities'][0]
        receipt = {'result': result, 'source': {k: item['source'][k] for k in ('reference', 'revision')},
                   'recorded_at': '2026-10-09T16:00:00Z', 'artifact_sha256': item['artifact_sha256'],
                   'scope': item['scope'], 'command': 'synthetic fixture test; not executed by validator',
                   'environment': 'unit-test fixture only', 'consumer': item['consumer'], 'interface': item['interface']}
        raw = json.dumps(receipt).encode()
        (self.root / 'receipt.json').write_bytes(raw)
        item['evidence'] = {'path': 'receipt.json', 'sha256': hashlib.sha256(raw).hexdigest()}

    def rejected(self, value=None):
        self.write(value)
        with self.assertRaises((ValueError, OSError)):
            validate_prd(self.prd)

    def test_real_prd_and_safe_share_candidate_with_unknowns(self):
        for path in (ROOT / 'PRD.md', EXAMPLE):
            self.assertEqual(validate_prd(path)['status'], 'declarations_valid')
        self.value['capabilities'][0]['status'] = 'unknown'
        self.write()
        self.assertEqual(validate_prd(self.prd)['capabilities'], 1)

    def test_missing_duplicate_sections_and_duplicate_json_keys_fail(self):
        for content in ('# No section', HEADING + '\n' + HEADING,
                        HEADING + '\n```json\n{"schema_version":1,"schema_version":1,"capabilities":[]}\n```'):
            self.prd.write_text(content)
            with self.assertRaises(ValueError): validate_prd(self.prd)

    def test_status_only_promotion_fails(self):
        for status in ('verified', 'reused', 'production_ready'):
            item = copy.deepcopy(self.value); item['capabilities'][0]['status'] = status
            self.rejected(item)

    def test_required_fields_and_types(self):
        for field in self.value['capabilities'][0]:
            item = copy.deepcopy(self.value); del item['capabilities'][0][field]
            self.rejected(item)
        for field, bad in [('limitations', []), ('source', {}), ('artifact_sha256', 'not-a-hash'),
                           ('contribution', {'change': 'build'}), ('status', {}), ('evidence', [])]:
            item = copy.deepcopy(self.value); item['capabilities'][0][field] = bad
            self.rejected(item)

    def test_promoted_claim_needs_passing_exact_receipt_and_source(self):
        item = self.value['capabilities'][0]; item['status'] = 'verified'
        for result in ('not_run', 'failed'):
            self.receipt(result); self.rejected()
        self.receipt(); self.write()
        self.assertEqual(validate_prd(self.prd)['status'], 'declarations_valid')
        for field, change in [('artifact_sha256', 'a' * 64), ('scope', 'physical device and security')]:
            bad = copy.deepcopy(self.value); bad['capabilities'][0][field] = change
            self.rejected(bad)
        bad = copy.deepcopy(self.value); bad['capabilities'][0]['source']['revision'] = None
        self.rejected(bad)
        bad = copy.deepcopy(self.value); bad['capabilities'][0]['source']['revision'] = 'different-source'
        self.rejected(bad)
        (self.root / 'receipt.json').write_text('{}')
        self.rejected()

    def test_reused_claim_requires_consumer_interface_license_attribution(self):
        item = self.value['capabilities'][0]; item['status'] = 'reused'
        self.receipt(); self.rejected()
        item['source'].update(license='MIT (synthetic test only)', attribution='Fixture author')
        item.update(consumer='Synthetic test consumer', interface='fixture-v1')
        self.rejected()  # Old receipt has no matching consumer or interface.
        self.receipt(); self.write()
        self.assertEqual(validate_prd(self.prd)['status'], 'declarations_valid')
        for field in ('license', 'attribution'):
            bad = copy.deepcopy(self.value); bad['capabilities'][0]['source'][field] = None
            self.rejected(bad)

    def test_evidence_path_containment(self):
        self.receipt()
        (self.root / 'link.json').symlink_to(self.root / 'receipt.json')
        for path in ('../receipt.json', str(self.root / 'receipt.json'), 'link.json'):
            bad = copy.deepcopy(self.value); bad['capabilities'][0]['evidence']['path'] = path
            self.rejected(bad)

    def test_cli_rejects_without_executing_evidence_commands(self):
        self.receipt()
        receipt_path = self.root / 'receipt.json'
        receipt = json.loads(receipt_path.read_text())
        marker = self.root / 'must-not-exist'
        receipt['command'] = 'touch ' + str(marker)
        raw = json.dumps(receipt).encode(); receipt_path.write_bytes(raw)
        self.value['capabilities'][0]['evidence']['sha256'] = hashlib.sha256(raw).hexdigest()
        self.write()
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'requirements.py'), str(self.prd)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())
        self.prd.write_text('# missing section')
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'requirements.py'), str(self.prd)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Requirements rejected', result.stderr)

    def test_benchmark_stops_before_generation_on_missing_section(self):
        # Exercise the actual requirements subprocess and benchmark failure receipt.
        # Only source capture and tool preflight are synthetic; no browser is run.
        source = self.root / 'source'; source.mkdir()
        for name in ('toolchain.json', 'benchmark.py', 'autonomy-baseline.json'):
            (source / name).write_bytes((ROOT / name).read_bytes())
        chrome = self.root / 'fake-chrome'; chrome.write_text('fixture')
        lock = json.loads((source / 'toolchain.json').read_text())
        def capture(repo, runtime, revision):
            runtime.mkdir()
            for name in ('benchmark.py', 'autonomy-baseline.json', 'requirements.py'):
                (runtime / name).write_bytes((ROOT / name).read_bytes())
            (runtime / 'PRD.md').write_text('# missing section')
            return {'commit': revision}
        def preflight(args, **kwargs):
            if '--version' in args: return 'v' + lock['node']
            if 'status' in args: return b''
            return 'a' * 40
        out = self.root / 'result'
        with patch.object(benchmark, 'ROOT', source), patch.object(benchmark, 'capture_snapshot', capture), \
             patch.object(benchmark.platform, 'python_version', return_value=lock['python']), \
             patch.object(benchmark.subprocess, 'check_output', side_effect=preflight), \
             patch.dict('os.environ', FACTORY_NODE='fixture-node', FACTORY_CHROME=str(chrome)):
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, 'requirements failed'):
                benchmark.main(out)
        receipt = json.loads((out / 'receipt.json').read_text())
        self.assertEqual(receipt['status'], 'failed')
        self.assertEqual([c['name'] for c in receipt['checks']], ['requirements'])
        self.assertFalse((out / 'app').exists())
