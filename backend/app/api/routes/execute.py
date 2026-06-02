import uuid
import time
import logging
from fastapi import APIRouter, HTTPException
from app.models.requests import ExecuteRequest
from app.models.responses import ExecuteResponse, TimingInfo
from app.sql.validator import execute_and_validate_sql

router = APIRouter()
logger = logging.getLogger("text-to-sql-backend")

@router.post("/execute", response_model=ExecuteResponse)
def execute_query(request: ExecuteRequest):
    """
    Execute user-provided or modified SQL queries against DuckDB after checking safety.
    """
    request_id = f"req_{uuid.uuid4().hex[:8]}"
    start_time = time.perf_counter()
    
    if request.schema_id != "demo_ecommerce":
        raise HTTPException(
            status_code=404, 
            detail=f"Schema ID '{request.schema_id}' not found."
        )
        
    logger.info(f"[{request_id}] Executing manual query request: {request.sql}")
    
    val_res, q_res, val_ex_ms = execute_and_validate_sql(
        request.sql,
        row_limit=request.row_limit
    )
    
    status = "success" if val_res.is_valid else "error"
    total_ms = int((time.perf_counter() - start_time) * 1000)
    
    timings = TimingInfo(
        generation_ms=None,
        validation_ms=val_ex_ms if status == "error" else 0,
        execution_ms=val_ex_ms if status == "success" else None,
        total_ms=total_ms
    )
    
    return ExecuteResponse(
        request_id=request_id,
        schema_id=request.schema_id,
        sql=request.sql,
        status=status,
        validation=val_res,
        result=q_res,
        timings=timings
    )
