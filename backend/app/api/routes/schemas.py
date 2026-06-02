from fastapi import APIRouter, HTTPException
from app.models.responses import SchemasResponse, SchemaInfo
from app.db.schema_loader import load_schema

router = APIRouter()

@router.get("/schemas", response_model=SchemasResponse)
def list_schemas():
    """
    List all registered relational database schemas.
    """
    try:
        demo_schema = load_schema(schema_id="demo_ecommerce")
        return SchemasResponse(schemas=[demo_schema])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load schemas: {str(e)}")

@router.get("/schemas/{schema_id}", response_model=SchemaInfo)
def get_schema(schema_id: str):
    """
    Retrieve details for a specific schema ID.
    """
    if schema_id != "demo_ecommerce":
        raise HTTPException(status_code=404, detail=f"Schema '{schema_id}' not found.")
    try:
        return load_schema(schema_id=schema_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load schema details: {str(e)}")
