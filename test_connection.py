# test_connection.py
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    connection = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        port=int(os.getenv('MYSQL_PORT')),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )
    
    if connection.is_connected():
        print("✅ Successfully connected to MySQL!")
        print(f"   Server version: {connection.get_server_info()}")
        print(f"   Database: {os.getenv('MYSQL_DATABASE')}")
    
    connection.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")