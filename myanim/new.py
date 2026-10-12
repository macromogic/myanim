"""Create a video project from projects/_template/ and copy in source material.

The project goes to --dir (default: $MYANIM_PROJECTS, else <skill>/projects), so videos can
live outside the skill repo, e.g. in a private videos repo.

myanim new rope-embeddings --source ~/blog/rope.md --title "RoPE in 60 s"
myanim new my-topic --source paper.pdf --source fig1.png
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "projects" / "_template"


def main(argv: list[str] | None = None):
    ap = argparse.ArgumentParser(
        prog="myanim new", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("slug", help="lowercase-dashes project name")
    ap.add_argument(
        "--source", action="append", default=[], type=Path, help="file to copy into source/ (repeatable)"
    )
    ap.add_argument("--title", help="human-readable title (default: from slug)")
    ap.add_argument("--mode", choices=["collaborative", "autonomous"], default="collaborative")
    ap.add_argument(
        "--dir",
        type=Path,
        default=Path(os.environ.get("MYANIM_PROJECTS", ROOT / "projects")),
        help="parent folder for the project (default: $MYANIM_PROJECTS or <skill>/projects)",
    )
    args = ap.parse_args(argv)

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.slug):
        sys.exit("slug must be lowercase letters, digits and dashes")
    dest = (args.dir.expanduser() / args.slug).resolve()
    if dest.exists():
        sys.exit(f"{dest} already exists")
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

    print(f"created {dest}/  (mode: {args.mode})")
    for c in copied:
        print(f"  + {c}")
    print(
        "next: Stage A (outline.md), Stage A2 (audience.md, checkpoint 1), "
        "Stage B (storyboard.md, checkpoint 2) -- see SKILL.md"
    )
    if dest.is_relative_to(ROOT):
        print("note: projects/ is not version-controlled (except _template and attention-demo)")


if __name__ == "__main__":
    main()
