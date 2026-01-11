# Chat-Driven SQL Database with LLM

## Overview
An intelligent database interface that allows users to create, populate, and query MySQL databases using natural language instead of SQL.

## Features
- 📁 Upload CSV files → automatic table creation
- 💬 Describe tables in English → LLM generates CREATE TABLE
- ➕ Describe data in English → LLM generates INSERT statements
- 🔍 Ask questions in English → LLM generates SELECT queries

## Setup

### 1. Install MySQL
```bash
# On Mac
brew install mysql
brew services start mysql

# On Ubuntu
sudo apt install mysql-server
sudo systemctl start mysql

# On Windows
# Download from https://dev.mysql.com/downloads/mysql/
```

### 2. Create Database
```bash
mysql -u root -p
CREATE DATABASE chatdb;
EXIT;
```

### 3. Configure Environment
Create `.env` file:
```
OPENAI_API_KEY=your-key-here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=chatdb
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run Application
```bash
python app.py
```

Open browser to: http://127.0.0.1:7860

## Usage Examples

### Upload CSV
1. Go to "Upload CSV" tab
2. Upload `data/demo.csv`
3. Name it "students"
4. Click "Create Table from CSV"

### Create Table from Chat
```
Create a table called employees with id, name, salary, and department
```

### Insert Data from Chat
```
Add three employees: Alice with salary 75000 in Engineering,
Bob with salary 68000 in Marketing, and Carol with salary 82000 in Engineering
```

### Query Data
Select table: `students`
Question: `Which students have a GPA above 3.5?`

## Tech Stack
- **Frontend:** Gradio
- **Backend:** Python 3.10+
- **LLM:** OpenAI GPT-4
- **Database:** MySQL 8.0+
- **Libraries:** pandas, SQLAlchemy, mysql-connector-python

## Project Structure
```
chat_sql_llm/
├── app.py              # Main Gradio UI
├── db_utils.py         # Database operations
├── llm_utils.py        # LLM API calls & prompts
├── ingest_utils.py     # CSV processing & data ingestion
├── data/
│   └── demo.csv        # Sample dataset
├── .env                # Environment variables
└── requirements.txt    # Dependencies
```

## Troubleshooting

**MySQL Connection Error:**
```bash
# Check MySQL is running
mysql -u root -p

# Reset password if needed
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
```

**OpenAI API Error:**
- Check API key is valid
- Ensure you have credits: https://platform.openai.com/usage

## Research Contribution
This project demonstrates Natural Language to SQL translation using:
1. Schema-aware prompting
2. Grounded LLM reasoning over real databases
3. Explainable query generation
