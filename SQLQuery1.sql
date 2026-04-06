CREATE DATABASE DataJam;
GO

USE DataJam;
GO

CREATE TABLE countries(
    country_code INT PRIMARY KEY,
    name VARCHAR(255),
    population INT
);

CREATE TABLE users(
    user_id INT PRIMARY KEY,
    email VARCHAR(255),
    created_at DATETIME2,
    country_code INT,
    FOREIGN KEY (country_code) REFERENCES countries(country_code)
);

CREATE TABLE categories(
    category_id INT PRIMARY KEY,
    slug VARCHAR(255),
    name VARCHAR(255)
);

CREATE TABLE shipping_regions(
    shipping_regions_id INT PRIMARY KEY,
    region VARCHAR(255),
    shipping_zone VARCHAR(255),
    estimated_days INT,
    country_code INT,
    FOREIGN KEY (country_code) REFERENCES countries(country_code)
);

CREATE TABLE orders(
    order_id INT PRIMARY KEY,
    created_at DATETIME2,
    total_amount DECIMAL(10,2),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE products(
    product_id INT PRIMARY KEY,
    name VARCHAR(255),
    price DECIMAL(10,2),
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE product_details(
    product_details_id INT PRIMARY KEY,
    product_id INT,
    stock INT,
    rating INT,
    weight INT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE order_items(
    order_items_id INT PRIMARY KEY,
    quantity INT,
    unit_price DECIMAL(10,2),
    order_id INT,
    product_id INT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);