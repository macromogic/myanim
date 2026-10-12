# Scaled dot-product attention, for one query

*Stand-in source note written for the MVP demo. Replace with real material for real projects.*

## 1. Scores: how well does each key match the query?

A token that is "looking" for context emits a **query** vector $q \in \mathbb{R}^{d_k}$.
Every token in the sequence offers a **key** vector $k_i \in \mathbb{R}^{d_k}$ and a
**value** vector $v_i$. The relevance of token $i$ to the query is the dot product
$q \cdot k_i$: large when the vectors point the same way, near zero when they are
orthogonal, negative when they point apart.

The scores are divided by $\sqrt{d_k}$. Without this, dot products of random
high-dimensional vectors grow in magnitude with $d_k$ and push the softmax into
regions where it is nearly one-hot and its gradients are tiny.

$$ s_i = \frac{q \cdot k_i}{\sqrt{d_k}} $$

## 2. Softmax turns scores into weights

$$ w_i = \frac{e^{s_i}}{\sum_j e^{s_j}} $$

Exponentiation makes every score positive and exaggerates differences; dividing by
the sum makes the weights add up to 1. The weights are a probability distribution
over the tokens: how much attention the query pays to each.

## 3. The output is a weighted average of values

$$ \text{output} = \sum_i w_i v_i $$

Stacking all queries into a matrix $Q$ (and keys into $K$, values into $V$) gives the
familiar form

$$ \text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right) V $$

where the softmax is applied row by row: each row is exactly the single-query
computation above.

## Worked example

$d_k = 2$. The query comes from the token "it"; the keys come from "cat", "on",
"the", "mat".

| token | key $k_i$ | value $v_i$ |
|---|---|---|
| cat | (1.5, 0.3) | (1.0, 0.0) |
| on | (-0.6, 1.2) | (0.0, 1.0) |
| the | (0.3, -1.1) | (-1.0, 0.5) |
| mat | (1.1, -0.2) | (0.5, -0.5) |

$q = (1.0, 0.6)$.
