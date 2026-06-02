import time
import re
import logging
from typing import Tuple
from app.core.config import settings
from app.llm.model_loader import get_model_and_tokenizer
from app.llm.prompt_builder import build_sqlcoder_prompt

logger = logging.getLogger("text-to-sql-backend")

# Exact mappings for the 10 demo queries to make mock execution seamless and realistic
MOCK_QUERIES = {
    "most orders": (
        "SELECT c.name, COUNT(o.order_id) AS order_count "
        "FROM customers c "
        "JOIN orders o ON c.customer_id = o.customer_id "
        "GROUP BY c.name "
        "ORDER BY order_count DESC;"
    ),
    "top 5 products": (
        "SELECT p.name, SUM(oi.quantity * oi.price) AS total_revenue "
        "FROM products p "
        "JOIN order_items oi ON p.product_id = oi.product_id "
        "GROUP BY p.name "
        "ORDER BY total_revenue DESC "
        "LIMIT 5;"
    ),
    "highest total sales": (
        "SELECT strftime('%Y-%m', o.order_date) AS month, SUM(o.total_amount) AS total_sales "
        "FROM orders o "
        "GROUP BY month "
        "ORDER BY total_sales DESC "
        "LIMIT 1;"
    ),
    "average order value": (
        "SELECT c.segment, AVG(o.total_amount) AS average_order_value "
        "FROM customers c "
        "JOIN orders o ON c.customer_id = o.customer_id "
        "GROUP BY c.segment;"
    ),
    "not placed any orders": (
        "SELECT c.name "
        "FROM customers c "
        "LEFT JOIN orders o ON c.customer_id = o.customer_id "
        "WHERE o.order_id IS NULL;"
    ),
    "more than 10 times": (
        "SELECT p.name, SUM(oi.quantity) AS total_quantity "
        "FROM products p "
        "JOIN order_items oi ON p.product_id = oi.product_id "
        "GROUP BY p.name "
        "HAVING total_quantity > 10;"
    ),
    "revenue by region": (
        "SELECT r.name, SUM(o.total_amount) AS total_revenue "
        "FROM regions r "
        "JOIN customers c ON r.region_id = c.region_id "
        "JOIN orders o ON c.customer_id = o.customer_id "
        "GROUP BY r.name;"
    ),
    "highest sales last quarter": (
        "SELECT p.category, SUM(oi.quantity * oi.price) AS total_sales "
        "FROM products p "
        "JOIN order_items oi ON p.product_id = oi.product_id "
        "JOIN orders o ON oi.order_id = o.order_id "
        "WHERE o.order_date >= '2026-01-01' AND o.order_date <= '2026-03-31' "
        "GROUP BY p.category "
        "ORDER BY total_sales DESC "
        "LIMIT 1;"
    ),
    "customer names and total amount": (
        "SELECT o.order_id, c.name AS customer_name, o.total_amount "
        "FROM orders o "
        "JOIN customers c ON o.customer_id = c.customer_id;"
    ),
    "more than 2 categories": (
        "SELECT c.name, COUNT(DISTINCT p.category) AS category_count "
        "FROM customers c "
        "JOIN orders o ON c.customer_id = o.customer_id "
        "JOIN order_items oi ON o.order_id = oi.order_id "
        "JOIN products p ON oi.product_id = p.product_id "
        "GROUP BY c.name "
        "HAVING category_count > 2;"
    ),
    "highest total order value last month": (
        "SELECT c.name, SUM(o.total_amount) AS total_order_value "
        "FROM customers c "
        "JOIN orders o ON c.customer_id = o.customer_id "
        "WHERE o.order_date >= '2026-05-01' AND o.order_date <= '2026-05-31' "
        "GROUP BY c.name "
        "ORDER BY total_order_value DESC "
        "LIMIT 10;"
    )
}

def clean_extracted_sql(model_output: str) -> str:
    """
    Cleans generated model output to extract only the SQL query, 
    removing markdown formatting and helper text.
    """
    # If the model repeated prompt, split by the marker
    if "### SQL:" in model_output:
        sql = model_output.split("### SQL:")[-1]
    elif "### Corrected SQL:" in model_output:
        sql = model_output.split("### Corrected SQL:")[-1]
    else:
        sql = model_output
        
    # Remove markdown code blocks ```sql ... ```
    sql = re.sub(r"```sql\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)
    
    # Strip whitespace
    sql = sql.strip()
    
    # Ensure it ends with a single semicolon or none
    if not sql.endswith(";"):
        sql += ";"
        
    return sql

def generate_sql(
    prompt_or_question: str, 
    schema_ddl: str | None = None,
    is_raw_prompt: bool = False
) -> Tuple[str, int]:
    """
    Generates SQL given either a prompt or raw question.
    Returns (generated_sql, generation_time_ms).
    """
    start_time = time.perf_counter()
    
    if settings.MOCK_MODEL:
        # Mock mode
        time.sleep(1.0) # Simulate LLM latency
        
        if is_raw_prompt:
            # If it's a correction prompt, extract and fix the failed SQL
            failed_sql_match = re.search(r"### Failed SQL:\s*(.*?)\s*###", prompt_or_question, re.DOTALL | re.IGNORECASE)
            if failed_sql_match:
                failed_sql = failed_sql_match.group(1).strip()
                # Dynamically correct specific mock errors
                corrected = failed_sql
                if "c.id" in failed_sql:
                    corrected = failed_sql.replace("c.id", "c.customer_id")
                elif "GROUP BY" not in failed_sql.upper() and "SUM(" in failed_sql.upper():
                    corrected = failed_sql.replace("LIMIT 5;", "").replace(";", "").strip() + " GROUP BY p.name LIMIT 5;"
                
                generation_ms = int((time.perf_counter() - start_time) * 1000)
                return corrected, generation_ms
            
        question_lower = prompt_or_question.lower()
        
        # If the user intentionally asked to trigger a recovery demo or fail
        if "trigger recovery" in question_lower or "fail" in question_lower:
            # Return an invalid SQL statement that uses 'c.id' instead of 'c.customer_id'
            matched_sql = (
                "SELECT c.name, COUNT(o.order_id) AS order_count "
                "FROM customers c "
                "JOIN orders o ON c.id = o.customer_id "
                "GROUP BY c.name "
                "ORDER BY order_count DESC;"
            )
        else:
            # Match the query based on substring keywords
            matched_sql = "SELECT * FROM customers LIMIT 5;" # fallback
            for key, query in MOCK_QUERIES.items():
                if key in question_lower:
                    matched_sql = query
                    break
                
        generation_ms = int((time.perf_counter() - start_time) * 1000)
        return matched_sql, generation_ms
        
    # Real Model Inference Mode
    try:
        import torch
        model, tokenizer = get_model_and_tokenizer()
        if not model or not tokenizer:
            raise RuntimeError("Model and tokenizer are not loaded.")
            
        # Build prompt if only raw question was supplied
        if is_raw_prompt:
            full_prompt = prompt_or_question
        else:
            if schema_ddl is None:
                raise ValueError("schema_ddl must be provided if is_raw_prompt is False")
            full_prompt = build_sqlcoder_prompt(schema_ddl, prompt_or_question)
            
        inputs = tokenizer(full_prompt, return_tensors="pt")
        inputs = {k: v.to(settings.DEVICE) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=settings.MAX_NEW_TOKENS,
                temperature=settings.TEMPERATURE,
                top_p=settings.TOP_P,
                do_sample=(settings.TEMPERATURE > 0),
                pad_token_id=tokenizer.eos_token_id
            )
            
        # Get generated tokens only (slice off the input tokens)
        input_len = inputs["input_ids"].shape[1]
        generated_tokens = outputs[0][input_len:]
        
        decoded_output = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        sql = clean_extracted_sql(decoded_output)
        
        generation_ms = int((time.perf_counter() - start_time) * 1000)
        return sql, generation_ms
        
    except Exception as e:
        logger.error(f"Error during model generation: {e}")
        generation_ms = int((time.perf_counter() - start_time) * 1000)
        # Fallback to simple select statement so backend doesn't crash
        return "SELECT * FROM customers LIMIT 1;", generation_ms
