from src.search.base import BaseSearcher, JobListing
from src.config import WELLFOUND_USER, WELLFOUND_PASS
from playwright.sync_api import sync_playwright
import time


class WellfoundSearcher(BaseSearcher):
    def __init__(self):
        self.browser = None
        self.page = None
        self._playwright = None

    def login(self) -> None:
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        self.page.goto("https://wellfound.com/login")
        time.sleep(2)
        try:
            self.page.fill("input[name='email']", WELLFOUND_USER)
            self.page.fill("input[name='password']", WELLFOUND_PASS)
            self.page.click("button[type=submit]")
            time.sleep(3)
        except Exception:
            pass

    def search(self, keywords: str, location: str = "remote", max_results: int = 10) -> list[JobListing]:
        encoded = keywords.replace(" ", "%20")
        url = f"https://wellfound.com/search/jobs?q={encoded}"
        self.page.goto(url)
        time.sleep(3)

        jobs = []
        cards = self.page.query_selector_all("a.work-finder-job-card")[:max_results]
        for card in cards:
            try:
                title_el = card.query_selector("h4")
                company_el = card.query_selector("span.company-name")
                title = title_el.inner_text().strip() if title_el else ""
                company = company_el.inner_text().strip() if company_el else ""
                href = card.get_attribute("href") or ""
                url_full = f"https://wellfound.com{href}" if href.startswith("/") else href
                jobs.append(JobListing(title=title, company=company, url=url_full, source="wellfound"))
            except Exception:
                continue
        return jobs

    def scrape_description(self, job: JobListing) -> str:
        self.page.goto(job.url)
        time.sleep(2)
        try:
            desc = self.page.query_selector("div.description")
            return desc.inner_text() if desc else ""
        except Exception:
            return ""

    def close(self) -> None:
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
