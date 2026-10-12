# Storyboard — Scaled dot-product attention (one query)

Total target ≈ 80 s · 3 scenes · all numbers come from `data.py` (storyboard numbers are illustrative copies) · preview with `myanim render`, review with `myanim review`.

**Color semantics (fixed for the whole video):** query = BLUE · key / score = ORANGE ·
value = GREEN · attention weight = PINK · transient highlight = YELLOW.

**Status legend:** `draft` (agent may change freely) → `approved` (change only the parts the
user asks about) → `locked` (do not touch code or timing without an explicit request).

Event ids in the tables are the ids used in code (`self.beat("<id>", ...)`) and in `timing.toml`.

---

## s01_scores — Scores: how well does each key match the query?
`status: approved` · `target: 25s` · `source: §1, §WE` · class `S01Scores`

**Objective:** a score is the dot product of query and key, so it measures alignment.

**Visuals:** left: small 2-D plane with the query arrow (BLUE, "it") and four key arrows
(ORANGE, "cat/on/the/mat"). Right: a 4×1 grid of scores labeled by token.

| event | visual | narration note | ~s |
|---|---|---|---|
| `title` | Title "1 · Scores" + subtitle | "The token *it* needs context. Which words should it look at?" | 2 |
| `show_query` | plane fades in, query arrow grows | "*it* emits a query vector." | 2 |
| `show_keys` | four key arrows grow, staggered | "Every token offers a key." | 2.5 |
| `project_cat` | dashed drop from the *cat* key onto the query direction; projection highlighted | "The dot product measures how far the key reaches along the query." | 3 |
| `score_cat` | score cell for *cat* appears: 1.68 | "For *cat*, it is large: 1.68." | 2 |
| `score_rest` | remaining scores appear, staggered | — | 2.5 |
| `alignment` | caption: aligned → large, orthogonal → ≈ 0, opposed → negative; *on* and *the* briefly flash | "*on* is almost perpendicular, *the* points away." | 3.5 |
| `scale` | formula `s_i = q·k_i/√d_k` appears top-right; scores morph to scaled values | "Finally we divide by √d_k so scores don't blow up as dimensions grow." | 4 |

**Transition out:** fade everything except the score column → next scene starts from scores.

---

## s02_softmax — Softmax turns scores into weights
`status: approved` · `target: 25s` · `source: §2` · class `S02Softmax`

**Objective:** exponentiate (positive, gaps stretched), then normalize (sum to 1).

**Visuals:** formula `w_i = e^{s_i} / Σ_j e^{s_j}` at top with named parts; bar chart of
the four tokens in the middle, on one fixed scale for scores and exps.

| event | visual | narration note | ~s |
|---|---|---|---|
| `title` | Title "2 · Softmax" | — | 1.5 |
| `scores_to_row` | score column lays down into a row on the bar baseline | — | 1.5 |
| `grow_bars` | ORANGE bars grow and lift their numbers (one negative) | "Scores can be any real number, even negative." | 2 |
| `show_formula` | softmax formula written | "Softmax fixes that in two steps." | 2 |
| `exponentiate` | numerator boxed; bars morph to e^{s_i} | "Exponentiate: everything becomes positive, and the gaps get stretched." | 4 |
| `sum` | denominator boxed; "Σ = 7.14" appears | "Add them up…" | 2.5 |
| `normalize` | bars become PINK weights (new scale), "Σ wᵢ = 1.00" | "…and divide. The weights add up to one." | 4 |
| `interpret` | *cat* bar highlighted; caption "it pays 46% of its attention to cat" | "Almost half of the attention of *it* goes to *cat*." | 3.5 |

**Transition out:** fade out; weights reappear as a column in the next scene.

---

## s03_weighted_sum — The output is a weighted average of values
`status: approved` · `target: 30s` · `source: §3` · class `S03WeightedSum`

**Objective:** output = Σ wᵢ vᵢ; then connect to the matrix formula.

**Visuals:** weights column (PINK) × values grid (GREEN, 4×2) = contributions grid;
column sums give the output vector. Then the full matrix formula with three boxed parts.

| event | visual | narration note | ~s |
|---|---|---|---|
| `title` | Title "3 · Weighted sum of values" | — | 1.5 |
| `show_tables` | weights column, "×", values grid | "Each token also carries a value: what it contributes." | 2.5 |
| `row_cat` | *cat* row highlighted; contribution row 0.46 × (1, 0) = (0.46, 0.00) | "Scale each value by its weight." | 3 |
| `rows_rest` | remaining contribution rows appear | — | 2.5 |
| `sum_columns` | line under the contributions; output (0.49, 0.07) boxed, labeled "output for *it*" | "Add them up: that is the output for *it*: mostly *cat*." | 3.5 |
| `clear_tables` | tables and caption fade out (the formula takes their place) | — | 1 |
| `general_form` | `Attention(Q,K,V) = softmax(QKᵀ/√d_k) V` is written | "With every query at once, this is the familiar formula." | 3 |
| `map_scores` | box QKᵀ/√d_k → label "scores (1)" | "Scores," | 2 |
| `map_softmax` | box softmax → "weights, row by row (2)" | "softmax, row by row," | 2 |
| `map_values` | box V → "weighted sum of values (3)" | "and a weighted sum of values." | 3 |

**Ending:** hold on the annotated formula.
