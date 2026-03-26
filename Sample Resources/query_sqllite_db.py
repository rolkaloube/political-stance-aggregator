import sqlite3

conn = sqlite3.connect("web_docs.db")
cursor = conn.cursor()

for row in cursor.execute("SELECT id, url, title, fetched_at FROM documents ORDER BY id DESC"):
    print(row)

conn.close()
