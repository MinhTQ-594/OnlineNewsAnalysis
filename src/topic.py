"""Topic extractor from Vietnamese news URLs."""

import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from scraper import VnExpressScraper
from tqdm import tqdm
tqdm.pandas()

class TopicExtractor:
    """Extract topic/category from news article URLs."""
    # DanTri topic mapping (from URL)
    VNEXPRESS_TOPICS = {
        "ThoiSu": "Thời sự",
        "TheGioi": "Thế giới",
        "KinhDoanh": "Kinh doanh",
        "KhoaHocCongNghe": "Khoa học công nghệ",
        "GocNhin": "Góc nhìn",
        "BatDongSan": "Bất động sản",
        "SucKhoe": "Sức khỏe",
        "TheThao": "Thể thao",
        "GiaiTri": "Giải trí",
        "PhapLuat": "Pháp luật",
        "GiaoDuc": "Giáo dục",
        "DoiSong": "Đời sống",
        "OtoXeMay": "Xe",
        "DuLich": "Du lịch",
        "YKien": "Ý kiến",
        "TamSu": "Tâm sự",
        "ThuGian": "Thư giãn"
    }

    DANTRI_TOPICS = {
        "the-gioi": "Thế giới",
        "thoi-su": "Thời sự",
        "phap-luat": "Pháp luật",
        "suc-khoe": "Sức khỏe",
        "doi-song": "Đời sống",
        "du-lich": "Du lịch",
        "kinh-doanh": "Kinh doanh",
        "bat-dong-san": "Bất động sản",
        "the-thao": "Thể thao",
        "giai-tri": "Giải trí",
        "giao-duc": "Giáo dục",
        "o-to-xe-may": "Xe",
        "noi-vu": "Nội vụ",
        "nhan-ai": "Nhân ái",
        "cong-nghe": "Công nghệ",
        "viec-lam": "Việc làm",
        "tinh-yeu": "Tình yêu",
        "khoa-hoc": "Khoa học"
    }

    def __init__(self):
        self.vnexpress_scraper = VnExpressScraper()

    def extract(self, url: str) -> dict:
        """
        Extract topic from URL. 
        Returns:
            {"topic": str, "topic_slug": str, "source": str}
        """
        if not url:
            return {"topic": "Khác", "topic_slug": "other", "source": "unknown"}

        url_lower = url.lower()

        if "dantri.com.vn" in url_lower:
            return self._extract_dantri(url)

        if "vnexpress.net" in url_lower:
            return self._extract_vnexpress(url)

        return {"topic": "Khác", "topic_slug": "other", "source": "unknown"}

    def _extract_dantri(self, url: str) -> dict:
        """Extract topic from DanTri URL (topic is in URL path)."""
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")

        if path_parts:
            slug = path_parts[0]
            topic = self.DANTRI_TOPICS.get(slug, slug.replace("-", " ").title())
            return {"topic": topic, "topic_slug": slug, "source": "DanTri"}

        return {"topic": "Khác", "topic_slug": "other", "source": "DanTri"}

    def _extract_vnexpress(self, url: str) -> dict:
        """Extract topic from VnExpress using data-source attribute in <body>."""
        html = self.vnexpress_scraper.fetch(url)
        if not html:
            return {"topic": "Khác", "topic_slug": "other", "source": "VnExpress"}

        soup = BeautifulSoup(html, "html.parser")

        # Get data-source from <body>
        body = soup.find("body")
        if not body:
            return {"topic": "Khác", "topic_slug": "other", "source": "VnExpress"}

        data_source = body.get("data-source", "")

        if not data_source:
            return {"topic": "Khác", "topic_slug": "other", "source": "VnExpress"}

        match = re.search(r"Detail-([A-Z][a-zA-Z]+)", data_source)
        if match:
            topic_key = match.group(1)
            topic = self.VNEXPRESS_TOPICS.get(topic_key, topic_key)
            slug = self._camel_to_slug(topic_key)
            return {"topic": topic, "topic_slug": slug, "source": "VnExpress"}

        return {"topic": "Khác", "topic_slug": "other", "source": "VnExpress"}

    def _camel_to_slug(self, text: str) -> str:
        slug = re.sub(r'(?<!^)(?=[A-Z])', '-', text).lower()
        return slug

import pandas as pd
import json

extractor = TopicExtractor()

with open(r"C:\Users\Chien\Documents\Project VDT\DS\data\sorted_processed_articles_corpus.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

df['topic'] = df['url'].progress_apply(lambda url: extractor.extract(url))
df['topic_name'] = df['topic'].progress_apply(lambda x: x['topic'])
df['topic_slug'] = df['topic'].progress_apply(lambda x: x['topic_slug'])
df['topic_source'] = df['topic'].progress_apply(lambda x: x['source'])

df.to_json(r"C:\Users\Chien\Documents\Project VDT\DS\data\new_data.json", orient="records", force_ascii=False, indent=2)
