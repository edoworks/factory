import pathlib
import unittest
import urllib.request
import urllib.error
import re
import json


ROOT = pathlib.Path(__file__).resolve().parents[1]


def _extract_factory_version(readme: str) -> str:
    match = re.search(r"FACTORY_VERSION=([0-9a-zA-Z.\-]+)", readme)
    if not match:
        return ""
    return match.group(1)


class ReleaseContractTests(unittest.TestCase):
    def test_quick_start_uses_exact_tag_archive(self):
        readme = (ROOT / "README.md").read_text()

        self.assertIn("FACTORY_VERSION=", readme)
        self.assertIn(
            "archive/refs/tags/v${FACTORY_VERSION}.tar.gz",
            readme,
        )
        self.assertNotIn("releases/latest/download/factory.tar.gz", readme)

    def test_documented_tag_archive_url_resolves(self):
        readme = (ROOT / "README.md").read_text()
        version = _extract_factory_version(readme)
        self.assertTrue(version, "FACTORY_VERSION not found in README")

        url = (
            "https://github.com/edoworks/factory/archive/refs/tags/"
            f"v{version}.tar.gz"
        )
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=30) as resp:
                self.assertEqual(resp.status, 200)
        except urllib.error.HTTPError as exc:
            self.fail(
                f"Documented tag archive URL returned {exc.code}: {url}"
            )

    def test_release_record_matches_readme_version(self):
        readme = (ROOT / "README.md").read_text()
        version = _extract_factory_version(readme)
        self.assertTrue(version, "FACTORY_VERSION not found in README")

        api_url = (
            "https://api.github.com/repos/edoworks/factory/releases/tags/"
            f"v{version}"
        )
        try:
            req = urllib.request.Request(api_url)
            req.add_header("Accept", "application/vnd.github+json")
            with urllib.request.urlopen(req, timeout=30) as resp:
                release = json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            self.fail(f"GitHub release API returned {exc.code} for {version}")

        self.assertEqual(
            release.get("tag_name"),
            f"v{version}",
            "Release tag does not match README version",
        )
        self.assertTrue(
            release.get("prerelease", True),
            "Release should be marked prerelease for pre-v1.0",
        )
        self.assertFalse(
            release.get("immutable", False),
            "README says the documented release is mutable",
        )
        self.assertEqual(
            release.get("assets"),
            [],
            "README says the documented release has no attached assets",
        )

    def test_license_contains_only_standard_mit_text(self):
        license_text = (ROOT / "LICENSE").read_text()

        self.assertTrue(license_text.startswith("MIT License\n"))
        self.assertTrue(
            license_text.rstrip().endswith(
                "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER "
                "DEALINGS IN THE\nSOFTWARE."
            )
        )
        self.assertNotIn("Brand Notice", license_text)
        self.assertTrue((ROOT / "TRADEMARKS.md").is_file())


if __name__ == "__main__":
    unittest.main()
