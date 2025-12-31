from typing import Optional

from config import MODEL_DIR, STOPWORDS_PATH, MODELS, ENSEMBLE_MODEL_KEY
from pipeline import Pipeline
from vector_store import MultiModelVectorStore


class ArticleRetriever:
    def __init__(self, model_dir: str = MODEL_DIR, stopwords_path: Optional[str] = STOPWORDS_PATH):
        self.pipeline = Pipeline(model_dir=model_dir, stopwords_path=stopwords_path)
        self.vector_store = MultiModelVectorStore()

    def index_corpus(self, df, model_key: str, text_col: str = "processed_title_description"):
        store = self.vector_store._get_store(model_key)
        store.index_articles(df, text_col=text_col)

    def find_related(self, url: str, model_key: str = "qwen3", top_k: int = 5) -> dict:
        result = self.pipeline.run(url)
        if not result:
            return {"error": f"Failed to scrape URL: {url}"}

        input_text = result["text"]
        related = self.vector_store.search(input_text, model_key=model_key, top_k=top_k)

        model_name = MODELS[model_key]["name"] if model_key != ENSEMBLE_MODEL_KEY else "Ensemble"

        return {
            "input_url": url,
            "input_text": input_text,
            "model_used": model_name,
            "related_articles": related,
        }

    def get_available_models(self) -> list[dict]:
        return self.vector_store.get_available_models()