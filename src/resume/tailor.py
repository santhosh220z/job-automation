from src.resume.parse import parse_resume
from src.resume.export import export_resume
from src.utils.llm_client import LLMClient
from pathlib import Path


def tailor_resume(resume_path: Path, jd_text: str, analysis: dict, output_path: Path) -> Path:
    resume_text = parse_resume(resume_path)
    llm = LLMClient()
    tailored_md = llm.tailor_resume(resume_text, jd_text, analysis)
    ext = output_path.suffix.lower()
    if ext not in (".pdf", ".docx"):
        ext = ".pdf"
        output_path = output_path.with_suffix(".pdf")
    export_resume(tailored_md, output_path, fmt=ext.lstrip("."))
    return output_path
