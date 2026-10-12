"""Render the component gallery and refresh assets/previews/ (PNG of last frame + MP4).

uv run python scripts/previews.py            # all components
uv run python scripts/previews.py -s formula # one component
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GALLERY = ROOT / "examples" / "component_gallery"
OUT = ROOT / "assets" / "previews"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--scenes")
    args = ap.parse_args()
    extra = ["-s", args.scenes] if args.scenes else []
    render = [sys.executable, str(ROOT / "scripts" / "render.py"), str(GALLERY), "--no-concat"] + extra
    for flags in ([], ["--still"]):
        if subprocess.run(render + flags).returncode:
            sys.exit(1)
    OUT.mkdir(parents=True, exist_ok=True)
    for src in list((GALLERY / "renders" / "preview").glob("*.mp4")) + list(
        (GALLERY / "renders" / "stills").glob("*.png")
    ):
        shutil.copy2(src, OUT / src.name)
        print(f"  {src.name} -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
