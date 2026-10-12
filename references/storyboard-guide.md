# Writing outlines and storyboards

Templates: `projects/_template/outline.md` and `storyboard.md`. Worked example:
`projects/attention-demo/`.

## Outline (Stage A)
1. **Audience**: who, what they already know, what they have seen but don't understand.
2. **Learning objectives**: 3–5 statements, each "viewer can explain/predict X". Tag
   each with its source section.
3. **Dependency order**: the chain of concepts; the storyboard follows it.
4. **Must stay faithful**: formulas, definitions, claims, numbers, the author's stated
   reasons. Quote or reference the section. These are not paraphrased into something
   subtly different.
5. **Free to restructure / design**: order inside a step, examples, metaphors, visuals.
   If you invent an example (numbers, toy data), say so and keep it consistent with the
   source's claims.
6. **Visual vs. narration** table. Animate processes, change, geometry, correspondence.
   Narrate motivation, history, caveats. Out-of-scope items are listed explicitly.

## Storyboard (Stage B)
Header: total target length, scene count, **concept → color mapping**, status legend.

Per scene:
```
## <scene_id> — <one-line claim the scene makes>
`status: draft` · `target: 25s` · `source: §2` · class `S02Softmax`
**Objective:** one sentence.
**Visuals:** layout in words (what is left/right/top), components used.
| event | visual | narration note | ~s |
**Transition out:** what the last frame is and how the next scene picks it up.
```
Rules:
- Event ids: short `snake_case` verbs/nouns (`show_keys`, `normalize`, `map_values`).
  They become code identifiers, timing keys and review frame names.
- Each beat changes one thing. If the narration note needs "and then", split it.
- First instance of a repeated operation gets its own beat; the rest are grouped.
- Write narration notes as the user might say them. Keep them short; they are cues, not a script.
- Numbers in the storyboard are illustrative copies; `data.py` is authoritative.
- Mark the scene's status. Only the user moves it to `approved` / `locked`.

## Editing an approved storyboard
When the user edits one scene, change only that scene's code and timing. Keep event
ids that still exist. If ids must change, also update `timing.toml`.
