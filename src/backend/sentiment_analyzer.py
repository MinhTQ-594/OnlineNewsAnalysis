"""Vietnamese Sentiment Analyzer using PhoBERT."""

from enum import Enum
from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class Sentiment(str, Enum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class SentimentAnalyzer:

    DEFAULT_MODEL = "wonrax/phobert-base-vietnamese-sentiment"

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        self.model_name = model_name or self.DEFAULT_MODEL
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        print(f"Loading sentiment model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()

        # Label mapping (wonrax model: 0=negative, 1=positive, 2=neutral)
        self.id2label = {0: Sentiment.NEGATIVE, 1: Sentiment.POSITIVE, 2: Sentiment.NEUTRAL}
        print(f"Sentiment analyzer ready on {self.device}")

    def analyze(self, text: str) -> dict:
        """Analyze sentiment of a single text.
        
        Returns:
            dict with keys: sentiment, confidence, scores
        """
        if not text or not text.strip():
            return {"sentiment": Sentiment.NEUTRAL, "confidence": 0.0, "scores": {}}

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding=True,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0]

        scores = {self.id2label[i].value: float(probs[i]) for i in range(len(probs))}
        pred_id = torch.argmax(probs).item()
        sentiment = self.id2label[pred_id]

        return {
            "sentiment": sentiment.value,
            "confidence": float(probs[pred_id]),
            "scores": scores,
        }

    def analyze_batch(self, texts: list[str], batch_size: int = 32) -> list[dict]:
        """Analyze sentiment for a batch of texts."""
        results = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch = [t if t and t.strip() else "" for t in batch]

            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                truncation=True,
                max_length=256,
                padding=True,
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)

            for j, prob in enumerate(probs):
                scores = {self.id2label[k].value: float(prob[k]) for k in range(len(prob))}
                pred_id = torch.argmax(prob).item()
                sentiment = self.id2label[pred_id]

                results.append({
                    "sentiment": sentiment.value,
                    "confidence": float(prob[pred_id]),
                    "scores": scores,
                })

        return results


_analyzer: Optional[SentimentAnalyzer] = None


def get_analyzer() -> SentimentAnalyzer:
    """Get or create singleton sentiment analyzer."""
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer


def analyze_sentiment(text: str) -> dict:
    """Convenience function to analyze single text."""
    return get_analyzer().analyze(text)


def analyze_sentiment_batch(texts: list[str], batch_size: int = 32) -> list[dict]:
    """Convenience function to analyze batch of texts."""
    return get_analyzer().analyze_batch(texts, batch_size)