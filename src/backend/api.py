import json
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import MODEL_DIR, STOPWORDS_PATH, CORPUS_PATH, MODELS, ENSEMBLE_MODEL_KEY
from pipeline import Pipeline
from vector_store import MultiModelVectorStore

app = FastAPI(title="News Article Retrieval API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline: Optional[Pipeline] = None
vector_store: Optional[MultiModelVectorStore] = None
corpus_data: Optional[dict] = None  # URL -> article data mapping


# Path to sentiment corpus
SENTIMENT_CORPUS_PATH = CORPUS_PATH.replace("sorted_processed_articles_corpus.json", "sentiment_corpus.json")


@app.on_event("startup")
async def startup():
    global pipeline, vector_store, corpus_data

    print("Loading pipeline...")
    pipeline = Pipeline(model_dir=MODEL_DIR, stopwords_path=STOPWORDS_PATH)

    print("Loading vector store...")
    vector_store = MultiModelVectorStore()

    print("Loading sentiment corpus...")
    try:
        with open(SENTIMENT_CORPUS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Create URL -> article mapping for quick lookup
        corpus_data = {item["url"]: item for item in data}
        print(f"Loaded {len(corpus_data)} articles with sentiment data.")
    except FileNotFoundError:
        print(f"Warning: Sentiment corpus not found at {SENTIMENT_CORPUS_PATH}")
        corpus_data = {}

    print("API ready!")


class SearchRequest(BaseModel):
    url: str
    model: str = "qwen3"
    top_k: int = 5
    sentiment_filter: Optional[str] = None  # "negative", "neutral", "positive", or None


class ArticleResult(BaseModel):
    url: str
    text: str
    score: float
    sentiment: Optional[str] = None
    sentiment_confidence: Optional[float] = None


class SearchResponse(BaseModel):
    input_url: str
    input_text: str
    model_used: str
    sentiment_filter: Optional[str]
    results: list[ArticleResult]
    total_before_filter: int


class IndexRequest(BaseModel):
    corpus_path: Optional[str] = None
    model: str = "qwen3"


class IndexResponse(BaseModel):
    status: str
    model: str
    count: int


class ModelInfo(BaseModel):
    key: str
    name: str


class ModelsResponse(BaseModel):
    models: list[ModelInfo]


class SentimentStatsResponse(BaseModel):
    total: int
    negative: int
    neutral: int
    positive: int


@app.get("/")
async def root():
    return {"message": "News Article Retrieval API", "status": "running"}


@app.get("/models", response_model=ModelsResponse)
async def get_models():
    if not vector_store:
        raise HTTPException(status_code=503, detail="Service not ready")

    return ModelsResponse(
        models=[ModelInfo(**m) for m in vector_store.get_available_models()]
    )


@app.get("/sentiments")
async def get_sentiments():
    """Get available sentiment filter options."""
    return {
        "sentiments": [
            {"key": "negative", "name": "Tiêu cực", "color": "#ef4444"},
            {"key": "neutral", "name": "Trung lập", "color": "#6b7280"},
            {"key": "positive", "name": "Tích cực", "color": "#22c55e"},
        ]
    }


@app.get("/sentiment-stats", response_model=SentimentStatsResponse)
async def get_sentiment_stats():
    """Get sentiment distribution statistics."""
    if not corpus_data:
        raise HTTPException(status_code=503, detail="Corpus not loaded")

    stats = {"negative": 0, "neutral": 0, "positive": 0}
    for article in corpus_data.values():
        sentiment = article.get("sentiment")
        if sentiment in stats:
            stats[sentiment] += 1

    return SentimentStatsResponse(
        total=len(corpus_data),
        **stats
    )


@app.post("/search", response_model=SearchResponse)
async def search_articles(request: SearchRequest):
    if not pipeline or not vector_store:
        raise HTTPException(status_code=503, detail="Service not ready")

    if not request.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")

    valid_models = list(MODELS.keys()) + [ENSEMBLE_MODEL_KEY]
    if request.model not in valid_models:
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose from: {valid_models}")

    # Validate sentiment filter
    valid_sentiments = [None, "negative", "neutral", "positive"]
    if request.sentiment_filter not in valid_sentiments:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sentiment filter. Choose from: {[s for s in valid_sentiments if s]}"
        )

    result = pipeline.run(request.url.strip())
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {request.url}")

    input_text = result["text"]
    
    # Get more results if filtering, to ensure we have enough after filter
    search_top_k = request.top_k * 3 if request.sentiment_filter else request.top_k
    related = vector_store.search(input_text, model_key=request.model, top_k=search_top_k)

    # Enrich results with sentiment data
    enriched_results = []
    for r in related:
        article_data = corpus_data.get(r["url"], {}) if corpus_data else {}
        enriched_results.append({
            "url": r["url"],
            "text": r["text"],
            "score": r["score"],
            "sentiment": article_data.get("sentiment"),
            "sentiment_confidence": article_data.get("sentiment_confidence"),
        })

    total_before_filter = len(enriched_results)

    # Apply sentiment filter if specified
    if request.sentiment_filter:
        enriched_results = [
            r for r in enriched_results
            if r["sentiment"] == request.sentiment_filter
        ]

    # Limit to top_k
    enriched_results = enriched_results[:request.top_k]

    model_name = MODELS[request.model]["name"] if request.model != ENSEMBLE_MODEL_KEY else "Ensemble"

    return SearchResponse(
        input_url=request.url,
        input_text=input_text,
        model_used=model_name,
        sentiment_filter=request.sentiment_filter,
        results=[ArticleResult(**r) for r in enriched_results],
        total_before_filter=total_before_filter,
    )


@app.post("/index", response_model=IndexResponse)
async def index_corpus(request: IndexRequest):
    if not vector_store:
        raise HTTPException(status_code=503, detail="Service not ready")

    if request.model not in MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose from: {list(MODELS.keys())}")

    corpus_path = request.corpus_path or CORPUS_PATH

    try:
        with open(corpus_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)

        store = vector_store._get_store(request.model)
        store.index_articles(df, text_col="processed_title_description", batch_size=64)

        return IndexResponse(status="success", model=request.model, count=len(df))

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Corpus file not found: {corpus_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "pipeline": pipeline is not None,
        "vector_store": vector_store is not None,
        "corpus_loaded": corpus_data is not None and len(corpus_data) > 0,
        "corpus_size": len(corpus_data) if corpus_data else 0,
    }