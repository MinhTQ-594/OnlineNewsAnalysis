import json
import argparse
import pandas as pd

from config import CORPUS_PATH, MODELS
from vector_store import ArticleVectorStore, TfidfVectorStore 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=list(MODELS.keys()) + ["all"], default="all")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    print(f"Loading corpus from {CORPUS_PATH}...")
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} articles.")

    models_to_index = list(MODELS.keys()) if args.model == "all" else [args.model]

    for model_key in models_to_index:
        print(f"\n{'='*50}")
        print(f"Indexing with model: {MODELS[model_key]['name']}")
        print(f"{'='*50}")

        model_config = MODELS[model_key]
        if model_config["type"] == "tfidf":
            store = TfidfVectorStore(model_key=model_key)
        else:
            store = ArticleVectorStore(model_key=model_key)

        store.index_articles(df, text_col="processed_title_description", batch_size=args.batch_size)

    print("\nDone!")


if __name__ == "__main__":
    main()