import os
import json
import argparse
from typing import Dict, List, Any

def generate_ddl_for_db(db_meta: Dict[str, Any]) -> str:
    """
    Generates standard DDL (CREATE TABLE statements) from Spider database metadata.
    """
    table_names = db_meta["table_names_original"]
    col_names = db_meta["column_names_original"] # [table_idx, col_name_original]
    col_types = db_meta["column_types"]
    primary_keys = db_meta["primary_keys"] # list of column indices
    foreign_keys = db_meta["foreign_keys"] # list of [col_idx, ref_col_idx]
    
    # 1. Group columns by table index
    table_columns: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(len(table_names))}
    for col_idx, (table_idx, name) in enumerate(col_names):
        if table_idx == -1: # Skip system wildcard '*' column
            continue
        table_columns[table_idx].append({
            "index": col_idx,
            "name": name,
            "type": col_types[col_idx].upper()
        })
        
    # 2. Build DDL for each table
    ddl_tables = []
    for table_idx, name in enumerate(table_names):
        cols = table_columns[table_idx]
        col_definitions = []
        pk_cols = []
        fk_definitions = []
        
        # Column defs
        for c in cols:
            c_type = c["type"]
            # Map Spider type names to standard SQL types
            if c_type == "NUMBER":
                c_type = "INTEGER"
            elif c_type == "TIME":
                c_type = "TIMESTAMP"
            col_definitions.append(f"    {c['name']} {c_type}")
            
            if c["index"] in primary_keys:
                pk_cols.append(c["name"])
                
        # Foreign key definitions for this table
        for from_idx, to_idx in foreign_keys:
            from_table_idx, from_name = col_names[from_idx]
            to_table_idx, to_name = col_names[to_idx]
            
            if from_table_idx == table_idx:
                to_table_name = table_names[to_table_idx]
                fk_definitions.append(
                    f"    FOREIGN KEY ({from_name}) REFERENCES {to_table_name}({to_name})"
                )
                
        # Put together table statements
        ddl_body = ",\n".join(col_definitions)
        if pk_cols:
            ddl_body += ",\n" + f"    PRIMARY KEY ({', '.join(pk_cols)})"
        if fk_definitions:
            ddl_body += ",\n" + ",\n".join(fk_definitions)
            
        table_ddl = f"CREATE TABLE {name} (\n{ddl_body}\n);"
        ddl_tables.append(table_ddl)
        
    return "\n\n".join(ddl_tables)

def convert_dataset(
    spider_json_path: str,
    tables_json_path: str,
    output_jsonl_path: str
):
    print(f"Loading tables from {tables_json_path}...")
    with open(tables_json_path, "r", encoding="utf-8") as f:
        tables_data = json.load(f)
        
    db_map = {db["db_id"]: db for db in tables_data}
    
    print(f"Loading queries from {spider_json_path}...")
    with open(spider_json_path, "r", encoding="utf-8") as f:
        spider_data = json.load(f)
        
    print(f"Converting {len(spider_data)} examples...")
    
    # Pre-generate DDL for each database
    ddl_cache = {}
    for db_id, db_meta in db_map.items():
        try:
            ddl_cache[db_id] = generate_ddl_for_db(db_meta)
        except Exception as e:
            print(f"Warning: Failed to generate DDL for db {db_id}: {e}")
            
    # Write output JSONL
    os.makedirs(os.path.dirname(output_jsonl_path), exist_ok=True)
    converted_count = 0
    
    with open(output_jsonl_path, "w", encoding="utf-8") as f:
        for idx, item in enumerate(spider_data):
            db_id = item["db_id"]
            question = item["question"]
            gold_sql = item["query"]
            
            if db_id not in ddl_cache:
                continue
                
            ddl_str = ddl_cache[db_id]
            
            # Format according to the SQLCoder model training prompt structure
            prompt = (
                "### Instructions:\n"
                "Your task is to convert a question into a SQL query, given a database schema.\n\n"
                "### Database Schema:\n"
                f"{ddl_str.strip()}\n\n"
                "### Question:\n"
                f"{question.strip()}\n\n"
                "### SQL:\n"
            )
            
            # Completion
            completion = f"{gold_sql.strip()};"
            
            # Standard formatting expected by Hugging Face training loaders
            record = {
                "prompt": prompt,
                "completion": completion,
                # Combined instruction text for causal language modeling fine-tuning
                "text": f"{prompt}{completion}"
            }
            
            f.write(json.dumps(record) + "\n")
            converted_count += 1
            
    print(f"Completed! Converted {converted_count} lines to {output_jsonl_path}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Spider dataset into SQLCoder training format.")
    parser.add_argument("--spider_json", type=str, required=True, help="Path to Spider train.json or dev.json")
    parser.add_argument("--tables_json", type=str, required=True, help="Path to Spider tables.json")
    parser.add_argument("--output_jsonl", type=str, required=True, help="Output destination path for training JSONL file")
    
    args = parser.parse_args()
    convert_dataset(args.spider_json, args.tables_json, args.output_jsonl)
