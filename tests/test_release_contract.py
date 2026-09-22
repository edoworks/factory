import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReleaseContractTests(unittest.TestCase):
    def test_quick_start_uses_exact_tag_archive(self):
        readme = (ROOT / "README.md").read_text()

        self.assertIn("FACTORY_VERSION=0.1.0-rc2", readme)
        self.assertIn(
            'archive/refs/tags/v${FACTORY_VERSION}.tar.gz',
            readme,
        )
        self.assertNotIn("releases/latest/download/factory.tar.gz", readme)


if __name__ == "__main__":
    unittest.main()
