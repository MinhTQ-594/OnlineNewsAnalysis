import json
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def load_articles(json_path):
    """Load articles from JSON file and filter out null entries."""
    print(f"Loading data from: {str(json_path)}")
    with open(str(json_path), "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        # Filter out null entries
        data = [article for article in raw_data if article is not None]
        print(f"Loaded {len(data)} valid articles (filtered out {len(raw_data) - len(data)} null entries)")
    return data

def create_article_index(data):
    """Create a mapping from URL to article index and full metadata."""
    idx = {}
    article_metadata = []
    
    for index, article in enumerate(data, 1):
        src_url = article.get('url', '')
        idx[src_url] = index
        
        # Store comprehensive metadata for each article
        metadata = {
            'index': index,
            'url': src_url,
            'source': article.get('Source', ''),
            'date': article.get('Date', ''),
            'time': article.get('Time', ''),
            'author': article.get('Author', ''),
            'title': article.get('Title', ''),
            'description': article.get('Description', ''),
            'tags': article.get('Tags', ''),
            'keywords': ', '.join(article.get('Key_words', [])) if article.get('Key_words') else '',
            'num_related_links': len(article.get('Related_link', []))
        }
        article_metadata.append(metadata)
    
    return idx, article_metadata

def create_related_links_mapping(data, idx):
    """Create a mapping of article URLs to their related article indices."""
    relevant = defaultdict(list)
    related_details = []
    
    for article in data:
        src_url = article.get('url', '')
        src_index = idx.get(src_url)
        relevant_urls = article.get('Related_link', [])
        
        for rel_url in relevant_urls:
            # Skip ad links
            if not rel_url.startswith("https://adclick"):
                if rel_url in idx:
                    rel_index = idx[rel_url]
                    relevant[src_url].append(rel_index)
                    
                    # Store detailed relationship for CSV
                    related_details.append({
                        'source_index': src_index,
                        'source_url': src_url,
                        'related_index': rel_index,
                        'related_url': rel_url
                    })
    
    return relevant, related_details

def save_index_to_json(idx, article_metadata, relevant, output_path):
    """Save the complete index to a JSON file."""
    index_data = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'total_articles': len(idx),
            'articles_with_relations': len(relevant)
        },
        'url_to_index': idx,
        'articles': article_metadata,
        'related_articles': {url: indices for url, indices in relevant.items()}
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved JSON index to: {output_path}")

def save_articles_to_csv(article_metadata, output_path):
    """Save article metadata to CSV."""
    if not article_metadata:
        print("No articles to save.")
        return
    
    fieldnames = article_metadata[0].keys()
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(article_metadata)
    
    print(f"Saved articles metadata to: {output_path}")

def save_related_links_to_csv(related_details, output_path):
    """Save related links mapping to CSV."""
    if not related_details:
        print("No related links to save.")
        return
    
    fieldnames = ['source_index', 'source_url', 'related_index', 'related_url']
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(related_details)
    
    print(f"Saved related links mapping to: {output_path}")

def main():
    # Setup paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    json_path = data_dir / "data_2025-12-16.json"
    
    # Load articles
    data = load_articles(json_path)
    
    # Create indices
    idx, article_metadata = create_article_index(data)
    relevant, related_details = create_related_links_mapping(data, idx)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"INDEXING SUMMARY")
    print(f"{'='*60}")
    print(f"Total articles indexed: {len(idx)}")
    print(f"Articles with related links: {len(relevant)}")
    print(f"Total related link relationships: {len(related_details)}")
    
    # Show sample data
    print(f"\n{'='*60}")
    print(f"SAMPLE DATA (First 5 articles)")
    print(f"{'='*60}")
    for i, article in enumerate(article_metadata[:5], 1):
        print(f"\n{i}. [{article['index']}] {article['title']}")
        print(f"   URL: {article['url'][:80]}...")
        print(f"   Date: {article['date']} | Tags: {article['tags']}")
        if article['url'] in relevant:
            print(f"   Related articles: {relevant[article['url']]}")
    
    # Save to files
    print(f"\n{'='*60}")
    print(f"SAVING INDEX FILES")
    print(f"{'='*60}")
    
    # Save comprehensive JSON index
    json_output = data_dir / "news_index.json"
    save_index_to_json(idx, article_metadata, relevant, json_output)
    
    # Save CSV files
    articles_csv = data_dir / "news_articles_index.csv"
    save_articles_to_csv(article_metadata, articles_csv)
    
    related_csv = data_dir / "news_related_links.csv"
    save_related_links_to_csv(related_details, related_csv)
    
    print(f"\n{'='*60}")
    print(f"INDEXING COMPLETE!")
    print(f"{'='*60}")
    print(f"✓ JSON index: {json_output}")
    print(f"✓ Articles CSV: {articles_csv}")
    print(f"✓ Related links CSV: {related_csv}")

if __name__ == "__main__":
    main()