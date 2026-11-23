"""Run the seeded candidate sampler and emit the six-case routing table."""

import sys
import os
import csv
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from query_fixture import run_sql, scalar
from checks import c1_structure, c2_cross, c3_magnitude, c4_filter
from questions_demo import QUESTIONS

DB = "data/mini.duckdb"
K = 5
RNG = np.random.default_rng(7)

# Per-family probabilities for drawing the reference or systematic-error query.
FAMILY_P = {
    "F1 Filtered count": (0.92, 0.03), "F2 Grouped aggregate": (0.85, 0.05),
    "F3 Join within a time window": (0.70, 0.15), "F4 One-to-many payment total": (0.30, 0.60),
    "F5 Entity definition": (0.38, 0.50), "F6 Ranking and ties": (0.55, 0.25),
}


def answer_once(q):
    """Draw a prewritten SQL candidate using the case’s simulation weights."""
    p_c, p_s = FAMILY_P[q["family"]]
    u = RNG.random()
    return q["gold"] if u < p_c else (q["sys_wrong"] if u < p_c + p_s else q["rand_wrong"])


def answer_k_times(q, k=K):
    out = []
    for _ in range(k):
        sql = answer_once(q)
        out.append((sql, scalar(run_sql(DB, sql))))
    return out


def majority(pairs):
    vals = [round(v, 2) if v is not None else None for _, v in pairs]
    cnt = Counter(vals)
    top_val, top_n = cnt.most_common(1)[0]
    sql = next(s for s, v in pairs if (round(v, 2) if v is not None else None) == top_val)
    return top_val, top_n / len(pairs), sql


rows = []
for q in QUESTIONS:
    pairs = answer_k_times(q)
    val, cons, sql = majority(pairs)
    c1 = c1_structure(sql)
    c2 = c2_cross(DB, sql, q["alt"])
    c3 = c3_magnitude(val, q["lo"], q["hi"])
    c4 = c4_filter(DB, sql)
    gold = scalar(run_sql(DB, q["gold"]))
    correct = int(val is not None and gold is not None and abs(val - gold) <= 1e-6 * max(1.0, abs(gold)))
    rows.append(dict(qid=q["qid"], family=q["family"], ask=q["ask"], answer=val, consistency=cons,
                     C1=int(c1[1] == "pass"), C2=int(c2[1] == "pass"), C3=int(c3[1] == "pass"),
                     C4=int(c4[1] == "pass"), correct=correct, sql=" ".join(sql.split())))

os.makedirs("out", exist_ok=True)
with open("out/routing_demo.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"Correct majority answers: {sum(r['correct'] for r in rows)}/{len(rows)}")
print("Wrote out/routing_demo.csv")
