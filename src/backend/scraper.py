import random
import time
from abc import ABC
from typing import Optional

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]


class BaseScraper(ABC):
    SOURCE: str = ""
    BASE_URL: str = ""
    TITLE_SELECTORS: list = []
    DESC_SELECTORS: list = []

    def fetch(self, url: str) -> Optional[str]:
        if not url or not url.startswith("http"):
            return None
        url = url.split("#")[0]

        headers = {
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
            "User-Agent": random.choice(USER_AGENTS),
            "Referer": self.BASE_URL,
        }

        for _ in range(3):
            try:
                time.sleep(random.uniform(0.5, 1.5))
                resp = requests.get(url, headers=headers, timeout=30, verify=False)
                if resp.status_code == 200:
                    resp.encoding = "utf-8"
                    return resp.text
            except requests.RequestException:
                pass
        return None

    def scrape(self, url: str) -> Optional[dict]:
        html = self.fetch(url)
        if not html or len(html) < 500:
            return None

        soup = BeautifulSoup(html, "html.parser")
        title = self._extract(soup, self.TITLE_SELECTORS, 10)
        desc = self._extract(soup, self.DESC_SELECTORS, 20)

        if not title:
            return None

        return {"url": url, "title": title, "description": desc or title[:200]}

    def _extract(self, soup: BeautifulSoup, selectors: list, min_len: int) -> Optional[str]:
        for sel in selectors:
            for el in soup.select(sel):
                text = el.get("content") if el.name == "meta" else el.get_text()
                if text and len(text.strip()) >= min_len:
                    return text.strip()
        return None


class VnExpressScraper(BaseScraper):
    SOURCE = "VnExpress"
    BASE_URL = "https://vnexpress.net/"
    TITLE_SELECTORS = ["h1.title-detail", "h1[class*='title']", "h1"]
    DESC_SELECTORS = ["p.description", "meta[name='description']"]


class DanTriScraper(BaseScraper):
    SOURCE = "DanTri"
    BASE_URL = "https://dantri.com.vn/"
    TITLE_SELECTORS = ["h1.title-detail", "h1[class*='title']", "h1"]
    DESC_SELECTORS = ["meta[name='twitter:description']", "meta[name='description']"]


def get_scraper(url: str) -> Optional[BaseScraper]:
    if "vnexpress.net" in url:
        return VnExpressScraper()
    if "dantri.com.vn" in url:
        return DanTriScraper()
    return None