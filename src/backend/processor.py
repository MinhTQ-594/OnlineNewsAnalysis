"""Vietnamese text processor."""

import re
from typing import Optional


class TextProcessor:
    """Process Vietnamese text: segment + remove stopwords."""

    def __init__(self, model_dir: str, stopwords_path: Optional[str] = None):
        import py_vncorenlp
        self.segmenter = py_vncorenlp.VnCoreNLP(save_dir=model_dir)

        self.stopword_pattern = None
        if stopwords_path:
            with open(stopwords_path, "r", encoding="utf-8") as f:
                words = [w.strip() for w in f if w.strip()]
            if words:
                self.stopword_pattern = re.compile(
                    r"\b(" + "|".join(map(re.escape, words)) + r")\b",
                    re.IGNORECASE
                )

    def process(self, text: str) -> str:
        """Segment, remove stopwords, normalize."""
        if not text:
            return ""

        segments = self.segmenter.word_segment(text)
        result = " ".join(segments)

        if self.stopword_pattern:
            result = self.stopword_pattern.sub("", result)

        result = re.sub(r"\s+", " ", result).strip()
        result = re.sub(r'["\']', "", result)
        return result