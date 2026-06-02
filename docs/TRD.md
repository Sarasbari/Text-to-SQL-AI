# Technical Requirements Document: text-to-sql-ai

## 1. System Architecture

```text
React + Vite + Monaco
        |
        | HTTP JSON
        v
FastAPI Backend
        |
        | prompt construction
        v
SQLCoder 7B + LoRA Adapter
        |
        | generated SQL
        v
SQL Safety + DuckDB Validation
        |
        | result / error
        v
Recovery Loop
```

## 2. Main Components

### 2.1 Training Pipeline

Responsible for:

- Loading the Spider benchmark.
- Converting Spider examples into SQLCoder prompt-completion format.
- Fine-tuning `defog/sqlcoder-7b-2` using QLoRA.
- Saving and pushing the LoRA adapter to HuggingFace Hub.

Recommended environment:

- Google Colab A100
- Python 3.10 or 3.11
- CUDA runtime compatible with `bitsandbytes`

Core libraries:

- `transformers`
- `datasets`
- `peft`
- `bitsandbytes`
- `trl`
- `accelerate`
- `huggingface_hub`

### 2.2 Backend

Responsible for:

- API request validation.
- Prompt assembly.
- Model loading.
- SQL generation.
- SQL safety checks.
- DuckDB execution.
- Recovery retries.
- Structured response formatting.

Recommended backend stack:

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic v2
- DuckDB
- Transformers
- PEFT

### 2.3 Frontend

Responsible for:

- Natural language input.
- Schema selection or schema upload.
- SQL display and editing.
- Query execution.
- Results rendering.
- Error and retry visualization.

Recommended frontend stack:

- React 18
- Vite
- TypeScript
- Tailwind CSS
- Monaco Editor
- TanStack Table, optional
- React Query, optional

## 3. Repository Structure

```text
text-to-sql-ai/
  backend/
    app/
      api/
        routes/
          health.py
          generate.py
          execute.py
          schemas.py
      core/
        config.py
        security.py
      db/
        duckdb_client.py
        schema_loader.py
      llm/
        model_loader.py
        prompt_builder.py
        sql_generator.py
        recovery.py
      sql/
        safety.py
        dialect.py
        validator.py
      models/
        requests.py
        responses.py
      main.py
    data/
      demo/
        ecommerce.duckdb
        ecommerce_schema.sql
    tests/
    pyproject.toml
    .env.example

  frontend/
    src/
      api/
      components/
      features/
        query-workbench/
        schema-browser/
        results-table/
      lib/
      App.tsx
      main.tsx
    package.json
    vite.config.ts
    tailwind.config.js

  training/
    notebooks/
      finetune_sqlcoder_spider_qlora.ipynb
    scripts/
      convert_spider_to_sqlcoder.py
      train_qlora.py
      push_adapter.py
    configs/
      qlora_sqlcoder_spider.yaml

  docs/
    PRD.md
    TRD.md
    UI_UX_BRIEF.md
    BACKEND_SCHEMA.md
    IMPLEMENTATION_PLAN.md
```

## 4. Model and Fine-Tuning Requirements

### 4.1 Base Model

Use:

```text
defog/sqlcoder-7b-2
```

### 4.2 Adapter

Use LoRA adapter training with PEFT.

Suggested LoRA config:

```python
r = 16
lora_alpha = 32
lora_dropout = 0.05
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
bias = "none"
task_type = "CAUSAL_LM"
```

### 4.3 Quantization

Use 4-bit QLoRA:

```python
load_in_4bit = True
bnb_4bit_quant_type = "nf4"
bnb_4bit_compute_dtype = "bfloat16"
bnb_4bit_use_double_quant = True
```

### 4.4 Training Arguments

Recommended starting values:

```text
epochs: 2-3
learning_rate: 2e-4
batch_size: 1-2
gradient_accumulation_steps: 8-16
max_seq_length: 2048 or 4096
optimizer: paged_adamw_8bit
warmup_ratio: 0.03
lr_scheduler_type: cosine
```

## 5. Dataset Conversion

Spider examples should be converted into SQLCoder's DDL prompt format.

Each training example should include:

- Database schema as DDL.
- User question.
- Target SQL.

Example format:

```text
### Instructions:
Your task is to convert a question into a SQL query, given a database schema.

### Database Schema:
CREATE TABLE customers (...);
CREATE TABLE orders (...);

### Question:
Which customers placed more than 3 orders?

### SQL:
SELECT ...
```

The exact runtime prompt format must match the training prompt format as closely as possible.

## 6. Backend Technical Requirements

### 6.1 Environment Variables

```text
APP_ENV=development
HF_TOKEN=
HF_ADAPTER_REPO=
BASE_MODEL_ID=defog/sqlcoder-7b-2
DEVICE=cuda
MAX_NEW_TOKENS=512
TEMPERATURE=0.0
TOP_P=0.95
RECOVERY_MAX_RETRIES=2
DEMO_DB_PATH=backend/data/demo/ecommerce.duckdb
```

### 6.2 Model Loading

The backend should load:

1. Base model tokenizer.
2. Base model in 4-bit mode if GPU supports it.
3. Private LoRA adapter from HuggingFace Hub.
4. PEFT merged or attached model for inference.

For local CPU-only development, provide a mock generation mode.

### 6.3 SQL Safety

Block SQL containing:

- `INSERT`
- `UPDATE`
- `DELETE`
- `DROP`
- `ALTER`
- `CREATE`
- `TRUNCATE`
- `MERGE`
- `COPY`
- `ATTACH`
- `DETACH`
- Multiple statements, unless explicitly supported later

Only `SELECT` and read-only `WITH` queries should be allowed in MVP.

### 6.4 DuckDB Validation

Validation steps:

1. Normalize generated SQL.
2. Ensure query is read-only.
3. Execute query against selected DuckDB database.
4. Limit result rows.
5. Return rows, columns, execution time, and errors.

### 6.5 Error Recovery

Recovery input:

- Original question
- Schema DDL
- Failed SQL
- DuckDB error message

Recovery output:

- Corrected SQL candidate
- Retry number
- Validation result

Stop recovery when:

- SQL succeeds
- Retry limit is reached
- Generated SQL does not change
- Safety check fails

## 7. Frontend Technical Requirements

### 7.1 Main Route

```text
/
```

The first screen should show the query workbench.

### 7.2 Key Components

- `QueryInput`
- `SchemaSelector`
- `SchemaBrowser`
- `SqlEditor`
- `ResultTable`
- `ErrorPanel`
- `RecoveryTimeline`
- `QueryHistory`

### 7.3 API Client

Frontend should call:

- `GET /health`
- `GET /schemas`
- `POST /generate`
- `POST /execute`

### 7.4 UI States

Required states:

- Initial
- Generating
- Validating
- Success
- Recovering
- Error
- Empty results

## 8. Testing Requirements

### Backend Tests

- Prompt builder tests.
- SQL safety tests.
- DuckDB execution tests.
- Recovery loop tests with mocked model.
- API contract tests.

### Frontend Tests

- Component rendering tests.
- API client tests.
- Generate flow test.
- Execute edited SQL test.
- Error panel test.

### Manual Demo Tests

Prepare 10 demo questions:

- 7 should succeed.
- 2 should trigger recoverable errors.
- 1 should show a clear failure.

## 9. Deployment Options

### Local Demo

- Backend runs on `localhost:8000`.
- Frontend runs on `localhost:5173`.
- Demo DuckDB file stored locally.

### GPU Server

- Backend deployed on a GPU VM.
- Frontend deployed on Vercel or static hosting.

### Optional HuggingFace Space

- Use Gradio or Docker Space for a simplified public demo.
- Keep private adapter access secure.

## 10. Observability

Log:

- Request ID
- Schema ID
- Prompt token length
- Generation latency
- Validation latency
- Retry count
- Error type

Do not log:

- HuggingFace tokens
- Private credentials
- Large uploaded database content

