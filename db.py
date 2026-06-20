import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ANMOL",
    database="retailmind_ai"
)

cursor = conn.cursor(buffered=True)