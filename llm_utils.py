"""
LLM utilities: OpenAI API calls and prompt templates
"""
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def call_llm(prompt, model="gpt-4o-mini", temperature=0):
    """
    Call OpenAI API with given prompt
    Args:
        prompt: The prompt string
        model: Model name (default: gpt-4)
        temperature: Creativity level (0 = deterministic)
    Returns:
        LLM response text
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling LLM: {e}"

# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

def prompt_create_table(description):
    """
    Prompt: Convert natural language description to CREATE TABLE statement
    """
    prompt = f"""You are a SQL expert. Convert the following natural language description into a MySQL CREATE TABLE statement.

User description: "{description}"

Requirements:
- Use appropriate data types (INT, VARCHAR, FLOAT, DATE, etc.)
- Include PRIMARY KEY where appropriate
- Use NOT NULL constraints when fields are essential
- Return ONLY the SQL statement, no explanation

Example:
Input: "Create a table called students with id, name, and gpa"
Output: CREATE TABLE students (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) NOT NULL, gpa FLOAT);

Now generate the CREATE TABLE statement:"""
    
    return call_llm(prompt)

def prompt_insert_rows(table_name, rows_description):
    """
    Prompt: Convert natural language row descriptions to INSERT statements
    """
    prompt = f"""You are a SQL expert. Convert the following natural language description into MySQL INSERT statements for the table '{table_name}'.

User description: "{rows_description}"

Requirements:
- Generate INSERT INTO statements
- Infer appropriate values and data types
- Return ONLY the SQL statements, one per line, no explanation
- Use single quotes for strings

Example:
Input for table 'students': "Add Alice with GPA 3.8 and Bob with GPA 3.5"
Output:
INSERT INTO students (name, gpa) VALUES ('Alice', 3.8);
INSERT INTO students (name, gpa) VALUES ('Bob', 3.5);

Now generate the INSERT statements:"""
    
    return call_llm(prompt)

def prompt_text_to_sql(question, schema):
    """
    Prompt: Convert English question to SQL SELECT query
    """
    prompt = f"""You are a SQL expert. Convert the following question into a MySQL SELECT query.

Table Schema:
{schema}

Question: "{question}"

Requirements:
- Write a valid MySQL SELECT query
- Use appropriate WHERE, ORDER BY, GROUP BY, LIMIT clauses as needed
- Return ONLY the SQL query, no explanation

Example:
Schema: Table students (id INT, name VARCHAR, gpa FLOAT)
Question: "Which students have GPA above 3.5?"
Output: SELECT name, gpa FROM students WHERE gpa > 3.5;

Now generate the SQL query:"""
    
    return call_llm(prompt)

def prompt_explain_results(question, sql_query, results):
    """
    Prompt: Explain query results in natural language
    """
    prompt = f"""You are a helpful assistant. Explain the following database query results in simple, natural language.

Question: "{question}"
SQL Query: {sql_query}
Results: {results}

Provide a brief, clear explanation (2-3 sentences maximum) of what the results show.

Example:
Question: "Which students have GPA above 3.5?"
Results: [('Alice', 3.8), ('Bob', 3.9)]
Explanation: "Two students have a GPA above 3.5: Alice with 3.8 and Bob with 3.9."

Now provide your explanation:"""
    
    return call_llm(prompt, temperature=0.3)