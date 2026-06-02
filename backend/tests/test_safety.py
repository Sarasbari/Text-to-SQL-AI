import pytest
from app.sql.safety import is_safe_sql, remove_sql_comments_and_strings

def test_remove_comments_and_strings():
    sql = "SELECT * FROM customers; -- this is a comment"
    cleaned, strings = remove_sql_comments_and_strings(sql)
    assert "--" not in cleaned
    assert "comment" not in cleaned
    
    sql_with_strings = "SELECT * FROM customers WHERE segment = 'VIP' AND name = 'DROP TABLE';"
    cleaned, strings = remove_sql_comments_and_strings(sql_with_strings)
    assert "DROP TABLE" not in cleaned
    assert "__STR_LITERAL_0__" in cleaned
    assert "__STR_LITERAL_1__" in cleaned
    assert len(strings) == 2

def test_safe_queries():
    # Simple SELECT
    safe, err = is_safe_sql("SELECT * FROM customers;")
    assert safe
    assert err is None
    
    # CTE
    safe, err = is_safe_sql("WITH sales AS (SELECT * FROM orders) SELECT * FROM sales;")
    assert safe
    assert err is None

    # Parentheses in select
    safe, err = is_safe_sql("(SELECT * FROM customers);")
    assert safe
    assert err is None

def test_unsafe_queries():
    # INSERT
    safe, err = is_safe_sql("INSERT INTO customers VALUES ('CUST_008', 'test');")
    assert not safe
    assert "Blocked keyword detected" in err
    
    # DELETE
    safe, err = is_safe_sql("DELETE FROM customers WHERE customer_id = 'CUST_001';")
    assert not safe
    assert "Blocked keyword detected" in err

    # DROP
    safe, err = is_safe_sql("DROP TABLE customers;")
    assert not safe
    assert "Blocked keyword detected" in err

    # ATTACH
    safe, err = is_safe_sql("ATTACH 'external.db' AS ext;")
    assert not safe
    assert "Blocked keyword detected" in err

def test_blocked_keywords_in_strings():
    # The word 'DELETE' is inside a string literal, so it should be allowed
    safe, err = is_safe_sql("SELECT * FROM customers WHERE segment = 'DELETE';")
    assert safe
    assert err is None

def test_multiple_statements():
    safe, err = is_safe_sql("SELECT * FROM customers; SELECT * FROM orders;")
    assert not safe
    assert "Multiple SQL statements are not allowed" in err
