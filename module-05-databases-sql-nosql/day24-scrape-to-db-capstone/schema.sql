-- Day 24 - Phase 1 Capstone
-- products table with a unique constraint enabling upserts

DROP TABLE IF EXISTS products;

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,   -- UNIQUE enables ON CONFLICT upserts
    price NUMERIC(10, 2),
    url VARCHAR(500),
    last_scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);