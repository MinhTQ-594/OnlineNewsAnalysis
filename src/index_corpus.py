import json
import pandas as pd

from config import CORPUS_PATH
from vector_store import ArticleVectorStore


def main():
    print(f"Loading corpus from {CORPUS_PATH}...")
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} articles.")
    print(f"Columns: {df.columns.tolist()}")

    print("\nInitializing vector store...")
    store = ArticleVectorStore()

    print("\nIndexing articles...")
    store.index_articles(df, text_col="processed_title_description", batch_size=32)

    print("\nDone!")


if __name__ == "__main__":
    main()