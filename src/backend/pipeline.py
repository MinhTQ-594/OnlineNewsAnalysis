from typing import Optional

from scraper import get_scraper
from processor import TextProcessor


class Pipeline:
    def __init__(self, model_dir: str, stopwords_path: Optional[str] = None):
        self.processor = TextProcessor(model_dir, stopwords_path)

    def run(self, url: str) -> Optional[dict]:
        scraper = get_scraper(url)
        if not scraper:
            return None

        data = scraper.scrape(url)
        if not data:
            return None

        combined = f"{data['title']}. {data['description']}"
        processed = self.processor.process(combined)

        return {"url": url, "text": processed}