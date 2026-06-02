# Portfolio Demo Queries: text-to-sql-ai

Use these 10 natural language questions to test the query generation, validation, and auto-correction capabilities in the web workbench.

---

### 1. Which customers placed the most orders?
- **SQL Equivalent:**
  ```sql
  SELECT c.name, COUNT(o.order_id) AS order_count 
  FROM customers c 
  JOIN orders o ON c.customer_id = o.customer_id 
  GROUP BY c.name 
  ORDER BY order_count DESC;
  ```

### 2. What were the top 5 products by revenue?
- **SQL Equivalent:**
  ```sql
  SELECT p.name, SUM(oi.quantity * oi.price) AS total_revenue 
  FROM products p 
  JOIN order_items oi ON p.product_id = oi.product_id 
  GROUP BY p.name 
  ORDER BY total_revenue DESC 
  LIMIT 5;
  ```

### 3. Which month had the highest total sales?
- **SQL Equivalent:**
  ```sql
  SELECT strftime('%Y-%m', o.order_date) AS month, SUM(o.total_amount) AS total_sales 
  FROM orders o 
  GROUP BY month 
  ORDER BY total_sales DESC 
  LIMIT 1;
  ```

### 4. What is the average order value by customer segment?
- **SQL Equivalent:**
  ```sql
  SELECT c.segment, AVG(o.total_amount) AS average_order_value 
  FROM customers c 
  JOIN orders o ON c.customer_id = o.customer_id 
  GROUP BY c.segment;
  ```

### 5. Which customers have not placed any orders?
- **SQL Equivalent:**
  ```sql
  SELECT c.name 
  FROM customers c 
  LEFT JOIN orders o ON c.customer_id = o.customer_id 
  WHERE o.order_id IS NULL;
  ```

### 6. Which products were ordered more than 10 times?
- **SQL Equivalent:**
  ```sql
  SELECT p.name, SUM(oi.quantity) AS total_quantity 
  FROM products p 
  JOIN order_items oi ON p.product_id = oi.product_id 
  GROUP BY p.name 
  HAVING total_quantity > 10;
  ```

### 7. What is the total revenue by region?
- **SQL Equivalent:**
  ```sql
  SELECT r.name, SUM(o.total_amount) AS total_revenue 
  FROM regions r 
  JOIN customers c ON r.region_id = c.region_id 
  JOIN orders o ON c.customer_id = o.customer_id 
  GROUP BY r.name;
  ```

### 8. Which category had the highest sales last quarter?
- **SQL Equivalent:**
  ```sql
  SELECT p.category, SUM(oi.quantity * oi.price) AS total_sales 
  FROM products p 
  JOIN order_items oi ON p.product_id = oi.product_id 
  JOIN orders o ON oi.order_id = o.order_id 
  WHERE o.order_date >= '2026-01-01' AND o.order_date <= '2026-03-31' 
  GROUP BY p.category 
  ORDER BY total_sales DESC 
  LIMIT 1;
  ```

### 9. Show orders with customer names and total amount.
- **SQL Equivalent:**
  ```sql
  SELECT o.order_id, c.name AS customer_name, o.total_amount 
  FROM orders o 
  JOIN customers c ON o.customer_id = c.customer_id;
  ```

### 10. Which customers bought products from more than 2 categories?
- **SQL Equivalent:**
  ```sql
  SELECT c.name, COUNT(DISTINCT p.category) AS category_count 
  FROM customers c 
  JOIN orders o ON c.customer_id = o.customer_id 
  JOIN order_items oi ON o.order_id = oi.order_id 
  JOIN products p ON oi.product_id = p.product_id 
  GROUP BY c.name 
  HAVING category_count > 2;
  ```
