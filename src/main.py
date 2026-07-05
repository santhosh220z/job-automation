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
from src.tracking.sheets import log_application
from src.utils.logger import logger
from pathlib import Path


def run():
    keyword = SEARCH_KEYWORDS[0] if SEARCH_KEYWORDS else "software engineer"
    location = SEARCH_LOCATION
    max_apps = MAX_APPLICATIONS_PER_RUN

    logger.info("Starting job application automation")
    logger.info(f"Searching: {keyword} in {location}, max {max_apps} applications")

    searchers = [
        ("LinkedIn", LinkedInSearcher, LinkedInApplicator),
        ("Indeed", IndeedSearcher, IndeedApplicator),
        ("Wellfound", WellfoundSearcher, WellfoundApplicator),
    ]

    total_applied = 0

    for name, SearcherCls, ApplicatorCls in searchers:
        if total_applied >= max_apps:
            break

        logger.info(f"--- Processing {name} ---")
        try:
            searcher = SearcherCls()
            searcher.login()
            jobs = searcher.search(keyword, location, max_results=5)
            logger.info(f"Found {len(jobs)} jobs on {name}")

            for job in jobs:
                if total_applied >= max_apps:
                    break

                logger.info(f"Processing: {job.title} at {job.company}")
                jd_text = searcher.scrape_description(job)
                if not jd_text:
                    logger.warning(f"No description for {job.url}, skipping")
                    continue

                analysis = analyze_resume_match(RESUME_PATH, jd_text)
                score = analysis.get("score", 0)
                logger.info(f"Match score: {score:.2f} (threshold: {LLM_MATCH_THRESHOLD})")

                resume_to_use = RESUME_PATH
                if score < LLM_MATCH_THRESHOLD:
                    logger.info("Score below threshold, tailoring resume")
                    tailored_path = RESUMES_DIR / f"tailored_{name.lower()}_{total_applied+1}.pdf"
                    resume_to_use = tailor_resume(RESUME_PATH, jd_text, analysis, tailored_path)
                    logger.info(f"Tailored resume saved to {resume_to_use}")

                applicator = ApplicatorCls()
                result = applicator.apply(job.url, resume_to_use)
                logger.info(f"Apply result: {result.message}")

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
            logger.error(f"Error processing {name}: {e}")
            continue

    logger.info(f"Done. Applied to {total_applied} jobs this run.")


if __name__ == "__main__":
    run()
