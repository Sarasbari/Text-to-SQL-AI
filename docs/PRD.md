# Product Requirements Document: text-to-sql-ai

## 1. Overview

`text-to-sql-ai` is a fine-tuned Text-to-SQL application that converts natural language questions into SQL queries using a LoRA-adapted `defog/sqlcoder-7b-2` model. The system validates generated SQL against DuckDB, attempts recovery from common generation or execution errors, and provides an interactive frontend where users can inspect, edit, execute, and export SQL results.

This project is designed as a second LLM engineering portfolio project, showing practical experience with fine-tuning, dataset transformation, model serving, backend validation, and full-stack AI product delivery.

## 2. Goals

- Fine-tune a capable open-source Text-to-SQL model using QLoRA on the Spider benchmark.
- Convert Spider examples into SQLCoder's DDL-first prompt format.
- Serve predictions through a clean FastAPI API.
- Validate generated SQL using DuckDB before showing final results.
- Add an error recovery loop that can retry SQL generation using execution errors as feedback.
- Build a professional React UI with Monaco Editor for SQL inspection and editing.
- Produce a portfolio-ready project with clear architecture, reproducible setup, and demo workflows.

## 3. Non-Goals

- Building a production-grade multi-tenant analytics platform.
- Supporting every SQL dialect at launch.
- Training a model from scratch.
- Creating a full database administration tool.
- Guaranteeing perfect SQL generation for arbitrary enterprise schemas.
- Supporting write operations such as `INSERT`, `UPDATE`, `DELETE`, `DROP`, or `ALTER` in the first version.

## 4. Target Users

### Primary User

An analyst, student, developer, or hiring reviewer who wants to ask natural language questions over relational data and see the generated SQL.

### Secondary User

The project creator, who wants to demonstrate applied LLM engineering skills:

- Dataset preparation
- Fine-tuning
- Inference serving
- SQL validation
- Error recovery
- Full-stack AI product implementation

## 5. User Problems

- Writing SQL manually is slow for users who know the business question but not the exact schema.
- LLM-generated SQL can be syntactically invalid or unsafe.
- Text-to-SQL demos often stop at generation and do not validate execution.
- Fine-tuning projects often lack a usable application layer.

## 6. Product Value

`text-to-sql-ai` bridges model training and real product behavior. It does not only generate SQL; it validates the query, retries when errors occur, and gives the user a practical editor-driven workflow.

## 7. Key Features

### 7.1 Natural Language to SQL

Users can enter a question such as:

```text
Which customers had the highest total order value last month?
```

The backend returns:

- Generated SQL
- Execution status
- Validation errors, if any
- Query results, if execution succeeds
- Retry metadata, if recovery was used

### 7.2 Schema-Aware Prompting

The app accepts or loads database schema metadata and converts it into the SQLCoder DDL prompt format.

Expected schema context:

- Tables
- Columns
- Types
- Primary keys
- Foreign keys
- Optional sample rows

### 7.3 SQL Validation

Generated SQL is validated before final display:

- Parse validation
- Read-only operation enforcement
- DuckDB execution check
- Error capture

### 7.4 Error Recovery Loop

If execution fails, the backend sends the original question, schema, failed SQL, and DuckDB error message back into the model with a correction prompt.

Recovery should support a configurable retry count, defaulting to `2`.

### 7.5 Monaco SQL Editor

The frontend shows generated SQL in Monaco Editor, allowing users to:

- Inspect SQL
- Manually edit SQL
- Re-run SQL
- Copy SQL
- Reset to generated SQL

### 7.6 Query Results Table

Successful execution returns a tabular result view with:

- Column names
- Row values
- Empty-state message
- Error-state message
- Optional CSV export

### 7.7 Training Pipeline

The project includes a Colab-ready fine-tuning notebook or scripts for:

- Loading Spider
- Converting examples to SQLCoder format
- Loading `defog/sqlcoder-7b-2`
- Applying QLoRA
- Training with `trl` SFTTrainer
- Saving LoRA adapter
- Pushing private adapter to HuggingFace Hub

## 8. User Stories

- As a user, I want to ask a question in plain English so that I can get SQL without manually writing it.
- As a user, I want to see the generated SQL so that I can trust and edit the output.
- As a user, I want the app to validate SQL before showing final results so that I do not rely on broken output.
- As a user, I want clear error messages so that I understand what failed.
- As a project reviewer, I want to see how the model was fine-tuned so that I can evaluate the engineering depth.
- As a developer, I want documented APIs so that I can extend the system later.

## 9. Functional Requirements

### FR1: Generate SQL

The backend shall expose an endpoint that accepts a user question and schema context, then returns generated SQL.

### FR2: Validate SQL

The backend shall validate generated SQL using DuckDB and return either successful results or a structured error response.

### FR3: Recover from Errors

The backend shall attempt SQL correction when DuckDB execution fails, up to a configured maximum number of retries.

### FR4: Execute Edited SQL

The frontend shall allow the user to edit SQL and send it back to the backend for execution.

### FR5: Manage Demo Schema

The app shall provide at least one built-in demo database so reviewers can test the system without setup friction.

### FR6: Show Query History

The frontend should keep a local query history for the current browser session.

### FR7: Prevent Unsafe SQL

The backend shall block non-read-only SQL commands.

### FR8: Export Results

The frontend should allow users to download query results as CSV.

## 10. Non-Functional Requirements

### Performance

- Simple queries should return within 5-20 seconds depending on model hosting.
- SQL validation with DuckDB should usually complete under 2 seconds for demo-sized datasets.

### Reliability

- API errors should return structured JSON.
- Failed model inference should not crash the backend process.
- DuckDB errors should be captured and surfaced cleanly.

### Security

- HuggingFace tokens must be stored in environment variables.
- Private LoRA adapter access must not be exposed to the frontend.
- Only read-only SQL should be allowed.
- Uploaded database files should be size-limited.

### Usability

- The first screen should be the working app, not a marketing page.
- The app should include a ready-to-use sample schema and question examples.
- Error states should be readable and actionable.

## 11. MVP Scope

The MVP includes:

- Fine-tuning notebook or script
- Spider-to-SQLCoder dataset converter
- FastAPI backend
- Model inference endpoint
- DuckDB validation endpoint
- Error recovery loop
- React frontend
- Monaco SQL editor
- Results table
- Demo database
- Setup documentation

## 12. Success Metrics

- Fine-tuning pipeline completes on Colab A100.
- LoRA adapter is pushed to private HuggingFace Hub repo.
- Backend can load the adapter and generate SQL.
- At least 10 demo questions run successfully end to end.
- Invalid SQL errors trigger recovery attempts.
- Frontend supports generate, edit, execute, and view results.
- GitHub repository clearly communicates architecture and setup.

## 13. Risks

- GPU memory constraints when loading a 7B model.
- SQLCoder prompt format mismatch reducing generation quality.
- Spider schemas may not perfectly match DuckDB syntax.
- Local inference may be slow without GPU.
- Error recovery may loop without meaningful improvement.

## 14. Mitigations

- Use QLoRA with 4-bit quantization.
- Keep training and inference prompt formats identical.
- Add SQL dialect normalization for DuckDB.
- Support remote inference as an optional path.
- Cap retries and expose retry metadata.

