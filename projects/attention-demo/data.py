"""All numbers shown on screen, computed in one place (source: attention-note.md, Worked example).

Every step uses the *displayed* (rounded) values of the previous step, so a viewer
who checks the arithmetic on screen gets exactly the numbers shown.
Run `uv run python projects/attention-demo/data.py` to print and self-check.
"""

import math

TOKENS = ["cat", "on", "the", "mat"]
QUERY_TOKEN = "it"
D_K = 2
Q = (1.0, 0.6)
KEYS = [(1.5, 0.3), (-0.6, 1.2), (0.3, -1.1), (1.1, -0.2)]
VALUES = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.5), (0.5, -0.5)]

RAW = [round(Q[0] * k[0] + Q[1] * k[1], 2) for k in KEYS]  # q . k_i
SCORES = [round(r / math.sqrt(D_K), 2) for r in RAW]  # / sqrt(d_k)
EXPS = [round(math.exp(s), 2) for s in SCORES]
EXP_SUM = round(sum(EXPS), 2)
WEIGHTS = [round(e / EXP_SUM, 2) for e in EXPS]
CONTRIB = [tuple(round(w * x, 2) for x in v) for w, v in zip(WEIGHTS, VALUES, strict=True)]  # w_i * v_i
OUTPUT = tuple(round(sum(c[d] for c in CONTRIB), 2) for d in range(2))

assert abs(sum(WEIGHTS) - 1.0) < 1e-9, WEIGHTS

if __name__ == "__main__":
    for name in ["RAW", "SCORES", "EXPS", "EXP_SUM", "WEIGHTS", "CONTRIB", "OUTPUT"]:
        print(f"{name:8s} {globals()[name]}")
