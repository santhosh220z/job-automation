from src.apply.base_applicator import BaseApplicator, ApplicationResult
from src.config import LINKEDIN_USER, LINKEDIN_PASS
from playwright.sync_api import sync_playwright
from pathlib import Path
import time


class LinkedInApplicator(BaseApplicator):
    def __init__(self):
        self.browser = None
        self.page = None
        self._playwright = None

    def _ensure_logged_in(self):
        if not self.browser:
            self._playwright = sync_playwright().start()
            self.browser = self._playwright.chromium.launch(headless=True)
            self.page = self.browser.new_page()
            self.page.goto("https://www.linkedin.com/login")
            self.page.fill("#username", LINKEDIN_USER)
            self.page.fill("#password", LINKEDIN_PASS)
            self.page.click("button[type=submit]")
            time.sleep(3)

    def apply(self, url: str, resume_path: Path, cover_letter: str = "") -> ApplicationResult:
        self._ensure_logged_in()
        try:
            self.page.goto(url)
            time.sleep(2)
            easy_apply = self.page.query_selector("button.jobs-apply-button")
            if not easy_apply:
                return ApplicationResult(False, "", url.split("/")[-1], url, "No Easy Apply button")
            easy_apply.click()
            time.sleep(2)
            if cover_letter:
                try:
                    ta = self.page.query_selector("textarea")
                    if ta:
                        ta.fill(cover_letter)
                except Exception:
                    pass
            submit = self.page.query_selector("button[aria-label='Submit application']")
            if submit:
                submit.click()
                time.sleep(2)
            else:
                next_btn = self.page.query_selector("button[aria-label='Next']")
                if next_btn:
                    next_btn.click()
                    time.sleep(1)
                review = self.page.query_selector("button[aria-label='Review']")
                if review:
                    review.click()
                    time.sleep(1)
                submit = self.page.query_selector("button[aria-label='Submit application']")
                if submit:
                    submit.click()
                    time.sleep(2)
            return ApplicationResult(True, "", url.split("/")[-1], url, "Applied via LinkedIn")
        except Exception as e:
            return ApplicationResult(False, "", url.split("/")[-1], url, str(e))

    def close(self):
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
