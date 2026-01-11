"""
Database utilities: MySQL connection, query execution, schema retrieval
"""
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def get_mysql_connection():
    """Create and return MySQL connection"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE', 'chatdb')
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_sqlalchemy_engine():
    """Create SQLAlchemy engine for complex operations"""
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD')
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = os.getenv('MYSQL_PORT', 3306)
    database = os.getenv('MYSQL_DATABASE', 'chatdb')
    
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    return create_engine(connection_string)

def run_sql(query, fetch=True):
    """
    Execute SQL query and return results
    Args:
        query: SQL query string
        fetch: If True, fetch and return results (for SELECT)
    Returns:
        For SELECT: List of tuples with results
        For INSERT/CREATE: Success message
    """
    connection = get_mysql_connection()
    if not connection:
        return "Error: Could not connect to database"
    
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        
        if fetch:
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            connection.close()
            return {"columns": columns, "rows": results}
        else:
            connection.commit()
            connection.close()
            return f"Success: Query executed. Rows affected: {cursor.rowcount}"
    
    except Error as e:
        connection.close()
        return f"Error executing query: {e}"

def get_table_schema(table_name):
    """
    Get schema information for a table
    Returns: String describing table structure
    """
    connection = get_mysql_connection()
    if not connection:
        return "Error: Could not connect to database"
    
    try:
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        schema = cursor.fetchall()
        connection.close()
        
        schema_str = f"Table: {table_name}\n"
        schema_str += "Columns:\n"
        for col in schema:
            schema_str += f"  - {col[0]} ({col[1]})\n"
        
        return schema_str
    
    except Error as e:
        connection.close()
        return f"Error fetching schema: {e}"

def list_tables():
    """Get list of all tables in database"""
    connection = get_mysql_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        connection.close()
        return tables
    
    except Error as e:
        connection.close()
        print(f"Error listing tables: {e}")
        return []

def init_database():
    """Initialize database if it doesn't exist"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('MYSQL_DATABASE', 'chatdb')}")
        connection.close()
        return "Database initialized successfully"
    except Error as e:
        return f"Error initializing database: {e}"