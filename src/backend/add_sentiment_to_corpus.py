"""Add sentiment labels to corpus data."""

import json
import argparse
from pathlib import Path
from tqdm import tqdm

from sentiment_analyzer import SentimentAnalyzer


def add_sentiment_to_corpus(
    input_path: str,
    output_path: str = None,
    text_col: str = "processed_title_description",
    batch_size: int = 32,
):

    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_sentiment{input_path.suffix}"
    else:
        output_path = Path(output_path)

    print(f"Loading corpus from {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} articles.")

    texts = [item.get(text_col, "") or "" for item in data]

    analyzer = SentimentAnalyzer()

    print(f"Analyzing sentiment for {len(texts)} texts...")
    all_results = []
    
    for i in tqdm(range(0, len(texts), batch_size), desc="Analyzing"):
        batch = texts[i : i + batch_size]
        results = analyzer.analyze_batch(batch, batch_size=batch_size)
        all_results.extend(results)

    # Add sentiment to data
    for item, result in zip(data, all_results):
        item["sentiment"] = result["sentiment"]
        item["sentiment_confidence"] = round(result["confidence"], 4)
        item["sentiment_scores"] = {k: round(v, 4) for k, v in result["scores"].items()}

    # Save
    print(f"Saving to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Print summary
    sentiment_counts = {}
    for item in data:
        s = item["sentiment"]
        sentiment_counts[s] = sentiment_counts.get(s, 0) + 1

    print("\nSentiment Distribution:")
    for sentiment, count in sorted(sentiment_counts.items()):
        pct = count / len(data) * 100
        print(f"  {sentiment}: {count} ({pct:.1f}%)")

    print(f"\nDone! Output saved to {output_path}")
    return data


def main():
    parser = argparse.ArgumentParser(description="Add sentiment labels to corpus")
    parser.add_argument("--input", "-i", required=True, help="Input corpus JSON path")
    parser.add_argument("--output", "-o", help="Output JSON path")
    parser.add_argument("--text-col", default="processed_title_description", help="Text column name")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    args = parser.parse_args()

    add_sentiment_to_corpus(
        input_path=args.input,
        output_path=args.output,
        text_col=args.text_col,
        batch_size=args.batch_size,
    )

if __name__ == "__main__":
    main()