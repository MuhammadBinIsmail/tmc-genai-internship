-- Day 20 - sample_queries.sql
-- Demonstrates SELECT, WHERE, ORDER BY, LIMIT, UPDATE, DELETE

-- 1. Basic SELECT with WHERE
SELECT full_name, email FROM customers WHERE city = 'Karachi';

-- 2. ORDER BY and LIMIT: 3 most recent orders
SELECT order_id, customer_id, order_date, status
FROM orders
ORDER BY order_date DESC
LIMIT 3;

-- 3. JOIN across all 3 tables: full order details per customer
SELECT
    c.full_name,
    o.order_id,
    o.status,
    oi.product_name,
    oi.unit_price,
    oi.quantity,
    (oi.unit_price * oi.quantity) AS line_total
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
ORDER BY o.order_id;

-- 4. Aggregate: total spent per customer (completed orders only)
SELECT
    c.full_name,
    SUM(oi.unit_price * oi.quantity) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'completed'
GROUP BY c.full_name
ORDER BY total_spent DESC;

-- 5. UPDATE: mark a pending order as completed
UPDATE orders
SET status = 'completed'
WHERE order_id = 2;

-- 6. DELETE: remove a cancelled order's items, then the order itself
DELETE FROM order_items WHERE order_id = 4;
DELETE FROM orders WHERE order_id = 4;

-- 7. Verify the delete worked
SELECT * FROM orders WHERE order_id = 4;