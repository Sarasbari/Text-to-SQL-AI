# Text-to-SQL AI query workbench

A portfolio-ready, full-stack Text-to-SQL workbench that converts English queries into SQL, validates them against a DuckDB relational database, and runs an auto-correction feedback loop on execution errors.

---

## 1. System Architecture

```text
       React + Monaco Workbench
                  │
                  ▼ [HTTP POST /generate]
          FastAPI Backend
                  │
                  ▼ [1. Prompt Construction]
          SQLCoder 7B (Model/Mock)
                  │
                  ▼ [2. Initial SQL generated]
          SQL Safety & Dialect Validation
                  │
                  ├── [Success] ──► Returns Data
                  │
                  └── [Failure] ──► Self-Correction Recovery Loop
                                            │
                                            ▼ [3. Reprompts with Error Context]
                                    SQLCoder (Corrected SQL)
                                            │
                                            ▼ [4. Re-validates query]
                                    DuckDB execution succeeds ──► Returns Data
```

---

## 2. Installation & Quickstart

Clone the repository and follow these steps to run the workbench locally in Mock mode (no GPU required).

### Step 2.1: Setup Backend & DuckDB Database
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r pyproject.toml
   # Or install directly:
   pip install fastapi uvicorn pydantic pydantic-settings duckdb pytest httpx
   ```
4. Build and seed the demo DuckDB database:
   ```bash
   python data/demo/create_demo_db.py
   ```
5. Start the FastAPI backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The backend documentation will be live at `http://localhost:8000/docs`.

### Step 2.2: Setup Frontend
1. Navigate to the `frontend/` directory:
   ```bash
   cd ../frontend
   ```
2. Install the node packages:
   ```bash
   npm install
   ```
3. Start the Vite React development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:5173`.

---

## 3. Workbench Operation

- **Natural Language Input:** Type questions in the query box.
- **Interactive Tree Browser:** Explore tables, columns, and foreign keys. Click a table or column name to insert it into your question box.
- **Monaco SQL Editor:** View generated SQL with syntax highlighting. You can modify queries manually and press `Ctrl + Enter` (or click `Run Query`) to execute your adjustments.
- **Results Table:** View rows, column definitions, and timings. Download dataset outputs as CSV.
- **Persistent Query History:** Reload past inputs and outputs from the local storage panel.

### Triggering the Error Recovery Loop (Demo Mode)
If you ask a question containing the word **`fail`** or **`trigger recovery`** (e.g. *"Show most orders (fail)"*), the system will:
1. Intentionally generate a query with a column binding error (`c.id` instead of `c.customer_id`).
2. Execute it in DuckDB and catch the binder exception.
3. Automatically build a correction prompt containing the error message and query.
4. Correct the code to `c.customer_id` and successfully display the outputs.
5. Render the multi-step progress inside the **Auto-Correction Timeline** panel at the bottom.

---

## 4. Fine-Tuning Pipeline (`/training`)

The repository includes scripts to convert dataset schemas and run QLoRA fine-tuning for `defog/sqlcoder-7b-2`.

### Step 4.1: Dataset Preprocessing
Transform the Spider dataset into the SQLCoder instruction DDL structure:
```bash
python training/scripts/convert_spider_to_sqlcoder.py \
    --spider_json /path/to/spider/train.json \
    --tables_json /path/to/spider/tables.json \
    --output_jsonl training/dataset_train_sqlcoder.jsonl
```

### Step 4.2: Fine-Tuning Execution
Run the PEFT/QLoRA trainer using parameters specified in `training/configs/qlora_sqlcoder_spider.yaml`:
```bash
python training/scripts/train_qlora.py \
    --config training/configs/qlora_sqlcoder_spider.yaml \
    --dataset training/dataset_train_sqlcoder.jsonl \
    --output_adapter training/adapter_weights
```

### Step 4.3: Push to Hugging Face
Upload your finished adapter weights to a private repository:
```bash
python training/scripts/push_adapter.py \
    --adapter_dir training/adapter_weights \
    --repo_id your-username/sqlcoder-spider-adapter \
    --token YOUR_HF_WRITE_TOKEN
```

### Google Colab Notebook
A Google Colab template is ready at `training/notebooks/finetune_sqlcoder_spider_qlora.ipynb` to execute the training pipeline on a rented cloud GPU (such as an A100 instance).

---

## 5. Verification & Tests

To run the backend test suite:
```bash
cd backend
.venv\Scripts\python -m pytest -v
```

To verify the frontend compiles for production:
```bash
cd frontend
npm run build
```
