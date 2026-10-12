# Pedagogy: explaining to a general audience

The bar is popular science: a curious viewer who does **not** share the source author's
background must be able to follow every step. A source written for experts (blog post,
paper) skips steps its readers already know; the video must not. Stage A2 (`audience.md`)
makes those decisions explicit *before* any storyboard.

## Principles
1. **Concrete before abstract.** Show a specific example doing the thing, then name it,
   then generalize. Never open with a definition.
2. **Every idea answers a question the viewer would ask.** Write the question first
   ("why would a gcd appear?", "does it always loop back?"). If no viewer would ask it
   yet, the idea comes too early: motivate it or move it.
3. **Let the viewer almost discover it.** Show the pattern before stating the rule (pause
   on "notice anything?"), then confirm.
4. **Name things only when they are needed,** and only once the viewer has seen them.
   Jargon used before it is earned ("permutation", "residue class") is a gap.
5. **Justify, don't assert, the key steps.** "Permutations decompose into cycles" is a
   claim; *following arrows until you must return* is an explanation. Spend screen time
   on the steps the conclusion depends on; cut asides.
6. **One new idea per beat, one recurring picture per video.** Reuse the same objects so
   the viewer's mental model carries over.
7. **Payoff closes the opening question,** in the opening's terms.

## Building the audience contract (`audience.md`)
- **Persona:** one concrete viewer ("can write a loop over an array; has never heard of
  cycle decomposition"). Avoid "anyone interested in X".
- **Knowledge map:** list *every* concept the explanation relies on (including ones the
  source never mentions because its readers know them). Mark each:
  `assume` (persona knows it; say so in the contract) · `remind` (≤ 5 s, one picture) ·
  `teach` (gets its own beats, motivated and justified on screen) · `skip` (out of scope:
  say how the video avoids needing it).
- **Gap list:** walk the source step by step and ask, for the persona: *what would I need
  to believe this step?* Each missing piece becomes a `teach` or `remind` item with a
  proposed bridging visual.
- **Motivation chain:** the sequence of questions the video answers, in order. Each scene
  answers one and raises the next.
- **Scope cuts:** what is deliberately left out and why (time, audience).

## Self-test before asking for approval
- Read the motivation chain aloud as the persona. Any step where the persona would say
  "why?" or "what is that?" without an answer on screen is a gap.
- Count `teach` items: more than ~3 per 2 minutes means the scope is too big; cut or split.
- Every `teach` item has a visual idea, not just narration.
