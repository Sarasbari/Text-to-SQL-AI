# App Flow and UI/UX Brief: text-to-sql-ai

## 1. Product Feel

The interface should feel like a focused AI workbench for data questions. It should be clean, technical, and confidence-building. The user should immediately understand that this is a real tool, not a landing page.

Design direction:

- Dense but readable.
- Practical over decorative.
- Editor-first.
- Clear model status and validation feedback.
- Professional enough for a portfolio demo.

## 2. First Screen

The first screen should be the actual application:

```text
Top Bar
------------------------------------------------
text-to-sql-ai        Demo Schema: Ecommerce

Main Workbench
------------------------------------------------
Left Panel              Center Panel
Schema Browser          Question Input
Tables                  Generate Button
Columns                 SQL Editor
Relationships           Validation Status

Bottom / Right Panel
------------------------------------------------
Results Table
Error Panel
Recovery Timeline
Query History
```

## 3. Core User Flow

### Flow 1: Generate and Execute SQL

1. User selects a schema.
2. User enters a natural language question.
3. User clicks `Generate`.
4. Frontend sends `POST /generate`.
5. Backend generates SQL.
6. Backend validates SQL in DuckDB.
7. If valid, frontend displays SQL and results.
8. If invalid, backend attempts recovery.
9. Frontend displays final SQL, result, and retry timeline.

### Flow 2: Edit and Re-run SQL

1. User modifies generated SQL in Monaco Editor.
2. User clicks `Run`.
3. Frontend sends `POST /execute`.
4. Backend checks safety and executes SQL.
5. Frontend updates results or displays errors.

### Flow 3: Inspect Schema

1. User opens schema browser.
2. User expands table names.
3. User sees columns, data types, keys, and relationships.
4. User can insert a table or column name into the question or SQL editor.

### Flow 4: Use Query History

1. User opens history panel.
2. User selects a previous question.
3. App restores question, generated SQL, and result summary.

## 4. Main Screens

### 4.1 Query Workbench

Primary screen for the app.

Required sections:

- Schema selector
- Natural language question box
- Generate button
- SQL editor
- Run button
- Copy SQL button
- Result table
- Error panel
- Recovery timeline

### 4.2 Schema Browser

Compact panel listing:

- Table names
- Column names
- Data types
- Primary keys
- Foreign keys

The schema browser should support expand and collapse interactions.

### 4.3 Results View

Results should appear in a table with:

- Sticky column header
- Row count
- Execution time
- CSV export button
- Empty-state message

### 4.4 Error View

Errors should show:

- Error type
- Error message
- Failed SQL, if useful
- Retry count
- Final status

Avoid raw stack traces in the UI.

### 4.5 Recovery Timeline

Show each attempt:

```text
Attempt 1: Generated SQL failed
DuckDB: Binder Error: column not found

Attempt 2: Corrected SQL succeeded
```

This is valuable for demonstrating the system's agent-like behavior.

## 5. UI Components

### Top Bar

Contains:

- App name
- Active schema
- Backend status indicator
- GitHub link, optional

### Question Input

Use a multiline textarea.

Placeholder:

```text
Ask a question about this database...
```

### Action Bar

Buttons:

- Generate
- Run
- Copy
- Reset
- Export CSV

Use icons where available.

### SQL Editor

Use Monaco Editor configured for SQL.

Settings:

- Dark or light theme matching app theme
- Line numbers enabled
- Min height around 280px
- Read/write mode
- Format-on-paste optional

### Result Table

Use a table optimized for scanning.

Display:

- Columns
- Rows
- Row count
- Execution duration

### Status Badges

States:

- Ready
- Generating
- Validating
- Recovering
- Success
- Error

## 6. Layout Guidance

Desktop layout:

```text
-------------------------------------------------
Top Bar
-------------------------------------------------
Schema Browser | Question + SQL Editor
               | Results / Errors / Recovery
-------------------------------------------------
```

Mobile layout:

```text
Top Bar
Question
Schema Accordion
SQL Editor
Actions
Results
Errors
History
```

## 7. Visual Style

Recommended style:

- Neutral background
- High-contrast editor region
- Subtle borders
- Compact controls
- Clear status colors

Suggested color roles:

- Background: near-white or deep neutral
- Primary action: blue or teal
- Success: green
- Warning/recovery: amber
- Error: red
- Editor: high-contrast neutral

Avoid making the whole UI a single purple, beige, or dark-blue theme.

## 8. Empty States

### No Question Yet

```text
Choose a schema and ask a question to generate SQL.
```

### No Results

```text
The query ran successfully and returned no rows.
```

### Backend Offline

```text
Backend is not reachable. Start the FastAPI server and try again.
```

## 9. UX Details That Matter

- Disable `Generate` while generation is running.
- Keep previous SQL visible while a new request is in progress.
- Show retry attempts as they happen if streaming is added later.
- Preserve edited SQL unless the user explicitly resets it.
- Clearly distinguish generated SQL from user-edited SQL.
- Never hide validation errors behind a generic failure message.

## 10. Demo Questions

For an ecommerce demo schema:

- Which customers placed the most orders?
- What were the top 5 products by revenue?
- Which month had the highest total sales?
- What is the average order value by customer segment?
- Which customers have not placed any orders?
- Which products were ordered more than 10 times?
- What is the total revenue by region?
- Which category had the highest sales last quarter?
- Show orders with customer names and total amount.
- Which customers bought products from more than 2 categories?

