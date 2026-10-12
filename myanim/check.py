"""Run a project's scenes as a QA dry run: all layout and animation checks, no video.

    myanim check <project>               # every scene in project.toml
    myanim check <project> -s s02_cycles # selected scenes

Takes seconds instead of a render. Exit code 1 if any scene raises or reports a warning,
so it can gate a render or a commit. The render's event logs are left untouched.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import traceback
from pathlib import Path

from myanim import ROOT
from myanim.render import load_project


def load_scene_class(project: Path, scene: dict):
    path = project / scene["file"]
    spec = importlib.util.spec_from_file_location(f"_myanim_check_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, scene["class"])


def main(argv: list[str] | None = None):
    ap = argparse.ArgumentParser(
        prog="myanim check", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("project", type=Path)
    ap.add_argument("-s", "--scenes", help="comma-separated scene ids (default: all)")
    args = ap.parse_args(argv)

    project = args.project.resolve()
    cfg = load_project(project)
    wanted = set(args.scenes.split(",")) if args.scenes else None
    scenes = [s for s in cfg["scenes"] if not wanted or s["id"] in wanted]
    if wanted and (unknown := wanted - {s["id"] for s in scenes}):
        sys.exit(f"unknown scene ids: {sorted(unknown)}")

    # Same import environment as a render: the skill's components, the project's data/shared.
    for p in (str(project / "scenes"), str(project), str(ROOT)):
        if p not in sys.path:
            sys.path.insert(0, p)
    os.chdir(project)
    import warnings

    warnings.filterwarnings("ignore", category=SyntaxWarning)
    from manim import config

    from components.scene import EduScene

    config.dry_run = True
    config.progress_bar = "none"
    config.verbosity = "ERROR"
    config.media_dir = str(project / "renders" / "media")  # TeX/text caches, not ./media
    EduScene.WRITE_REPORT = False

    problems = 0
    for scene in scenes:
        try:
            instance = load_scene_class(project, scene)()
            instance.render()
        except Exception:
            problems += 1
            print(f"!! {scene['id']}: scene raised")
            print("".join(traceback.format_exc().splitlines(keepends=True)[-12:]))
            continue
        warns = instance._warnings
        problems += len(warns)
        status = "ok" if not warns else f"{len(warns)} warning(s)"
        print(
            f"{'=' if not warns else '!'} {scene['id']}: {status}, {len(instance._events)} events, "
            f"{instance.time:.1f}s"
        )
        for w in warns:
            print(f"    {w['event']}: {w['kind']} | {w['detail']}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
