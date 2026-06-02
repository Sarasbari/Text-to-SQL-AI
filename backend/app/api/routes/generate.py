import uuid
import time
import logging
from fastapi import APIRouter, HTTPException
from app.models.requests import GenerateRequest
from app.models.responses import GenerateResponse, ValidationResult, TimingInfo
from app.db.schema_loader import load_schema
from app.llm.sql_generator import generate_sql
from app.sql.validator import execute_and_validate_sql
from app.llm.recovery import run_recovery_loop

router = APIRouter()
logger = logging.getLogger("text-to-sql-backend")

@router.post("/generate", response_model=GenerateResponse)
def generate_query(request: GenerateRequest):
    """
    Generate SQL from a natural language question, validate safety, 
    run it in DuckDB, and execute self-correction if binding errors occur.
    """
    request_id = f"req_{uuid.uuid4().hex[:8]}"
    start_time = time.perf_counter()
    
    # 1. Load Schema
    if request.schema_id != "demo_ecommerce":
        raise HTTPException(
            status_code=404, 
            detail=f"Schema ID '{request.schema_id}' not found."
        )
        
    try:
        schema = load_schema(schema_id=request.schema_id)
    except Exception as e:
        logger.error(f"Error loading schema {request.schema_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to load schema: {str(e)}"
        )

    # 2. Generate initial SQL
    logger.info(f"[{request_id}] Generating SQL for question: {request.question}")
    generated_sql, gen_ms = generate_sql(request.question, schema_ddl=schema.ddl)
    
    final_sql = generated_sql
    status = "success"
    validation = ValidationResult(is_valid=True, is_safe=True)
    recovery_attempts = []
    query_result = None
    
    validation_ms = 0
    execution_ms = 0
    
    # 3. Execute and validate SQL if requested
    if request.execute:
        logger.info(f"[{request_id}] Executing initial generated SQL: {generated_sql}")
        val_res, q_res, val_ex_ms = execute_and_validate_sql(
            generated_sql, 
            row_limit=request.row_limit
        )
        validation_ms += val_ex_ms
        
        # If query is unsafe or valid, we don't recover
        if not val_res.is_safe:
            logger.warning(f"[{request_id}] Generated SQL is flagged as UNSAFE: {generated_sql}")
            final_sql = generated_sql
            status = "error"
            validation = val_res
            query_result = None
        elif val_res.is_valid:
            logger.info(f"[{request_id}] Initial SQL validation and execution succeeded.")
            final_sql = generated_sql
            status = "success"
            validation = val_res
            query_result = q_res
            execution_ms = val_ex_ms
        else:
            # Query is safe but has syntax or binding errors
            logger.warning(f"[{request_id}] Initial SQL execution failed. Error: {val_res.error_message}")
            
            # Start error recovery loop
            if request.max_retries > 0:
                logger.info(f"[{request_id}] Triggering recovery loop with {request.max_retries} retries...")
                rec_sql, rec_status, attempts, rec_q_res, rec_val_ms = run_recovery_loop(
                    question=request.question,
                    schema_ddl=schema.ddl,
                    failed_sql=generated_sql,
                    initial_error_msg=val_res.error_message or "Unknown execution error",
                    max_retries=request.max_retries,
                    row_limit=request.row_limit
                )
                
                final_sql = rec_sql
                status = rec_status
                recovery_attempts = attempts
                query_result = rec_q_res
                validation_ms += rec_val_ms
                
                if rec_status == "success":
                    logger.info(f"[{request_id}] Recovery loop successfully corrected the query!")
                    validation = ValidationResult(is_valid=True, is_safe=True)
                    # Use last attempt validation time as execution duration
                    execution_ms = rec_val_ms
                else:
                    logger.error(f"[{request_id}] Recovery loop failed to find a valid query.")
                    last_err = attempts[-1].error_message if attempts else "Recovery failed"
                    validation = ValidationResult(
                        is_valid=False,
                        is_safe=True,
                        error_type="RECOVERY_FAILED",
                        error_message=last_err
                    )
            else:
                final_sql = generated_sql
                status = "error"
                validation = val_res
                query_result = None
    else:
        # Non-execution query generation
        status = "success"
        validation = ValidationResult(
            is_valid=True,
            is_safe=True,
            error_type=None,
            error_message=None
        )

    # 4. Timings calculation
    total_ms = int((time.perf_counter() - start_time) * 1000)
    
    timings = TimingInfo(
        generation_ms=gen_ms,
        validation_ms=validation_ms,
        execution_ms=execution_ms if request.execute and status == "success" else None,
        total_ms=total_ms
    )

    return GenerateResponse(
        request_id=request_id,
        question=request.question,
        schema_id=request.schema_id,
        generated_sql=generated_sql,
        final_sql=final_sql,
        status=status,
        validation=validation,
        recovery=recovery_attempts,
        result=query_result,
        timings=timings
    )
