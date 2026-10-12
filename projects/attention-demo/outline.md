# Content outline — Scaled dot-product attention (one query)

Source: `source/attention-note.md` (stand-in note). Section refs: §1 Scores, §2 Softmax,
§3 Weighted sum, §WE Worked example.

## Audience
Programmers / ML learners who know vectors, dot products and have *heard of* softmax.
They have seen `softmax(QKᵀ/√d_k)V` but cannot say what each piece does.

## Learning objectives
1. A score is a dot product: it measures how aligned a key is with the query. (§1)
2. Softmax turns arbitrary scores into positive weights that sum to 1. (§2)
3. The output is the weight-averaged value vectors. (§3)
4. The matrix formula is the same computation for every query at once. (§3)

## Dependency order
dot product → scores → (scaling) → softmax → weights → weighted sum → matrix form

## Must stay faithful (do not alter)
- s_i = q·k_i / √d_k; w_i = e^{s_i} / Σ_j e^{s_j}; output = Σ_i w_i v_i (§1–§3)
- Softmax is applied row-wise in the matrix form (§3)
- The worked example numbers (§WE); derived values live in `data.py`
- Reason for √d_k: large dot products push softmax towards one-hot / small gradients (§1)

## Free to restructure / design
- Order of presentation inside each step, captions, geometric 2-D picture of the
  dot product, colors, bar charts for the distribution.

## Visual vs. narration
| Idea | Best medium |
|---|---|
| dot product = alignment | **animate** (2-D vectors, projection) |
| √d_k scaling rationale | narration + one caption (a variance argument is too long here) |
| exp then normalize | **animate** (bars morph) |
| weighted sum | **animate** (row-by-row table) |
| matrix form ↔ single query | **animate** (formula parts boxed and labeled) |
| multi-head, masking, learned projections | out of scope; mention in narration if at all |
