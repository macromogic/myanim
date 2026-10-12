"""`myanim` command line: one entry point for every tool of the skill.

Each subcommand keeps its own argument parser (`myanim <command> -h` for details); this module
only dispatches, importing the command lazily so `myanim --help` stays fast.
"""

from __future__ import annotations

import argparse
import importlib
import sys

COMMANDS = {
    # name: (module, one-line help)
    "setup": ("myanim.setup_env", "check tools and LaTeX, download fonts (--dev: git hooks)"),
    "skill": ("myanim.skill", "install | uninstall | status of the /myanim Claude Code skill"),
    "new": ("myanim.new", "create a video project from the template"),
    "check": ("myanim.check", "QA dry run of scenes: layout and animation checks, no video"),
    "render": ("myanim.render", "render scenes (skips unchanged), concatenate full.mp4"),
    "review": ("myanim.review", "contact + motion sheets and QA report of rendered scenes"),
    "fonts": ("myanim.fonts", "sync | list | add-cjk | verify the pinned fonts"),
    "previews": ("myanim.previews", "render the component gallery into assets/previews"),
}


def main(argv: list[str] | None = None):
    argv = sys.argv[1:] if argv is None else argv
    ap = argparse.ArgumentParser(
        prog="myanim",
        description="Tools for producing educational Manim videos with the myanim skill.",
        epilog="Run `myanim <command> -h` for the options of a command.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = ap.add_subparsers(dest="command", metavar="<command>")
    for name, (_, help_text) in COMMANDS.items():
        sub.add_parser(name, help=help_text, add_help=False)
    if not argv or argv[0] in ("-h", "--help"):
        ap.print_help()
        sys.exit(0 if argv else 2)
    name, rest = argv[0], argv[1:]
    if name not in COMMANDS:
        ap.error(f"unknown command {name!r} (choose from {', '.join(COMMANDS)})")
    module = importlib.import_module(COMMANDS[name][0])
    module.main(rest)


if __name__ == "__main__":
    main()
