from fastapi import FastAPI, UploadFile, File
from pdf_parser import parse_pdf
from storage import init_db, save_to_db, query_db
from models import PDFContent
import uvicorn
import os
import traceback
from multiprocessing import Pool, cpu_count
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.on_event("startup")
def startup_event():
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        traceback.print_exc()

def process_file(file_info: tuple) -> dict:
    """Xử lý một file PDF từ dữ liệu bytes"""
    filename, file_content = file_info
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        logger.info(f"Processing file: {filename}")
        pdf_data = parse_pdf(file_path)
        logger.info(f"Parsed {len(pdf_data)} entries from {filename}")
        file_size = len(file_content)
        file_id = save_to_db(pdf_data, filename, file_size)
        logger.info(f"Saved to DB with file_id: {file_id}")
        return {"filename": filename, "status": "processed"}
    except Exception as e:
        logger.error(f"Error processing file {filename}: {e}")
        traceback.print_exc()
        return {"filename": filename, "status": "error", "error": str(e)}

@app.post("/upload_pdf/")
async def upload_pdf(files: list[UploadFile] = File(...)):
    try:
        file_data = [(file.filename, await file.read()) for file in files]
        logger.info(f"Received {len(file_data)} files for processing")
        num_processes = min(cpu_count() - 1, len(files)) or 1
        with Pool(processes=num_processes) as pool:
            results = pool.map(process_file, file_data)
        return {"message": "PDFs processed", "details": results}
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        traceback.print_exc()
        return {"message": "Error processing PDFs", "error": str(e)}, 500

@app.get("/query/", response_model=list[PDFContent])
def query_pdf(search: str):
    try:
        results = query_db(search)
        
        logger.info(f"Query returned {len(results)} results for search: {search}")
        return results
    except Exception as e:
        logger.error(f"Error querying database: {e}")
        traceback.print_exc()
        return {"message": "Error querying PDFs", "error": str(e)}, 500

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)