import time
from typing import Tuple, Any
from app.db.duckdb_client import get_duckdb_conn
from app.sql.safety import is_safe_sql
from app.models.responses import ValidationResult, QueryResult

def execute_and_validate_sql(
    sql: str, 
    db_path: str | None = None, 
    row_limit: int = 100
) -> Tuple[ValidationResult, QueryResult | None, int]:
    """
    Validates SQL safety and executes it against DuckDB.
    Returns (ValidationResult, QueryResult or None, execution_ms).
    """
    # 1. Safety Check
    start_time = time.perf_counter()
    is_safe, safety_err = is_safe_sql(sql)
    if not is_safe:
        validation_time_ms = int((time.perf_counter() - start_time) * 1000)
        return ValidationResult(
            is_valid=False,
            is_safe=False,
            error_type="UNSAFE_SQL",
            error_message=safety_err
        ), None, validation_time_ms

    # 2. Execution and database validation
    try:
        with get_duckdb_conn(db_path=db_path, read_only=True) as conn:
            exec_start = time.perf_counter()
            # Execute statement
            cursor = conn.execute(sql)
            
            # Retrieve column names
            description = cursor.description
            columns = [desc[0] for desc in description] if description else []
            
            # Fetch limit + 1 rows to determine truncation
            raw_rows = cursor.fetchmany(row_limit + 1)
            exec_end = time.perf_counter()
            
            execution_ms = int((exec_end - exec_start) * 1000)
            
            row_count = len(raw_rows)
            truncated = row_count > row_limit
            
            if truncated:
                raw_rows = raw_rows[:row_limit]
                row_count = row_limit
                
            # Convert row values to list of list of primitives
            # Handling decimal and datetime formats that aren't JSON-serializable
            rows = []
            for row in raw_rows:
                processed_row = []
                for val in row:
                    if hasattr(val, "isoformat"):
                        processed_row.append(val.isoformat())
                    elif type(val).__name__ == "Decimal":
                        processed_row.append(float(val))
                    else:
                        processed_row.append(val)
                rows.append(processed_row)
                
            query_res = QueryResult(
                columns=columns,
                rows=rows,
                row_count=row_count,
                truncated=truncated
            )
            
            validation = ValidationResult(
                is_valid=True,
                is_safe=True,
                error_type=None,
                error_message=None
            )
            
            return validation, query_res, execution_ms
            
    except Exception as e:
        exec_end = time.perf_counter()
        execution_ms = int((exec_end - exec_start) * 1000) if 'exec_start' in locals() else 0
        
        validation = ValidationResult(
            is_valid=False,
            is_safe=True,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        return validation, None, execution_ms
