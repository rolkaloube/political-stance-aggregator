import sqlite3
from flask import Flask, render_template_string

app = Flask(__name__)
DB_NAME = "sample_candidate_data.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM people")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_data = [
            ("Alice Johnson", "alice@example.com"),
            ("Bob Smith", "bob@example.com"),
            ("Carol Davis", "carol@example.com"),
        ]
        cursor.executemany(
            "INSERT INTO people (name, email) VALUES (?, ?)",
            sample_data
        )
        conn.commit()

    conn.close()


def get_people():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM people ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return rows


HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>SQLite Data Viewer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
        }
        h1 {
            margin-bottom: 20px;
        }
        table {
            border-collapse: collapse;
            width: 700px;
            max-width: 100%;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 10px;
            text-align: left;
        }
        th {
            background: #f4f4f4;
        }
        tr:nth-child(even) {
            background: #fafafa;
        }
    </style>
</head>
<body>
    <h1>People from SQLite Database</h1>
    <table>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
        </tr>
        {% for person in people %}
        <tr>
            <td>{{ person.id }}</td>
            <td>{{ person.name }}</td>
            <td>{{ person.email }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""


@app.route("/")
def home():
    people = get_people()
    return render_template_string(HTML_TEMPLATE, people=people)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
