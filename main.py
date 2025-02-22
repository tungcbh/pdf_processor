from fastapi import FastAPI, UploadFile, File
from pdf_parser import parse_pdf
from storage import init_db, save_to_db, query_db
from models import PDFContent
import uvicorn
import os
import traceback

app = FastAPI()
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.on_event("startup")
def startup_event():
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        traceback.print_exc()

@app.post("/upload_pdf/")
async def upload_pdf(files: list[UploadFile] = File(...)):
    results = []
    try:
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            file_content = await file.read()
            with open(file_path, "wb") as f:
                f.write(file_content)
            pdf_data = parse_pdf(file_path)
            file_size = len(file_content)  # Kích thước file (bytes)
            save_to_db(pdf_data, file.filename, file_size)
            results.append({"filename": file.filename, "status": "processed"})
        return {"message": "PDFs processed", "details": results}
    except Exception as e:
        print(f"Error processing upload: {e}")
        traceback.print_exc()
        return {"message": "Error processing PDFs", "error": str(e)}, 500

@app.get("/query/", response_model=list[PDFContent])
def query_pdf(search: str):
    try:
        results = query_db(search)
        return results
    except Exception as e:
        print(f"Error querying database: {e}")
        traceback.print_exc()
        return {"message": "Error querying PDFs", "error": str(e)}, 500

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)