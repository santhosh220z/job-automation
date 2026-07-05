from src.apply.base_applicator import BaseApplicator, ApplicationResult
from playwright.sync_api import sync_playwright
from pathlib import Path
import time


class ATSApplicator(BaseApplicator):
    def __init__(self):
        self.browser = None
        self.page = None
        self._playwright = None

    def _ensure_browser(self):
        if not self.browser:
            self._playwright = sync_playwright().start()
            self.browser = self._playwright.chromium.launch(headless=True)
            self.page = self.browser.new_page()

    def apply(self, url: str, resume_path: Path, cover_letter: str = "") -> ApplicationResult:
        self._ensure_browser()
        try:
            self.page.goto(url)
            time.sleep(3)
            buttons = self.page.query_selector_all("a, button")
            apply_btn = None
            for btn in buttons:
                text = btn.inner_text().lower()
                if "apply" in text or "submit" in text:
                    apply_btn = btn
                    break
            if not apply_btn:
                return ApplicationResult(False, "", url, url, "No apply button found")
            apply_btn.click()
            time.sleep(3)
            upload = self.page.query_selector("input[type='file']")
            if upload:
                upload.set_input_files(str(resume_path))
                time.sleep(2)
            final = self.page.query_selector("button[type='submit']")
            if final:
                final.click()
                time.sleep(2)
            company = url.split("/")[2] if "//" in url else ""
            return ApplicationResult(True, company, url, url, "Applied via ATS generic")
        except Exception as e:
            return ApplicationResult(False, "", url, url, str(e))

    def close(self):
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
