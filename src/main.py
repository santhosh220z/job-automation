from src.config import (
    RESUME_PATH, SEARCH_KEYWORDS, SEARCH_LOCATION,
    MAX_APPLICATIONS_PER_RUN, LLM_MATCH_THRESHOLD,
    RESUMES_DIR,
)
from src.resume.parse import parse_resume
from src.resume.analyze import analyze_resume_match
from src.resume.tailor import tailor_resume
from src.search.linkedin_search import LinkedInSearcher
from src.search.indeed_search import IndeedSearcher
from src.search.wellfound_search import WellfoundSearcher
from src.apply.linkedin_apply import LinkedInApplicator
from src.apply.indeed_apply import IndeedApplicator
from src.apply.wellfound_apply import WellfoundApplicator
from src.tracking.sheets import log_application, update_status, get_applications
from src.tracking.email_monitor import check_for_replies, mark_as_read
from src.utils.logger import logger
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Callable


def run(
    keywords: Optional[str] = None,
    location: Optional[str] = None,
    max_apps: Optional[int] = None,
    platforms: Optional[list[str]] = None,
    on_log: Optional[Callable[[str], None]] = None,
):
    def log(msg: str):
        logger.info(msg)
        if on_log:
            on_log(msg)

    keyword = keywords or (SEARCH_KEYWORDS[0] if SEARCH_KEYWORDS else "software engineer")
    loc = location or SEARCH_LOCATION
    limit = max_apps or MAX_APPLICATIONS_PER_RUN

    log("Starting job application automation")
    log(f"Searching: {keyword} in {loc}, max {limit} applications")

    all_searchers = [
        ("LinkedIn", LinkedInSearcher, LinkedInApplicator),
        ("Indeed", IndeedSearcher, IndeedApplicator),
        ("Wellfound", WellfoundSearcher, WellfoundApplicator),
    ]

    searchers = all_searchers
    if platforms:
        searchers = [(n, s, a) for n, s, a in all_searchers if n.lower() in (p.lower() for p in platforms)]

    total_applied = 0
    start_time = datetime.now(timezone.utc)

    for name, SearcherCls, ApplicatorCls in searchers:
        if total_applied >= limit:
            break

        log(f"--- Processing {name} ---")
        try:
            searcher = SearcherCls()
            searcher.login()
            jobs = searcher.search(keyword, loc, max_results=5)
            log(f"Found {len(jobs)} jobs on {name}")

            for job in jobs:
                if total_applied >= limit:
                    break

                log(f"Processing: {job.title} at {job.company}")
                jd_text = searcher.scrape_description(job)
                if not jd_text:
                    log(f"No description for {job.url}, skipping")
                    continue

                analysis = analyze_resume_match(RESUME_PATH, jd_text)
                score = analysis.get("score", 0)
                log(f"Match score: {score:.2f} (threshold: {LLM_MATCH_THRESHOLD})")

                resume_to_use = RESUME_PATH
                if score < LLM_MATCH_THRESHOLD:
                    log("Score below threshold, tailoring resume")
                    tailored_path = RESUMES_DIR / f"tailored_{name.lower()}_{total_applied+1}.pdf"
                    resume_to_use = tailor_resume(RESUME_PATH, jd_text, analysis, tailored_path)
                    log(f"Tailored resume saved to {resume_to_use}")

                applicator = ApplicatorCls()
                result = applicator.apply(job.url, resume_to_use)
                log(f"Apply result: {result.message}")

                if result.success:
                    total_applied += 1
                    log_application(
                        company=job.company or result.company,
                        role=job.title,
                        url=job.url,
                        status="Applied",
                        notes=f"Source: {name}, Score: {score:.2f}",
                    )

                applicator.close()

            searcher.close()

        except Exception as e:
            log(f"Error processing {name}: {e}")
            continue

    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    log(f"Done. Applied to {total_applied} jobs this run. ({elapsed:.0f}s)")

    return total_applied, elapsed


def check_replies(on_log: Optional[Callable[[str], None]] = None):
    def log(msg: str):
        logger.info(msg)
        if on_log:
            on_log(msg)

    log("--- Checking Gmail for application replies ---")
    try:
        replies = check_for_replies()
        log(f"Found {len(replies)} unread replies")
        if not replies:
            log("No new replies.")
            return 0, 0

        applications = get_applications()
        url_to_entry = {}
        for entry in applications:
            if entry.get("URL"):
                url_to_entry[entry["URL"].strip()] = entry

        matched_count = 0
        interview_count = 0
        for reply in replies:
            snippet = reply.get("snippet", "")
            subject = reply.get("subject", "")
            log(f"Reply from {reply['from']}: {subject}")
            matched = False
            for app_url, entry in url_to_entry.items():
                company_lower = entry.get("Company", "").lower()
                if company_lower and company_lower in snippet.lower():
                    is_interview = "interview" in snippet.lower()
                    new_status = "Interview" if is_interview else "Replied"
                    update_status(app_url, new_status, notes=f"Reply: {subject}")
                    log(f"Updated {entry['Company']} status to '{new_status}'")
                    matched = True
                    matched_count += 1
                    if is_interview:
                        interview_count += 1
                    break
            if matched:
                mark_as_read(reply["id"])
            else:
                log(f"No matching application found for reply: {subject}")
        return matched_count, interview_count
    except Exception as e:
        log(f"Gmail check failed: {e}")
        return 0, 0


if __name__ == "__main__":
    def console_log(msg: str):
        print(msg)

    run(), check_replies(on_log=None)