from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT


class ArticleVectorStore:
    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
        collection_name: str = COLLECTION_NAME,
        qdrant_host: str = QDRANT_HOST,
        qdrant_port: int = QDRANT_PORT,
    ):
        self.model = SentenceTransformer(model_name)
        self.collection_name = collection_name
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