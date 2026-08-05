# noqa: INP001

"""Update manifest version."""

import json
import sys
from pathlib import Path


def update_manifest() -> None:
    """Update the manifest file."""
    version = "0.0.0"
    for index, value in enumerate(sys.argv):
        if value in ["--version", "-V"] and index + 1 < len(sys.argv):
            version = sys.argv[index + 1]

    manifest_path = (
        Path.cwd() / "custom_components" / "fritzbox_voicemail" / "manifest.json"
    )

    with manifest_path.open() as manifestfile:
        manifest = json.load(manifestfile)

    manifest["version"] = version

    with manifest_path.open("w") as manifestfile:
        json.dump(manifest, manifestfile, indent=4, sort_keys=True)
        manifestfile.write("\n")


if __name__ == "__main__":
    update_manifest()
