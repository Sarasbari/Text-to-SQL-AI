# Text-to-SQL Backend

This folder contains the FastAPI Python backend for query generation, SQL execution validation, and the error recovery loop.

## Architecture

- `app/api/routes/`: Router endpoints (`/health`, `/schemas`, `/generate`, `/execute`).
- `app/core/`: Application settings and configurations.
- `app/db/`: Client interfaces for DuckDB and schema readers.
- `app/llm/`: Model loader, prompt builder, and execution correction.
- `app/sql/`: SQL safety checker, dialect translator, and query runner.
- `app/models/`: Input/output Pydantic schemas.
