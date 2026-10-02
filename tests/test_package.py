import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location("verify_package", Path(__file__).parents[1] / "scripts/verify-package.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.archive = self.directory / "tabnav-v1.2.3.zip"
        manifest = {"manifest_version": 3, "version": "1.2.3", "background": {"service_worker": "assets/background.js"}, "icons": {"16": "icons/icon-16.png"}}
        self.files = {"manifest.json": json.dumps(manifest), "assets/background.js": "", "icons/icon-16.png": "image", "popup.html": "", "newtab.html": '<script src="/assets/newtab.js"></script>', "assets/newtab.js": ""}

    def prepare(self):
        with zipfile.ZipFile(self.archive, "w") as archive:
            for path, contents in self.files.items():
                archive.writestr(path, contents)
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        (self.directory / "release.json").write_text(json.dumps({"version": "1.2.3", "archive": self.archive.name, "sha256": digest, "sourceCommit": "a" * 40}))
        (self.directory / f"{self.archive.name}.sha256").write_text(f"{digest}  {self.archive.name}\n")

    def test_accepts_installable_package(self):
        self.prepare()
        self.assertEqual(validator.verify("v1.2.3", self.directory)["version"], "1.2.3")

    def test_rejects_private_files_and_source_maps(self):
        for path in (".env", "assets/app.js.map", "src/app.ts", "private.pem", "../escape.js"):
            with self.subTest(path=path):
                self.files[path] = "must not ship"
                self.prepare()
                with self.assertRaises(ValueError):
                    validator.verify("v1.2.3", self.directory)
                del self.files[path]

    def test_rejects_corrupt_checksum(self):
        self.prepare()
        with self.archive.open("ab") as archive:
            archive.write(b"tampered")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            validator.verify("v1.2.3", self.directory)

    def test_rejects_missing_html_dependency(self):
        del self.files["assets/newtab.js"]
        self.prepare()
        with self.assertRaisesRegex(ValueError, "Missing runtime assets"):
            validator.verify("v1.2.3", self.directory)

    def test_rejects_manifest_version_mismatch(self):
        manifest = json.loads(self.files["manifest.json"])
        manifest["version"] = "1.2.2"
        self.files["manifest.json"] = json.dumps(manifest)
        self.prepare()
        with self.assertRaisesRegex(ValueError, "manifest version"):
            validator.verify("v1.2.3", self.directory)

    def test_rejects_unsafe_tag(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError, "Invalid release tag"):
            validator.verify("../v1.2.3", self.directory)


if __name__ == "__main__":
    unittest.main()
