import json
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import MODEL_DIR, STOPWORDS_PATH, CORPUS_PATH
from pipeline import Pipeline
from vector_store import ArticleVectorStore

app = FastAPI(title="News Article Retrieval API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline: Optional[Pipeline] = None
vector_store: Optional[ArticleVectorStore] = None


@app.on_event("startup")
async def startup():
    global pipeline, vector_store

    print("Loading pipeline...")
    pipeline = Pipeline(model_dir=MODEL_DIR, stopwords_path=STOPWORDS_PATH)

    print("Loading vector store...")
    vector_store = ArticleVectorStore()

    print("API ready!")


class SearchRequest(BaseModel):
    url: str
    top_k: int = 5


class ArticleResult(BaseModel):
    url: str
    text: str
    score: float


class SearchResponse(BaseModel):
    input_url: str
    input_text: str
    results: list[ArticleResult]


class IndexRequest(BaseModel):
    corpus_path: Optional[str] = None


class IndexResponse(BaseModel):
    status: str
    count: int


@app.get("/")
async def root():
    return {"message": "News Article Retrieval API", "status": "running"}


@app.post("/search", response_model=SearchResponse)
async def search_articles(request: SearchRequest):
    if not pipeline or not vector_store:
        raise HTTPException(status_code=503, detail="Service not ready")

    if not request.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")

    result = pipeline.run(request.url.strip())
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {request.url}")

    input_text = result["text"]
    related = vector_store.search(input_text, top_k=request.top_k)

    return SearchResponse(
        input_url=request.url,
        input_text=input_text,
        results=[
            ArticleResult(url=r["url"], text=r["text"], score=r["score"])
            for r in related
        ],
    )


@app.post("/index", response_model=IndexResponse)
async def index_corpus(request: IndexRequest):
    if not vector_store:
        raise HTTPException(status_code=503, detail="Service not ready")

    corpus_path = request.corpus_path or CORPUS_PATH

    try:
        with open(corpus_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)

        vector_store.index_articles(df, text_col="processed_title_description", batch_size=64)

        return IndexResponse(status="success", count=len(df))

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
    }