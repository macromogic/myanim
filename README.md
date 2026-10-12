# myanim: an AI-assisted Manim skill for educational videos

An agent Skill (entry point: [`SKILL.md`](SKILL.md)) for turning technical material into
short educational animations with Manim Community Edition. The workflow is:
source → outline → storyboard → scenes → render → review → reusable components.

## Setup (macOS, Apple Silicon)
```bash
brew install uv cairo pango pkgconf ninja ffmpeg   # + MacTeX/BasicTeX for MathTex
uv sync                                            # if pycairo fails with an xcrun/x86_64 error, see references/manim-notes.md
uv run python scripts/fonts.py sync                # download pinned fonts (~50 MB, not in git)
uv run pre-commit install                          # git hooks (lint, format, guards)
uv run manim --version                              # Manim Community v0.22.0
```
Python 3.12 is pinned in `.python-version`. Fonts (Libertinus Serif, IBM Plex Mono, Noto
Serif CJK) are downloaded from pinned upstream releases by `scripts/fonts.py sync` and
registered automatically; no system font installation is needed. CJK text defaults to
Simplified Chinese glyph forms; set `[style] cjk = "JP"` (TC/HK/JP/KR) in a project's
`project.toml` and re-run `sync`. Details: `assets/fonts/README.md`.

## Git hooks
`.pre-commit-config.yaml` runs on every commit:
- hygiene: trailing whitespace, final newline, LF line endings, valid TOML/YAML,
  merge-conflict markers, private keys, broken symlinks, files > 500 KB
- `ruff` lint (auto-fix) and `ruff format` (config in `pyproject.toml`)
- `no-generated-binaries`: blocks font files and render output, even if force-added
- `data-selfcheck`: runs a changed `projects/*/data.py`, so its asserts on on-screen numbers must hold

Run everything manually: `uv run pre-commit run --all-files`.

## Quick start
```bash
uv run python scripts/new_project.py my-topic --source path/to/post.md   # scaffold
# ... agent writes outline.md, storyboard.md, data.py, scenes/ (see SKILL.md) ...
uv run python scripts/render.py projects/my-topic        # 480p preview, changed scenes only
uv run python scripts/review.py projects/my-topic        # contact sheets + QA report
uv run python scripts/render.py projects/my-topic -q final
```
With Claude Code in this folder, the skill is available as `manim-edu`
(`.claude/skills/manim-edu/SKILL.md` → `SKILL.md`). Example request:
*"Use manim-edu on projects/my-topic/source/post.md and propose a storyboard."*

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
scripts/            new_project, render, review, previews
projects/           _template + one folder per video
```
