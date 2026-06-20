from db import conn

if conn.is_connected():
    print("Database Connected Successfully")