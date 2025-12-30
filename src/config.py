import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

MODEL_DIR = r"C:\Users\Chien\Documents\VnCoreNLP"
STOPWORDS_PATH = os.path.join(BASE_DIR, "data", "stopwords_processed.txt")
CORPUS_PATH = os.path.join(BASE_DIR, "data", "sorted_processed_articles_corpus.json")

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "news_articles"

EMBEDDING_MODEL = "b00l26/Qwen3-Embedding-0.6B-finetune-news-final"