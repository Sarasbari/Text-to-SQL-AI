import os
from contextlib import contextmanager
import duckdb
from app.core.config import settings

@contextmanager
def get_duckdb_conn(db_path: str | None = None, read_only: bool = True):
    """
    Context manager that yields a DuckDB connection.
    Defaults to the seeded ecommerce database path.
    """
    target_path = db_path or settings.DEMO_DB_PATH
    
    # Ensure the parent directory exists
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # Connect to the DuckDB instance
    conn = duckdb.connect(database=target_path, read_only=read_only)
    try:
        yield conn
    finally:
        conn.close()
