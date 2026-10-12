# Evaluation & iteration log: Scaled dot-product attention (one query)

MVP demonstration project, 2026-10-12. Source: stand-in note `source/attention-note.md`
(written for the demo; not a real blog post). Mode: collaborative, but the storyboard
was **not** reviewed by the user before implementation (the brief asked for an
end-to-end build). The user reviewed the rendered video afterwards; after fixes, all scenes
were approved on 2026-10-12.

## Summary
| criterion | status | notes |
|---|---|---|
| technical / mathematical correctness | ✅ checked | formulas match §1–§3 symbol by symbol; all numbers from `data.py` with chained rounding + assert; output (0.49, 0.07) can be verified from the on-screen contributions |
| visual clarity | ✅ after 4 fix rounds | no automated layout warnings; frames reviewed by eye per event (contact sheets) |
| animation pacing | ⚠️ unverified with voice | final full.mp4 = 66.9 s (1080p60) vs. 80 s target. Holds 0.5–3 s; retime via `timing.toml` once narration is recorded |
| rendering reliability | ✅ | all scenes render at 480p15 and 1080p60; unchanged scenes skipped; failures print a readable traceback |
| asset reuse | first project, so the library was built here | all components were written for this MVP and then generalized + given gallery demos: `MatrixGrid` (s01, s03 ×4 instances), `WeightBars` (s02, 2 scales), `Formula` (s02, s03), text helpers (all), `EduScene` (all). Not promoted: 2-D vector plane, formula annotation (see components/README.md) |

## Iterations
| # | checked | problems found | fix |
|---|---|---|---|
| 1 | s01 contact sheet | *cat* key nearly collinear with query: hid the query arrow and label; caption overlapped source tag; layout checker silent | new *cat* key (1.5, 0.3), numbers re-derived; source tag moved top-right; overlap threshold 15 % → 2 % |
| 1 | review.py freeze report | 4 s "static hold" that actually contained the projection animation | freezedetect noise 0.001 → 0.0003 |
| 2 | s01 + s02 sheets | projection line ran through "q (it)" label; plane small; "-0.25" crowding "the" | q label up-left; plane enlarged; bar label depth increased |
| 2 | s02 render | crash: `VGroup(*self.mobjects)` with a non-VMobject; Rich traceback wrapped to 20 cols | `Group(...)`; `COLUMNS=160` + stderr-only error output in render.py |
| 2 | s02 logic | ReplacementTransform of a group whose parts were added separately would leave ghosts | `EduScene.consolidate()` |
| 3 | s01 frame | yellow projection covered the blue query arrow | `q.set_z_index(2)` |
| 3 | s02 frame | token labels top-aligned, so "on" looked off-baseline | bottom-align bar labels |
| 4 | s03 sheet | output "0.490.07" merged; annotation labels straddled box outlines; ambiguous "×" | output as `MatrixGrid`; labels extend away from neighbors; explanatory caption. New auto-checks: `text_crowding`, `text_crosses_box` (they flagged exactly these 3 defects on a dry run) |
| 5 | component gallery | new `text_crowding` check caught a negative-bar value label touching its token label | WeightBars default label depth accounts for negative value labels |
| 6 | retime test | `interpret` wait 2.2 → 3.0 s in `timing.toml` | only s02 re-rendered (hash now per-scene timing section) |

## Human corrections
- Use `uv` for environment setup (instead of pip/venv). Applied; recorded in project memory.
- First video review (2026-10-12): (1) s03 highlight box restarted from row 1 on each
  move → `Succession`; (2) `q` should be math → `math_label`; (3) s02 numbers moved behind
  the table cells → animate cells directly. Also fixed, found via the new motion sheets:
  s02 labels flying through growing bars → split into `scores_to_row` + `grow_bars`.
  New checks `concurrent_animations` / `regrouped_onscreen` + motion sheets added to the Skill.
- Follow-up: the s03 formula was written over the still-fading tables → split into
  `clear_tables` + `general_form`; new check `crossfade_overlap`.
- Math font: Computer Modern kept (Libertinus Math compared side by side, declined for now).
- 2026-10-12: user approved all three scenes (status `approved` in project.toml and storyboard).

## Decisions taken without asking
- Topic: attention for one query (a single, well-known formula that exercises
  vectors, tables, distributions and formula annotation).
- Wrote the source note myself so traceability could be demonstrated (§ refs in source tags).
- Toy data chosen for visual separation (lesson 1), tokens "it" → cat/on/the/mat.
- √d_k rationale kept to one sentence in the narration note; the variance argument is
  left out (outline: narration, not animation).

## Open issues / limitations
- Layout QA is bounding-box only: line-over-text, z-order, and semantic clarity need eyes.
- No validation that narration fits the beat lengths (needs the user's recording).
- The ×-between-tables notation is still slightly informal (element-wise row scaling).
- s01 → s02 hand-off is seamless; s02 → s03 is a fade (weights column is rebuilt, not
  carried over). Could hand off the weights as a column like s01 → s02.
- Formula part boxes hug tall glyphs (the scores box touches the parentheses); cosmetic.
- (resolved 2026-10-12) fonts are now bundled in `assets/fonts/`, so renders are machine-independent.

## Lessons promoted to references/lessons.md
1–9 (example data for the picture, chained rounding, strict text thresholds, straddling
labels, line-over-text blind spot, freeze threshold, shared hand-off, first-instance beat,
symbols in captions).
