"""
Data ingestion utilities: CSV upload, table creation, data insertion
"""
import pandas as pd
from db_utils import run_sql, get_table_schema
from llm_utils import call_llm

def infer_sql_type(dtype, sample_values):
    """Infer SQL data type from pandas dtype"""
    if pd.api.types.is_integer_dtype(dtype):
        return "INT"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "DATETIME"
    else:
        # Check string length for VARCHAR
        max_len = max([len(str(v)) for v in sample_values if pd.notna(v)], default=255)
        return f"VARCHAR({min(max_len * 2, 500)})"

def csv_to_sql(file_path, table_name):
    """
    Convert CSV file to CREATE TABLE and INSERT statements, then execute
    Args:
        file_path: Path to CSV file
        table_name: Name for the new table
    Returns:
        Success/error message
    """
    try:
        # Read CSV
        df = pd.read_csv(file_path)
        
        if df.empty:
            return "Error: CSV file is empty"
        
        # Generate CREATE TABLE statement
        columns = []
        for col in df.columns:
            sql_type = infer_sql_type(df[col].dtype, df[col].head())
            clean_col = col.strip().replace(' ', '_').replace('-', '_')
            columns.append(f"{clean_col} {sql_type}")
        
        create_stmt = f"CREATE TABLE {table_name} ({', '.join(columns)});"
        
        # Execute CREATE TABLE
        result = run_sql(create_stmt, fetch=False)
        if "Error" in result:
            return f"Error creating table: {result}"
        
        # Generate and execute INSERT statements
        insert_count = 0
        for _, row in df.iterrows():
            values = []
            for val in row:
                if pd.isna(val):
                    values.append("NULL")
                elif isinstance(val, str):
                    # Escape single quotes
                    escaped = val.replace("'", "''")
                    values.append(f"'{escaped}'")
                else:
                    values.append(str(val))
            
            insert_stmt = f"INSERT INTO {table_name} VALUES ({', '.join(values)});"
            result = run_sql(insert_stmt, fetch=False)
            
            if "Error" not in result:
                insert_count += 1
        
        return f"Success! Created table '{table_name}' and inserted {insert_count} rows."
    
    except Exception as e:
        return f"Error processing CSV: {e}"

def create_table_from_text(description):
    """
    Create table from natural language description using LLM
    """
    from llm_utils import prompt_create_table
    
    # Get CREATE TABLE SQL from LLM
    sql = prompt_create_table(description)
    
    # Clean up response
    sql = sql.strip()
    if sql.startswith("```sql"):
        sql = sql.replace("```sql", "").replace("```", "").strip()
    
    # Execute
    result = run_sql(sql, fetch=False)
    return f"Generated SQL:\n{sql}\n\nResult: {result}"

def insert_rows_from_text(table_name, rows_description):
    """
    Insert rows from natural language description using LLM
    """
    from llm_utils import prompt_insert_rows
    
    # Get INSERT SQL from LLM
    sql = prompt_insert_rows(table_name, rows_description)
    
    # Clean up response
    sql = sql.strip()
    if sql.startswith("```sql"):
        sql = sql.replace("```sql", "").replace("```", "").strip()
    
    # Split multiple INSERT statements
    statements = [s.strip() + ';' for s in sql.split(';') if s.strip()]
    
    results = []
    for stmt in statements:
        result = run_sql(stmt, fetch=False)
        results.append(result)
    
    return f"Generated SQL:\n{sql}\n\nResults:\n" + "\n".join(results)