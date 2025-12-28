from sentence_transformers import SentenceTransformer
import json 
import torch
import argparse
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import tqdm
from typing import List, Dict, Any
import numpy as np
from dotenv import load_dotenv

load_dotenv()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_embedding_model(model_name: str = "google/embeddinggemma-300m"):
    """
    Load and return a SentenceTransformer embedding model.

    Args:
        model_name (str): The name of the pre-trained model to load.

    Returns:
        SentenceTransformer: The loaded embedding model.
    """
    model = SentenceTransformer(model_name)
    return model
def embed_text(text: str, model: SentenceTransformer):
    """
    Embed a single piece of text using the provided embedding model.

    Args:
        text (str): The text to embed.
        model (SentenceTransformer): The embedding model to use.

    Returns:
        numpy.ndarray: The embedding vector for the input text.
    """
    model = model.to(device)
    embedding = model.encode(text)
    return embedding

def embed_corpus(json_path: str, model: SentenceTransformer) -> List[Dict[str, Any]]:
    """
    Embed a corpus of text data from a JSON file using the provided embedding model.
    Returns data structured for Qdrant insertion.

    Args:
        json_path (str): The path to the JSON file containing the corpus.
        model (SentenceTransformer): The embedding model to use.

    Returns:
        List[Dict]: List of dictionaries with 'id', 'vector', and 'payload' for each article.
    """
    qdrant_points = []
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data = data[:10]
    print(f"Embedding {len(data)} articles...")
    
    for idx, article in tqdm.tqdm(enumerate(data), desc= "Embedding articles..."):
        text_field = article.get('processed_title_description', '')
        
        if not text_field:
            print(f"Warning: Article {article.get('article_index', idx)} has empty text field. Skipping.")
            continue
        
        # Generate embedding
        embedding = embed_text(text_field, model)
        
        # Structure for Qdrant
        point = {
            'id': article.get('article_index', idx),
            'vector': embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
            'payload': {
                'article_index': article.get('article_index', idx),
                'url': article.get('url', ''),
                'processed_title_description': text_field,
                'related_index': article.get('related_index', [])
            }
        }
        
        qdrant_points.append(point)
        
        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1}/{len(data)} articles...")
    
    print(f"Successfully embedded {len(qdrant_points)} articles.")
    return qdrant_points


def push_to_qdrant(
    json_path: str,
    collection_name: str,
    model: SentenceTransformer = None,
    model_name: str = "google/embeddinggemma-300m",
    qdrant_url: str = "localhost",
    qdrant_port: int = 6333,
    vector_size: int = None,
    distance_metric: Distance = Distance.COSINE,
    batch_size: int = 100
) -> None:
    """
    Main function to embed a JSON corpus and push it to Qdrant.
    Can be imported and used by other modules.

    Args:
        json_path (str): Path to the JSON file containing articles.
        collection_name (str): Name of the Qdrant collection to create/use.
        model (SentenceTransformer, optional): Pre-loaded embedding model. If None, will load from model_name.
        model_name (str): Name of the model to load if model is None.
        qdrant_url (str): Qdrant server URL (default: "localhost").
        qdrant_port (int): Qdrant server port (default: 6333).
        vector_size (int, optional): Size of the embedding vectors. Auto-detected if None.
        distance_metric (Distance): Distance metric for similarity search (default: COSINE).
        batch_size (int): Number of points to upload in each batch (default: 100).

    Returns:
        None

    Example:
        >>> from embedding_model import push_to_qdrant
        >>> push_to_qdrant(
        ...     json_path="data/processed_articles_corpus.json",
        ...     collection_name="news_articles",
        ...     qdrant_url="localhost"
        ... )
    """
    # Load model if not provided
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    if model is None:
        print(f"Loading embedding model: {model_name}")
        model = get_embedding_model(model_name)
    
    # Embed corpus
    print(f"Embedding corpus from {json_path}...")
    qdrant_points = embed_corpus(json_path, model)
    
    if not qdrant_points:
        print("No points to upload. Exiting.")
        return
    
    # Auto-detect vector size if not provided
    if vector_size is None:
        vector_size = len(qdrant_points[0]['vector'])
        print(f"Auto-detected vector size: {vector_size}")
    
    # Initialize Qdrant client
    print(f"Connecting to Qdrant at {qdrant_url}:{qdrant_port}...")
    client = QdrantClient(host=qdrant_url, port=qdrant_port)
    
    # Create collection
    try:
        collections = client.get_collections().collections
        collection_exists = any(col.name == collection_name for col in collections)
        
        if collection_exists:
            print(f"Collection '{collection_name}' already exists. Deleting and recreating...")
            client.delete_collection(collection_name)
        
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=distance_metric)
        )
        print(f"Created collection '{collection_name}' with vector size {vector_size}")
    except Exception as e:
        print(f"Error creating collection: {e}")
        raise
    
    # Upload points in batches
    print(f"Uploading {len(qdrant_points)} points to Qdrant in batches of {batch_size}...")
    for i in range(0, len(qdrant_points), batch_size):
        batch = qdrant_points[i:i + batch_size]
        
        points = [
            PointStruct(
                id=point['id'],
                vector=point['vector'],
                payload=point['payload']
            )
            for point in batch
        ]
        
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        print(f"Uploaded batch {i // batch_size + 1}/{(len(qdrant_points) + batch_size - 1) // batch_size}")
    
    # Verify upload
    collection_info = client.get_collection(collection_name)
    print(f"\n✓ Successfully uploaded {collection_info.points_count} points to collection '{collection_name}'")
    print(f"✓ Vector dimension: {collection_info.config.params.vectors.size}")
    print(f"✓ Distance metric: {collection_info.config.params.vectors.distance}")


def search_similar_articles(
    query_text: str,
    collection_name: str,
    model: SentenceTransformer = None,
    model_name: str = "google/embeddinggemma-300m",
    qdrant_url: str = "localhost",
    qdrant_port: int = 6333,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for similar articles in Qdrant based on query text.

    Args:
        query_text (str): The text query to search for.
        collection_name (str): Name of the Qdrant collection to search.
        model (SentenceTransformer, optional): Pre-loaded embedding model.
        model_name (str): Name of the model to load if model is None.
        qdrant_url (str): Qdrant server URL.
        qdrant_port (int): Qdrant server port.
        top_k (int): Number of similar articles to return.

    Returns:
        List[Dict]: List of search results with scores and payloads.
    """
    # Load model if not provided
    if model is None:
        model = get_embedding_model(model_name)
    
    # Embed query
    query_vector = embed_text(query_text, model)
    
    # Search in Qdrant
    client = QdrantClient(host=qdrant_url, port=qdrant_port)
    
    search_results = client.search(
        collection_name=collection_name,
        query_vector=query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector,
        limit=top_k
    )
    
    # Format results
    results = []
    for hit in search_results:
        results.append({
            'article_index': hit.payload['article_index'],
            'url': hit.payload['url'],
            'processed_title_description': hit.payload['processed_title_description'],
            'related_index': hit.payload['related_index'],
            'similarity_score': hit.score
        })
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed a JSON corpus and push to Qdrant.")
    parser.add_argument('--json_path', type=str, default= '/mnt/disk1/huync/project-ds/OnlineNewsAnalysis/data/processed_articles_corpus.json',required=False, help='Path to the JSON file containing articles.')
    parser.add_argument('--collection_name', type=str, required=True, help='Name of the Qdrant collection to create/use.')
    parser.add_argument('--model_name', type=str, default="Qwen/Qwen3-Embedding-0.6B", help='Name of the embedding model to use.')
    parser.add_argument('--qdrant_url', type=str, default="localhost", help='Qdrant server URL.')
    parser.add_argument('--qdrant_port', type=int, default=6333, help='Qdrant server port.')
    parser.add_argument('--vector_size', type=int, default=None, help='Size of the embedding vectors. Auto-detected if not provided.')
    parser.add_argument('--distance_metric', type=str, default="COSINE", help='Distance metric for similarity search (COSINE, EUCLIDIAN, DOT).')
    parser.add_argument('--batch_size', type=int, default=5, help='Number of points to upload in each batch.')
    
    args = parser.parse_args()
    
    distance_enum = Distance[args.distance_metric.upper()]

    push_to_qdrant(
        json_path=args.json_path,
        collection_name=args.collection_name,
        model_name=args.model_name,
        qdrant_url=args.qdrant_url,
        qdrant_port=args.qdrant_port,
        vector_size=args.vector_size,
        distance_metric=distance_enum,
        batch_size=args.batch_size
    )