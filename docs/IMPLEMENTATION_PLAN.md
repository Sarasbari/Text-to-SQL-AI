# Implementation Plan with Antigravity Prompts: text-to-sql-ai

## 1. Implementation Strategy

Build the project in phases so each layer is testable before the next one depends on it.

Recommended order:

1. Documentation and repo scaffold.
2. Demo database and schema loader.
3. Backend API without real model, using mock SQL generation.
4. DuckDB validation and SQL safety.
5. React workbench UI.
6. Fine-tuning pipeline.
7. Real model loading with LoRA adapter.
8. Error recovery loop.
9. End-to-end demo polish.

## 2. Phase 0: Project Scaffold

### Goals

- Create repository structure.
- Add backend, frontend, training, and docs folders.
- Add root README and environment examples.

### Deliverables

- Root `README.md`
- `.gitignore`
- `backend/`
- `frontend/`
- `training/`
- `docs/`

### Antigravity Prompt

```text
Create the initial repository scaffold for a project named text-to-sql-ai.

Stack:
- Backend: FastAPI, Python 3.11, Pydantic v2, DuckDB
- Frontend: React 18, Vite, TypeScript, Tailwind, Monaco Editor
- Training: QLoRA fine-tuning scripts for defog/sqlcoder-7b-2

Create a clean folder structure with backend, frontend, training, and docs directories.
Add README files where useful.
Do not implement business logic yet.
Keep the structure production-friendly but simple enough for a portfolio MVP.
```

## 3. Phase 1: Demo DuckDB Database

### Goals

- Create a small ecommerce demo database.
- Provide DDL and seed data.
- Ensure demo questions can be answered.

### Deliverables

- `backend/data/demo/ecommerce_schema.sql`
- `backend/data/demo/create_demo_db.py`
- `backend/data/demo/ecommerce.duckdb`

### Antigravity Prompt

```text
Implement a demo ecommerce DuckDB database for text-to-sql-ai.

Create:
- customers table
- products table
- orders table
- order_items table
- regions or categories if helpful

Add realistic seed data with enough variety for aggregate, join, group by, and date questions.
Create a Python script that builds backend/data/demo/ecommerce.duckdb from SQL or Python data.
Also export the schema DDL to backend/data/demo/ecommerce_schema.sql.

Keep data small and deterministic.
```

## 4. Phase 2: Backend API Skeleton

### Goals

- Create FastAPI app.
- Add health, schemas, generate, and execute routes.
- Use mock SQL generation at first.

### Deliverables

- `backend/app/main.py`
- `backend/app/api/routes/*.py`
- `backend/app/models/requests.py`
- `backend/app/models/responses.py`
- `backend/.env.example`

### Antigravity Prompt

```text
Build the FastAPI backend skeleton for text-to-sql-ai.

Implement:
- GET /health
- GET /schemas
- GET /schemas/{schema_id}
- POST /generate
- POST /execute

Use Pydantic v2 request and response models.
For /generate, return a mock SQL query based on the selected demo schema.
Do not load the real LLM yet.

Add clean module boundaries:
- api/routes
- core/config
- db/duckdb_client
- db/schema_loader
- llm/prompt_builder
- llm/sql_generator
- sql/safety
- sql/validator
- models

Include basic tests for health and schemas.
```

## 5. Phase 3: SQL Safety and DuckDB Validation

### Goals

- Enforce read-only SQL.
- Execute safe queries in DuckDB.
- Return structured success and error responses.

### Deliverables

- `backend/app/sql/safety.py`
- `backend/app/sql/validator.py`
- `backend/app/db/duckdb_client.py`
- Backend tests

### Antigravity Prompt

```text
Implement SQL safety and DuckDB validation for the text-to-sql-ai backend.

Requirements:
- Allow SELECT queries.
- Allow read-only WITH queries.
- Block INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, MERGE, COPY, ATTACH, DETACH.
- Reject multiple statements for MVP.
- Execute safe SQL against the selected DuckDB demo database.
- Return columns, rows, row_count, truncated, and timing metadata.
- Capture DuckDB errors into a structured ValidationResult.

Add unit tests for safe SQL, unsafe SQL, multiple statements, successful execution, and execution errors.
```

## 6. Phase 4: Prompt Builder

### Goals

- Build SQLCoder-compatible prompts.
- Keep prompt format reusable for training and inference.

### Deliverables

- `backend/app/llm/prompt_builder.py`
- Prompt builder tests

### Antigravity Prompt

```text
Implement the SQLCoder prompt builder for text-to-sql-ai.

The prompt must include:
- Instruction text
- Database schema DDL
- Natural language question
- SQL answer marker

Design it so the same format can be used by training conversion scripts and runtime inference.
Add tests that verify the prompt includes the DDL, question, and final SQL marker.
```

## 7. Phase 5: Frontend Workbench

### Goals

- Build the main React UI.
- Connect to mock backend.
- Support generate, edit, run, and results display.

### Deliverables

- `frontend/src/App.tsx`
- `frontend/src/features/query-workbench/*`
- `frontend/src/components/*`
- API client

### Antigravity Prompt

```text
Build the React frontend for text-to-sql-ai.

Stack:
- React 18
- Vite
- TypeScript
- Tailwind CSS
- Monaco Editor

Create the app as a working query workbench, not a landing page.

Required UI:
- Top bar with app name and backend status
- Schema selector
- Schema browser with expandable tables and columns
- Natural language question input
- Generate button
- Monaco SQL editor
- Run, Copy, Reset, and Export CSV actions
- Results table
- Error panel
- Recovery timeline placeholder
- Query history for current browser session

Connect to the FastAPI endpoints:
- GET /health
- GET /schemas
- POST /generate
- POST /execute

Make the interface responsive and practical for repeated use.
```

## 8. Phase 6: Spider to SQLCoder Dataset Conversion

### Goals

- Convert Spider dataset into SQLCoder training format.
- Preserve schema DDL and target SQL.

### Deliverables

- `training/scripts/convert_spider_to_sqlcoder.py`
- `training/configs/dataset_config.yaml`
- Sample converted JSONL

### Antigravity Prompt

```text
Implement a Spider-to-SQLCoder dataset conversion script.

Input:
- Spider train/dev JSON files
- Spider database schema metadata

Output:
- JSONL file where each row contains a SQLCoder-style prompt and completion

Each example must include:
- Database DDL
- Natural language question
- Gold SQL answer

Add CLI arguments for input paths and output path.
Add a small test or sample fixture to verify one converted example.
The prompt format should match backend/app/llm/prompt_builder.py.
```

## 9. Phase 7: QLoRA Fine-Tuning

### Goals

- Fine-tune `defog/sqlcoder-7b-2` using QLoRA.
- Save adapter.
- Push adapter to private HuggingFace Hub repo.

### Deliverables

- `training/notebooks/finetune_sqlcoder_spider_qlora.ipynb`
- `training/scripts/train_qlora.py`
- `training/scripts/push_adapter.py`
- `training/configs/qlora_sqlcoder_spider.yaml`

### Antigravity Prompt

```text
Create the QLoRA fine-tuning pipeline for defog/sqlcoder-7b-2 on the converted Spider SQLCoder-format dataset.

Use:
- transformers
- datasets
- peft
- bitsandbytes
- trl SFTTrainer
- accelerate
- huggingface_hub

Target environment:
- Google Colab A100

Implement:
- Config-driven training script
- 4-bit NF4 quantization
- LoRA config for attention and MLP projection modules
- SFTTrainer setup
- Checkpoint saving
- Adapter saving
- Optional push to private HuggingFace Hub repo

Include clear Colab instructions and environment setup cells or script comments.
```

## 10. Phase 8: Real Model Inference

### Goals

- Replace mock generator with SQLCoder + LoRA adapter.
- Keep mock mode available for development.

### Deliverables

- `backend/app/llm/model_loader.py`
- `backend/app/llm/sql_generator.py`
- Updated `/generate`

### Antigravity Prompt

```text
Implement real model inference for the text-to-sql-ai backend.

Requirements:
- Load defog/sqlcoder-7b-2 tokenizer and model.
- Load private LoRA adapter from HuggingFace Hub using HF_TOKEN.
- Support 4-bit loading when CUDA is available.
- Provide a MOCK_MODEL=true mode for local CPU development.
- Generate SQL from the SQLCoder prompt builder.
- Extract only the SQL from model output.
- Add timing metadata.
- Handle model loading and inference errors cleanly.

Do not expose HuggingFace credentials to the frontend.
```

## 11. Phase 9: Error Recovery Loop

### Goals

- Retry failed SQL with correction prompts.
- Surface retry timeline to frontend.

### Deliverables

- `backend/app/llm/recovery.py`
- Updated generate route
- Recovery UI wired to response

### Antigravity Prompt

```text
Implement the SQL error recovery loop for text-to-sql-ai.

When generated SQL fails DuckDB validation:
- Build a correction prompt using the original question, schema DDL, failed SQL, and DuckDB error message.
- Ask the model for corrected SQL.
- Re-run SQL safety and DuckDB validation.
- Repeat up to max_retries.
- Stop if SQL succeeds, SQL is unsafe, retry limit is reached, or the corrected SQL is unchanged.

Return a recovery timeline with each attempt:
- attempt_number
- failed_sql
- error_message
- corrected_sql
- status

Update the frontend to display the recovery timeline.
```

## 12. Phase 10: End-to-End Demo Polish

### Goals

- Make the project demo-ready.
- Add setup docs.
- Add demo script.
- Verify frontend and backend together.

### Deliverables

- Root README
- Demo GIF or screenshots, optional
- `docs/demo_questions.md`
- Passing tests

### Antigravity Prompt

```text
Polish text-to-sql-ai into a portfolio-ready demo.

Tasks:
- Write a strong root README with architecture, setup, training, and demo instructions.
- Add a list of 10 demo questions.
- Ensure backend tests pass.
- Ensure frontend build passes.
- Verify the app works with the demo DuckDB database.
- Add clear notes for mock model mode vs real LoRA adapter mode.
- Include troubleshooting for HuggingFace token, CUDA, bitsandbytes, and DuckDB errors.

Keep the documentation concise but complete enough for a recruiter or engineer to run the project.
```

## 13. Recommended Development Milestones

### Milestone 1: Local Backend Works

Definition of done:

- `GET /health` returns ok.
- `GET /schemas` returns demo schema.
- `POST /execute` runs a hand-written SQL query.
- Unsafe SQL is blocked.

### Milestone 2: UI Works with Mock Generation

Definition of done:

- User can ask a question.
- Mock SQL appears in Monaco.
- User can run SQL.
- Results appear in table.

### Milestone 3: Training Pipeline Runs

Definition of done:

- Spider conversion works.
- QLoRA training starts successfully on Colab A100.
- Adapter is saved.
- Adapter can be pushed to HuggingFace Hub.

### Milestone 4: Real Inference Works

Definition of done:

- Backend loads base model and adapter.
- `/generate` returns model-generated SQL.
- SQL is validated in DuckDB.

### Milestone 5: Recovery Works

Definition of done:

- Backend retries failed SQL.
- Frontend displays recovery attempts.
- Demo includes at least one visible recovery case.

## 14. Practical Build Notes

- Keep mock mode from day one. It makes frontend and backend development possible without GPU.
- Use one built-in demo database before adding uploads.
- Make prompt format a shared contract between training and inference.
- Add safety checks before execution, even for local demos.
- Treat DuckDB errors as model feedback, not only as user-facing failures.
- Keep the project readable. A hiring reviewer should understand the architecture in 5 minutes.

