#!/usr/bin/env python3
"""Install the bundled pet; never change Codex settings or select a pet."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid


PET_ID = "yantuan-ragdoll"
FILES = ("pet.json", "spritesheet.webp")


class InstallError(Exception):
    """A refused or unsuccessful installation."""


def safe_path(path):
    """Keep symlinks visible instead of resolving them before checking."""
    path = Path(os.path.abspath(os.path.expanduser(str(path))))
    for component in (path, *path.parents):
        if component.is_symlink():
            raise InstallError("Refusing a symlink path: {}".format(component))
    return path


def default_pets_dir():
    codex_home = os.environ.get("CODEX_HOME") or "~/.codex"
    return Path(codex_home).expanduser() / "pets"


def install(source, pets_dir, replace=False):
    """Return (destination, optional_backup), copying exactly FILES."""
    source = safe_path(source)
    for name in FILES:
        asset = safe_path(source / name)
        if not asset.is_file():
            raise InstallError("Missing regular source file: {}".format(asset))
    try:
        manifest = json.loads((source / "pet.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise InstallError("Cannot read bundled pet.json: {}".format(exc)) from exc
    if not isinstance(manifest, dict) or manifest.get("id") != PET_ID:
        raise InstallError("Bundled pet.json must have id {!r}.".format(PET_ID))
    if manifest.get("spritesheetPath") != "spritesheet.webp":
        raise InstallError("Bundled spritesheetPath must be 'spritesheet.webp'.")

    pets_dir = safe_path(pets_dir)
    destination = safe_path(pets_dir / PET_ID)
    if destination.exists():
        if not destination.is_dir():
            raise InstallError("Destination is not a directory: {}".format(destination))
        if not replace:
            raise InstallError(
                "Already installed: {}. Use --replace to keep a backup and replace it."
                .format(destination)
            )
    # A source nested in the destination would move away during replacement.
    if source == destination or destination in source.parents:
        raise InstallError("Source must be outside the installation destination.")

    pets_dir.mkdir(parents=True, exist_ok=True)
    safe_path(pets_dir)
    staging = Path(tempfile.mkdtemp(prefix=".{}-install-".format(PET_ID), dir=pets_dir))
    backup = None
    try:
        for name in FILES:
            safe_path(source / name)
            shutil.copy2(source / name, staging / name)
        # Check again immediately before changing an existing installation.
        safe_path(destination)
        if destination.exists():
            if not replace:
                raise InstallError("Destination appeared during installation; refusing to overwrite.")
            if not destination.is_dir():
                raise InstallError("Destination is not a directory: {}".format(destination))
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup = pets_dir / "{}.backup-{}-{}".format(PET_ID, stamp, uuid.uuid4().hex)
            destination.rename(backup)
        try:
            staging.rename(destination)
        except OSError as exc:
            if backup is not None:
                if destination.exists() or destination.is_symlink():
                    raise InstallError(
                        "Install failed and destination is occupied; original is safe at {}."
                        .format(backup)
                    ) from exc
                try:
                    backup.rename(destination)
                except OSError as rollback_exc:
                    raise InstallError(
                        "Install failed; could not restore automatically. Original is safe at {}: {}"
                        .format(backup, rollback_exc)
                    ) from exc
            raise InstallError("Installation failed; original installation was preserved: {}".format(exc)) from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination, backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pets-dir", type=Path, default=default_pets_dir(),
                        help="Pets directory (default: $CODEX_HOME/pets or ~/.codex/pets)")
    parser.add_argument("--replace", action="store_true",
                        help="Replace an existing directory after retaining a timestamped backup")
    args = parser.parse_args()
    source = Path(__file__).resolve().parent.parent / "pets" / PET_ID
    try:
        destination, backup = install(source, args.pets_dir, args.replace)
    except (InstallError, OSError) as exc:
        print("Installation refused or failed: {}".format(exc), file=sys.stderr)
        return 1
    print("Installed: {}".format(destination))
    if backup is not None:
        print("Previous installation retained: {}".format(backup))
    print("Open the Codex pet picker and select 焰团. No Codex settings were changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
