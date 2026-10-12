# myanim: an AI-assisted Manim skill for educational videos

An agent Skill (entry point: [`SKILL.md`](SKILL.md)) for turning technical material into
short educational animations with Manim Community Edition. The workflow is:
source → outline → storyboard → scenes → render → review → reusable components.

## Install
```bash
brew install uv ffmpeg cairo pango pkgconf ninja     # + MacTeX/BasicTeX for MathTex
git clone git@github.com:macromogic/myanim.git && cd myanim
uv tool install --python 3.12 --editable .           # puts the `myanim` command on your PATH
myanim setup                                         # checks tools/LaTeX, downloads pinned fonts (~50 MB)
myanim skill install                                 # makes /myanim available in every Claude Code session
```
- `--editable` runs the CLI straight from this clone: `git pull` updates the CLI and the skill
  together. Inside the clone, `uv run python -m myanim ...` works without installing.
- `myanim setup` reports anything missing with the command to fix it (`--dev` also installs
  the git hooks, for working on the skill itself). If building `pycairo` fails with an
  `xcrun`/x86_64 error, or `myanim` says `No module named 'myanim'`, see
  `references/manim-notes.md`.
- Fonts (Libertinus Serif, IBM Plex Mono, Noto Serif CJK) are not stored in git; CJK defaults
  to Simplified Chinese glyph forms (`[style] cjk` in a project's `project.toml`, then
  `myanim fonts sync`, for TC/HK/JP/KR).
- `myanim skill install` links `~/.claude/skills/myanim` to this clone (`status`, `uninstall`).

## Use
In Claude Code, from any folder (e.g. your blog or a private videos repo):
- `/myanim path/to/post.md`, or just ask: *"Make a short explainer video from path/to/post.md."*
- The agent creates a project folder (asks where; `$MYANIM_PROJECTS` sets the default), then
  stops twice for your review: the **audience contract** (who the video is for, what it must
  explain) and the **storyboard**. After that it renders previews, reviews its own frames and
  produces `renders/final/full.mp4`.

Video projects are working data and are not part of this repo (only `projects/_template` and
the workflow demo `projects/attention-demo` are tracked).

## Git hooks
`.pre-commit-config.yaml` runs on every commit:
- hygiene: trailing whitespace, final newline, LF line endings, valid TOML/YAML,
  merge-conflict markers, private keys, broken symlinks, files > 500 KB
- `ruff` lint (auto-fix) and `ruff format` (config in `pyproject.toml`)
- `no-generated-binaries`: blocks font files and render output, even if force-added
- `data-selfcheck`: runs a changed `projects/*/data.py`, so its asserts on on-screen numbers must hold

Run everything manually: `uv run pre-commit run --all-files`.

## The CLI
```bash
myanim new my-topic --source post.md --dir ~/videos   # project from the template
myanim check ~/videos/my-topic        # seconds: all layout/animation checks, no video
myanim render ~/videos/my-topic       # 480p preview, changed scenes only
myanim review ~/videos/my-topic       # contact + motion sheets, QA report
myanim render ~/videos/my-topic -q final
myanim fonts list | sync | add-cjk JP | verify
myanim previews                       # component gallery -> assets/previews
```
`myanim <command> -h` shows each command's options.

## Reference project
`projects/attention-demo/`: scaled dot-product attention for one query, 3 scenes, ~67 s.
Outline, storyboard, data, scenes, review report and evaluation are all included. Rendered
video: `projects/attention-demo/renders/final/full.mp4` (after running the final render).

## Layout
```
SKILL.md            workflow the agent follows
references/         design system, Manim notes, storyboard guide, QA checklist, lessons
components/         shared Manim package (style tokens, EduScene, MatrixGrid, WeightBars, Formula, text)
assets/             shared static resources; previews/ of components
examples/           component_gallery (runnable demos → previews)
myanim/             the CLI (new, check, render, review, fonts, previews, setup, skill)
projects/           _template + one folder per video
```
