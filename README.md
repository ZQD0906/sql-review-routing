# Automated SQL Answering and Review Routing

A Python and DuckDB prototype for deciding which answers to business questions can be released automatically and which should go to an analyst. The runnable demo uses six prewritten question families and a deterministic fixture of 300 synthetic orders.

## Why agreement can fail

A candidate query can return a plausible number while counting at the wrong grain. For a fixture question about buyer payments, the sampler repeatedly chose a query that joins line items and payments through orders before summing. Each payment is then counted once per matching line item.

| Check | Fixture result |
| --- | ---: |
| Most common candidate answer | 254,669.78 |
| Independent reference total | 123,491.09 |
| Candidate agreement | 3 of 5 |
| Join-structure check | Flagged |
| Independent recomputation | Flagged |

The example illustrates why repeated sampling and independent checks carry different information. The demo also covers unique buyers, order status, review counts, and purchase versus delivery dates.

## Routing design

1. Execute five candidates for each question and select the most frequent scalar result. The offline harness draws from fixed candidate queries using a seed.
2. Record candidate agreement, a join-structure flag, and agreement with an independently written reference query. Magnitude and filter sensitivity are additional diagnostics. The bundled checks are heuristics for these examples.
3. With enough labeled questions, fit a logistic ranking model using the three main signals. Choose the score threshold on calibration data, then report observed release coverage, errors among released answers, and a one-sided 95% binomial upper bound on a held-out set. Queue low-score answers for manual review.

The six-case run returned **5 correct majority answers out of 6**. That count checks the offline example. Fitting and evaluating the routing model requires a separate labeled dataset. Keep near-duplicate query templates together when splitting such a dataset and check the binomial independence assumption.

### Why report an upper bound?

For zero errors among $n$ independently evaluated released answers, the one-sided 95% Clopper–Pearson upper bound is

$$
p_{\mathrm{upper}} = 1 - 0.05^{1/n}.
$$

With 15 releases and zero observed errors, the upper bound is **18.10%**. It takes **59** zero-error releases for the bound to fall below 5%. This is a sample-size illustration.

## Run the offline demo

From the repository root, using Python 3.13:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/make_fixture.py
python src/build_db.py
python src/trap_demo.py data/mini.duckdb
python src/pipeline.py
python src/release_bound.py 0 15
python src/release_bound.py 0 59
```

The routing run writes `out/routing_demo.csv` with the chosen SQL, scalar answer, agreement, diagnostics, and fixture correctness label. The scripts run locally after dependencies are installed and use a schema inspired by the [Olist public dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

[Candidate and reference queries](src/questions_demo.py) · [Routing harness](src/pipeline.py) · [Query checks](src/checks.py) · [Release-error bound](src/release_bound.py)
