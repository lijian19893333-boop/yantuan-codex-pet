"""Validate malformed manifests and atlas occupancy in temporary directories."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

try:
    from PIL import Image
except ImportError:
    Image = None

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate.py"
SPEC = importlib.util.spec_from_file_location("pet_validate", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ManifestTests(unittest.TestCase):
    def test_sprite_path_cannot_escape_pet_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = {
                "id": "yantuan-ragdoll", "displayName": "焰团",
                "spritesheetPath": "../other.webp", "description": "test",
                "spriteVersionNumber": 2,
            }
            (Path(folder) / "pet.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "spritesheetPath"):
                validator.validate(folder)


@unittest.skipIf(Image is None, "Pillow is optional; install requirements-dev.txt for image tests")
class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "pet.json").write_text(json.dumps({
            "id": "yantuan-ragdoll", "displayName": "焰团",
            "spritesheetPath": "spritesheet.webp", "description": "test",
            "spriteVersionNumber": 2,
        }), encoding="utf-8")
        self.atlas = Image.new("RGBA", validator.ATLAS_SIZE, (0, 0, 0, 0))
        self.addCleanup(self.atlas.close)
        for row, count in enumerate(validator.EXPECTED_OCCUPANCY):
            for column in range(count):
                self.atlas.putpixel((column * 192 + 20, row * 208 + 20), (255, 255, 255, 255))

    def save(self):
        self.atlas.save(self.root / "spritesheet.webp", lossless=True)

    def test_exact_occupancy_is_accepted(self):
        self.save()
        occupancy = validator.validate(self.root)
        self.assertEqual(tuple(map(len, occupancy)), validator.EXPECTED_OCCUPANCY)

    def test_even_one_visible_pixel_in_unused_cell_is_rejected(self):
        self.atlas.putpixel((7 * 192 + 20, 20), (255, 255, 255, 1))
        self.save()
        with self.assertRaisesRegex(ValueError, "Unused cells must be fully transparent"):
            validator.validate(self.root)

    def test_missing_expected_frame_is_rejected(self):
        self.atlas.putpixel((20, 20), (0, 0, 0, 0))
        self.save()
        with self.assertRaisesRegex(ValueError, "Row 0"):
            validator.validate(self.root)


if __name__ == "__main__":
    unittest.main()
