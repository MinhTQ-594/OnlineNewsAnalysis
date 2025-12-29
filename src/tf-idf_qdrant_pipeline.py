import json
import argparse
from typing import List, Dict, Any
from tqdm import tqdm

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

def load_corpus(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = []
    payloads = []

    for idx, article in enumerate(data):
        text_field = article.get("processed_title_description", "")
        if not text_field:
            continue

        texts.append(text_field)

        payloads.append({
            "article_index": article.get("article_index", idx),
            "url": article.get("url", ""),
            "processed_title_description": text_field,
            "related_index": article.get("related_index", [])
        })

    print(f"Loaded {len(texts)} documents")
    return texts, payloads

# TF-IDF Vectorization
def build_tfidf(
    texts: List[str],
    max_features: int,
    min_df: int,
    max_df: float
):
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=max_features,
        min_df=min_df,
        max_df=max_df,
        norm="l2"   
    )

    tfidf_matrix = vectorizer.fit_transform(texts)
    print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
    return tfidf_matrix, vectorizer

# Push vectors to Qdrant 
def push_to_qdrant(
    tfidf_matrix,
    payloads: List[Dict[str, Any]],
    collection_name: str,
    qdrant_url: str,
    qdrant_port: int,
    batch_size: int
):
    vector_size = tfidf_matrix.shape[1]
    print(f"Vector size: {vector_size}")

    client = QdrantClient(host=qdrant_url, port=qdrant_port, timeout=120)

    try:
        client.get_collection(collection_name)
        print(f"Collection '{collection_name}' exists. Deleting...")
        client.delete_collection(collection_name)
    except Exception:
        pass


    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )

    print(f"Created collection '{collection_name}'")

    points = []
    for i in tqdm(range(tfidf_matrix.shape[0]), desc="Uploading TF-IDF vectors"):
        vector = tfidf_matrix[i].toarray().squeeze().tolist()

        points.append(
            PointStruct(
                id=payloads[i]["article_index"],
                vector=vector,
                payload=payloads[i]
            )
        )

        if len(points) == batch_size:
            client.upsert(collection_name=collection_name, points=points)
            points = []

    if points:
        client.upsert(collection_name=collection_name, points=points)

    info = client.get_collection(collection_name)
    print(f"Uploaded {info.points_count} points to '{collection_name}'")


# Search 
def search_similar_articles(
    query_text: str,
    vectorizer: TfidfVectorizer,
    collection_name: str,
    qdrant_url: str,
    qdrant_port: int,
    top_k: int
):
    client = QdrantClient(host=qdrant_url, port=qdrant_port)

    query_vec = vectorizer.transform([query_text]).toarray().squeeze().tolist()

    hits = client.search(
        collection_name=collection_name,
        query_vector=query_vec,
        limit=top_k
    )

    results = []
    for hit in hits:
        results.append({
            "article_index": hit.payload["article_index"],
            "url": hit.payload["url"],
            "processed_title_description": hit.payload["processed_title_description"],
            "related_index": hit.payload["related_index"],
            "similarity_score": hit.score
        })

    return results


# Main
def main(args):
    texts, payloads = load_corpus(args.json_path)

    tfidf_matrix, vectorizer = build_tfidf(
        texts,
        max_features=args.max_features,
        min_df=args.min_df,
        max_df=args.max_df
    )

    push_to_qdrant(
        tfidf_matrix=tfidf_matrix,
        payloads=payloads,
        collection_name=args.collection_name,
        qdrant_url=args.qdrant_url,
        qdrant_port=args.qdrant_port,
        batch_size=args.batch_size
    )

    # # sanity check
    # print("\nExample search result:")
    # results = search_similar_articles(
    #     query_text=texts[0],
    #     vectorizer=vectorizer,
    #     collection_name=args.collection_name,
    #     qdrant_url=args.qdrant_url,
    #     qdrant_port=args.qdrant_port,
    #     top_k=5
    # )

    # for r in results:
    #     print(r)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="TF-IDF + Qdrant pipeline (metadata identical to dense pipeline)"
    )

    parser.add_argument("--json_path", type=str, required=True)
    parser.add_argument("--collection_name", type=str, required=True)
    parser.add_argument("--qdrant_url", type=str, default="localhost")
    parser.add_argument("--qdrant_port", type=int, default=6333)
    parser.add_argument("--batch_size", type=int, default=1)

    parser.add_argument("--max_features", type=int, default=20000)
    parser.add_argument("--min_df", type=int, default=3)
    parser.add_argument("--max_df", type=float, default=0.9)

    args = parser.parse_args()
    main(args)