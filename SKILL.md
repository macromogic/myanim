---
name: myanim
description: Turn technical source material (blog posts, papers, formulas, code, notes) into short, high-quality educational Manim animations about math, algorithms, ML and CS systems. Use when the user wants to plan a storyboard from material, implement or revise Manim scenes, render and inspect previews, retime scenes, or reuse/promote animation components. Not for text-to-speech or narrated-video production.
---

# Manim educational video skill

## Where things are and how to run them
`SKILL_DIR` = the folder containing this SKILL.md (Claude Code reports it as the skill's base
directory); `components/`, `references/`, `projects/_template/` below are relative to it.
All tools are subcommands of the `myanim` CLI and work from any working directory:

    myanim new | check | render | review | fonts | previews | setup | skill   (myanim <cmd> -h)

If `myanim` is not on PATH (or fails with `No module named 'myanim'`), use the fallback
`PYTHONPATH="$SKILL_DIR" uv run --project "$SKILL_DIR" python -m myanim ...` and suggest the
install from the README (`uv tool install --python 3.12 --editable "$SKILL_DIR"`).

- **First use on a machine:** if `myanim render` / `myanim check` fails with missing fonts,
  LaTeX packages or tools, run `myanim setup` and report what it lists as missing.
- **Video projects** are working data, not part of the skill: create them where the user wants
  (`myanim new --dir <folder>`, default `$MYANIM_PROJECTS` or `SKILL_DIR/projects`, which
  is not version-controlled except `_template` and `attention-demo`).
- **Invocation:** `/myanim <path to source>` or a request like "make a video from this post".

## Read first
- `references/pedagogy.md` (the popular-science bar; mandatory before Stage A2)
- `references/design-system.md` (colors, type, layout, pacing; mandatory for every scene)
- `references/manim-notes.md` (Manim CE 0.22 gotchas found in practice)
- `components/README.md` (what already exists: reuse before writing new code)
- `references/lessons.md` (accumulated lessons from earlier projects)

## Autonomy
`project.toml` → `mode`:
- **collaborative** (default): two checkpoints. (1) Stop after Stage A2 and ask the user to
  review the outline + audience contract; record approval as `status: approved` in
  `audience.md`. (2) Stop after Stage B for the storyboard; record approval by setting scene
  `status = "approved"` in `project.toml` and the storyboard. Never storyboard or render
  against an unapproved audience contract.
- **autonomous**: run all stages without stopping. Same files, same scripts; log every
  decision you would otherwise have asked about in `evaluation.md` → "Decisions taken".

Status rules for each scene (`draft` → `approved` → `locked`):
- `draft`: change freely.
- `approved`: change only what the user asked for; keep the event ids, order and visuals.
- `locked`: do not touch its scene file or timing unless the user explicitly names it.
Never regenerate a scene the request does not concern. Each scene is its own file, and
`render.py` skips scenes whose inputs did not change.

## Workflow

### Stage 0: set up the project
`myanim new <slug> --source <file> [--title "..."] [--dir <folder>]`
creates `<folder>/<slug>/` from `projects/_template/` and copies the source material into
`source/`. Ask the user where videos should live if it is not clear.

### Stage A: content analysis → `outline.md`
Read all the source material. Fill in the template sections: audience and assumed
knowledge, 3–5 learning objectives, dependency order, **must stay faithful** (formulas,
claims, numbers; with source section refs), **free to restructure/design**, and a
*visual vs. narration* table: animate only what motion clarifies (processes, change,
correspondence, geometry). Leave definitions, history and caveats to narration or a static frame.

### Stage A2: audience contract → `audience.md` (checkpoint 1)
The source was written for *its* readers; the video must work for a general audience
(`references/pedagogy.md`). Write: a concrete persona; a knowledge map marking every
concept the explanation relies on as `assume` / `remind` / `teach` / `skip`; the gap list
(steps the source skips that the persona can't, each with a bridging visual); the
motivation chain (questions the video answers, in order); scope cuts. Run the self-test in
`pedagogy.md`. **Collaborative mode: stop here and ask for review.** Restructuring hooks and
transitions is not enough: every `teach` item needs beats that justify it on screen.

### Stage B: storyboard → `storyboard.md`
Follow `references/storyboard-guide.md`, built on the approved `audience.md`: scene order
follows the motivation chain, every `teach` item gets beats, nothing is named before it is
shown. One scene = one learning objective, 15–35 s.
Per scene: id, status, target seconds, source refs, objective, visuals, a beat table
(`event id | visual | narration note | ~s`), and the transition out. Fix the
concept→color mapping for the whole video at the top. Narration notes are for the
user's own voice-over only; no TTS.
Register scenes in `project.toml`. **Collaborative mode: stop here and ask for review (checkpoint 2).**

### Stage C: assets and visual design
Resource order: (1) user-provided visuals in `source/`, (2) `components/` and `assets/`,
(3) plain Manim, (4) new code. Reuse when it fits. Do not bend a component into
something that hurts clarity; write a new local helper instead.

### Stage D: implementation
- Put every on-screen number in `data.py`, computed in code, with each step using the
  *displayed* rounded values of the previous step. Self-check with `assert`s.
- Put concept colors and objects handed between scenes in `shared.py`. Scene N+1
  rebuilds scene N's final object with the same function, so the cut is seamless.
- One file per scene in `scenes/`; subclass `EduScene`, set `SCENE_ID`.
- Group every visual step as `self.beat("event_id", *animations, run=…, wait=…)`. Event ids
  are the storyboard's ids. They are stable handles for retiming, review frames and
  (later) narration sync. Use `self.consolidate(group)` before animating a group whose
  parts entered the scene separately.
- Use tokens from `components.style`; no raw hex colors or ad-hoc font sizes in scenes.
- Symbols in math mode (`MathTex`, `math_label`); chained moves of one object in a
  `Succession`; animate on-screen objects directly, never via a new group.
- Captions come from data (f-strings), never hand-copied numbers.
- No on-screen source tags: source references stay in the outline/storyboard. Cite a public
  source on screen (`source_tag`) only when the user asks for it.

### Stage E: render and QA (loop until clean)
```
myanim check <project>             # seconds: all layout/animation checks, no video
myanim render <project>            # 480p preview, changed scenes only
myanim review <project>            # frames + report
```
Then **look at** `renders/review/<scene>_sheet.png` (settled frame per event) **and**
`<scene>_motion.png` (25/50/75 % through each animation) for every changed scene. Motion
bugs (jumps, objects passing behind others, cluttered paths) only show in the second. Work through `references/qa-checklist.md`. `review.py` /
`EduScene` automatically report out-of-frame objects, overlapping or crowded text, text
crossing box outlines, the same object animated twice at once, re-grouped on-screen
objects (layer changes), new content appearing over content still fading out, and static holds ≥ 3 s. They cannot judge meaning, pacing
or line-over-text clutter. You must judge those from the frames, and for timing, from
the video. Fix, re-render (only changed scenes re-render), re-review.
A render without errors is not a finished scene.

Retiming without code changes: edit `timing.toml` (`event = { run = 1.5, wait = 2 }`, or
`_speed` per scene). Final: `render.py <project> -q final` (1080p60) → `renders/final/full.mp4`.

### Stage F: wrap-up and library maintenance
1. Fill `evaluation.md`: correctness, clarity, pacing, reliability, human
   corrections, reuse, open issues.
2. Promotion check for each helper written in the project. Promote to `components/` only
   if it is (a) tested in this render, (b) plausibly useful for ≥ 2 other topics, and
   (c) parameterized without project-specific data. To promote: move the code and add a
   docstring (use cases, params, example, limitations), a gallery scene in
   `examples/component_gallery/` + `project.toml` entry, run `myanim previews`,
   add a row to `components/README.md`. Otherwise leave it in the project.
3. Add generalizable lessons (not project trivia) to `references/lessons.md`. Fold
   repeated lessons into the design system or the Manim notes.

## Narration (out of scope for the MVP, but keep compatible)
The user records their own voice-over. Keep narration notes in the storyboard. The event
log `renders/qa/<Scene>.events.json` (start / anim_end / end per event) plus `timing.toml`
are the intended hooks for future alignment. Do not build audio processing unless asked.

## Files at a glance
| path | role |
|---|---|
| `components/` | shared package: `style`, `EduScene`, `MatrixGrid`, `WeightBars`, `Formula`, `mixed`, `code_block`, `count_to`, text helpers |
| `assets/` | shared static resources (`previews/` of components; SVGs/images you promote) |
| `examples/component_gallery/` | one runnable demo per component (source of previews) |
| `projects/_template/` | skeleton copied by `myanim new` (incl. `audience.md`) |
| `<project>/` | per-video working data: **not version-controlled** (only `_template` and `attention-demo` are) |
| `projects/attention-demo/` | complete reference project (outline → storyboard → scenes → evaluation) |
| `myanim/` | the `myanim` CLI: `new`, `check`, `render`, `review`, `fonts`, `previews`, `setup`, `skill` |
| `references/` | pedagogy, design system, Manim notes, storyboard guide, QA checklist, lessons |
