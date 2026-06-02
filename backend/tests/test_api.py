import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["duckdb_ready"] is True
    assert data["version"] == "0.1.0"

def test_get_schemas():
    response = client.get("/schemas")
    assert response.status_code == 200
    data = response.json()
    assert "schemas" in data
    assert len(data["schemas"]) == 1
    assert data["schemas"][0]["schema_id"] == "demo_ecommerce"
    assert "customers" in [t["name"] for t in data["schemas"][0]["tables"]]

def test_get_schema_by_id():
    response = client.get("/schemas/demo_ecommerce")
    assert response.status_code == 200
    data = response.json()
    assert data["schema_id"] == "demo_ecommerce"
    assert len(data["tables"]) > 0

    response = client.get("/schemas/nonexistent")
    assert response.status_code == 404

def test_generate_query_success():
    payload = {
        "question": "Which customers placed the most orders?",
        "schema_id": "demo_ecommerce",
        "execute": True,
        "max_retries": 2
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "SELECT" in data["generated_sql"].upper()
    assert data["validation"]["is_valid"] is True
    assert data["validation"]["is_safe"] is True
    assert data["result"] is not None
    assert len(data["result"]["columns"]) > 0
    assert len(data["result"]["rows"]) > 0
    assert data["timings"]["generation_ms"] > 0
    assert data["timings"]["total_ms"] > 0

def test_generate_query_with_recovery():
    # Adding 'fail' to the question triggers mock recovery
    payload = {
        "question": "Which customer placed the most orders? (fail)",
        "schema_id": "demo_ecommerce",
        "execute": True,
        "max_retries": 2
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Recovery should succeed
    assert data["status"] == "success"
    # First generated was wrong (uses c.id), final should be fixed (uses c.customer_id)
    assert "c.id" in data["generated_sql"]
    assert "c.customer_id" in data["final_sql"]
    
    assert len(data["recovery"]) == 1
    assert data["recovery"][0]["attempt_number"] == 1
    assert data["recovery"][0]["status"] == "success"
    assert "Binder Error" in data["recovery"][0]["error_message"]

def test_execute_query_success():
    payload = {
        "sql": "SELECT name, email FROM customers WHERE segment = 'VIP';",
        "schema_id": "demo_ecommerce"
    }
    response = client.post("/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["validation"]["is_valid"] is True
    assert data["result"]["row_count"] == 2 # Asha Patel & Emma Watson are VIPs
    assert data["result"]["columns"] == ["name", "email"]

def test_execute_query_unsafe():
    payload = {
        "sql": "DELETE FROM customers;",
        "schema_id": "demo_ecommerce"
    }
    response = client.post("/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "error"
    assert data["validation"]["is_safe"] is False
    assert "Blocked keyword" in data["validation"]["error_message"]
    assert data["result"] is None
