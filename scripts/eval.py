import json
import os
from collections import defaultdict
import statistics

def run_eval():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    payload_path = os.path.join(base_dir, 'data', 'processed', 'kumo_payload.json')
    pred_path = os.path.join(base_dir, 'data', 'processed', 'prediction_response.json')
    
    labels_path = os.path.join(base_dir, 'data', 'processed', 'predict_labels.json')
    if not os.path.exists(payload_path) or not os.path.exists(pred_path) or not os.path.exists(labels_path):
        print("Required files not found. Have you run prepare_payload.py and predict.py?")
        return
        
    print("Loading predictions and payload...")
    with open(payload_path, 'r') as f:
        payload = json.load(f)
    with open(pred_path, 'r') as f:
        preds = json.load(f)
    with open(labels_path, 'r') as f:
        labels = json.load(f)
        
    predict_rows = payload.get('predict', {}).get('instance_table', {}).get('rows', [])
    predictions = preds.get('predictions', [])
    
    user_scores = defaultdict(list)
    user_true_labels = defaultdict(list)
    all_scores = []
    
    # Instance format: ["instance_id", "anchor_time", "user_id", "product_id"]
    for i, (row, pred) in enumerate(zip(predict_rows, predictions)):
        user_id = row[2]
        product_id = row[3]
        label = labels[i] # Ground truth label we set (True or False)
        prob = pred.get('probabilities', {}).get('true', 0.0)
        
        all_scores.append(prob)
        user_scores[user_id].append({"product_id": product_id, "score": prob, "true_label": label})
        
    # Stats
    high_score_count = sum(1 for s in all_scores if s > 0.5)
    print(f"\n--- Prediction Distribution ---")
    print(f"Total Predictions: {len(all_scores)}")
    print(f"Average True Probability: {statistics.mean(all_scores):.4f}")
    print(f"Median True Probability: {statistics.median(all_scores):.4f}")
    print(f"Max True Probability: {max(all_scores):.4f}")
    print(f"Min True Probability: {min(all_scores):.4f}")
    print(f"Scores > 0.5: {high_score_count} ({(high_score_count/len(all_scores))*100:.2f}%)")
    
    # Hit Rate Calculation
    # For each user, if their top scored product is actually label == True, it's a hit!
    hits = 0
    total_users = len(user_scores)
    
    for uid, items in user_scores.items():
        # Sort by score descending
        sorted_items = sorted(items, key=lambda x: x['score'], reverse=True)
        top_item = sorted_items[0]
        
        if top_item['true_label'] == True:
            hits += 1
            
    hit_rate = (hits / total_users) * 100 if total_users > 0 else 0
    
    print(f"\n--- Evaluation Results ---")
    print(f"Total Evaluated Users: {total_users}")
    print(f"Hits (Top recommended product was actually interacted with): {hits}")
    print(f"Mock Hit Rate (HR@1): {hit_rate:.2f}%\n")
    print("Evaluation completed successfully.")

if __name__ == "__main__":
    run_eval()
