# Backend Schema: text-to-sql-ai

## 1. API Overview

Base URL:

```text
http://localhost:8000
```

Core endpoints:

- `GET /health`
- `GET /schemas`
- `GET /schemas/{schema_id}`
- `POST /generate`
- `POST /execute`

## 2. Pydantic Models

### 2.1 HealthResponse

```python
class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    model_loaded: bool
    duckdb_ready: bool
    version: str
```

Example:

```json
{
  "status": "ok",
  "model_loaded": true,
  "duckdb_ready": true,
  "version": "0.1.0"
}
```

## 3. Schema Models

### 3.1 ColumnInfo

```python
class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool = True
    is_primary_key: bool = False
    references: str | None = None
```

### 3.2 TableInfo

```python
class TableInfo(BaseModel):
    name: str
    columns: list[ColumnInfo]
    row_count: int | None = None
```

### 3.3 SchemaInfo

```python
class SchemaInfo(BaseModel):
    schema_id: str
    name: str
    dialect: Literal["duckdb"] = "duckdb"
    ddl: str
    tables: list[TableInfo]
```

### 3.4 SchemasResponse

```python
class SchemasResponse(BaseModel):
    schemas: list[SchemaInfo]
```

## 4. Generate SQL

Endpoint:

```text
POST /generate
```

Purpose:

Generate SQL from a natural language question, validate it, and optionally run recovery.

### 4.1 GenerateRequest

```python
class GenerateRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    schema_id: str
    max_retries: int = Field(default=2, ge=0, le=5)
    execute: bool = True
    row_limit: int = Field(default=100, ge=1, le=1000)
```

Example:

```json
{
  "question": "Which customers placed the most orders?",
  "schema_id": "demo_ecommerce",
  "max_retries": 2,
  "execute": true,
  "row_limit": 100
}
```

### 4.2 GenerateResponse

```python
class GenerateResponse(BaseModel):
    request_id: str
    question: str
    schema_id: str
    generated_sql: str
    final_sql: str
    status: Literal["success", "error"]
    validation: "ValidationResult"
    recovery: list["RecoveryAttempt"] = []
    result: "QueryResult | None" = None
    timings: "TimingInfo"
```

Example success:

```json
{
  "request_id": "req_123",
  "question": "Which customers placed the most orders?",
  "schema_id": "demo_ecommerce",
  "generated_sql": "SELECT c.name, COUNT(o.id) AS order_count FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.name ORDER BY order_count DESC LIMIT 10;",
  "final_sql": "SELECT c.name, COUNT(o.id) AS order_count FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.name ORDER BY order_count DESC LIMIT 10;",
  "status": "success",
  "validation": {
    "is_valid": true,
    "is_safe": true,
    "error_type": null,
    "error_message": null
  },
  "recovery": [],
  "result": {
    "columns": ["name", "order_count"],
    "rows": [["Asha Patel", 12], ["Rahul Mehta", 9]],
    "row_count": 2,
    "truncated": false
  },
  "timings": {
    "generation_ms": 7320,
    "validation_ms": 42,
    "total_ms": 7362
  }
}
```

## 5. Execute SQL

Endpoint:

```text
POST /execute
```

Purpose:

Execute user-edited SQL after safety validation.

### 5.1 ExecuteRequest

```python
class ExecuteRequest(BaseModel):
    sql: str = Field(min_length=1, max_length=10000)
    schema_id: str
    row_limit: int = Field(default=100, ge=1, le=1000)
```

Example:

```json
{
  "schema_id": "demo_ecommerce",
  "sql": "SELECT * FROM customers LIMIT 10;",
  "row_limit": 100
}
```

### 5.2 ExecuteResponse

```python
class ExecuteResponse(BaseModel):
    request_id: str
    schema_id: str
    sql: str
    status: Literal["success", "error"]
    validation: "ValidationResult"
    result: "QueryResult | None" = None
    timings: "TimingInfo"
```

## 6. Shared Response Models

### 6.1 ValidationResult

```python
class ValidationResult(BaseModel):
    is_valid: bool
    is_safe: bool
    error_type: str | None = None
    error_message: str | None = None
```

### 6.2 QueryResult

```python
class QueryResult(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    truncated: bool = False
```

### 6.3 RecoveryAttempt

```python
class RecoveryAttempt(BaseModel):
    attempt_number: int
    failed_sql: str
    error_message: str
    corrected_sql: str | None = None
    status: Literal["success", "failed", "blocked"]
```

### 6.4 TimingInfo

```python
class TimingInfo(BaseModel):
    generation_ms: int | None = None
    validation_ms: int | None = None
    execution_ms: int | None = None
    total_ms: int
```

## 7. Error Response Format

Use a consistent API error envelope:

```python
class ApiError(BaseModel):
    request_id: str
    error_code: str
    message: str
    details: dict[str, Any] = {}
```

Example:

```json
{
  "request_id": "req_456",
  "error_code": "UNSAFE_SQL",
  "message": "Only read-only SELECT queries are allowed.",
  "details": {
    "blocked_keyword": "DROP"
  }
}
```

## 8. Database Tables for Optional Persistence

The MVP can run without a persistent application database. If query history persistence is added, use SQLite or DuckDB with the following tables.

### 8.1 query_runs

```sql
CREATE TABLE query_runs (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    schema_id TEXT NOT NULL,
    question TEXT NOT NULL,
    generated_sql TEXT,
    final_sql TEXT,
    status TEXT NOT NULL,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    generation_ms INTEGER,
    validation_ms INTEGER,
    execution_ms INTEGER,
    total_ms INTEGER
);
```

### 8.2 recovery_attempts

```sql
CREATE TABLE recovery_attempts (
    id TEXT PRIMARY KEY,
    query_run_id TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    failed_sql TEXT NOT NULL,
    error_message TEXT NOT NULL,
    corrected_sql TEXT,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

### 8.3 schemas

```sql
CREATE TABLE schemas (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dialect TEXT NOT NULL,
    ddl TEXT NOT NULL,
    db_path TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

## 9. Backend Module Responsibilities

### `prompt_builder.py`

- Builds SQLCoder-style prompts.
- Ensures train and inference formats remain aligned.

### `model_loader.py`

- Loads tokenizer, base model, and LoRA adapter.
- Supports mock mode for CPU-only development.

### `sql_generator.py`

- Runs model inference.
- Extracts SQL from model output.

### `safety.py`

- Blocks unsafe keywords.
- Rejects multiple statements.
- Allows only `SELECT` or read-only `WITH`.

### `validator.py`

- Executes SQL through DuckDB.
- Captures structured error messages.

### `recovery.py`

- Constructs correction prompts.
- Runs bounded retry loop.
- Returns recovery timeline.

