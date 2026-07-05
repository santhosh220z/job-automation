from src.search.base import BaseSearcher, JobListing
from playwright.sync_api import sync_playwright
import time


class LeverSearcher(BaseSearcher):
    def __init__(self, company_careers_url: str):
        self.company_url = company_careers_url
        self.browser = None
        self.page = None
        self._playwright = None

    def login(self) -> None:
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()

    def search(self, keywords: str, location: str = "remote", max_results: int = 10) -> list[JobListing]:
        self.page.goto(self.company_url)
        time.sleep(3)
        jobs = []
        links = self.page.query_selector_all("a[href*='/jobs/']")[:max_results]
        for link in links:
            try:
                title = link.inner_text().strip()
                href = link.get_attribute("href") or ""
                if not title:
                    continue
                url_full = href if href.startswith("http") else f"{self.company_url.rstrip('/')}{href}"
                jobs.append(JobListing(title=title, company="", url=url_full, source="lever"))
            except Exception:
                continue
        return jobs

    def scrape_description(self, job: JobListing) -> str:
        self.page.goto(job.url)
        time.sleep(2)
        try:
            desc = self.page.query_selector(".posting-description")
            return desc.inner_text() if desc else ""
        except Exception:
            return ""

    def close(self) -> None:
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
