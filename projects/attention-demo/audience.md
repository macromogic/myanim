# Audience contract — Scaled dot-product attention (one query)

Stage A2 (`references/pedagogy.md`). **Retroactive:** this stage was added to the workflow
after this demo was approved; written afterwards to show the format, not reviewed before
the storyboard.
`status: retroactive`

## Persona
A programmer / ML learner who knows vectors, dot products and has heard of softmax; has
seen `softmax(QKᵀ/√d_k)V` but cannot say what each piece does.

## Knowledge map
| concept | needed for | decision | how |
|---|---|---|---|
| vectors, dot product | scores | assume | — |
| dot product as alignment | scores | teach | 2-D plane, projection of the key onto the query |
| why divide by √d_k | scaling | skip (narration) | one caption; the variance argument is out of scope |
| exp, normalization | softmax | teach | bars morph: exponentiate, then divide by the sum |
| weighted average | output | teach | row-by-row table |
| matrix form = all queries at once | generalization | teach | formula parts boxed and mapped to scenes 1–3 |

## Gaps in the source
| # | source step | what the persona is missing | bridging idea |
|---|---|---|---|
| 1 | §1 "relevance is the dot product" | why a dot product measures relevance | projection picture |
| 2 | §3 "softmax applied row by row" | how the single-query picture becomes the matrix form | map each formula part back to its scene |

## Motivation chain
1. Which tokens should "it" look at? → scores = dot products.
2. Scores can be anything; how do we turn them into shares? → softmax.
3. What does the query actually receive? → weighted sum of values.
4. How does this relate to the formula everyone quotes? → the matrix form, row by row.

## Scope cuts
- √d_k variance argument, multi-head attention, masking, learned projections.
