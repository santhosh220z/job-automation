from src.search.base import BaseSearcher, JobListing
from src.config import LINKEDIN_USER, LINKEDIN_PASS
from playwright.sync_api import sync_playwright
import time


class LinkedInSearcher(BaseSearcher):
    def __init__(self):
        self.browser = None
        self.page = None
        self._playwright = None

    def login(self) -> None:
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        self.page.goto("https://www.linkedin.com/login")
        self.page.fill("#username", LINKEDIN_USER)
        self.page.fill("#password", LINKEDIN_PASS)
        self.page.click("button[type=submit]")
        time.sleep(3)

    def search(self, keywords: str, location: str = "remote", max_results: int = 10) -> list[JobListing]:
        encoded = keywords.replace(" ", "%20")
        url = f"https://www.linkedin.com/jobs/search/?keywords={encoded}&location={location}"
        self.page.goto(url)
        time.sleep(3)

        jobs = []
        cards = self.page.query_selector_all(".job-card-container")[:max_results]
        for card in cards:
            try:
                title_el = card.query_selector(".job-card-list__title")
                company_el = card.query_selector(".job-card-container__company-name")
                link_el = card.query_selector("a.job-card-list__title")
                title = title_el.inner_text().strip() if title_el else ""
                company = company_el.inner_text().strip() if company_el else ""
                href = link_el.get_attribute("href") if link_el else ""
                url_full = f"https://www.linkedin.com{href}" if href and href.startswith("/") else href
                jobs.append(JobListing(title=title, company=company, url=url_full, source="linkedin"))
            except Exception:
                continue
        return jobs

    def scrape_description(self, job: JobListing) -> str:
        self.page.goto(job.url)
        time.sleep(2)
        try:
            desc = self.page.query_selector(".jobs-description-content__text")
            return desc.inner_text() if desc else ""
        except Exception:
            return ""

    def close(self) -> None:
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
