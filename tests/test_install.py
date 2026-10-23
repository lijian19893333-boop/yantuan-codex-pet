"""Installer tests only use temporary directories, never the real Codex home."""

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "install.py"
SPEC = importlib.util.spec_from_file_location("pet_install", MODULE_PATH)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "pet.json").write_text(json.dumps({
            "id": installer.PET_ID, "spritesheetPath": "spritesheet.webp"
        }), encoding="utf-8")
        (self.source / "spritesheet.webp").write_bytes(b"new-sprite-bytes")
        (self.source / "private-note.txt").write_text("must not copy", encoding="utf-8")
        self.pets_dir = self.root / "custom-home" / "pets"
        self.destination = self.pets_dir / installer.PET_ID

    def old_install(self):
        self.destination.mkdir(parents=True)
        (self.destination / "pet.json").write_text("original", encoding="utf-8")
        (self.destination / "user-note.txt").write_text("preserve", encoding="utf-8")

    def test_custom_directory_copies_only_two_files(self):
        destination, backup = installer.install(self.source, self.pets_dir)
        self.assertEqual(destination, self.destination)
        self.assertIsNone(backup)
        self.assertEqual(sorted(p.name for p in destination.iterdir()), sorted(installer.FILES))
        self.assertEqual((destination / "spritesheet.webp").read_bytes(), b"new-sprite-bytes")
        self.assertFalse((self.pets_dir.parent / "config.toml").exists())

    def test_default_respects_codex_home(self):
        with patch.dict(os.environ, {"CODEX_HOME": str(self.root / "alternate")}):
            self.assertEqual(installer.default_pets_dir(), self.root / "alternate" / "pets")

    def test_existing_install_requires_explicit_replace(self):
        self.old_install()
        with self.assertRaises(installer.InstallError):
            installer.install(self.source, self.pets_dir)
        self.assertEqual((self.destination / "pet.json").read_text(), "original")
        self.assertEqual(list(self.pets_dir.iterdir()), [self.destination])

    def test_replace_retains_complete_backup_and_uses_unique_name(self):
        self.old_install()
        destination, backup = installer.install(self.source, self.pets_dir, replace=True)
        self.assertEqual(backup.parent, self.pets_dir)
        self.assertTrue(backup.name.startswith(installer.PET_ID + ".backup-"))
        self.assertEqual((backup / "pet.json").read_text(), "original")
        self.assertEqual((backup / "user-note.txt").read_text(), "preserve")
        self.assertEqual((destination / "spritesheet.webp").read_bytes(), b"new-sprite-bytes")
        _, second_backup = installer.install(self.source, self.pets_dir, replace=True)
        self.assertNotEqual(backup, second_backup)
        self.assertTrue(backup.is_dir())

    def test_symlink_destination_is_refused_even_with_replace(self):
        self.pets_dir.mkdir(parents=True)
        other = self.root / "unrelated"
        other.mkdir()
        (other / "keep").write_text("safe")
        self.destination.symlink_to(other, target_is_directory=True)
        with self.assertRaises(installer.InstallError):
            installer.install(self.source, self.pets_dir, replace=True)
        self.assertEqual((other / "keep").read_text(), "safe")
        self.assertTrue(self.destination.is_symlink())

    def test_symlink_parent_is_refused(self):
        real = self.root / "real"
        real.mkdir()
        link = self.root / "linked"
        link.symlink_to(real, target_is_directory=True)
        with self.assertRaises(installer.InstallError):
            installer.install(self.source, link / "pets")
        self.assertEqual(list(real.iterdir()), [])

    def test_symlink_source_file_is_refused(self):
        sprite = self.source / "spritesheet.webp"
        sprite.unlink()
        other = self.root / "other.webp"
        other.write_bytes(b"leave alone")
        sprite.symlink_to(other)
        with self.assertRaises(installer.InstallError):
            installer.install(self.source, self.pets_dir)
        self.assertFalse(self.pets_dir.exists())

    def test_failed_final_rename_restores_original(self):
        self.old_install()
        real_rename = Path.rename

        def fail_staging_rename(path, target):
            if path.name.startswith(".{}-install-".format(installer.PET_ID)):
                raise OSError("simulated final rename failure")
            return real_rename(path, target)

        with patch.object(Path, "rename", fail_staging_rename):
            with self.assertRaises(installer.InstallError):
                installer.install(self.source, self.pets_dir, replace=True)
        self.assertEqual((self.destination / "pet.json").read_text(), "original")
        self.assertEqual((self.destination / "user-note.txt").read_text(), "preserve")
        self.assertEqual(list(self.pets_dir.iterdir()), [self.destination])

    def test_copy_failure_leaves_original_untouched(self):
        self.old_install()
        with patch.object(installer.shutil, "copy2", side_effect=OSError("simulated copy failure")):
            with self.assertRaises(OSError):
                installer.install(self.source, self.pets_dir, replace=True)
        self.assertEqual((self.destination / "pet.json").read_text(), "original")
        self.assertEqual(list(self.pets_dir.iterdir()), [self.destination])


if __name__ == "__main__":
    unittest.main()
