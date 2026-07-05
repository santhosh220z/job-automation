from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESUMES_DIR = DATA_DIR / "resumes"
CREDENTIALS_DIR = DATA_DIR / "credentials"

RESUME_PATH = RESUMES_DIR / os.getenv("RESUME_PATH", "resume.pdf")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

LINKEDIN_USER = os.getenv("LINKEDIN_USER", "")
LINKEDIN_PASS = os.getenv("LINKEDIN_PASS", "")
INDEED_USER = os.getenv("INDEED_USER", "")
INDEED_PASS = os.getenv("INDEED_PASS", "")
WELLFOUND_USER = os.getenv("WELLFOUND_USER", "")
WELLFOUND_PASS = os.getenv("WELLFOUND_PASS", "")

GM_CREDENTIALS_PATH = CREDENTIALS_DIR / os.getenv("GM_CREDENTIALS_FILE", "service_account.json")
GM_TOKEN_PATH = CREDENTIALS_DIR / os.getenv("GM_TOKEN_FILE", "gmail_token.json")
SHEET_ID = os.getenv("SHEET_ID", "")

LLM_MATCH_THRESHOLD = float(os.getenv("LLM_MATCH_THRESHOLD", "0.6"))
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

SEARCH_KEYWORDS = os.getenv("SEARCH_KEYWORDS", "software engineer").split(",")
SEARCH_LOCATION = os.getenv("SEARCH_LOCATION", "remote")
MAX_APPLICATIONS_PER_RUN = int(os.getenv("MAX_APPLICATIONS_PER_RUN", "10"))
