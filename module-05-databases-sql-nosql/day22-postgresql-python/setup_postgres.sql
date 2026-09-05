-- Day 22 - PostgreSQL & Python Integration
-- schema with JSONB and array types

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    city VARCHAR(50),
    tags TEXT[],              -- Postgres array type: e.g. {'vip','wholesale'}
    metadata JSONB,           -- Postgres JSONB type: flexible semi-structured data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_total DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO customers (full_name, email, city, tags, metadata) VALUES
    ('Ahmed Khan', 'ahmed.khan@example.com', 'Karachi',
     ARRAY['vip', 'repeat_customer'],
     '{"preferred_payment": "card", "newsletter": true}'),
    ('Sara Ali', 'sara.ali@example.com', 'Lahore',
     ARRAY['wholesale'],
     '{"preferred_payment": "bank_transfer", "newsletter": false}'),
    ('Bilal Raza', 'bilal.raza@example.com', 'Islamabad',
     ARRAY[]::TEXT[],
     '{"preferred_payment": "cash", "newsletter": true}');

INSERT INTO orders (customer_id, order_total, status) VALUES
    (1, 57.48, 'completed'),
    (1, 65.00, 'pending'),
    (2, 202.00, 'completed'),
    (3, 45.00, 'cancelled');