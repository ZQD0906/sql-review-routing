"""Illustrative query checks for the six fixed fixture cases."""

import re
from query_fixture import run_sql, scalar

# These tables can contain several rows per order.
ONE_TO_MANY = ["order_items", "order_payments", "order_reviews", "geolocation"]


def c1_structure(sql: str):
    """Flag joins likely to duplicate order-level values before aggregation."""
    s = sql.lower()
    joined = [t for t in ONE_TO_MANY if re.search(r"\bjoin\s+" + t + r"\b", s)]
    has_dedup = bool(re.search(r"\b(distinct|group\s+by)\b", s)) or "with" in s[:6]
    if len(joined) >= 2:
        return ("C1 Join structure", "fail", f"Joined multiple one-to-many tables: {joined}.")
    if len(joined) == 1 and re.search(r"sum\s*\(", s) and not has_dedup:
        return ("C1 Join structure", "fail", f"Direct sum after a join to {joined[0]} without visible grouping.")
    return ("C1 Join structure", "pass", "No matching join pattern flagged.")


def c2_cross(db: str, sql_a: str, sql_b: str, tol: float = 0.005):
    """Compare two paths for the same metric within a relative tolerance."""
    a, b = scalar(run_sql(db, sql_a)), scalar(run_sql(db, sql_b))
    if a is None or b is None:
        return ("C2 Recompute", "na", "A path did not return a scalar.")
    if a == 0 and b == 0:
        return ("C2 Recompute", "pass", "Both paths returned zero.")
    rel = abs(a - b) / max(abs(a), abs(b))
    verdict = "pass" if rel <= tol else "fail"
    return ("C2 Recompute", verdict, f"Path A={a}, path B={b}, relative difference={rel:.3f}.")


def c3_magnitude(value, lo, hi):
    """Flag values outside the case’s illustrative reference range."""
    if value is None:
        return ("C3 Magnitude", "na", "No scalar result.")
    verdict = "pass" if lo <= value <= hi else "fail"
    return ("C3 Magnitude", verdict, f"Value={value}, reference range=[{lo}, {hi}].")


def c4_filter(db: str, sql: str):
    """Check whether removing a simple filter changes the result."""
    if not re.search(r"\bwhere\b", sql, re.I):
        return ("C4 Filter sensitivity", "na", "Query has no WHERE clause.")
    stripped = re.sub(r"\bwhere\b.*?(?=\bgroup\b|\border\b|\blimit\b|$)", " ", sql, flags=re.I | re.S)
    a, b = scalar(run_sql(db, sql)), scalar(run_sql(db, stripped))
    if a is None or b is None:
        return ("C4 Filter sensitivity", "na", "The modified query did not return a scalar.")
    verdict = "fail" if a == b else "pass"
    return ("C4 Filter sensitivity", verdict, f"With the filter={a}, without it={b}.")
