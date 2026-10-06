import subprocess
import tempfile
from pathlib import Path
import unittest

from snapshot import capture_snapshot, verify_snapshot


class SnapshotTests(unittest.TestCase):
    def test_revision_and_snapshot_bytes_must_match(self):
        with tempfile.TemporaryDirectory(prefix='factory-snapshot-test-') as folder:
            root = Path(folder); repo = root / 'source'; repo.mkdir()
            def git(*args):
                return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.STDOUT).decode().strip()
            git('init', '-q'); (repo / 'source.txt').write_text('committed bytes\n')
            git('add', 'source.txt')
            git('-c', 'user.name=Factory Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')
            head = git('rev-parse', 'HEAD')
            with self.assertRaisesRegex(ValueError, 'revision'):
                capture_snapshot(repo, root / 'wrong-revision', '0' * 40)
            identity = capture_snapshot(repo, root / 'snapshot', head)
            self.assertEqual(identity['tree'], git('rev-parse', 'HEAD^{tree}'))
            (repo / 'source.txt').write_text('later working edit\n')
            verify_snapshot(root / 'snapshot', identity)
            self.assertEqual((root / 'snapshot/source.txt').read_text(), 'committed bytes\n')
            with self.assertRaisesRegex(ValueError, 'dirty'):
                capture_snapshot(repo, root / 'dirty', head)
            (root / 'snapshot/source.txt').write_text('tampered snapshot\n')
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                verify_snapshot(root / 'snapshot', identity)
