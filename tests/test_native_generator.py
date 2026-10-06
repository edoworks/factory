"""Pure source generation only: no XcodeGen, builds, or simulator interaction."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import factory

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / 'specs/couch-clash.json').read_text())


class NativeGeneratorTests(unittest.TestCase):
    def setUp(self):
        if shutil.disk_usage(ROOT).free - 2 * 1024 * 1024 < 2 * 1024 ** 3:
            self.fail('Source-only disk gate: require 2 GiB free after a 2 MiB write budget')
        self.temp = tempfile.TemporaryDirectory(prefix='factory-native-source-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.spec = self.root / 'spec.json'
        self.spec.write_text(json.dumps(SPEC))

    def generate(self, name, target='ios'):
        result = factory.generate(self.spec, self.root / name, 'b' * 40, target)
        self.assertLess(sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file()), 2 * 1024 * 1024)
        return result

    def test_native_source_is_deterministic_and_declares_complete_closure(self):
        first = self.generate('first'); second = self.generate('second')
        self.assertEqual(first, second)
        for name, digest in first['files'].items():
            data = (self.root / 'first' / name).read_bytes()
            self.assertEqual(data, (self.root / 'second' / name).read_bytes())
            self.assertEqual(factory.digest(data), digest)
        for name, digest in first['source_closure'].items():
            self.assertEqual(factory.digest((ROOT / name).read_bytes()), digest)
        self.assertTrue(all('templates/ios/' + name in first['source_closure'] for name in factory.IOS_TEMPLATES))
        self.assertEqual(first['native_qualification'], 'unbuilt_unexecuted')
        self.assertEqual(first['revision_status'], 'caller_supplied_unverified')

    def test_same_spec_controls_native_identity_and_core_without_rewriting_templates(self):
        self.generate('original')
        changed = copy.deepcopy(SPEC)
        changed.update(id='alternate-game', title='Quoted "title": sample')
        changed['questions'][0]['points'] = 333
        self.spec.write_text(json.dumps(changed)); self.generate('changed')
        project = json.loads((self.root / 'changed/project.json').read_text())
        app = project['targets']['GeneratedApp']
        self.assertEqual(app['settings']['base']['PRODUCT_BUNDLE_IDENTIFIER'], 'local.factory.alternate-game')
        original_project = json.loads((self.root / 'original/project.json').read_text())
        tests_id = project['targets']['GeneratedAppTests']['settings']['base']['PRODUCT_BUNDLE_IDENTIFIER']
        self.assertEqual(tests_id, 'local.factory.alternate-game.tests')
        self.assertNotEqual(tests_id, original_project['targets']['GeneratedAppTests']['settings']['base']['PRODUCT_BUNDLE_IDENTIFIER'])
        self.assertEqual(app['info']['properties']['CFBundleDisplayName'], changed['title'])
        self.assertIn('333', (self.root / 'changed/Web/spec.mjs').read_text())
        self.assertEqual((self.root / 'original/Sources/BundledWebView.swift').read_bytes(),
                         (self.root / 'changed/Sources/BundledWebView.swift').read_bytes())

    def test_native_preserves_web_code_and_rejects_unsafe_outputs(self):
        web = self.generate('web', 'web'); native = self.generate('native')
        for name in ('app.mjs', 'engine.mjs', 'engine.test.mjs', 'spec.mjs', 'style.css'):
            self.assertEqual((self.root / 'web' / name).read_bytes(), (self.root / 'native/Web' / name).read_bytes())
        self.assertEqual(web['spec_sha256'], native['spec_sha256'])
        original = {str(p.relative_to(self.root / 'native')): p.read_bytes()
                    for p in (self.root / 'native').rglob('*') if p.is_file()}
        with self.assertRaises(ValueError): self.generate('native')
        self.assertEqual(original, {str(p.relative_to(self.root / 'native')): p.read_bytes()
                                   for p in (self.root / 'native').rglob('*') if p.is_file()})
        (self.root / 'link').symlink_to(self.root / 'web', target_is_directory=True)
        with self.assertRaises(ValueError): self.generate('link/escape')
        with self.assertRaises(ValueError): self.generate('invalid', 'android')
        self.assertFalse((self.root / 'invalid').exists())

    def test_native_generation_stays_inside_audited_source_closure(self):
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'tests/isolated_generate.py'),
                                 str(ROOT), str(self.spec), str(self.root / 'isolated'), 'b' * 40, 'ios'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt['audit'], 'undeclared read and network probes rejected')
        self.assertTrue(all('templates/ios/' + name in receipt['observed_reads'] for name in factory.IOS_TEMPLATES))
