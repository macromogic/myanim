# Manim CE notes (v0.22, verified in this repo)

## Setup
- Install with uv (`uv sync`). Building `pycairo` needs Homebrew `cairo`, `pango`,
  `pkgconf`. **If `/usr/local/bin/ninja` is an x86_64 leftover**, meson runs the
  compiler under Rosetta and the build fails with `xcrun: unable to load libxcrun …
  need 'x86_64'`. Fix: `brew install ninja` (arm64), then either remove the x86_64 one
  or run `NINJA=/opt/homebrew/bin/ninja uv sync`. (On the dev machine the x86_64 ninja
  came from an Intel Homebrew kept for Apple's Game Porting Toolkit; it was removed on
  2026-10-12 and the rest of that Homebrew kept. Other x86_64 tools there may still
  shadow builds.)
- LaTeX (MacTeX/TeX Live with `dvisvgm`) is required for `MathTex`.
- **`myanim: ModuleNotFoundError: No module named 'myanim'`** (editable install): on macOS,
  Python ≥ 3.12.10 skips `.pth` files that carry the "hidden" file flag. On the dev machine
  some process outside uv/git/pre-commit repeatedly sets that flag on dot-folders *inside the
  workspace* (`.venv`, `.git`, `.ruff_cache`), so `uv run myanim` in the clone breaks again
  after a fix. Robust: use the global tool install (`uv tool install --editable .`, its
  environment lives in `~/.local/share/uv/tools`, unaffected) or `uv run python -m myanim`
  inside the clone (doesn't rely on the `.pth`). `chflags -R nohidden .venv` is a temporary fix;
  `myanim setup` reports hidden `.pth` files.
- pydub prints `SyntaxWarning`s on Python 3.12+; `render.py` silences them.

## Rendering
- Always render through `myanim render`. It sets `PYTHONPATH` so scenes can
  `from components import ...` and `import data`, widens the terminal so Rich
  tracebacks stay readable, and skips unchanged scenes.
- Quality presets: preview `-ql` (480p15) for iteration, draft `-qm` (720p30),
  final `-qh` (1080p60). Event timing does not depend on quality.
- Scene code runs fully even when Manim reuses cached partial movies, so event logs
  and layout checks are always current.
- To test scene logic fast without rendering video:
  `config.dry_run = True; MyScene().render()` (see the debugging snippet in lessons.md).

## API facts that bit us
- `MathTex("a", "b", ...)`: parts are compiled as **one** expression and split by
  internal markers, so a part may hold unbalanced braces: `r"w_i = \frac{"`,
  `"e^{s_i}"`, `"}{"`, ... The part `"}{"` becomes the fraction bar. `\left(`/`\right)`
  across parts works too. The `Formula` component builds on this.
- `VGroup(*self.mobjects)` fails if the scene holds a plain `Mobject`. Use
  `Group(*self.mobjects)` for "fade out everything".
- `ReplacementTransform(group, new)` when the group's parts were added to the scene
  individually leaves **ghost copies** of those parts. Call
  `self.consolidate(group)` first (EduScene helper).
- `AnimationGroup`/`LaggedStart` call `begin()` on **all** sub-animations when the group
  starts, so each `Transform(box, target_i)` records the box's position *at group start*:
  chained moves restart from the first position. `Succession` begins each sub-animation
  when it is reached, so chained moves are continuous. (Auto-checked:
  `concurrent_animations`.)
- `mob.animate...` stores its target in the shared attribute `mob.target`; the animation is
  assembled when played. Building two `.animate` moves of the same object before playing
  the first (e.g. a list of moves prepared up front) makes the first one go to the *second*
  target. Use `Transform(mob, mob.copy().move_to(p), path_arc=…)` for moves built ahead.
  (Auto-checked: `pending_animate`.)
- `ChangeDecimalToValue(num, v)` reads `num`'s current value when the animation is
  *constructed*. Chained steps built up front (e.g. a counter in a `Succession`) all
  restart from the old value. Use `count_to(num, start, end)`. (Auto-checked: `stale_start`.)
- `play(FadeOut(VGroup(a, b)))` where a, b are already on screen adds that new VGroup on
  top, so a, b are drawn in front of everything for the animation (things moving past
  them slip behind). Use `FadeOut(a), FadeOut(b)`. (Auto-checked: `regrouped_onscreen`.)
- `MathTex` at `font_size=s` renders ~0.75× the size of `Text` at `s`. Use
  `math_label()` (scales by `style.TEX_SCALE`) for labels that sit next to Text.
- `config.tex_template` is set by `components` to load `libertinus-type1`, so
  `\text{}` matches the body font; math symbols stay Computer Modern.
- `Arrow(..., buff=0)` is needed for vectors starting exactly at the origin.
- z-order: later-added objects draw on top. When a highlight (e.g. a projection line)
  should sit *under* an existing object, `set_z_index(2)` the object that must stay visible.
- `Text.move_to(point, aligned_edge=UP)` aligns tops: labels without ascenders
  ("on", "a") then look misaligned against ones with ascenders. Use `aligned_edge=DOWN`
  for rows of words (wrong only for descenders).
- Unicode subscripts (ᵢ) in `Text` depend on the font; prefer `MathTex`.
- Formatting `-0.0` gives `"-0.00"`; format `v + 0.0`.

## Structure conventions
- Every on-screen number comes from `data.py` (computed, rounded at the same steps as
  shown, `assert`ed).
- Cross-scene hand-off objects are built by one function in `shared.py`.
- `EduScene.beat()` raises on duplicate event ids. Event ids are API: renaming one
  breaks `timing.toml` overrides and review frame names.
