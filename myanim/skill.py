"""Make the myanim skill available in every Claude Code session (user-level install).

    myanim skill install     # link ~/.claude/skills/myanim -> this repo
    myanim skill status      # show where /myanim points
    myanim skill uninstall   # remove the link

Claude Code loads personal skills from ~/.claude/skills/<name>/SKILL.md, and the entry may be
a symlink to a directory elsewhere. Linking the whole repo keeps every relative path in
SKILL.md (myanim/, components/, references/) valid, and `git pull` updates the skill.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = "myanim"


def main(argv: list[str] | None = None):
    ap = argparse.ArgumentParser(
        prog="myanim skill", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--target",
        type=Path,
        default=Path.home() / ".claude" / "skills",
        help="skills directory (default: ~/.claude/skills)",
    )
    ap.add_argument("action", choices=["install", "uninstall", "status"], nargs="?", default="status")
    args = ap.parse_args(argv)

    link = args.target.expanduser() / NAME
    if args.action == "status":
        if link.is_symlink():
            print(f"installed: {link} -> {link.resolve()}")
        else:
            print(f"not installed ({link}); run: myanim skill install")
        return
    if args.action == "uninstall":
        if link.is_symlink():
            link.unlink()
            print(f"removed {link}")
        elif link.exists():
            sys.exit(f"{link} is not a symlink created by this script; remove it by hand if intended")
        else:
            print(f"{link} not installed")
        return

    if link.is_symlink():
        if link.resolve() == ROOT:
            print(f"already installed: {link} -> {ROOT}")
            return
        sys.exit(f"{link} points to {link.resolve()}; run `myanim skill uninstall` first")
    if link.exists():
        sys.exit(f"{link} exists and is not a symlink; refusing to overwrite")
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(ROOT, target_is_directory=True)
    print(f"installed: {link} -> {ROOT}")
    print("start a new Claude Code session anywhere and type /myanim (or ask for a video from a document)")


if __name__ == "__main__":
    main()
