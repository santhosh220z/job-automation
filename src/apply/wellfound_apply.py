from src.apply.base_applicator import BaseApplicator, ApplicationResult
from src.config import WELLFOUND_USER, WELLFOUND_PASS
from playwright.sync_api import sync_playwright
from pathlib import Path
import time


class WellfoundApplicator(BaseApplicator):
    def __init__(self):
        self.browser = None
        self.page = None
        self._playwright = None

    def _ensure_logged_in(self):
        if not self.browser:
            self._playwright = sync_playwright().start()
            self.browser = self._playwright.chromium.launch(headless=True)
            self.page = self.browser.new_page()
            self.page.goto("https://wellfound.com/login")
            time.sleep(2)
            self.page.fill("input[name='email']", WELLFOUND_USER)
            self.page.fill("input[name='password']", WELLFOUND_PASS)
            self.page.click("button[type=submit]")
            time.sleep(3)

    def apply(self, url: str, resume_path: Path, cover_letter: str = "") -> ApplicationResult:
        self._ensure_logged_in()
        try:
            self.page.goto(url)
            time.sleep(2)
            apply_btn = self.page.query_selector("a.apply-button, button.apply-button")
            if not apply_btn:
                return ApplicationResult(False, "", url, url, "No apply button found")
            apply_btn.click()
            time.sleep(3)
            upload = self.page.query_selector("input[type='file']")
            if upload:
                upload.set_input_files(str(resume_path))
                time.sleep(2)
            submit = self.page.query_selector("button[type='submit']")
            if submit:
                submit.click()
                time.sleep(2)
            return ApplicationResult(True, "", url, url, "Applied via Wellfound")
        except Exception as e:
            return ApplicationResult(False, "", url, url, str(e))

    def close(self):
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
