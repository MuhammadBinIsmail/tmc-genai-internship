-- Day 21 - Advanced SQL: Joins, Aggregates, Indexing
-- run against shop_db (built in Day 20)

USE shop_db;

-- Add customers with no orders yet, so JOIN differences are visible
INSERT INTO customers (full_name, email, city) VALUES
    ('Omar Sheikh', 'omar.sheikh@example.com', 'Karachi'),
    ('Nida Farooq', 'nida.farooq@example.com', 'Lahore');


-- 1. INNER JOIN: only customers who have placed at least one order
SELECT c.full_name, o.order_id, o.status
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id;


-- 2. LEFT JOIN: all customers, with NULLs for those who haven't ordered
SELECT c.full_name, o.order_id, o.status
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;


-- 3. RIGHT JOIN: all orders, with NULLs if a customer record were missing
--    (included for completeness; MySQL doesn't support FULL JOIN directly)
SELECT c.full_name, o.order_id, o.status
FROM customers c
RIGHT JOIN orders o ON c.customer_id = o.customer_id;


-- 4. FULL JOIN equivalent in MySQL: LEFT JOIN UNION RIGHT JOIN
SELECT c.full_name, o.order_id, o.status
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
UNION
SELECT c.full_name, o.order_id, o.status
FROM customers c
RIGHT JOIN orders o ON c.customer_id = o.customer_id;


-- 5. GROUP BY + HAVING: customers who have spent more than $50 total
SELECT
    c.full_name,
    SUM(oi.unit_price * oi.quantity) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'completed'
GROUP BY c.full_name
HAVING total_spent > 50
ORDER BY total_spent DESC;


-- 6. Subquery: customers who have placed more orders than the average customer
SELECT full_name, order_count
FROM (
    SELECT c.full_name, COUNT(o.order_id) AS order_count
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.full_name
) AS customer_order_counts
WHERE order_count > (
    SELECT AVG(order_count) FROM (
        SELECT COUNT(order_id) AS order_count
        FROM orders
        GROUP BY customer_id
    ) AS avg_calc
);


-- 7. CTE (Common Table Expression): same "above average" logic, more readable
WITH customer_order_counts AS (
    SELECT c.customer_id, c.full_name, COUNT(o.order_id) AS order_count
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.full_name
),
avg_orders AS (
    SELECT AVG(order_count) AS avg_count FROM customer_order_counts
)
SELECT coc.full_name, coc.order_count
FROM customer_order_counts coc, avg_orders
WHERE coc.order_count > avg_orders.avg_count;


-- 8. Window function: running total of spend per customer, ordered by order date
SELECT
    c.full_name,
    o.order_id,
    o.order_date,
    (oi.unit_price * oi.quantity) AS order_line_total,
    SUM(oi.unit_price * oi.quantity) OVER (
        PARTITION BY c.customer_id ORDER BY o.order_date
    ) AS running_total
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
ORDER BY c.full_name, o.order_date;


-- 9. Window function: rank customers by total spend
SELECT
    full_name,
    total_spent,
    RANK() OVER (ORDER BY total_spent DESC) AS spend_rank
FROM (
    SELECT c.full_name, SUM(oi.unit_price * oi.quantity) AS total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'completed'
    GROUP BY c.full_name
) AS spend_summary;


-- 10. Indexing & EXPLAIN: check query performance before/after an index
EXPLAIN SELECT * FROM orders WHERE customer_id = 1;

CREATE INDEX idx_orders_customer_id ON orders(customer_id);

EXPLAIN SELECT * FROM orders WHERE customer_id = 1;


-- 11. Transaction: demonstrate ACID - move an order from one status to another
--     as a single atomic unit, rolling back if anything fails
START TRANSACTION;

UPDATE orders SET status = 'shipped' WHERE order_id = 3;
INSERT INTO order_items (order_id, product_name, unit_price, quantity)
    VALUES (3, 'Gift Wrap', 3.50, 1);

-- If both succeeded, commit; if either failed, this transaction could be
-- rolled back instead with: ROLLBACK;
COMMIT;

-- Verify the transaction applied
SELECT * FROM orders WHERE order_id = 3;
SELECT * FROM order_items WHERE order_id = 3;