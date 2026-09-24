import pathlib
import unittest
import urllib.request
import urllib.error
import re
import json
import os


ROOT = pathlib.Path(__file__).resolve().parents[1]


def _github_json(url: str) -> dict:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _extract_factory_version(readme: str) -> str:
    match = re.search(r"FACTORY_VERSION=([0-9a-zA-Z.\-]+)", readme)
    if not match:
        return ""
    return match.group(1)


def _extract_factory_revision(readme: str) -> str:
    match = re.search(r"FACTORY_REVISION=([0-9a-f]{40})", readme)
    if not match:
        return ""
    return match.group(1)


class ReleaseContractTests(unittest.TestCase):
    def test_quick_start_uses_exact_tag_archive(self):
        readme = (ROOT / "README.md").read_text()

        self.assertIn("FACTORY_VERSION=", readme)
        self.assertIn("FACTORY_REVISION=", readme)
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
            release = _github_json(api_url)
        except urllib.error.HTTPError as exc:
            self.fail(f"GitHub release API returned {exc.code} for {version}")

        self.assertEqual(
            release.get("tag_name"),
            f"v{version}",
            "Release tag does not match README version",
        )
        self.assertIn("prerelease", release)
        self.assertTrue(
            release["prerelease"],
            "Release should be marked prerelease for pre-v1.0",
        )
        self.assertIn("immutable", release)
        self.assertFalse(
            release["immutable"],
            "README says the documented release is mutable",
        )
        self.assertIn("assets", release)
        self.assertEqual(
            release["assets"],
            [],
            "README says the documented release has no attached assets",
        )

        ref_url = (
            "https://api.github.com/repos/edoworks/factory/git/ref/tags/"
            f"v{version}"
        )
        try:
            tag_ref = _github_json(ref_url)
        except urllib.error.HTTPError as exc:
            self.fail(f"GitHub tag API returned {exc.code} for {version}")
        tag_object = tag_ref.get("object", {})
        if tag_object.get("type") == "tag":
            try:
                annotated_tag = _github_json(
                    "https://api.github.com/repos/edoworks/factory/git/tags/"
                    f"{tag_object.get('sha', '')}"
                )
            except urllib.error.HTTPError as exc:
                self.fail(f"GitHub annotated tag API returned {exc.code} for {version}")
            tag_object = annotated_tag.get("object", {})
        self.assertEqual(
            tag_object.get("sha"),
            _extract_factory_revision(readme),
            "Release tag moved from the documented source revision",
        )

    def test_license_contains_only_standard_mit_text(self):
        license_text = (ROOT / "LICENSE").read_text()

        expected_license = """MIT License

Copyright (c) 2026 Edoworks

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        self.assertEqual(license_text, expected_license)

        expected_trademark = """# Trademark Notice

The "edoworks" name and logo are trademarks of the owner. The MIT license in
`LICENSE` covers the code only. Use of the "edoworks" name, logo, or brand for
products or services requires written permission from the owner.
"""
        self.assertEqual((ROOT / "TRADEMARKS.md").read_text(), expected_trademark)


if __name__ == "__main__":
    unittest.main()
