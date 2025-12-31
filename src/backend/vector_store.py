from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import pickle
from config import MODELS, QDRANT_HOST, QDRANT_PORT, ENSEMBLE_MODEL_KEY

class TfidfVectorStore:  
    def __init__(
        self,
        model_key: str,
        qdrant_host: str = QDRANT_HOST,
        qdrant_port: int = QDRANT_PORT,
    ):
        model_config = MODELS[model_key]
        with open(model_config["pkl_path"], "rb") as f:
            self.vectorizer = pickle.load(f)
        self.collection_name = model_config["collection"]
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.vector_size = len(self.vectorizer.get_feature_names_out())

    def create_collection(self, recreate: bool = False):
        collections = [c.name for c in self.client.get_collections().collections]

        if self.collection_name in collections:
            if recreate:
                self.client.delete_collection(self.collection_name)
            else:
                print(f"Collection '{self.collection_name}' already exists.")
                return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
        )
        print(f"Created collection '{self.collection_name}'.")

    def index_articles(self, df, text_col: str = "processed_title_description", batch_size: int = 32):
        self.create_collection(recreate=True)

        texts = df[text_col].tolist()
        urls = df["url"].tolist() if "url" in df.columns else [f"article_{i}" for i in range(len(df))]

        total = len(texts)
        for i in range(0, total, batch_size):
            batch_texts = texts[i : i + batch_size]
            batch_urls = urls[i : i + batch_size]

            embeddings = self.vectorizer.transform(batch_texts).toarray()

            points = [
                PointStruct(
                    id=i + j,
                    vector=emb.tolist(),
                    payload={"url": url, "text": text},
                )
                for j, (emb, url, text) in enumerate(zip(embeddings, batch_urls, batch_texts))
            ]

            self.client.upsert(collection_name=self.collection_name, points=points)
            print(f"Indexed {min(i + batch_size, total)}/{total}")

        print(f"Done. Total indexed: {total}")

    def search(self, query_text: str, top_k: int = 5) -> list[dict]:
        query_embedding = self.vectorizer.transform([query_text]).toarray().squeeze()

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding.tolist(),
            limit=top_k,
        )

        return [
            {
                "url": hit.payload.get("url", ""),
                "text": hit.payload.get("text", ""),
                "score": hit.score,
            }
            for hit in results.points
        ]

class ArticleVectorStore:
    def __init__(
        self,
        model_key: str,
        qdrant_host: str = QDRANT_HOST,
        qdrant_port: int = QDRANT_PORT,
    ):
        model_config = MODELS[model_key]
        self.model = SentenceTransformer(model_config["model_path"])
        self.collection_name = model_config["collection"]
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.vector_size = self.model.get_sentence_embedding_dimension()

    def create_collection(self, recreate: bool = False):
        collections = [c.name for c in self.client.get_collections().collections]

        if self.collection_name in collections:
            if recreate:
                self.client.delete_collection(self.collection_name)
            else:
                print(f"Collection '{self.collection_name}' already exists.")
                return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
        )
        print(f"Created collection '{self.collection_name}'.")

    def index_articles(self, df, text_col: str = "processed_title_description", batch_size: int = 32):
        self.create_collection(recreate=True)

        texts = df[text_col].tolist()
        urls = df["url"].tolist() if "url" in df.columns else [f"article_{i}" for i in range(len(df))]

        total = len(texts)
        for i in range(0, total, batch_size):
            batch_texts = texts[i : i + batch_size]
            batch_urls = urls[i : i + batch_size]

            embeddings = self.model.encode_document(batch_texts)

            points = [
                PointStruct(
                    id=i + j,
                    vector=emb.tolist(),
                    payload={"url": url, "text": text},
                )
                for j, (emb, url, text) in enumerate(zip(embeddings, batch_urls, batch_texts))
            ]

            self.client.upsert(collection_name=self.collection_name, points=points)
            print(f"Indexed {min(i + batch_size, total)}/{total}")

        print(f"Done. Total indexed: {total}")

    def search(self, query_text: str, top_k: int = 5) -> list[dict]:
        query_embedding = self.model.encode_query([query_text])[0]

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding.tolist(),
            limit=top_k,
        )

        return [
            {
                "url": hit.payload.get("url", ""),
                "text": hit.payload.get("text", ""),
                "score": hit.score,
            }
            for hit in results.points
        ]

class MultiModelVectorStore:
    def __init__(
        self,
        qdrant_host: str = QDRANT_HOST,
        qdrant_port: int = QDRANT_PORT,
        rrf_k: int = 60,
    ):
        self.stores: dict = {}
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.rrf_k = rrf_k

    def _get_store(self, model_key: str):  # <-- SỬA: trả về đúng loại store
        if model_key not in self.stores:
            model_config = MODELS[model_key]
            if model_config["type"] == "tfidf":
                self.stores[model_key] = TfidfVectorStore(
                    model_key=model_key,
                    qdrant_host=self.qdrant_host,
                    qdrant_port=self.qdrant_port,
                )
            else:
                self.stores[model_key] = ArticleVectorStore(
                    model_key=model_key,
                    qdrant_host=self.qdrant_host,
                    qdrant_port=self.qdrant_port,
                )
        return self.stores[model_key]

    def _ensemble_search(self, query_text: str, top_k: int = 5) -> list[dict]:
        all_results = {}

        for model_key in MODELS: 
            store = self._get_store(model_key)
            results = store.search(query_text, top_k=top_k * 2)

            for rank, item in enumerate(results):
                url = item["url"]
                rrf_score = 1.0 / (self.rrf_k + rank + 1)

                if url not in all_results:
                    all_results[url] = {"url": url, "text": item["text"], "rrf_score": 0.0}
                all_results[url]["rrf_score"] += rrf_score

        sorted_results = sorted(all_results.values(), key=lambda x: x["rrf_score"], reverse=True)

        return [
            {"url": r["url"], "text": r["text"], "score": r["rrf_score"]}
            for r in sorted_results[:top_k]
        ]

    def search(self, query_text: str, model_key: str, top_k: int = 5) -> list[dict]:
        if model_key == ENSEMBLE_MODEL_KEY:
            return self._ensemble_search(query_text, top_k=top_k)
        return self._get_store(model_key).search(query_text, top_k=top_k)

    def get_available_models(self) -> list[dict]:
        models = [{"key": key, "name": config["name"]} for key, config in MODELS.items()]
        models.append({"key": ENSEMBLE_MODEL_KEY, "name": "Ensemble"})
        return models