import json
from sentence_transformers import InputExample

train_json_path = '/mnt/disk1/huync/project-ds/OnlineNewsAnalysis/finetune/datasets/train_sorted_processed_articles_corpus.json'
test_json_path = '/mnt/disk1/huync/project-ds/OnlineNewsAnalysis/finetune/datasets/test_sorted_processed_articles_corpus.json'

with open(train_json_path, 'r') as f:
    train_data = json.load(f)
print(f"Number of training samples: {len(train_data)}")

with open(test_json_path, 'r') as f:
    test_data = json.load(f)
print(f"Number of testing samples: {len(test_data)}")

def preprocess_for_finetuning(data_path, output_path):
    """ Convert to triplet format: (anchor, positive, negative)"""

    with open(data_path, 'r') as f:
        data = json.load(f)
    
    examples = []
    for item in data:
        anchor_text = item['processed_title_description']
        anchor_idx = item['article_index']

        for pos_idx in item['related_index']:
            pos_article = next((x for x in data if x['article_index'] == pos_idx), None)
            if pos_article:
                examples.append({
                    'anchor': anchor_text,
                    'positive': pos_article['processed_title_description'],
                })
    with open(output_path, 'w') as f:
        json.dump(examples, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(examples)} triplet examples to {output_path}")

preprocess_for_finetuning(train_json_path, './datasets/finetune_train_triplets.json')
preprocess_for_finetuning(test_json_path, './datasets/finetune_test_triplets.json')

    