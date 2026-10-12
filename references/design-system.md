# Design system

Tokens live in `components/style.py`. This file explains how to use them. Principles
are drawn from good mathematical explainer animation in general: one idea at a
time, color as meaning, motion that shows a relationship. No single creator's look is copied.

## 1. Color = meaning
- Dark background (`BG`), light text (`TEXT`), secondary text in `MUTED`.
- Before writing code, give each **concept** one accent and write the mapping at the
  top of the storyboard and in `shared.py`, e.g. query = BLUE, key/score = ORANGE,
  value = GREEN, weight/probability = PINK.
- An accent never changes meaning within a video. If two things share a color, the viewer
  will assume they are related.
- `YELLOW` is reserved for transient "look here" highlights (boxes, flashes). Remove
  it once the point is made.
- ≤ 3 accents visible at once. De-emphasize context with `MUTED` or opacity `DIM_OPACITY`
  instead of removing it when it is still needed for orientation.
- A derived quantity may inherit its source's color (scores come from keys → ORANGE).

## 2. Typography
- Body text: `FONT` = Libertinus Serif with Noto Serif CJK SC as CJK fallback. Code:
  `MONO_FONT` = IBM Plex Mono (same CJK fallback). Titles use `TITLE_WEIGHT` (semibold).
  Fonts are downloaded into `assets/fonts/` by `scripts/fonts.py sync` (pinned + checksummed);
  always pass the token, never a family name.
  Math: LaTeX via `MathTex` / `Formula`, in **Computer Modern** (user decision 2026-10-12:
  keep the familiar LaTeX look; Libertinus Math was compared and declined for now. To
  switch later: add `\usepackage{libertinust1math}` to `TEX_TEMPLATE` in `style.py`,
  re-measure `TEX_SCALE`, re-render and re-check layouts).
- Mixed Latin/CJK strings work in one `Text`: Pango picks glyphs per character. CJK
  glyph forms default to SC; a project selects TC/HK/JP/KR with `[style] cjk = "…"` in
  `project.toml` (`scripts/fonts.py sync` fetches it).
- **Symbols are always math.** Any variable or symbol (q, k_i, w_i, d_k, Σ) is set with
  `MathTex`, also inside labels: `math_label(r"q\ \text{(it)}")`, never `Text("q (it)")`.
  `\text{}` in math uses Libertinus, so words and symbols mix cleanly on one baseline.
- Sizes: title 44, heading 34 (scene titles), body 30, caption 26, label 24, small 20,
  math 40 (primary formula 44–56). Libertinus has a small x-height: don't go below 20.
- Inline math in a Text caption: prefer plain words. If a symbol is essential, build a
  MathTex caption rather than using unicode subscripts (fonts lack them).
- Numbers: fixed decimals per quantity (`{:.2f}`); never show `-0.00`.

## 3. Layout
Frame is 14.2 × 8 units. Zones:
- top-left: scene title + subtitle (`scene_title`)
- top-right: source tag (`source_tag`, e.g. "source §2"), for traceability
- bottom center (y ≈ −3.35): one caption (`caption` / `place_caption`)
- middle band (y ≈ −2.7 … 2.4): content. Usually one main visual, at most two
  side by side (diagram left, numbers/formula right).
Rules: keep `FRAME_MARGIN` (0.5) from edges; minimum gap between text items 0.08
(checked); labels never straddle box outlines (checked); align repeated items on a
grid; leave empty space rather than shrinking text below 20.

## 4. Motion and pacing
- One **beat** = one idea = one `self.beat()` call: animate (0.6–2 s), then hold (0.5–2 s).
  The hold is when the viewer reads; a key insight gets `WAIT_LONG`.
- Introduce → transform → highlight. Prefer transforming an existing object into its next
  state (`Transform`, `ReplacementTransform`, `animate_to`) over fading in a new one:
  continuity shows causality.
- Stagger lists (`LaggedStart`, lag 0.25–0.35). The first item of a repeated operation
  is shown slowly and alone, the rest quickly (e.g. `score_cat` then `score_rest`).
- Don't move what the viewer is reading. Don't animate decoration.
- **Continuity:** an object that moves several times moves *from where it is*: chain
  the moves with `Succession` (or separate beats), never several `Transform`s of the same
  object in one `LaggedStart`/`AnimationGroup` (each would restart from the old position).
- **One kind of motion at a time:** if things travel to a new layout *and* new things
  grow there, split it into two beats (rearrange, then grow), so nothing crosses
  growing shapes. Values rest on the side where their bar will grow.
- **Clear, then show:** never bring something in where something else is still fading out
  in the same beat; fade the old content (0.6–0.8 s), then write the new. Overlapping
  crossfades are fine only when the two occupy different areas.
- **Layers:** moving objects stay in front of what they pass over. Animate on-screen
  objects themselves (`FadeOut(*parts)`), not a new `VGroup` of them, which re-adds them
  on top. Use `set_z_index` when an object must stay visible over a highlight.
- Scene length 15–35 s; 6–10 beats. Holds ≥ 3 s get flagged. Make sure they are deliberate.
- Transitions: end each scene on the object the next one starts from (hand-off via
  `shared.py`), or fade to empty. No flashy wipes.

## 5. Visual vocabulary
| content | default treatment |
|---|---|
| vectors, geometry | `NumberPlane` with muted grid, `Arrow`s in concept colors, labels at tips |
| small matrices / tables | `MatrixGrid` (heat tint for magnitudes, highlight row/col/cell) |
| distributions, small vectors | `WeightBars` (fixed scale; rescale via second instance) |
| formulas | `Formula` with named parts; box parts with `.box()`; color parts by concept |
| correspondences | box both ends in the same color, or label with "1 · …, 2 · …" |
| code | Manim `Code` with `MONO_FONT`; show ≤ 12 lines; highlight the active line |
| system diagrams | rounded rectangles (`SURFACE` fill, `GRID` stroke), arrows in `MUTED`, active path in an accent |
