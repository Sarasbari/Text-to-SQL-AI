import os
import pytest
from app.sql.validator import execute_and_validate_sql

# Set demo database path for tests
DEMO_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "demo", "ecommerce.duckdb"
)

def test_successful_query():
    sql = "SELECT customer_id, name, segment FROM customers ORDER BY customer_id LIMIT 3;"
    val_res, query_res, exec_ms = execute_and_validate_sql(sql, db_path=DEMO_DB_PATH)
    
    assert val_res.is_valid
    assert val_res.is_safe
    assert val_res.error_message is None
    
    assert query_res is not None
    assert query_res.columns == ["customer_id", "name", "segment"]
    assert len(query_res.rows) == 3
    assert query_res.row_count == 3
    assert not query_res.truncated
    assert query_res.rows[0] == ["CUST_001", "Asha Patel", "VIP"]

def test_truncated_query():
    sql = "SELECT * FROM customers;"
    # Enforce row limit of 2
    val_res, query_res, exec_ms = execute_and_validate_sql(sql, db_path=DEMO_DB_PATH, row_limit=2)
    
    assert val_res.is_valid
    assert query_res is not None
    assert len(query_res.rows) == 2
    assert query_res.row_count == 2
    assert query_res.truncated

def test_syntax_or_binding_error():
    # column 'nonexistent_col' does not exist
    sql = "SELECT nonexistent_col FROM customers;"
    val_res, query_res, exec_ms = execute_and_validate_sql(sql, db_path=DEMO_DB_PATH)
    
    assert not val_res.is_valid
    assert val_res.is_safe
    assert "Binder Error" in val_res.error_message
    assert query_res is None

def test_unsafe_query_in_validator():
    # Query contains forbidden keyword
    sql = "DROP TABLE regions;"
    val_res, query_res, exec_ms = execute_and_validate_sql(sql, db_path=DEMO_DB_PATH)
    
    assert not val_res.is_valid
    assert not val_res.is_safe
    assert "Blocked keyword" in val_res.error_message
    assert query_res is None
