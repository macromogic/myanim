# Component library

Import in scenes: `from components import *`. Each component's docstring has a full
usage example. Previews (last frame PNG + MP4) are in `assets/previews/`, rendered from
`examples/component_gallery/scenes/gallery.py` by `myanim previews`.

| component | file | use for | key parameters | preview | limitations |
|---|---|---|---|---|---|
| `style` | `style.py` | design tokens: palette, sizes, spacing, pacing | n/a | n/a | font must exist on the render machine |
| `EduScene` | `scene.py` | base class: `beat()` timed events, `timing.toml` overrides, event log, layout QA, `consolidate()` | `SCENE_ID`, `CHECK_LAYOUT` | n/a | QA is bounding-box based: misses line-over-text, z-order, meaning |
| `MatrixGrid` | `matrix_grid.py` | small matrices/tables, heat tint, row/col/cell highlight, value morphing | `values, fmt, cell_size, row_labels, col_labels (str or Mobject), heat, heat_range, brackets, text_color` | `matrix_grid.png/.mp4` | ≤ ~8×8 readable; numbers only (no symbolic cells) |
| `WeightBars` | `weight_bars.py` | small signed vectors / distributions that change; rescale by swapping instances | `values, labels, value_range, max_height, color(s), fmt, label_depth`; `animate_to()`, `move_baseline_to()`, `bar_group()` | `weight_bars.png/.mp4` | vertical only; no axis ticks; ≤ ~10 bars |
| `Formula` | `formula.py` | MathTex with **named parts**: color/box/transform parts by name | `parts=[(key, tex), …], colors`; `f["key"]`, `f.box(*keys)` | `formula.png/.mp4` | box is a rectangle around glyph bounds (tight around tall parts) |
| `mixed` / `baseline_y` | `mixed.py` | one line of prose (incl. CJK) with inline `$...$` math on a shared baseline; `scene_title`/`caption` route `$...$` through it | `s, size, color, math_color, t2c, weight`; `line.prose`, `line.math` | — | single line; `$` cannot appear literally |
| `count_to` | `anim.py` | counter steps with an explicit start value (safe in `Succession`) | `number, start, end, integer` | — | integers switch at the step midpoint |
| `code_block` | `code.py` | monochrome code panel (no Pygments colors), `//` comments muted, CJK comments OK | `lines, size`; `block.lines[i]` | run `myanim previews` | no syntax highlighting by design; `//` comments only |
| text helpers | `text.py` | `scene_title`, `caption`/`place_caption`, `label`, `math`; `source_tag` only for public citations the user asks for | text, color, size | `text.png/.mp4` | caption is one line, auto-shrinks if too wide |

## Promotion criteria (from SKILL.md, Stage F)
Promote a project helper here only when it is tested in a real render, plausibly useful
for ≥ 2 other topics, and free of project data. Every promotion adds: docstring (use
cases, parameters, example, limitations), a gallery scene + `project.toml` entry,
regenerated previews, and a row in this table.

## Candidates seen but not promoted (yet)
- *bend a row into a ring*: arc-length-preserving bend driven by one ValueTracker
  (curvature 0 → full circle, slots/cards/labels follow via updaters), so items keep their
  order instead of collapsing through the centre as with endpoint interpolation. Built for a
  permutation-cycles video; promote on second use (any rotation / modular-arithmetic topic).
- *cards in slots + cart-legal moves*: a row of slots with cards, arc moves with constant lift,
  a move log that can be replayed backwards ("rewind"). Promote once a second
  array-manipulation video (sorting, in-place permutation) needs it.
- *labeled 2-D vector plane* (`s01_scores.py`: plane + arrows + tip labels + projection):
  likely reusable (dot products, linear maps, gradients) but only used once. Promote on
  second use.
- *formula part annotation* (`s03_weighted_sum.py` `annotate`): box + label with
  `aligned_edge`; candidate for a `Formula.annotate()` method on second use.
