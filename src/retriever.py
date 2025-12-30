from typing import Optional

from config import MODEL_DIR, STOPWORDS_PATH
from pipeline import Pipeline
from vector_store import ArticleVectorStore


class ArticleRetriever:
    def __init__(self, model_dir: str = MODEL_DIR, stopwords_path: Optional[str] = STOPWORDS_PATH):
        self.pipeline = Pipeline(model_dir=model_dir, stopwords_path=stopwords_path)
        self.vector_store = ArticleVectorStore()

    def index_corpus(self, df, text_col: str = "processed_title_description"):
        self.vector_store.index_articles(df, text_col=text_col)

    def find_related(self, url: str, top_k: int = 5) -> dict:
        result = self.pipeline.run(url)
        if not result:
            return {"error": f"Failed to scrape URL: {url}"}

        input_text = result["text"]
        related = self.vector_store.search(input_text, top_k=top_k)

        return {
            "input_url": url,
            "input_text": input_text,
            "related_articles": related,
        }