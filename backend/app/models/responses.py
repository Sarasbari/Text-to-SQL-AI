from typing import Literal, Any
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    model_loaded: bool
    duckdb_ready: bool
    version: str

class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool = True
    is_primary_key: bool = False
    references: str | None = None

class TableInfo(BaseModel):
    name: str
    columns: list[ColumnInfo]
    row_count: int | None = None

class SchemaInfo(BaseModel):
    schema_id: str
    name: str
    dialect: Literal["duckdb"] = "duckdb"
    ddl: str
    tables: list[TableInfo]

class SchemasResponse(BaseModel):
    schemas: list[SchemaInfo]

class ValidationResult(BaseModel):
    is_valid: bool
    is_safe: bool
    error_type: str | None = None
    error_message: str | None = None

class QueryResult(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    truncated: bool = False

class RecoveryAttempt(BaseModel):
    attempt_number: int
    failed_sql: str
    error_message: str
    corrected_sql: str | None = None
    status: Literal["success", "failed", "blocked"]

class TimingInfo(BaseModel):
    generation_ms: int | None = None
    validation_ms: int | None = None
    execution_ms: int | None = None
    total_ms: int

class GenerateResponse(BaseModel):
    request_id: str
    question: str
    schema_id: str
    generated_sql: str
    final_sql: str
    status: Literal["success", "error"]
    validation: ValidationResult
    recovery: list[RecoveryAttempt] = []
    result: QueryResult | None = None
    timings: TimingInfo

class ExecuteResponse(BaseModel):
    request_id: str
    schema_id: str
    sql: str
    status: Literal["success", "error"]
    validation: ValidationResult
    result: QueryResult | None = None
    timings: TimingInfo

class ApiError(BaseModel):
    request_id: str
    error_code: str
    message: str
    details: dict[str, Any] = {}
