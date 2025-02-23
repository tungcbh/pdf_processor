import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env (nếu có)
load_dotenv()

class DBConfig:
    HOST = os.getenv("DB_HOST", "localhost")
    DATABASE = os.getenv("DB_NAME", "pdf_processor")
    USER = os.getenv("DB_USER", "postgres")
    PASSWORD = os.getenv("DB_PASSWORD", "123456")
    PORT = int(os.getenv("DB_PORT", "5432"))