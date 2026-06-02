import re
from typing import Tuple

BLOCKED_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", 
    "CREATE", "TRUNCATE", "MERGE", "COPY", "ATTACH", "DETACH"
}

def remove_sql_comments_and_strings(sql: str) -> Tuple[str, list[str]]:
    """
    Strips single line and multiline comments, and extracts string literals 
    to avoid false keyword matching. Returns (cleaned_sql, extracted_strings).
    """
    # Replace multiline comments /* ... */
    sql = re.sub(r'/\*.*?\*/', ' ', sql, flags=re.DOTALL)
    # Replace single line comments -- ...
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    
    # Extract string literals to prevent matching keywords inside strings
    # Match '...' (handling escaped single quotes '') and "..."
    string_pattern = r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\""
    strings = []
    
    def replace_string(match):
        strings.append(match.group(0))
        return f" __STR_LITERAL_{len(strings)-1}__ "
        
    cleaned_sql = re.sub(string_pattern, replace_string, sql)
    return cleaned_sql, strings

def is_safe_sql(sql: str) -> Tuple[bool, str | None]:
    """
    Validates that a SQL query is read-only and safe for execution.
    Returns (is_safe, error_message).
    """
    if not sql or not sql.strip():
        return False, "Query is empty."
        
    cleaned, _ = remove_sql_comments_and_strings(sql)
    
    # Check for multiple statements separated by semicolons
    # Splitting by semicolon, ignoring trailing empty parts
    statements = [s.strip() for s in cleaned.split(";") if s.strip()]
    if len(statements) > 1:
        return False, "Multiple SQL statements are not allowed."
    
    # If no statements found, query might be just comments
    if not statements:
        return False, "Query contains no executable statements."
        
    statement = statements[0]
    
    # Tokenize by splitting on whitespace and special characters
    tokens = re.findall(r'\b\w+\b', statement.upper())
    
    # Check for blocked keywords
    for token in tokens:
        if token in BLOCKED_KEYWORDS:
            return False, f"Blocked keyword detected: {token}"
            
    # Enforce read-only prefix (SELECT or WITH)
    # Skip any leading symbols like parentheses
    first_token_match = re.search(r'\b\w+\b', statement)
    if not first_token_match:
        return False, "Unable to parse SQL statement."
        
    first_token = first_token_match.group(0).upper()
    if first_token not in ("SELECT", "WITH"):
        return False, f"Query must start with SELECT or WITH, found: {first_token}"
        
    return True, None
