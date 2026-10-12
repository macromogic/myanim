"""Create projects/<slug>/ from projects/_template/ and copy in source material.

uv run python scripts/new_project.py rope-embeddings --source ~/blog/rope.md --title "RoPE in 60 s"
uv run python scripts/new_project.py my-topic --source paper.pdf --source fig1.png
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "projects" / "_template"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", help="lowercase-dashes project name")
    ap.add_argument(
        "--source", action="append", default=[], type=Path, help="file to copy into source/ (repeatable)"
    )
    ap.add_argument("--title", help="human-readable title (default: from slug)")
    ap.add_argument("--mode", choices=["collaborative", "autonomous"], default="collaborative")
    args = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.slug):
        sys.exit("slug must be lowercase letters, digits and dashes")
    dest = ROOT / "projects" / args.slug
    if dest.exists():
        sys.exit(f"{dest.relative_to(ROOT)} already exists")
    missing = [s for s in args.source if not s.exists()]
    if missing:
        sys.exit(f"source not found: {missing}")

    shutil.copytree(TEMPLATE, dest, ignore=shutil.ignore_patterns("renders", "__pycache__"))
    title = args.title or args.slug.replace("-", " ").capitalize()
    copied = []
    for src in args.source:
        shutil.copy2(src, dest / "source" / src.name)
        copied.append(f"source/{src.name}")
    for path in dest.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".toml"}:
            text = path.read_text().replace("{{title}}", title)
            if path.name == "project.toml":
                text = text.replace("source = []", f"source = {copied!r}".replace("'", '"'))
                text = text.replace('mode = "collaborative"', f'mode = "{args.mode}"')
            path.write_text(text)

    print(f"created {dest.relative_to(ROOT)}/  (mode: {args.mode})")
    for c in copied:
        print(f"  + {c}")
    print("next: Stage A (outline.md) and Stage B (storyboard.md) -- see SKILL.md")


if __name__ == "__main__":
    main()
