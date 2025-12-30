import os
import json
import pandas as pd
import gradio as gr
from retriever import ArticleRetriever

MODEL_DIR = r"C:\Users\Chien\Documents\VnCoreNLP"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 
STOPWORDS_PATH = os.path.join(BASE_DIR, "data", "stopwords_processed.txt")
CORPUS_PATH = os.path.join(BASE_DIR, "data", "sorted_processed_articles_corpus.json")

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Initialize
retriever = None
def init_retriever():
    global retriever
    print("Loading retriever...")
    retriever = ArticleRetriever(
        model_dir=MODEL_DIR,
        stopwords_path=STOPWORDS_PATH,
        qdrant_host=QDRANT_HOST,
        qdrant_port=QDRANT_PORT,
    )
    print("Retriever loaded.")


def index_corpus():
    """Index corpus into Qdrant."""
    print(f"Loading corpus from {CORPUS_PATH}...")
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} articles.")

    print("Indexing into Qdrant...")
    retriever.index_corpus(df)
    return f"Indexed {len(df)} articles into Qdrant."


def find_related_articles(url: str, top_k: int = 5):
    """Find related articles for input URL."""
    if not url.strip():
        return "Please enter a URL.", ""

    if retriever is None:
        return "Retriever not initialized.", ""

    result = retriever.find_related(url.strip(), top_k=int(top_k))

    if "error" in result:
        return f"{result['error']}", ""

    # Format output
    input_info = f"**Input URL:** {result['input_url']}\n\n**Processed Text:**\n{result['input_text'][:300]}..."

    related_output = "##Related Articles\n\n"
    for i, article in enumerate(result["related_articles"], 1):
        score_pct = article["score"] * 100
        related_output += f"### {i}. (Score: {score_pct:.1f}%)\n"
        related_output += f"**URL:** [{article['url']}]({article['url']})\n\n"
        related_output += f"**Text:** {article['text'][:200]}...\n\n---\n\n"

    return input_info, related_output


# Gradio UI
def create_ui():
    with gr.Blocks(title="Related Article Finder", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 📰 Related Vietnamese News Article Finder")
        gr.Markdown("Enter a VnExpress or DanTri article URL to find related articles.")

        with gr.Row():
            with gr.Column(scale=2):
                url_input = gr.Textbox(
                    label="Article URL",
                    placeholder="https://vnexpress.net/...",
                    lines=1,
                )
                top_k_slider = gr.Slider(
                    minimum=1, maximum=10, value=5, step=1, label="Number of results"
                )
                with gr.Row():
                    search_btn = gr.Button("🔍 Find Related", variant="primary")
                    index_btn = gr.Button("📥 Re-index Corpus")

        with gr.Row():
            with gr.Column():
                input_info = gr.Markdown(label="Input Article")
            with gr.Column():
                results_output = gr.Markdown(label="Related Articles")

        index_status = gr.Textbox(label="Index Status", interactive=False)

        # Events
        search_btn.click(
            fn=find_related_articles,
            inputs=[url_input, top_k_slider],
            outputs=[input_info, results_output],
        )
        index_btn.click(fn=index_corpus, outputs=[index_status])

    return app


if __name__ == "__main__":
    init_retriever()
    app = create_ui()
    app.launch(server_name="0.0.0.0", server_port=7860)