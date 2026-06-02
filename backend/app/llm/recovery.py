import logging
from typing import List, Tuple, Any, Literal
from app.core.config import settings
from app.llm.prompt_builder import build_correction_prompt
from app.llm.sql_generator import generate_sql
from app.sql.validator import execute_and_validate_sql
from app.models.responses import RecoveryAttempt, ValidationResult, QueryResult

logger = logging.getLogger("text-to-sql-backend")

def run_recovery_loop(
    question: str,
    schema_ddl: str,
    failed_sql: str,
    initial_error_msg: str,
    max_retries: int | None = None,
    db_path: str | None = None,
    row_limit: int = 100
) -> Tuple[str, Literal["success", "error"], List[RecoveryAttempt], QueryResult | None, int]:
    """
    Executes the self-correction recovery loop.
    Returns (final_sql, status, list_of_attempts, QueryResult or None, total_validation_ms).
    """
    limit = max_retries if max_retries is not None else settings.RECOVERY_MAX_RETRIES
    attempts: List[RecoveryAttempt] = []
    
    current_failed_sql = failed_sql
    current_error_msg = initial_error_msg
    total_val_ms = 0
    
    logger.info(f"Starting SQL recovery loop for question. Max retries: {limit}")
    
    for i in range(1, limit + 1):
        logger.info(f"Recovery attempt {i} of {limit}...")
        
        # 1. Build the correction prompt
        correction_prompt = build_correction_prompt(
            schema_ddl=schema_ddl,
            question=question,
            failed_sql=current_failed_sql,
            error_message=current_error_msg
        )
        
        # 2. Ask model for corrected SQL (is_raw_prompt=True)
        corrected_sql, gen_ms = generate_sql(correction_prompt, is_raw_prompt=True)
        
        # Check if model output hasn't changed (loop prevention)
        if corrected_sql.strip() == current_failed_sql.strip():
            logger.info("Model returned unchanged SQL. Terminating recovery loop.")
            attempts.append(RecoveryAttempt(
                attempt_number=i,
                failed_sql=current_failed_sql,
                error_message=current_error_msg,
                corrected_sql=corrected_sql,
                status="failed"
            ))
            break
            
        # 3. Validate corrected SQL
        val_res, query_res, val_ms = execute_and_validate_sql(
            corrected_sql,
            db_path=db_path,
            row_limit=row_limit
        )
        total_val_ms += val_ms
        
        # Log attempt metadata
        status_outcome = "success" if val_res.is_valid else ("blocked" if not val_res.is_safe else "failed")
        attempts.append(RecoveryAttempt(
            attempt_number=i,
            failed_sql=current_failed_sql,
            error_message=current_error_msg,
            corrected_sql=corrected_sql,
            status=status_outcome
        ))
        
        if val_res.is_valid:
            logger.info(f"Recovery succeeded on attempt {i}!")
            return corrected_sql, "success", attempts, query_res, total_val_ms
            
        if not val_res.is_safe:
            logger.warning(f"Recovery generated unsafe SQL on attempt {i}. Terminating.")
            return corrected_sql, "error", attempts, None, total_val_ms
            
        # Update failed state for next iteration
        current_failed_sql = corrected_sql
        current_error_msg = val_res.error_message or "Unknown execution error"
        
    logger.info("Recovery loop completed without finding a valid query.")
    return current_failed_sql, "error", attempts, None, total_val_ms
