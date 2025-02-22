from pydantic import BaseModel

class PDFContent(BaseModel):
    filename: str
    page: int
    line: int
    content: str