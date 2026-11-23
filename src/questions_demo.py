"""Six hand-written questions and candidate queries for the fixture."""


QUESTIONS = [
    dict(qid="q01", family="F1 Filtered count",
         ask="How many orders were placed in October?",
         gold="SELECT count(*) FROM orders WHERE order_purchase_timestamp >= '2017-10-01' "
              "AND order_purchase_timestamp < '2017-11-01'",
         alt="SELECT count(DISTINCT order_id) FROM orders WHERE strftime(order_purchase_timestamp, '%Y-%m') = '2017-10'",
         sys_wrong="SELECT count(*) FROM orders WHERE order_delivered_customer_date >= '2017-10-01' "
                   "AND order_delivered_customer_date < '2017-11-01'",
         rand_wrong="SELECT count(*) FROM orders WHERE order_purchase_timestamp >= '2017-10-01' "
                    "AND order_purchase_timestamp <= '2017-11-01'",
         lo=10, hi=300),

    dict(qid="q02", family="F2 Grouped aggregate",
         ask="What was the top seller’s total item revenue?",
         gold="SELECT round(max(s), 2) FROM (SELECT seller_id, sum(price) AS s FROM order_items GROUP BY seller_id)",
         alt="SELECT round(sum(price), 2) FROM order_items WHERE seller_id = "
             "(SELECT seller_id FROM order_items GROUP BY seller_id ORDER BY sum(price) DESC LIMIT 1)",
         sys_wrong="SELECT round(max(s), 2) FROM (SELECT seller_id, sum(price + freight_value) AS s "
                   "FROM order_items GROUP BY seller_id)",
         rand_wrong="SELECT round(max(price), 2) FROM order_items",
         lo=500, hi=50000),

    dict(qid="q03", family="F3 Join within a time window",
         ask="What was the total item value of orders placed in October?",
         gold="SELECT round(sum(i.price), 2) FROM orders o JOIN order_items i ON i.order_id = o.order_id "
              "WHERE o.order_purchase_timestamp >= '2017-10-01' AND o.order_purchase_timestamp < '2017-11-01'",
         alt="SELECT round(sum(price), 2) FROM order_items WHERE order_id IN "
             "(SELECT order_id FROM orders WHERE strftime(order_purchase_timestamp, '%Y-%m') = '2017-10')",
         sys_wrong="SELECT round(sum(i.price), 2) FROM orders o JOIN order_items i ON i.order_id = o.order_id "
                   "WHERE o.order_approved_at >= '2017-10-01' AND o.order_approved_at < '2017-11-01'",
         rand_wrong="SELECT round(sum(i.price + i.freight_value), 2) FROM orders o "
                    "JOIN order_items i ON i.order_id = o.order_id "
                    "WHERE o.order_purchase_timestamp >= '2017-10-01' AND o.order_purchase_timestamp < '2017-11-01'",
         lo=1000, hi=200000),

    dict(qid="q04", family="F4 One-to-many payment total",
         ask="How much did buyers pay across all orders in the fixture?",
         gold="SELECT round(sum(payment_value), 2) FROM order_payments",
         alt="SELECT round(sum(x), 2) FROM (SELECT order_id, sum(payment_value) AS x FROM order_payments GROUP BY order_id)",
         sys_wrong="SELECT round(sum(p.payment_value), 2) FROM orders o "
                   "JOIN order_items i ON i.order_id = o.order_id "
                   "JOIN order_payments p ON p.order_id = o.order_id",
         rand_wrong="SELECT round(sum(p.payment_value), 2) FROM order_payments p "
                    "JOIN order_reviews r ON r.order_id = p.order_id",
         lo=5e4, hi=3e5),

    dict(qid="q05", family="F5 Entity definition",
         ask="How many unique buyers placed orders?",
         gold="SELECT count(DISTINCT customer_unique_id) FROM customers",
         alt="SELECT count(*) FROM (SELECT customer_unique_id FROM customers GROUP BY customer_unique_id)",
         sys_wrong="SELECT count(DISTINCT customer_id) FROM customers",
         rand_wrong="SELECT count(*) FROM orders",
         lo=50, hi=400),

    dict(qid="q06", family="F6 Ranking and ties",
         ask="How many late-delivered line items did the highest-count seller have?",
         gold="SELECT max(c) FROM (SELECT i.seller_id, count(*) AS c FROM order_items i "
              "JOIN orders o ON o.order_id = i.order_id "
              "WHERE o.order_delivered_customer_date > o.order_estimated_delivery_date "
              "GROUP BY i.seller_id)",
         alt="SELECT count(*) FROM order_items i JOIN orders o ON o.order_id = i.order_id "
             "WHERE o.order_delivered_customer_date > o.order_estimated_delivery_date "
             "AND i.seller_id = (SELECT i2.seller_id FROM order_items i2 JOIN orders o2 ON o2.order_id = i2.order_id "
             "WHERE o2.order_delivered_customer_date > o2.order_estimated_delivery_date "
             "GROUP BY i2.seller_id ORDER BY count(*) DESC LIMIT 1)",
         sys_wrong="SELECT max(c) FROM (SELECT i.seller_id, count(*) AS c FROM order_items i "
                   "JOIN orders o ON o.order_id = i.order_id "
                   "WHERE o.order_delivered_customer_date > o.order_estimated_delivery_date "
                   "OR o.order_delivered_customer_date IS NULL GROUP BY i.seller_id)",
         rand_wrong="SELECT count(*) FROM orders WHERE order_delivered_customer_date > order_estimated_delivery_date",
         lo=1, hi=200),
]
