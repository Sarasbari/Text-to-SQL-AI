# Text-to-SQL AI query workbench

This repository contains a full-stack Text-to-SQL system that translates natural language questions into SQL queries, executes and validates them against a DuckDB database, and uses a feedback recovery loop to self-correct SQL generation errors.

## Repository Structure

- `backend/`: FastAPI Python application containing the inference, database client, safety checks, validation, and error recovery logic.
- `frontend/`: React + TypeScript + Tailwind + Monaco Editor query workbench interface.
- `training/`: Conversion and QLoRA fine-tuning scripts/notebooks for `defog/sqlcoder-7b-2`.
- `docs/`: Product, technical, schema, and UI/UX design documents:
  - [Product Requirements Document (PRD)](./docs/PRD.md)
  - [Technical Requirements Document (TRD)](./docs/TRD.md)
  - [App Flow and UI/UX Brief](./docs/UI_UX_BRIEF.md)
  - [Backend Schema Specifications](./docs/BACKEND_SCHEMA.md)
  - [Phase-based Implementation Plan](./docs/IMPLEMENTATION_PLAN.md)

## How to Run

Instructions for setting up and running the backend, frontend, and dataset training will be detailed in later phases.
