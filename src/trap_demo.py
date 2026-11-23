"""Compare five fixed SQL pairs on the synthetic fixture."""

import sys
import duckdb

con = duckdb.connect(sys.argv[1], read_only=True)


def q(sql):
    return con.execute(sql).fetchall()[0][0]


print("=" * 68)
print("1. Joining line items and payments duplicates payment rows")
naive = q("""
SELECT round(sum(p.payment_value), 2)
FROM orders o
JOIN order_items i ON i.order_id = o.order_id
JOIN order_payments p ON p.order_id = o.order_id
""")
right = q("SELECT round(sum(payment_value), 2) FROM order_payments")
print(f"  Naive query = {naive}")
print(f"  Reference query = {right}")
print(f"  Inflation ratio = {round(naive / right, 2)}x")

print("=" * 68)
print("2. Order-level customer IDs overcount unique buyers")
naive = q("SELECT count(DISTINCT customer_id) FROM customers")
right = q("SELECT count(DISTINCT customer_unique_id) FROM customers")
print(f"  Naive query = {naive}")
print(f"  Reference query = {right}")
print(f"  Inflation ratio = {round(naive / right, 2)}x")

print("=" * 68)
print("3. Multiple reviews can refer to one order")
naive = q("SELECT count(*) FROM order_reviews")
right = q("SELECT count(DISTINCT order_id) FROM order_reviews")
print(f"  Naive query = {naive}")
print(f"  Reference query = {right}")
print(f"  Difference     = {naive - right}")

print("=" * 68)
print("4. The sales definition excludes canceled and unavailable orders")
naive = q("SELECT round(sum(i.price), 2) FROM orders o JOIN order_items i ON i.order_id = o.order_id")
right = q("""
SELECT round(sum(i.price), 2) FROM orders o JOIN order_items i ON i.order_id = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
""")
print(f"  Naive query = {naive}")
print(f"  Reference query = {right}")
print(f"  Inflation percentage = {round((naive / right - 1) * 100, 1)}%")

print("=" * 68)
print("5. Purchase and delivery timestamps define different cohorts")
naive = q("""
SELECT count(*) FROM orders
WHERE order_purchase_timestamp >= '2017-10-01' AND order_purchase_timestamp < '2017-11-01'
""")
right = q("""
SELECT count(*) FROM orders
WHERE order_delivered_customer_date >= '2017-10-01' AND order_delivered_customer_date < '2017-11-01'
""")
print(f"  By purchase date = {naive}")
print(f"  By delivery date = {right}")
print(f"  Difference       = {abs(naive - right)}")
print("=" * 68)
con.close()
