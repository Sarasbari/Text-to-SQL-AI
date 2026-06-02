def build_sqlcoder_prompt(schema_ddl: str, question: str) -> str:
    """
    Builds a prompt compatible with the defog/sqlcoder-7b-2 format.
    Ensures that training and inference prompt syntax remain aligned.
    """
    prompt = (
        "### Instructions:\n"
        "Your task is to convert a question into a SQL query, given a database schema.\n\n"
        "### Database Schema:\n"
        f"{schema_ddl.strip()}\n\n"
        "### Question:\n"
        f"{question.strip()}\n\n"
        "### SQL:\n"
    )
    return prompt

def build_correction_prompt(schema_ddl: str, question: str, failed_sql: str, error_message: str) -> str:
    """
    Builds a prompt for model self-correction if the generated SQL causes a DuckDB error.
    """
    prompt = (
        "### Instructions:\n"
        "Your previous SQL query generated an error. Correct the SQL query to answer the question, given the database schema and the error message.\n\n"
        "### Database Schema:\n"
        f"{schema_ddl.strip()}\n\n"
        "### Question:\n"
        f"{question.strip()}\n\n"
        "### Failed SQL:\n"
        f"{failed_sql.strip()}\n\n"
        "### Database Error:\n"
        f"{error_message.strip()}\n\n"
        "### Corrected SQL:\n"
    )
    return prompt
