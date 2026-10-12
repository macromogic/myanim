# Assets

Shared static resources reusable across projects.

- `previews/`: generated previews of each component (do not edit by hand; run
  `uv run python scripts/previews.py`).
- Put promoted static resources (SVG icons, diagrams, images) in a topic subfolder, e.g.
  `assets/svg/`, and load them with `SVGMobject("assets/svg/x.svg")` / `ImageMobject`.
  Each needs a one-line entry below: file, what it depicts, license/origin.

Project-specific images stay in `projects/<slug>/source/`.

| file | description | origin |
|---|---|---|
| (none yet) | | |
