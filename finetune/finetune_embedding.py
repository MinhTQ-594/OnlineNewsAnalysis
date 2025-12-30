import torch
import transformers
import traceback
import numpy as np 
import json
from datetime import datetime
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from sentence_transformers.losses import MultipleNegativesRankingLoss
from sentence_transformers.similarity_functions import SimilarityFunction
from sentence_transformers.trainer import SentenceTransformerTrainer
from sentence_transformers.training_args import (
    BatchSamplers,
    MultiDatasetBatchSamplers,
    SentenceTransformerTrainingArguments,
)
import logging
from sentence_transformers.evaluation import InformationRetrievalEvaluator

train_dataset_path = '/mnt/disk1/aiotlab/huync/project-ds/OnlineNewsAnalysis/finetune/ft_data/finetune_train_triplets.json'

train_dataset = load_dataset("json", data_files = train_dataset_path)

logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)

model_name = "Qwen/Qwen3-Embedding-0.6B"
num_epochs = 2
batch_size = 128  
max_seq_length = 256

output_dir = (
    "output/finetune_news-" + model_name.replace("/", "-") + "-" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
)

model = SentenceTransformer(model_name)
model.max_seq_length = max_seq_length
logging.info(model)

train_loss  = MultipleNegativesRankingLoss(model)

test_dataset_corpus_path = '/mnt/disk1/aiotlab/huync/project-ds/OnlineNewsAnalysis/finetune/ft_data/test_sorted_processed_articles_corpus.json'
train_dataset_corpus_path = '/mnt/disk1/aiotlab/huync/project-ds/OnlineNewsAnalysis/finetune/ft_data/train_sorted_processed_articles_corpus.json'
queries = {}
corpus = {}
relevant_docs = {}

# Load ALL articles into corpus (both train and test)
with open(train_dataset_corpus_path, 'r') as f:
    train_data = json.load(f)

with open(test_dataset_corpus_path, 'r') as f:
    test_data = json.load(f)

# Build complete corpus from all articles
all_data = train_data + test_data
for item in all_data:
    article_id = str(item['article_index'])
    corpus[article_id] = item['processed_title_description']

# Use only test articles as queries
for item in test_data:
    query_id = str(item['article_index'])
    queries[query_id] = item['processed_title_description']
    relevant_docs[query_id] = set(str(idx) for idx in item['related_index'])

dev_evaluator = InformationRetrievalEvaluator(
    queries=queries,
    corpus=corpus,
    relevant_docs=relevant_docs,
)

args = SentenceTransformerTrainingArguments(
    # Required parameter:
    output_dir=output_dir,
    # Optional training parameters:
    num_train_epochs=num_epochs,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=64,  # Very small for 12GB GPU
    warmup_ratio=0.1,
    bf16=True,  # Set to True if you have a GPU that supports BF16
    batch_sampler=BatchSamplers.NO_DUPLICATES,  # MultipleNegativesRankingLoss benefits from no duplicate samples in a batch
    gradient_accumulation_steps=8,  # Simulate batch size 128 (16*8) with minimal VRAM
    gradient_checkpointing=True,  # Trade compute for memory
    logging_first_step=True,
    # Optional tracking/debugging parameters:
    eval_strategy="steps",
    eval_steps=10,  # Reduced from 1000 for more frequent checkpoints
    save_strategy="steps",
    save_steps=500,
    save_total_limit=5,
    logging_steps=10,  # More frequent logging
    run_name="finetune_news",  # Will be used in W&B if `wandb` is installed
    report_to="wandb",  # Explicitly enable wandb logging (default if wandb is installed)
    # Memory optimization
    dataloader_num_workers=2,  # Reduce CPU memory usage
    dataloader_pin_memory=False,  # Reduce memory transfer overhead
    fp16_full_eval=False,  # Use BF16 for eval too
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    loss=train_loss,
    evaluator=dev_evaluator,
)
trainer.train()

final_output_dir = f"{output_dir}/final"
model.save(final_output_dir)

# 9. (Optional) save the model to the Hugging Face Hub!
# It is recommended to run `huggingface-cli login` to log into your Hugging Face account first
# model_name = model_name if "/" not in model_name else model_name.split("/")[-1]
# try:
#     model.push_to_hub(f"{model_name}-finetune-news-final")
# except Exception:
#     logging.error(
#         f"Error uploading model to the Hugging Face Hub:\n{traceback.format_exc()}To upload it manually, you can run "
#         f"`huggingface-cli login`, followed by loading the model using `model = SentenceTransformer({final_output_dir!r})` "
#         f"and saving it using `model.push_to_hub('{model_name}-finetune-news')`."
#     )