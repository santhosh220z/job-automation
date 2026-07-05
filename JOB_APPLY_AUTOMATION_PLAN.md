# Job Application Automation — Plan

## Overview
Automated pipeline that searches job platforms, matches your resume against job descriptions, tailors the resume when there's a mismatch, auto-applies, and tracks everything in Google Sheets + Gmail.

## Stack
- **Python 3.11+** | **Playwright** (headless browser) | **OpenAI + Anthropic** (LLMs)
- **pdfplumber** (PDF) / **python-docx** (DOCX) for resume parsing
- **gspread** (Google Sheets) / **google-api-python-client** (Gmail)
- **GitHub Actions** (manual trigger) — all secrets in GitHub Secrets

## Platform Targets (priority order)
| Priority | Platform | Approach |
|---|---|---|
| Must | LinkedIn | Playwright search + apply |
| Must | Indeed | Playwright search + apply |
| Must | Wellfound (AngelList) | Playwright search + apply |
| Nice | Naukri | Playwright search + apply |
| Nice | Greenhouse / Lever / Workday | Generic ATS form filler |

## Project Structure
```
job-apply-automation/
├── .github/workflows/run-automation.yml
├── src/
│   ├── main.py                       # Orchestrator
│   ├── config.py                     # Env vars, paths
│   ├── resume/
│   │   ├── parse.py                  # PDF/DOCX/MD -> text
│   │   ├── analyze.py                # LLM resume-JD matching
│   │   ├── tailor.py                 # LLM section rewrite
│   │   └── export.py                 # Text -> PDF/DOCX
│   ├── search/
│   │   ├── base.py                   # Abstract searcher
│   │   ├── linkedin_search.py
│   │   ├── indeed_search.py
│   │   ├── wellfound_search.py
│   │   ├── naukri_search.py
│   │   ├── greenhouse_search.py
│   │   ├── lever_search.py
│   │   └── workday_search.py
│   ├── apply/
│   │   ├── base_applicator.py
│   │   ├── linkedin_apply.py
│   │   ├── indeed_apply.py
│   │   ├── wellfound_apply.py
│   │   └── ats_apply.py
│   └── tracking/
│       ├── sheets.py                 # Google Sheets CRUD
│       └── email_monitor.py          # Gmail API
├── data/resumes/
├── requirements.txt
└── README.md
```

## Core Flow
```
Trigger (manual) -> Search all platforms -> For each job:
  1. Scrape job description
  2. Parse resume -> LLM match score
  3. Score >= threshold ->  Apply
     Score < threshold ->  Tailor resume -> Apply with tailored version
  4. Log to Google Sheets (Company | Role | Date | Status | URL)
  5. Gmail watcher -> update status on replies
```

## LLM Strategy
- **Claude 3.5 Sonnet** — job analysis (long context, nuanced matching)
- **GPT-4o mini** — resume rewriting (structured, cheaper)
- **Hybrid tailoring**: LLM rewrites + keyword injection for ATS optimization

## Implementation Phases
| # | Phase | Key Deliverables |
|---|---|---|
| 1 | Foundation | config.py, parse.py, requirements.txt, GitHub Actions workflow |
| 2 | LLM Client | Unified OpenAI + Anthropic wrapper with fallback |
| 3 | Resume Analyzer & Tailor | analyze.py, tailor.py, export.py |
| 4 | Job Search (core) | LinkedIn, Indeed, Wellfound search scripts |
| 5 | Job Search (extended) | Naukri, Greenhouse, Lever, Workday |
| 6 | Auto-Apply (core) | LinkedIn, Indeed, Wellfound apply scripts |
| 7 | Auto-Apply (ATS) | Generic Greenhouse/Lever/Workday filler |
| 8 | Google Sheets Logging | sheets.py |
| 9 | Gmail Monitor | email_monitor.py |
| 10 | Orchestrator | main.py — wires everything together |
| 11 | Deployment | GitHub Actions + secrets + docs |

## GitHub Secrets Required
| Secret | Purpose |
|---|---|
| OPENAI_API_KEY | GPT-4o mini |
| ANTHROPIC_API_KEY | Claude 3.5 Sonnet |
| GM_CREDENTIALS_JSON | Google service account |
| GM_TOKEN_JSON | Gmail OAuth token |
| LINKEDIN_USER / LINKEDIN_PASS | LinkedIn login |
| INDEED_USER / INDEED_PASS | Indeed login |
| WELLFOUND_USER / WELLFOUND_PASS | Wellfound login |
| RESUME_BASE64 | Base resume file |

## What You Need to Prepare
1. **Base resume** (Markdown recommended — easier for LLM to edit, then export to PDF/DOCX)
2. **Google Cloud Project** — enable Sheets + Gmail APIs, create service account + OAuth
3. **Active accounts** on LinkedIn, Indeed, Wellfound
4. **OpenAI + Anthropic API keys**
