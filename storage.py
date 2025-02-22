import psycopg2
from config import DBConfig

def get_db_connection():
    return psycopg2.connect(
        host=DBConfig.HOST,
        database=DBConfig.DATABASE,
        user=DBConfig.USER,
        password=DBConfig.PASSWORD,
        port=DBConfig.PORT
    )

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pdf_content (
                    filename TEXT,
                    page INTEGER,
                    line INTEGER,
                    content TEXT
                )''')
    conn.commit()
    conn.close()

def save_to_db(data: list):
    conn = get_db_connection()
    c = conn.cursor()
    c.executemany(
        "INSERT INTO pdf_content (filename, page, line, content) VALUES (%s, %s, %s, %s)",
        [(item["filename"], item["page"], item["line"], item["content"]) for item in data]
    )
    conn.commit()
    conn.close()

def query_db(search_text: str) -> list:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM pdf_content WHERE content ILIKE %s", (f"%{search_text}%",))
    results = [{"filename": row[0], "page": row[1], "line": row[2], "content": row[3]} for row in c.fetchall()]
    conn.close()
    return results