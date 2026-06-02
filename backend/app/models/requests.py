from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    schema_id: str
    max_retries: int = Field(default=2, ge=0, le=5)
    execute: bool = True
    row_limit: int = Field(default=100, ge=1, le=1000)

class ExecuteRequest(BaseModel):
    sql: str = Field(..., min_length=1, max_length=10000)
    schema_id: str
    row_limit: int = Field(default=100, ge=1, le=1000)
