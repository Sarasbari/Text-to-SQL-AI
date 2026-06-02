export interface ColumnInfo {
  name: string;
  type: string;
  nullable: boolean;
  is_primary_key: boolean;
  references: string | null;
}

export interface TableInfo {
  name: string;
  columns: ColumnInfo[];
  row_count: number | null;
}

export interface SchemaInfo {
  schema_id: string;
  name: string;
  dialect: 'duckdb';
  ddl: string;
  tables: TableInfo[];
}

export interface SchemasResponse {
  schemas: SchemaInfo[];
}

export interface ValidationResult {
  is_valid: boolean;
  is_safe: boolean;
  error_type: string | null;
  error_message: string | null;
}

export interface QueryResult {
  columns: string[];
  rows: any[][];
  row_count: number;
  truncated: boolean;
}

export interface RecoveryAttempt {
  attempt_number: number;
  failed_sql: string;
  error_message: string;
  corrected_sql: string | null;
  status: 'success' | 'failed' | 'blocked';
}

export interface TimingInfo {
  generation_ms: number | null;
  validation_ms: number | null;
  execution_ms: number | null;
  total_ms: number;
}

export interface GenerateResponse {
  request_id: string;
  question: string;
  schema_id: string;
  generated_sql: string;
  final_sql: string;
  status: 'success' | 'error';
  validation: ValidationResult;
  recovery: RecoveryAttempt[];
  result: QueryResult | null;
  timings: TimingInfo;
}

export interface ExecuteResponse {
  request_id: string;
  schema_id: string;
  sql: string;
  status: 'success' | 'error';
  validation: ValidationResult;
  result: QueryResult | null;
  timings: TimingInfo;
}
