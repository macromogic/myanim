"""One-time setup and health check for the myanim skill.

    myanim setup            # check tools, download fonts
    myanim setup --dev      # also install the git pre-commit hooks

Python dependencies are installed by `uv run` itself (it syncs the environment first).
This script checks the non-Python tools Manim needs and downloads the pinned fonts.
Exit code 1 if anything required is missing.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_TOOLS = {
    "ffmpeg": "brew install ffmpeg",
    "ffprobe": "brew install ffmpeg",
    "latex": "install MacTeX (brew install --cask mactex-no-gui) or TeX Live",
    "dvisvgm": "comes with MacTeX / TeX Live",
    "kpsewhich": "comes with MacTeX / TeX Live",
}
REQUIRED_TEX_PACKAGES = {"libertinus-type1.sty": "tlmgr install libertinus-type1"}


def ok(msg: str):
    print(f"  ok   {msg}")


def bad(msg: str, fix: str):
    print(f"  MISS {msg}  ->  {fix}")


def main(argv: list[str] | None = None):
    ap = argparse.ArgumentParser(
        prog="myanim setup", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--dev", action="store_true", help="install pre-commit hooks (for working on the skill)")
    args = ap.parse_args(argv)
    missing = 0

    print("tools")
    for tool, fix in REQUIRED_TOOLS.items():
        if shutil.which(tool):
            ok(tool)
        else:
            bad(tool, fix)
            missing += 1

    print("LaTeX packages")
    for sty, fix in REQUIRED_TEX_PACKAGES.items():
        found = (
            shutil.which("kpsewhich")
            and subprocess.run(["kpsewhich", sty], capture_output=True, text=True).stdout.strip()
        )
        if found:
            ok(sty)
        else:
            bad(sty, fix)
            missing += 1

    print("python")
    try:
        import manim  # noqa: F401

        ok(f"manim {manim.__version__}")
    except Exception as e:  # pragma: no cover - environment problem
        bad(f"manim import failed ({e})", "see references/manim-notes.md (pycairo / ninja)")
        missing += 1

    # macOS: Python >= 3.12.10 skips .pth files with the "hidden" flag, which breaks the editable
    # install (`myanim` then fails with ModuleNotFoundError outside the repo folder).
    import site
    import stat

    hidden = [
        p
        for d in site.getsitepackages()
        for p in Path(d).glob("*.pth")
        if getattr(p.stat(), "st_flags", 0) & getattr(stat, "UF_HIDDEN", 0)
    ]
    if hidden:
        bad(f"{len(hidden)} hidden .pth file(s) in {hidden[0].parent}", f'chflags -R nohidden "{sys.prefix}"')
        missing += 1
    else:
        ok("editable install visible to Python")

    print("fonts")
    if subprocess.run([sys.executable, "-m", "myanim", "fonts", "sync"]).returncode:
        missing += 1

    if args.dev:
        print("git hooks")
        if subprocess.run([sys.executable, "-m", "pre_commit", "install"], cwd=ROOT).returncode:
            missing += 1

    print("\nall set." if not missing else f"\n{missing} item(s) need attention (see MISS lines above).")
    print("next: myanim skill install   # use /myanim from any folder")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
