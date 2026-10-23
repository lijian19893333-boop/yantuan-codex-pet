#!/usr/bin/env python3
"""Validate the bundled manifest and sprite atlas (Pillow required)."""

import argparse
import json
from pathlib import Path
import sys


PET_ID = "yantuan-ragdoll"
ATLAS_SIZE = (1536, 2288)
CELL_SIZE = (192, 208)
ROWS = 11
COLUMNS = 8
# Row 0 includes one extra neutral-look cell after its six idle frames.
# Rows 9 and 10 are eight directional still frames each, not animation loops.
EXPECTED_OCCUPANCY = (7, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8)


def validate(pet_dir):
    pet_dir = Path(pet_dir)
    manifest_path = pet_dir / "pet.json"
    sprite_path = pet_dir / "spritesheet.webp"
    if pet_dir.is_symlink() or manifest_path.is_symlink() or sprite_path.is_symlink():
        raise ValueError("Pet directory and asset files must not be symlinks.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("pet.json must be a JSON object.")
    expected = {
        "id": PET_ID,
        "displayName": "焰团",
        "spritesheetPath": "spritesheet.webp",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ValueError("{} must be {!r}.".format(key, value))
    if not isinstance(manifest.get("description"), str) or not manifest["description"].strip():
        raise ValueError("description must be a nonempty string.")
    version = manifest.get("spriteVersionNumber")
    if type(version) is not int or version != 2:
        raise ValueError("spriteVersionNumber must be 2 for this 11-row atlas.")
    try:
        from PIL import Image
    except ImportError as exc:
        raise ValueError("Pillow is required for validation: python3 -m pip install -r requirements-dev.txt") from exc
    with Image.open(sprite_path) as atlas:
        if atlas.format != "WEBP":
            raise ValueError("spritesheet.webp must be a WebP image.")
        if atlas.size != ATLAS_SIZE:
            raise ValueError("Atlas must be {} pixels, got {}.".format(ATLAS_SIZE, atlas.size))
        if "A" not in atlas.getbands():
            raise ValueError("Atlas must have an alpha channel.")
        atlas.load()
        alpha = atlas.getchannel("A")
        extrema = alpha.getextrema()
        if extrema[0] != 0 or extrema[1] == 0:
            raise ValueError("Atlas must contain transparent background and visible pixels.")
        occupancy = []
        for row in range(ROWS):
            occupied = []
            for column in range(COLUMNS):
                left, top = column * CELL_SIZE[0], row * CELL_SIZE[1]
                cell = alpha.crop((left, top, left + CELL_SIZE[0], top + CELL_SIZE[1]))
                if cell.getbbox() is not None:
                    occupied.append(column + 1)
            expected_cells = list(range(1, EXPECTED_OCCUPANCY[row] + 1))
            if occupied != expected_cells:
                raise ValueError(
                    "Row {} must occupy cells {}; got {}. Unused cells must be fully transparent."
                    .format(row, expected_cells, occupied)
                )
            occupancy.append(occupied)
    return occupancy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pet-dir", type=Path,
                        default=Path(__file__).resolve().parent.parent / "pets" / PET_ID)
    args = parser.parse_args()
    try:
        occupancy = validate(args.pet_dir)
    except (OSError, ValueError) as exc:
        print("Validation failed: {}".format(exc), file=sys.stderr)
        return 1
    print("Manifest, WebP, dimensions and transparency: OK")
    print("Atlas: 11 rows × 8 columns; cells: 192 × 208 pixels")
    print("Occupied cells per row: {}".format([len(row) for row in occupancy]))
    print("Nonempty cell numbers by row: {}".format(occupancy))
    print("Row 0: six idle frames + one neutral-look cell; rows 9–10: eight directional stills each.")
    print("Cell occupancy checks image content; animation behavior still requires a Codex preview.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
