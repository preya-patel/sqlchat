"""
Main Gradio Application - Chat-Driven SQL Database Interface
"""
import gradio as gr
from db_utils import init_database, list_tables, get_table_schema, run_sql
from llm_utils import prompt_text_to_sql, prompt_explain_results
from ingest_utils import csv_to_sql, create_table_from_text, insert_rows_from_text
import os

# Initialize database on startup
init_database()

# =============================================================================
# TAB 1: Upload CSV
# =============================================================================

def upload_csv_handler(file, table_name):
    """Handle CSV file upload"""
    if file is None:
        return "Please upload a CSV file"
    if not table_name:
        return "Please provide a table name"
    
    result = csv_to_sql(file.name, table_name)
    return result

# =============================================================================
# TAB 2: Create Table from Chat
# =============================================================================

def create_table_handler(description):
    """Create table from natural language"""
    if not description:
        return "Please provide a table description"
    
    result = create_table_from_text(description)
    return result

# =============================================================================
# TAB 3: Insert Rows from Chat
# =============================================================================

def insert_rows_handler(table_name, rows_description):
    """Insert rows from natural language"""
    if not table_name or not rows_description:
        return "Please provide both table name and row description"
    
    result = insert_rows_from_text(table_name, rows_description)
    return result

# =============================================================================
# TAB 4: Query with Natural Language
# =============================================================================

def query_handler(question, table_name):
    """Handle natural language question"""
    if not question or not table_name:
        return "Please provide both a question and select a table", "", ""
    
    # Get table schema
    schema = get_table_schema(table_name)
    
    # Generate SQL
    sql = prompt_text_to_sql(question, schema)
    
    # Clean SQL
    sql = sql.strip()
    if sql.startswith("```sql"):
        sql = sql.replace("```sql", "").replace("```", "").strip()
    
    # Execute query
    results = run_sql(sql, fetch=True)
    
    if isinstance(results, str) and "Error" in results:
        return results, sql, ""
    
    # Format results
    result_text = f"Columns: {', '.join(results['columns'])}\n\n"
    for row in results['rows']:
        result_text += str(row) + "\n"
    
    # Get explanation
    explanation = prompt_explain_results(question, sql, results['rows'])
    
    return result_text, sql, explanation

# =============================================================================
# GRADIO INTERFACE
# =============================================================================

with gr.Blocks(title="Chat-Driven SQL Database", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown("# 🗄️ Chat-Driven SQL Database with LLM")
    gr.Markdown("### Upload data, create tables, and query using natural language")
    
    with gr.Tabs():
        
        # TAB 1: Upload CSV
        with gr.Tab("📁 Upload CSV"):
            gr.Markdown("### Upload a CSV file and create a table automatically")
            with gr.Row():
                csv_file = gr.File(label="Upload CSV File", file_types=[".csv"])
                csv_table_name = gr.Textbox(label="Table Name", placeholder="e.g., students")
            csv_button = gr.Button("Create Table from CSV", variant="primary")
            csv_output = gr.Textbox(label="Result", lines=5)
            
            csv_button.click(
                fn=upload_csv_handler,
                inputs=[csv_file, csv_table_name],
                outputs=csv_output
            )
        
        # TAB 2: Create Table from Chat
        with gr.Tab("💬 Create Table (Chat)"):
            gr.Markdown("### Describe a table in natural language")
            gr.Markdown("**Example:** *Create a table called employees with id, name, salary, and department*")
            table_desc = gr.Textbox(
                label="Table Description",
                placeholder="Describe the table you want to create...",
                lines=3
            )
            create_button = gr.Button("Create Table", variant="primary")
            create_output = gr.Textbox(label="Result", lines=8)
            
            create_button.click(
                fn=create_table_handler,
                inputs=table_desc,
                outputs=create_output
            )
        
        # TAB 3: Insert Rows from Chat
        with gr.Tab("➕ Insert Data (Chat)"):
            gr.Markdown("### Add rows using natural language")
            gr.Markdown("**Example:** *Add Alice with salary 75000 in Engineering, and Bob with salary 68000 in Marketing*")
            insert_table = gr.Textbox(label="Table Name", placeholder="e.g., employees")
            rows_desc = gr.Textbox(
                label="Row Description",
                placeholder="Describe the rows you want to insert...",
                lines=3
            )
            insert_button = gr.Button("Insert Rows", variant="primary")
            insert_output = gr.Textbox(label="Result", lines=8)
            
            insert_button.click(
                fn=insert_rows_handler,
                inputs=[insert_table, rows_desc],
                outputs=insert_output
            )
        
        # TAB 4: Query Data
        with gr.Tab("🔍 Query Data"):
            gr.Markdown("### Ask questions about your data in English")
            gr.Markdown("**Example:** *Which students have a GPA above 3.5?*")
            
            # Refresh tables button
            def refresh_tables():
                return gr.Dropdown(choices=list_tables())
            
            with gr.Row():
                query_question = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask a question about your data...",
                    lines=2
                )
                query_table = gr.Dropdown(
                    label="Select Table",
                    choices=list_tables(),
                    interactive=True
                )
            
            refresh_btn = gr.Button("🔄 Refresh Tables", size="sm")
            refresh_btn.click(fn=refresh_tables, outputs=query_table)
            
            query_button = gr.Button("Get Answer", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    query_results = gr.Textbox(label="Query Results", lines=8)
                with gr.Column():
                    query_sql = gr.Textbox(label="Generated SQL", lines=4)
                    query_explanation = gr.Textbox(label="Explanation", lines=4)
            
            query_button.click(
                fn=query_handler,
                inputs=[query_question, query_table],
                outputs=[query_results, query_sql, query_explanation]
            )
    
    gr.Markdown("---")
    gr.Markdown("### 📊 Current Tables")
    tables_display = gr.Textbox(value=lambda: "\n".join(list_tables()) or "No tables yet", label="Available Tables", lines=3)

if __name__ == "__main__":
    print("🚀 Starting Chat-Driven SQL Database...")
    print("📊 Initializing database...")
    print("🌐 Launching Gradio interface...")
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)