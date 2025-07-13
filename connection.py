import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",       # Use your actual MySQL password
    database="mysql",          # Or your own database name
    port=3306
)

if conn.is_connected():
    print("✅ Connected to MySQL!")
else:
    print("❌ Failed to connect.")

cursor = conn.cursor()
cursor.execute("SHOW DATABASES")

for db in cursor:
    print("📁", db[0])

cursor.close()
conn.close()
