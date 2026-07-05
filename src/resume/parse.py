from pathlib import Path
from typing import Optional


def parse_resume(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return _parse_pdf(path)
    elif ext == ".docx":
        return _parse_docx(path)
    elif ext in (".md", ".txt"):
        return _parse_text(path)
    else:
        raise ValueError(f"Unsupported resume format: {ext}")


def _parse_pdf(path: Path) -> str:
    import pdfplumber

    text_parts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _parse_docx(path: Path) -> str:
    from docx import Document

    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def _parse_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")
