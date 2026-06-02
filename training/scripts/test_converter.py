import os
import json
import tempfile
from convert_spider_to_sqlcoder import generate_ddl_for_db, convert_dataset

def test_ddl_generation():
    # Mock tables.json metadata entry
    mock_db = {
        "db_id": "test_db",
        "table_names_original": ["users", "posts"],
        "column_names_original": [
            [-1, "*"],
            [0, "user_id"],
            [0, "username"],
            [1, "post_id"],
            [1, "user_id"],
            [1, "title"]
        ],
        "column_types": ["text", "number", "text", "number", "number", "text"],
        "primary_keys": [1, 3],
        "foreign_keys": [[4, 1]] # posts.user_id -> users.user_id
    }
    
    ddl = generate_ddl_for_db(mock_db)
    print("Generated DDL:\n", ddl)
    
    # Assertions
    assert "CREATE TABLE users" in ddl
    assert "CREATE TABLE posts" in ddl
    assert "user_id INTEGER" in ddl or "user_id text" in ddl # column index 1 is mapped
    assert "PRIMARY KEY (user_id)" in ddl
    assert "FOREIGN KEY (user_id) REFERENCES users(user_id)" in ddl

def test_full_conversion():
    # Create temporary inputs
    with tempfile.TemporaryDirectory() as tmpdir:
        tables_path = os.path.join(tmpdir, "tables.json")
        train_path = os.path.join(tmpdir, "train.json")
        output_path = os.path.join(tmpdir, "output.jsonl")
        
        mock_tables = [{
            "db_id": "test_db",
            "table_names_original": ["users"],
            "column_names_original": [[-1, "*"], [0, "id"], [0, "name"]],
            "column_types": ["text", "number", "text"],
            "primary_keys": [1],
            "foreign_keys": []
        }]
        
        mock_train = [{
            "db_id": "test_db",
            "question": "Show all user names.",
            "query": "SELECT name FROM users"
        }]
        
        with open(tables_path, "w") as f:
            json.dump(mock_tables, f)
        with open(train_path, "w") as f:
            json.dump(mock_train, f)
            
        # Run conversion
        convert_dataset(train_path, tables_path, output_path)
        
        # Verify output exists and contains prompt
        assert os.path.exists(output_path)
        with open(output_path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1
            record = json.loads(lines[0])
            
            assert "prompt" in record
            assert "completion" in record
            assert "text" in record
            assert "CREATE TABLE users" in record["prompt"]
            assert "Show all user names." in record["prompt"]
            assert "SELECT name FROM users;" in record["completion"]
            
    print("Full conversion test passed!")

if __name__ == "__main__":
    test_ddl_generation()
    test_full_conversion()
    print("All converter tests passed successfully!")
