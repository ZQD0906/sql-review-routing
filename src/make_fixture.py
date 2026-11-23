"""Generate a deterministic, synthetic Olist-shaped fixture."""

import os
import random
import csv
from datetime import datetime, timedelta

random.seed(20260815)
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "mini")
os.makedirs(OUT, exist_ok=True)

N_CUST_UNIQUE = 120
N_ORDERS = 300
STATES = ["SP", "RJ", "MG", "RS", "PR", "BA"]
CATS = ["cama_mesa_banho", "beleza_saude", "esporte_lazer", "moveis_decoracao", "informatica_acessorios"]
STATUS = (["delivered"] * 82 + ["shipped"] * 6 + ["canceled"] * 7 + ["unavailable"] * 3 + ["invoiced"] * 2)

base = datetime(2017, 9, 1)

customers, orders, items, payments, reviews, products, sellers = [], [], [], [], [], [], []

for i in range(40):
    sellers.append({"seller_id": f"s{i:03d}", "seller_zip_code_prefix": 10000 + i,
                    "seller_city": "sao paulo", "seller_state": random.choice(STATES)})
for i in range(60):
    products.append({"product_id": f"p{i:03d}", "product_category_name": random.choice(CATS),
                     "product_weight_g": random.randint(100, 8000)})

uniq = [f"u{i:04d}" for i in range(N_CUST_UNIQUE)]
for o in range(N_ORDERS):
    cid = f"c{o:05d}"                      # Order-specific customer key.
    cuid = random.choice(uniq)             # Stable customer key.
    customers.append({"customer_id": cid, "customer_unique_id": cuid,
                      "customer_zip_code_prefix": 20000 + o % 500,
                      "customer_city": "rio de janeiro", "customer_state": random.choice(STATES)})
    st = random.choice(STATUS)
    ts = base + timedelta(days=random.randint(0, 120), hours=random.randint(0, 23))
    appr = ts + timedelta(hours=random.randint(1, 40))
    deliv = ts + timedelta(days=random.randint(3, 30)) if st == "delivered" else ""
    orders.append({"order_id": f"o{o:05d}", "customer_id": cid, "order_status": st,
                   "order_purchase_timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                   "order_approved_at": appr.strftime("%Y-%m-%d %H:%M:%S"),
                   "order_delivered_customer_date": deliv.strftime("%Y-%m-%d %H:%M:%S") if deliv else "",
                   "order_estimated_delivery_date": (ts + timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S")})

    n_item = random.choices([1, 2, 3, 5], weights=[62, 24, 10, 4])[0]
    for k in range(n_item):
        items.append({"order_id": f"o{o:05d}", "order_item_id": k + 1,
                      "product_id": random.choice(products)["product_id"],
                      "seller_id": random.choice(sellers)["seller_id"],
                      "shipping_limit_date": (ts + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
                      "price": round(random.uniform(15, 480), 2),
                      "freight_value": round(random.uniform(7, 45), 2)})

    n_pay = random.choices([1, 2, 3], weights=[80, 15, 5])[0]
    order_total = sum(it["price"] + it["freight_value"] for it in items if it["order_id"] == f"o{o:05d}")
    shares = [random.random() for _ in range(n_pay)]
    s = sum(shares)
    for k in range(n_pay):
        payments.append({"order_id": f"o{o:05d}", "payment_sequential": k + 1,
                         "payment_type": random.choice(["credit_card", "boleto", "voucher"]),
                         "payment_installments": random.choice([1, 1, 2, 3, 6]),
                         "payment_value": round(order_total * shares[k] / s, 2)})

    n_rev = 1 if random.random() > 0.06 else 2      # Some orders receive two reviews.
    for k in range(n_rev):
        reviews.append({"review_id": f"r{len(reviews):05d}", "order_id": f"o{o:05d}",
                        "review_score": random.choice([1, 2, 3, 4, 5, 5, 5, 4]),
                        "review_creation_date": (ts + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")})


def dump(name, rows):
    path = os.path.join(OUT, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


dump("olist_customers_dataset.csv", customers)
dump("olist_orders_dataset.csv", orders)
dump("olist_order_items_dataset.csv", items)
dump("olist_order_payments_dataset.csv", payments)
dump("olist_order_reviews_dataset.csv", reviews)
dump("olist_products_dataset.csv", products)
dump("olist_sellers_dataset.csv", sellers)
