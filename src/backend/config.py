import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

MODEL_DIR = r"C:\Users\Chien\Documents\VnCoreNLP"
STOPWORDS_PATH = os.path.join(BASE_DIR, "data", "stopwords_processed.txt")
CORPUS_PATH = os.path.join(BASE_DIR, "data", "sorted_processed_articles_corpus.json")
TFIDF_PKL_PATH = os.path.join(BASE_DIR, "src", "backend", "tfidf_vectorizer.pkl")

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

MODELS = {
    "qwen3": {
        "name": "Qwen3",
        "model_path": "b00l26/Qwen3-Embedding-0.6B-finetune-news-final",
        "collection": "news_articles_qwen3",
        "type": "sentence_transformer", 
    },
    "embeddinggemma": {
        "name": "EmbeddingGemma",
        "model_path": "b00l26/embeddinggemma-300m-finetune-news-finalize",
        "collection": "news_articles_gemma",
        "type": "sentence_transformer", 
    },
        "dangvantuan": {
        "name": "dangvantuan",
        "model_path": "b00l26/vietnam-embedding-finetune-news",
        "collection": "news_articles_dangvantuan",
        "type": "sentence_transformer", 
    },
    "tfidf": {  
        "name": "TF-IDF",
        "pkl_path": TFIDF_PKL_PATH,
        "collection": "news_articles_tfidf",
        "type": "tfidf",
    },
}

ENSEMBLE_MODEL_KEY = "ensemble"