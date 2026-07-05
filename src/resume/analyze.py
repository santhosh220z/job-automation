from src.resume.parse import parse_resume
from src.utils.llm_client import LLMClient
from src.config import LLM_MATCH_THRESHOLD
from pathlib import Path


def analyze_resume_match(resume_path: Path, jd_text: str) -> dict:
    resume_text = parse_resume(resume_path)
    llm = LLMClient()
    result = llm.analyze_match(resume_text, jd_text)
    result["passes_threshold"] = result.get("score", 0) >= LLM_MATCH_THRESHOLD
    return result
