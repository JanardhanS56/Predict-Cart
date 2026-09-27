from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
import os

app = FastAPI(title="PredictCart Beta - Recommendation API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for in-memory data
users_df = None
products_df = None
recommendations_map = {}

def load_data():
    global users_df, products_df, recommendations_map
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    # Load users and products
    users_path = os.path.join(data_dir, 'raw', 'users.csv')
    products_path = os.path.join(data_dir, 'raw', 'products.csv')
    
    if os.path.exists(users_path):
        users_df = pd.read_csv(users_path).fillna("")
    if os.path.exists(products_path):
        products_df = pd.read_csv(products_path).fillna("")
        
    # Load predictions and payload to map users to products
    payload_path = os.path.join(data_dir, 'processed', 'kumo_payload.json')
    pred_path = os.path.join(data_dir, 'processed', 'prediction_response.json')
    
    if os.path.exists(payload_path) and os.path.exists(pred_path):
        with open(payload_path, 'r') as f:
            payload = json.load(f)
        with open(pred_path, 'r') as f:
            preds = json.load(f)
            
        predict_rows = payload.get('predict', {}).get('instance_table', {}).get('rows', [])
        predictions = preds.get('predictions', [])
        
        # Build mapping
        for row, pred in zip(predict_rows, predictions):
            user_id = row[2] # user_id is index 2 in predict_instances based on columns ["instance_id", "anchor_time", "user_id", "product_id", "label"]
            product_id = row[3] # product_id is index 3
            prob = pred.get('probabilities', {}).get('true', 0.0)
            
            if user_id not in recommendations_map:
                recommendations_map[user_id] = []
            recommendations_map[user_id].append({"product_id": product_id, "score": prob})
            
        # Sort recommendations by score descending
        for u in recommendations_map:
            recommendations_map[u] = sorted(recommendations_map[u], key=lambda x: x['score'], reverse=True)

# Load data on startup
@app.on_event("startup")
async def startup_event():
    load_data()

@app.get("/api/users")
async def get_users():
    """Returns a list of 20 mock users from the dataset."""
    if users_df is None:
        return []
    
    # Let's prioritize users who actually have recommendations mapped
    users_with_recs = list(recommendations_map.keys())
    
    if users_with_recs:
        selected_users = users_df[users_df['user_id'].isin(users_with_recs)].head(20)
    else:
        selected_users = users_df.head(20)
        
    return selected_users.to_dict(orient="records")

@app.get("/api/products")
async def get_products():
    """Returns the product catalog."""
    if products_df is None:
        return []
    return products_df.to_dict(orient="records")

class RecommendationRequest(BaseModel):
    user_id: str

@app.post("/api/recommendations")
async def get_recommendations(req: RecommendationRequest):
    """Accepts a user_id. Returns a list of 'Next Best Offer' products based on Kumo predictions."""
    try:
        uid = int(req.user_id)
    except ValueError:
        uid = req.user_id
        
    if uid not in recommendations_map:
        return {"user_id": uid, "recommendations": []}
        
    recs = recommendations_map[uid]
    
    # Enrich with product details
    enriched_recs = []
    if products_df is not None:
        for r in recs:
            p_info = products_df[products_df['product_id'] == r['product_id']]
            if not p_info.empty:
                p_dict = p_info.iloc[0].to_dict()
                p_dict['recommendation_score'] = r['score']
                enriched_recs.append(p_dict)
    
    return {"user_id": uid, "recommendations": enriched_recs}
