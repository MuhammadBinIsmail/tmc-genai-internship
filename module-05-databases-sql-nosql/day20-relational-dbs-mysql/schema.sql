-- Day 20 - Relational DBs & SQL Fundamentals (MySQL)
-- schema.sql - 3-table normalized schema with sample data

CREATE DATABASE IF NOT EXISTS shop_db;
USE shop_db;

-- Drop in reverse dependency order so foreign keys don't block the drop
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

-- Table 1: customers
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    city VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: orders
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Table 3: order_items
CREATE TABLE order_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- Sample data

INSERT INTO customers (full_name, email, city) VALUES
    ('Ahmed Khan', 'ahmed.khan@example.com', 'Karachi'),
    ('Sara Ali', 'sara.ali@example.com', 'Lahore'),
    ('Bilal Raza', 'bilal.raza@example.com', 'Islamabad'),
    ('Ayesha Malik', 'ayesha.malik@example.com', 'Karachi');

INSERT INTO orders (customer_id, status) VALUES
    (1, 'completed'),
    (1, 'pending'),
    (2, 'completed'),
    (3, 'cancelled'),
    (4, 'completed');

INSERT INTO order_items (order_id, product_name, unit_price, quantity) VALUES
    (1, 'Wireless Mouse', 15.99, 2),
    (1, 'USB-C Cable', 8.50, 3),
    (2, 'Mechanical Keyboard', 65.00, 1),
    (3, 'Laptop Stand', 22.00, 1),
    (3, 'Monitor', 180.00, 1),
    (4, 'Webcam', 45.00, 1),
    (5, 'Desk Lamp', 19.99, 2);