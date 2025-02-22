import fitz  # PyMuPDF
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def parse_pdf(file_path: str) -> List[Dict]:
    """Parse PDF tuần tự (không dùng multiprocessing)"""
    doc = fitz.open(file_path)
    num_pages = len(doc)
    if num_pages == 0:
        doc.close()
        return []

    pdf_data = []
    for page_num in range(num_pages):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        lines = text.split("\n")
        for line_num, line in enumerate(lines):
            if line.strip():  # Bỏ qua dòng trống
                pdf_data.append({
                    "filename": file_path.split("/")[-1],
                    "page": page_num + 1,
                    "line": line_num + 1,
                    "content": line.strip()
                })
    doc.close()
    logger.info(f"Parsed {len(pdf_data)} entries from {file_path}")
    return pdf_data