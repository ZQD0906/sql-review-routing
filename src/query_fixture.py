"""Execute bundled example queries against the synthetic fixture."""

import duckdb


def run_sql(db_path, sql):
    try:
        with duckdb.connect(db_path, read_only=True, config={"enable_external_access": "false"}) as connection:
            rows = connection.execute(sql).fetchmany(2)
    except duckdb.Error as error:
        return {"ok": False, "rows": None, "error": str(error)}
    return {"ok": True, "rows": rows, "error": None}


def scalar(result):
    rows = result["rows"]
    if not result["ok"] or len(rows) != 1 or len(rows[0]) != 1:
        return None
    try:
        return float(rows[0][0])
    except (TypeError, ValueError):
        return None
