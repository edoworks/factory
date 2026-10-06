import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
module = importlib.util.spec_from_file_location('factory', ROOT / 'factory.py')
factory = importlib.util.module_from_spec(module)
module.loader.exec_module(factory)
SPEC = json.loads((ROOT / 'specs/couch-clash.json').read_text())


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='factory-test-')
        self.root = Path(self.temp.name).resolve()
        self.spec = self.root / 'spec.json'
        self.spec.write_text(json.dumps(SPEC))

    def tearDown(self):
        self.temp.cleanup()

    def generate(self, name):
        return factory.generate(self.spec, self.root / name, 'a' * 40)

    def test_deterministic_output_and_file_integrity(self):
        first, second = self.generate('one'), self.generate('two')
        self.assertEqual(first, second)
        for path in (self.root / 'one').iterdir():
            self.assertEqual(path.read_bytes(), (self.root / 'two' / path.name).read_bytes())
        for name, digest in first['files'].items():
            self.assertEqual(factory.digest((self.root / 'one' / name).read_bytes()), digest)

    def test_version_unknown_fields_and_invalid_rules(self):
        mutations = [lambda s: s.update(schema_version=2), lambda s: s.update(unknown=True),
                     lambda s: s['questions'][0].update(points=True),
                     lambda s: s['stages'][0].update(kind='reveal'),
                     lambda s: s['questions'][0].update(id='constructor'),
                     lambda s: s['questions'][0]['options'].append(s['questions'][0]['options'][0]),
                     lambda s: s.update(assets=['https://example.com/source.js'])]
        for mutate in mutations:
            spec = copy.deepcopy(SPEC); mutate(spec)
            with self.assertRaises(ValueError): factory.validate(spec)

    def test_nonempty_destination_is_untouched(self):
        dest = self.root / 'app'; dest.mkdir(); (dest / 'owner.txt').write_text('preserve')
        with self.assertRaises(ValueError): self.generate('app')
        self.assertEqual((dest / 'owner.txt').read_text(), 'preserve')
        self.assertEqual(list(dest.iterdir()), [dest / 'owner.txt'])

    def test_existing_empty_destination_supported(self):
        (self.root / 'app').mkdir(); self.generate('app')
        self.assertTrue((self.root / 'app/index.html').is_file())

    def test_symlink_and_traversal_rejected(self):
        (self.root / 'real').mkdir(); (self.root / 'link').symlink_to(self.root / 'real', target_is_directory=True)
        for path in [self.root / 'link' / 'app', self.root / 'real' / '..' / 'escape', ROOT / 'output']:
            with self.assertRaises(ValueError): factory.generate(self.spec, path, 'a' * 40)
        self.assertEqual(list((self.root / 'real').iterdir()), [])

    def test_exact_revision_required(self):
        with self.assertRaises(ValueError): factory.generate(self.spec, self.root / 'app', 'main')

    def test_meaningful_spec_change_changes_identity_and_config(self):
        one = self.generate('one'); changed = copy.deepcopy(SPEC)
        changed['title'] = 'Another Rivalry'; changed['questions'][0]['points'] = 333
        self.spec.write_text(json.dumps(changed)); two = self.generate('two')
        self.assertNotEqual(one['spec_sha256'], two['spec_sha256'])
        self.assertIn('Another Rivalry', (self.root / 'two/spec.mjs').read_text())
        self.assertIn('333', (self.root / 'two/spec.mjs').read_text())


if __name__ == '__main__':
    unittest.main()
