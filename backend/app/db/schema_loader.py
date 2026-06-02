import re
from typing import List, Dict, Any
from app.db.duckdb_client import get_duckdb_conn
from app.models.responses import SchemaInfo, TableInfo, ColumnInfo

def load_schema(db_path: str | None = None, schema_id: str = "demo_ecommerce") -> SchemaInfo:
    """
    Loads database metadata from DuckDB catalog and constructs TableInfo and DDL.
    """
    tables: List[TableInfo] = []
    
    with get_duckdb_conn(db_path=db_path, read_only=True) as conn:
        # Get list of tables in 'main' schema
        res = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main' AND table_type = 'BASE TABLE'"
        ).fetchall()
        table_names = [r[0] for r in res]
        
        # Get foreign key details from duckdb_constraints
        # We query duckdb_constraints() to find relationships
        fk_map: Dict[str, Dict[str, str]] = {} # e.g. { "customers": { "region_id": "regions(region_id)" } }
        
        try:
            constraints = conn.execute(
                "SELECT table_name, constraint_type, expression FROM duckdb_constraints()"
            ).fetchall()
            
            for table_name, const_type, expr in constraints:
                if const_type == "FOREIGN KEY" and expr:
                    # expression typically looks like "FOREIGN KEY(region_id) REFERENCES regions(region_id)"
                    # Let's parse it using regex
                    match = re.search(r"FOREIGN\s+KEY\s*\((.*?)\)\s+REFERENCES\s+(.*?)\((.*?)\)", expr, re.IGNORECASE)
                    if match:
                        fk_col = match.group(1).strip()
                        ref_table = match.group(2).strip()
                        ref_col = match.group(3).strip()
                        if table_name not in fk_map:
                            fk_map[table_name] = {}
                        fk_map[table_name][fk_col] = f"{ref_table}({ref_col})"
        except Exception as e:
            # Fallback if duckdb_constraints() fails
            print(f"Warning: Failed to load constraints: {e}")
            
        # Build TableInfo objects
        for t_name in table_names:
            cols: List[ColumnInfo] = []
            
            # Fetch columns using PRAGMA table_info
            columns_data = conn.execute(f"PRAGMA table_info('{t_name}')").fetchall()
            # cid, name, type, notnull, dflt_value, pk
            
            # Get table row count
            row_count_res = conn.execute(f"SELECT COUNT(*) FROM {t_name}").fetchone()
            row_count = row_count_res[0] if row_count_res else 0
            
            for _, c_name, c_type, notnull, _, pk in columns_data:
                is_pk = pk > 0
                nullable = notnull == 0
                
                # Check for reference
                ref = fk_map.get(t_name, {}).get(c_name)
                
                cols.append(ColumnInfo(
                    name=c_name,
                    type=c_type,
                    nullable=nullable,
                    is_primary_key=is_pk,
                    references=ref
                ))
                
            tables.append(TableInfo(
                name=t_name,
                columns=cols,
                row_count=row_count
            ))

    # Generate schema DDL string for LLM prompting
    ddl_lines = []
    for table in tables:
        ddl_lines.append(f"CREATE TABLE {table.name} (")
        col_lines = []
        pk_cols = []
        fk_lines = []
        
        for col in table.columns:
            nullable_str = " NOT NULL" if not col.nullable else ""
            col_lines.append(f"    {col.name} {col.type}{nullable_str}")
            if col.is_primary_key:
                pk_cols.append(col.name)
            if col.references:
                # Extract reference table and column
                ref_match = re.search(r"(.*?)\((.*?)\)", col.references)
                if ref_match:
                    ref_table, ref_col = ref_match.groups()
                    fk_lines.append(f"    FOREIGN KEY ({col.name}) REFERENCES {ref_table}({ref_col})")
                    
        # Add column definitions
        ddl_body = ",\n".join(col_lines)
        
        # Add primary key constraints
        if pk_cols:
            ddl_body += ",\n" + f"    PRIMARY KEY ({', '.join(pk_cols)})"
            
        # Add foreign key constraints
        if fk_lines:
            ddl_body += ",\n" + ",\n".join(fk_lines)
            
        ddl_lines.append(ddl_body)
        ddl_lines.append(");\n")
        
    generated_ddl = "\n".join(ddl_lines)
    
    return SchemaInfo(
        schema_id=schema_id,
        name="Ecommerce Demo" if schema_id == "demo_ecommerce" else schema_id,
        dialect="duckdb",
        ddl=generated_ddl,
        tables=tables
    )
