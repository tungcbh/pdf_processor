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
    # Tạo bảng pdf_files
    c.execute('''CREATE TABLE IF NOT EXISTS pdf_files (
                    id SERIAL PRIMARY KEY,
                    filename TEXT UNIQUE NOT NULL,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_size INTEGER
                 )''')
    # Tạo bảng pdf_content
    c.execute('''CREATE TABLE IF NOT EXISTS pdf_content (
                    id SERIAL PRIMARY KEY,
                    file_id INTEGER REFERENCES pdf_files(id) ON DELETE CASCADE,
                    page INTEGER,
                    line INTEGER,
                    content TEXT
                 )''')
    conn.commit()
    conn.close()

def save_to_db(pdf_data: list, filename: str, file_size: int) -> int:
    conn = get_db_connection()
    c = conn.cursor()
    # Lưu metadata vào pdf_files
    c.execute("INSERT INTO pdf_files (filename, file_size) VALUES (%s, %s) ON CONFLICT (filename) DO NOTHING RETURNING id",
              (filename, file_size))
    file_id = c.fetchone()
    if not file_id:  # Nếu file đã tồn tại
        c.execute("SELECT id FROM pdf_files WHERE filename = %s", (filename,))
        file_id = c.fetchone()
    file_id = file_id[0]
    
    # Lưu nội dung vào pdf_content
    content_data = [(file_id, item["page"], item["line"], item["content"]) for item in pdf_data]
    c.executemany("INSERT INTO pdf_content (file_id, page, line, content) VALUES (%s, %s, %s, %s)", content_data)
    conn.commit()
    conn.close()
    return file_id

def query_db(search_text: str) -> list:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT f.filename, c.page, c.line, c.content
        FROM pdf_content c
        JOIN pdf_files f ON c.file_id = f.id
        WHERE c.content ILIKE %s
    """, (f"%{search_text}%",))
    results = [{"filename": row[0], "page": row[1], "line": row[2], "content": row[3]} for row in c.fetchall()]
    conn.close()
    return results