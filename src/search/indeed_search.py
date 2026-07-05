from src.search.base import BaseSearcher, JobListing
from src.config import INDEED_USER, INDEED_PASS
from playwright.sync_api import sync_playwright
import time


class IndeedSearcher(BaseSearcher):
    def __init__(self):
        self.browser = None
        self.page = None
        self._playwright = None

    def login(self) -> None:
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        self.page.goto("https://secure.indeed.com/auth")
        time.sleep(2)
        try:
            self.page.fill("#ifl-InputFormField-email", INDEED_USER)
            self.page.click("button[type=submit]")
            time.sleep(2)
            self.page.fill("#ifl-InputFormField-password", INDEED_PASS)
            self.page.click("button[type=submit]")
            time.sleep(3)
        except Exception:
            pass

    def search(self, keywords: str, location: str = "remote", max_results: int = 10) -> list[JobListing]:
        encoded_k = keywords.replace(" ", "+")
        encoded_l = location.replace(" ", "+")
        url = f"https://www.indeed.com/jobs?q={encoded_k}&l={encoded_l}"
        self.page.goto(url)
        time.sleep(3)

        jobs = []
        cards = self.page.query_selector_all("td.resultContent")[:max_results]
        for card in cards:
            try:
                title_el = card.query_selector(".jobTitle")
                company_el = card.query_selector(".companyName")
                link_el = card.query_selector("a.jcs-JobTitle")
                title = title_el.get_attribute("title") or title_el.inner_text().strip() if title_el else ""
                company = company_el.inner_text().strip() if company_el else ""
                href = link_el.get_attribute("href") if link_el else ""
                url_full = f"https://www.indeed.com{href}" if href and href.startswith("/") else href
                jobs.append(JobListing(title=title, company=company, url=url_full, source="indeed"))
            except Exception:
                continue
        return jobs

    def scrape_description(self, job: JobListing) -> str:
        self.page.goto(job.url)
        time.sleep(2)
        try:
            desc = self.page.query_selector("#jobDescriptionText")
            return desc.inner_text() if desc else ""
        except Exception:
            return ""

    def close(self) -> None:
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
