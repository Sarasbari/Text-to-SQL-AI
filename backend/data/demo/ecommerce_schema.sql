-- Ecommerce Demo Database Schema for text-to-sql-ai

CREATE TABLE regions (
    region_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    sales_manager VARCHAR
);

CREATE TABLE customers (
    customer_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    segment VARCHAR NOT NULL, -- e.g., 'Retail', 'Corporate', 'VIP'
    region_id VARCHAR REFERENCES regions(region_id),
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE products (
    product_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    price DOUBLE NOT NULL,
    stock INTEGER NOT NULL
);

CREATE TABLE orders (
    order_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR REFERENCES customers(customer_id),
    order_date TIMESTAMP NOT NULL,
    total_amount DOUBLE NOT NULL,
    status VARCHAR NOT NULL -- e.g., 'Completed', 'Processing', 'Cancelled'
);

CREATE TABLE order_items (
    item_id VARCHAR PRIMARY KEY,
    order_id VARCHAR REFERENCES orders(order_id),
    product_id VARCHAR REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    price DOUBLE NOT NULL
);
