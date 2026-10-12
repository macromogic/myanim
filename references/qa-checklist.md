# QA checklist (Stage E)

Run `scripts/render.py` then `scripts/review.py`, open every changed scene's contact sheet,
and go through this list. Record unresolved items in `evaluation.md`.

## Automatic (reported by EduScene / review.py; fix all)
- [ ] no `out_of_frame`
- [ ] no `text_overlap` / `text_crowding` (gap < 0.08)
- [ ] no `text_crosses_box`
- [ ] no `concurrent_animations` (same object animated twice at once → jumps)
- [ ] no `regrouped_onscreen` (new group of on-screen objects → layer order changes)
- [ ] no `crossfade_overlap` (something appears where something else is still fading out)
- [ ] each `static hold ≥ 3 s` is deliberate (a key insight or the final frame)
- [ ] duration within ±30 % of `target_seconds` (or the storyboard is updated)

## Correctness (agent judgment, every time)
- [ ] every formula matches the source (compare symbol by symbol)
- [ ] every number on screen comes from `data.py`; arithmetic is checkable from what is shown
- [ ] no claim beyond the source; invented examples are labeled as such in the outline
- [ ] concept colors match the storyboard mapping in every scene

## Visual clarity (look at the frames)
- [ ] every symbol is in math mode (`MathTex` / `math_label`), words in the body font
- [ ] one focal point per beat; the eye knows where to go
- [ ] no lines or arrows running through labels (not auto-detected)
- [ ] nothing important hidden behind another object (check z-order)
- [ ] text readable at 480p: if it is hard to read in the preview, it is too small
- [ ] repeated items aligned; spacing consistent
- [ ] highlights (YELLOW) removed after their point is made

## Temporal behavior (open every `<scene>_motion.png`; watch `full.mp4` at least once)
- [ ] moving objects never jump back or restart from an old position
- [ ] nothing passes *behind* an object it should pass in front of
- [ ] in-flight paths don't cross other moving or growing objects (split the beat if so)
- [ ] each beat holds long enough to read what changed
- [ ] nothing moves while the viewer must read it
- [ ] scene hand-offs are seamless (same object, same position)
- [ ] no flicker or ghost copies after transforms

## Final
- [ ] `render.py -q final` succeeds; `renders/final/full.mp4` plays end to end
