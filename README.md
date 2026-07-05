# Job Application Automation

Automated pipeline that searches job platforms, matches your resume against job descriptions, tailors the resume when needed, auto-applies, and tracks applications in Google Sheets + Gmail.

## Quick Start

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
playwright install chromium

# Configure
cp .env.example .env
# Fill in your API keys, credentials, and login info

# Run
python src/main.py
```

## Project Structure

```
src/
  main.py          # Entry point / orchestrator
  config.py        # Environment variable loader
  resume/          # Parse, analyze, tailor, export resume
  search/          # Job search per platform
  apply/           # Auto-apply per platform
  tracking/        # Google Sheets + Gmail monitoring
data/
  resumes/         # Base and generated resume files
  credentials/     # Google service account and OAuth tokens
```

## Pipelines

1. **Search** - LinkedIn, Indeed, Wellfound (browser automation)
2. **Match** - LLM compares resume vs job description
3. **Tailor** - LLM rewrites resume sections + injects ATS keywords
4. **Apply** - Playwright fills forms and submits
5. **Track** - Google Sheets log + Gmail reply monitoring

## GitHub Actions

Trigger manually via the Actions tab with optional keyword/location overrides.
