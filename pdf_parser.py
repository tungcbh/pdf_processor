import fitz  # PyMuPDF

def parse_pdf(file_path: str) -> list:
    pdf_data = []
    doc = fitz.open(file_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        lines = text.split("\n")
        for line_num, line in enumerate(lines):
            if line.strip():  # skip empty lineline
                pdf_data.append({
                    "filename": file_path.split("/")[-1],
                    "page": page_num + 1,
                    "line": line_num + 1,
                    "content": line.strip()
                })
    doc.close()
    return pdf_data