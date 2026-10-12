# Lessons (append after each project; fold recurring ones into the design system)

Format: **lesson**: evidence (project, event). How to apply.

## From attention-demo (2026-10-12)

1. **Pick example data for the picture, not just the math.** The first *cat* key was
   nearly collinear with the query and hid the query arrow and label (s01 `show_keys`).
   Choose toy vectors with ≥ 15° angular separation and distinct lengths, then confirm
   the derived numbers (e.g. weights sum to 1.00 after rounding) in `data.py`.
2. **Chain rounding on displayed values.** Computing the output from unrounded weights
   gave 0.52 while the on-screen arithmetic gives 0.53. Every step in `data.py` uses the
   previous step's rounded value.
3. **Overlap thresholds must be strict for text.** A caption overlapping the source tag by
   9.5 % of its box was clearly visible but passed a 15 % threshold. Text boxes are
   tight: any overlap is a defect, and gaps < 0.08 read as one word ("0.490.07", s03).
4. **The most common layout defect is a label straddling a box edge** (s03 `map_*`).
   Now auto-checked. Place annotation labels so they extend *away* from neighboring
   boxes (`aligned_edge`), alternating above/below.
5. **Line-over-text and z-order problems are not auto-detected.** The projection line
   covered the query arrow (s01 `project_cat`). Look at the frames.
6. **Freeze detection needs a low noise threshold** (`n=0.0003`). At the ffmpeg default,
   thin lines being drawn at 480p were reported as a 4 s freeze.
7. **Hand-off by shared builder works.** s01 ends and s02 starts with
   `final_score_column()` from `shared.py`; the cut is invisible.
8. **Split the first instance of a repeated operation into its own beat**
   (`score_cat` → `score_rest`, `row_cat` → `rows_rest`). It reads well and gives
   narration a natural place to explain the operation once.
9. **A math symbol in a caption can mislead.** "×" between the weight column and the
   value table reads as a matrix product; a caption ("multiply each value by its
   token's weight") disambiguates it. Prefer words or exact notation.

## Debugging snippet: run a scene's logic without rendering video
```python
# from the project dir: PYTHONPATH=../..:. uv run python this.py
import sys

sys.path.insert(0, "scenes")
from manim import config
from s03_weighted_sum import S03WeightedSum

config.dry_run = True
config.progress_bar = "none"
s = S03WeightedSum()
s.render()
print(s._warnings)  # layout warnings per event
```

## Fonts (2026-10-12)
10. **Bundle fonts; use Pango fallback lists for CJK.** `font="Libertinus Serif, Noto Serif CJK SC"`
    renders mixed Latin/CJK in one `Text`. Font files in `assets/fonts/` are registered with
    `manimpango.register_font` at import, so renders don't depend on the machine. Verified by
    uninstalling the system copies. Manim's "Font … not in [...]" warning for lists is spurious
    (filtered; `check_families` verifies instead).
11. **Changing the body font changes perceived size.** Libertinus' small x-height made 22 pt
    labels hard to read at 480p; sizes were raised ~2 pt. After a font change, re-review every
    contact sheet; the layout checker passed both before and after, so it can't judge legibility.

## From the user's first review of attention-demo (2026-10-12)
12. **Settled frames hide motion bugs.** Three defects the user saw in the video were
    invisible in event contact sheets: a highlight box restarting from row 1 on every move
    (concurrent Transforms in a LaggedStart), numbers travelling *behind* fading cells
    (new VGroup re-added on top), labels flying through growing bars. Now: two automatic
    checks (`concurrent_animations`, `regrouped_onscreen`) caught the first two on a dry
    run, and `review.py` writes mid-animation motion sheets (25/50/75 %) for the rest.
13. **Symbols in math mode, always.** `Text("q (it)")` looked like body text, not a
    variable. Use `math_label(r"q\ \text{(it)}")`.
14. **Split rearrange from grow.** Moving a column into a row while bars grow underneath
    was busy; two beats (`scores_to_row`, `grow_bars`) read cleanly.
15. **Clear, then show.** In s03 the matrix formula was written over the tables while
    they were still fading (one beat, same area). It is invisible in settled frames and was
    found by the user. Now auto-checked (`crossfade_overlap`); fixed by splitting into
    `clear_tables` + `general_form`.
16. **Fonts: pin and download, don't commit.** `assets/fonts/fonts.toml` pins each file to
    an upstream release + sha256; `scripts/fonts.py sync` restores them. A fresh-clone test
    (fonts removed → clear error → sync → re-render) gave pixel-identical frames.

## From oa-interval-permutation (first real blog post, 2026-10-12)
17. **Video ≠ blog.** Reorder for viewers: open on the result + a puzzle, end every scene on
    the question the next one answers, keep one recurring object (the row) across scenes,
    push engineering details (memory errors, integer types) to narration.
18. **State captured at the wrong time is the #1 motion-bug family.** Seen four times:
    LaggedStart transforms (demo 1), `ChangeDecimalToValue` start value, shared `mob.target`
    of `.animate` built ahead, straight-line interpolation for a layout change. Rules: build
    chained moves with explicit targets (`Transform(mob, mob.copy()...)`), counters with
    `count_to`, layout changes with a parametric path (ValueTracker + updaters).
19. **Layout changes need a path, not endpoints.** Row→ring by endpoint interpolation
    collapses everything into the centre; bend along a curve with preserved arc length.
20. **Checks must be refined against false positives with regression tests.** Each new
    check was run on the old buggy code (must fire) and the current scenes (must stay quiet);
    the regroup check was narrowed to "regrouped objects crossed by a mover".
21. **CJK + math:** LaTeX can't set CJK here; `mixed()` places Pango prose and MathTex on one
    measured baseline. Lone Latin letters in prose are symbols → `symbol_in_text`.
22. **Third-party theming breaks color semantics** (Pygments in `Code`). Prefer monochrome
    components whose only colors come from `style`.
23. **Test the checker itself on known-bad input.** The overlap checks had silently skipped
    every `MathTex` since the start (a MathTex parent reports fill opacity 0; only its glyphs
    carry opacity). Found only when a zoomed frame showed a caption covering an index label.
    Now: visibility from glyphs, glyph-level overlap tests, `mixed()` lines as one text unit,
    identity de-duplication. Re-run all scenes of all projects after changing a check.
