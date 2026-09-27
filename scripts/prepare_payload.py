import pandas as pd
import json
import random
from datetime import datetime, timezone
import os

def main():
    random.seed(42)
    # 1. Load data
    users = pd.read_csv('data/raw/users.csv')
    products = pd.read_csv('data/raw/products.csv')
    sessions = pd.read_csv('data/raw/sessions.csv').rename(columns={'referrer_source': 'referrer_channel'})
    interactions = pd.read_csv('data/raw/interactions.csv').rename(columns={'interaction_type': 'action_type'})
    purchases = pd.read_csv('data/raw/purchases.csv').rename(columns={'order_date': 'timestamp'})
    reviews = pd.read_csv('data/raw/reviews.csv').rename(columns={'review_date': 'timestamp'})

    # Convert timestamps
    sessions['start_time'] = pd.to_datetime(sessions['start_time'])
    interactions['timestamp'] = pd.to_datetime(interactions['timestamp'])
    purchases['timestamp'] = pd.to_datetime(purchases['timestamp'])
    reviews['timestamp'] = pd.to_datetime(reviews['timestamp'])

    # String mapping for IDs to ints (since stype=ID usually prefers integers or string, we'll map to ints for speed)
    def build_mapping(series):
        unique_vals = series.dropna().unique()
        return {val: i for i, val in enumerate(unique_vals)}

    def apply_mapping(df, col, mapping):
        if col in df.columns:
            df[col] = df[col].map(mapping)

    user_map = build_mapping(users['user_id'])
    product_map = build_mapping(products['product_id'])
    session_map = build_mapping(sessions['session_id'])
    interaction_map = build_mapping(interactions['interaction_id'])
    purchase_map = build_mapping(purchases['purchase_id'])
    review_map = build_mapping(reviews['review_id'])

    for df in [users, products, interactions, purchases, reviews, sessions]:
        apply_mapping(df, 'user_id', user_map)
        apply_mapping(df, 'product_id', product_map)
        apply_mapping(df, 'session_id', session_map)
        apply_mapping(df, 'interaction_id', interaction_map)
        apply_mapping(df, 'purchase_id', purchase_map)
        apply_mapping(df, 'review_id', review_map)
    
    # 2. Time Split
    all_timestamps = pd.concat([
        interactions['timestamp'],
        purchases['timestamp'],
        reviews['timestamp']
    ]).dropna()
    
    split_time = all_timestamps.quantile(0.8)
    anchor_iso = pd.to_datetime(split_time).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    context_interactions = interactions[interactions['timestamp'] <= split_time]
    future_interactions = interactions[interactions['timestamp'] > split_time]
    context_purchases = purchases[purchases['timestamp'] <= split_time]
    context_reviews = reviews[reviews['timestamp'] <= split_time]

    # Generate prediction target candidates
    # We want to predict if a user will interact with a product in the future.
    future_pairs = set(zip(future_interactions['user_id'], future_interactions['product_id']))
    context_pairs = set(zip(context_interactions['user_id'], context_interactions['product_id']))
    
    all_product_ids = list(products['product_id'].dropna().unique())
    all_user_ids = list(users['user_id'].dropna().unique())
    
    # Select active users for instances
    active_users = context_interactions['user_id'].unique()
    
    # 3. Build instances
    context_instances = []
    predict_instances = []
    inst_id = 0
    
    # Let's create say 100 predict instances (some true, mostly false)
    # For predict, we just define the instance row. Kumo will score all products if we don't give a target, but we are doing binary classification.
    # Wait, the prompt said: "predicts which products each user will engage with... We frame this as Binary Classification"
    for u, p in list(future_pairs)[:150]:
        predict_instances.append({
            "instance_id": inst_id,
            "anchor_time": anchor_iso,
            "user_id": int(u),
            "product_id": int(p),
            "label": True
        })
        inst_id += 1
        
        # 2 negatives per true
        neg_count = 0
        while neg_count < 2:
            neg_p = random.choice(all_product_ids)
            if (u, neg_p) not in future_pairs and (u, neg_p) not in context_pairs:
                predict_instances.append({
                    "instance_id": inst_id,
                    "anchor_time": anchor_iso,
                    "user_id": int(u),
                    "product_id": int(neg_p),
                    "label": False
                })
                inst_id += 1
                neg_count += 1
                
    # Also we need some context instances to train? The Kumo API accepts 'context' which is training data.
    for u, p in list(context_pairs)[:200]:
        context_instances.append({
            "instance_id": inst_id,
            "anchor_time": anchor_iso,
            "user_id": int(u),
            "product_id": int(p),
            "label": True
        })
        inst_id += 1
        neg_count = 0
        while neg_count < 2:
            neg_p = random.choice(all_product_ids)
            if (u, neg_p) not in context_pairs:
                context_instances.append({
                    "instance_id": inst_id,
                    "anchor_time": anchor_iso,
                    "user_id": int(u),
                    "product_id": int(neg_p),
                    "label": False
                })
                inst_id += 1
                neg_count += 1
                
    # Function to extract ego graph for a list of instances
    def extract_ego_graphs(instances_list):
        ego_users = []
        ego_products = []
        ego_sessions = []
        ego_interactions = []
        ego_purchases = []
        ego_reviews = []
        
        # Pre-index for faster lookup
        users_idx = users.set_index('user_id')
        products_idx = products.set_index('product_id')
        sess_idx = sessions.groupby('user_id')
        inter_idx = context_interactions.groupby('session_id')
        purch_idx = context_purchases.groupby('session_id')
        rev_idx = context_reviews.groupby('user_id')
        
        for inst in instances_list:
            iid = inst['instance_id']
            u = inst['user_id']
            p_target = inst['product_id']
            
            # User
            if u in users_idx.index:
                row = users_idx.loc[u]
                ego_users.append([iid, u, row['age'], row['gender'], row['country'], row['income_level'], row['loyalty_tier'], row['preferred_category']])
                
            # Sessions
            user_sessions = sess_idx.get_group(u) if u in sess_idx.groups else pd.DataFrame()
            if not user_sessions.empty:
                for _, s_row in user_sessions.iterrows():
                    sid = s_row['session_id']
                    ego_sessions.append([iid, sid, u, s_row['start_time'], s_row['device_type'], s_row['referrer_channel'], s_row['is_converted']])
                    
                    # Interactions
                    if sid in inter_idx.groups:
                        for _, i_row in inter_idx.get_group(sid).iterrows():
                            ego_interactions.append([iid, i_row['interaction_id'], sid, i_row['product_id'], i_row['timestamp'], i_row['action_type'], i_row['dwell_time_ms']])
                            
                    # Purchases
                    if sid in purch_idx.groups:
                        for _, p_row in purch_idx.get_group(sid).iterrows():
                            # Note: purchases schema expects: ["instance_id", "purchase_id", "session_id", "product_id", "timestamp", "quantity", "unit_price", "total_amount"]
                            ego_purchases.append([iid, p_row['purchase_id'], sid, p_row['product_id'], p_row['timestamp'], p_row['quantity'], p_row['unit_price'], p_row['total_amount']])
            
            # Reviews
            user_reviews = rev_idx.get_group(u) if u in rev_idx.groups else pd.DataFrame()
            if not user_reviews.empty:
                for _, r_row in user_reviews.iterrows():
                    # Note: reviews schema expects: ["instance_id", "review_id", "user_id", "product_id", "timestamp", "rating", "review_text"]
                    ego_reviews.append([iid, r_row['review_id'], u, r_row['product_id'], r_row['timestamp'], r_row['rating'], r_row['review_text']])
            
            # Products
            # We must include the target product
            prod_ids = {p_target}
            # And any product interacted/purchased/reviewed by user
            if not user_sessions.empty:
                for sid in user_sessions['session_id']:
                    if sid in inter_idx.groups:
                        prod_ids.update(inter_idx.get_group(sid)['product_id'].unique())
                    if sid in purch_idx.groups:
                        prod_ids.update(purch_idx.get_group(sid)['product_id'].unique())
            if not user_reviews.empty:
                prod_ids.update(user_reviews['product_id'].unique())
            
            for pid in prod_ids:
                if pid in products_idx.index:
                    p_row = products_idx.loc[pid]
                    ego_products.append([iid, pid, p_row['category'], p_row['brand'], p_row['price'], p_row['rating_avg'], p_row['review_count'], p_row['stock_quantity'], p_row.get('is_active', True)])
                    
        return ego_users, ego_products, ego_sessions, ego_interactions, ego_purchases, ego_reviews

    # Convert datatypes safely
    users['age'] = users['age'].astype(float)
    users['gender'] = users['gender'].astype(str)
    users['country'] = users['country'].astype(str)
    users['income_level'] = users['income_level'].astype(str)
    users['loyalty_tier'] = users['loyalty_tier'].astype(str)
    users['preferred_category'] = users['preferred_category'].astype(str)
    products['price'] = products['price'].astype(float)
    products['rating_avg'] = products['rating_avg'].astype(float)
    products['review_count'] = products['review_count'].astype(float)
    products['stock_quantity'] = products['stock_quantity'].astype(float)
    sessions['is_converted'] = sessions['is_converted'].astype(str)
    context_interactions['dwell_time_ms'] = context_interactions['dwell_time_ms'].astype(float)
    context_purchases['quantity'] = context_purchases['quantity'].astype(float)
    context_purchases['unit_price'] = context_purchases['unit_price'].astype(float)
    context_purchases['total_amount'] = context_purchases['total_amount'].astype(float)
    context_reviews['rating'] = context_reviews['rating'].astype(float)

    c_users, c_prods, c_sess, c_inters, c_purch, c_revs = extract_ego_graphs(context_instances)
    p_users, p_prods, p_sess, p_inters, p_purch, p_revs = extract_ego_graphs(predict_instances)
    
    # Format times in the arrays
    def format_time(val):
        if pd.isna(val): return None
        try:
            ts = pd.to_datetime(val)
            return ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            return None

    def clean_rows(rows, time_cols):
        clean = []
        for r in rows:
            new_r = []
            for i, val in enumerate(r):
                if i in time_cols:
                    new_r.append(format_time(val))
                elif pd.isna(val):
                    new_r.append(None)
                elif isinstance(val, str):
                    new_r.append(val[:1000])
                else:
                    new_r.append(val)
            clean.append(new_r)
        return clean
    
    # Column definitions based on extract_ego_graphs order
    u_cols = ["instance_id", "user_id", "age", "gender", "country", "income_level", "loyalty_tier", "preferred_category"]
    p_cols = ["instance_id", "product_id", "category", "brand", "price", "rating_avg", "review_count", "stock_quantity", "is_active"]
    s_cols = ["instance_id", "session_id", "user_id", "start_time", "device_type", "referrer_channel", "is_converted"]
    i_cols = ["instance_id", "interaction_id", "session_id", "product_id", "timestamp", "action_type", "dwell_time_ms"]
    pu_cols = ["instance_id", "purchase_id", "session_id", "product_id", "timestamp", "quantity", "unit_price", "total_amount"]
    r_cols = ["instance_id", "review_id", "user_id", "product_id", "timestamp", "rating", "review_text"]
    
    c_users = clean_rows(c_users, [])
    p_users = clean_rows(p_users, [])
    c_prods = clean_rows(c_prods, [])
    p_prods = clean_rows(p_prods, [])
    c_sess = clean_rows(c_sess, [3])
    p_sess = clean_rows(p_sess, [3])
    c_inters = clean_rows(c_inters, [4])
    p_inters = clean_rows(p_inters, [4])
    c_purch = clean_rows(c_purch, [4])
    p_purch = clean_rows(p_purch, [4])
    c_revs = clean_rows(c_revs, [4])
    p_revs = clean_rows(p_revs, [4])
    
    c_inst_rows = [[r["instance_id"], r["anchor_time"], r["user_id"], r["product_id"], r["label"]] for r in context_instances]
    p_inst_rows = [[r["instance_id"], r["anchor_time"], r["user_id"], r["product_id"]] for r in predict_instances]
    
    import os
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/predict_labels.json', 'w') as f:
        json.dump([r["label"] for r in predict_instances], f)
    
    # 4. Construct payload
    payload = {
        "model": "kumo-relational",
        "task": {
            "kind": "binary_classification",
            "target": {
                "column_name": "label",
                "dtype": "bool",
                "classes": ["false", "true"],
                "positive_class": "true"
            },
            "entity_table_names": ["users"],
            "anchor_time_column": "anchor_time"
        },
        "schema": {
            "instance_table": {
                "columns": {
                    "instance_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                    "anchor_time": {"dtype": "timestamp[us]", "stype": "timestamp", "nullable": False},
                    "user_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                    "product_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                    "label": {"dtype": "bool", "stype": "categorical", "nullable": True}
                },
                "primary_key": "instance_id"
            },
            "related_tables": {
                "users": {
                    "columns": {
                        "instance_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "user_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "age": {"dtype": "float64", "stype": "numerical"},
                        "gender": {"dtype": "string", "stype": "categorical"},
                        "country": {"dtype": "string", "stype": "categorical"},
                        "income_level": {"dtype": "string", "stype": "categorical"},
                        "loyalty_tier": {"dtype": "string", "stype": "categorical"},
                        "preferred_category": {"dtype": "string", "stype": "categorical"}
                    },
                    "primary_key": ["instance_id", "user_id"]
                },
                "products": {
                    "columns": {
                        "instance_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "product_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "category": {"dtype": "string", "stype": "categorical"},
                        "brand": {"dtype": "string", "stype": "categorical"},
                        "price": {"dtype": "float64", "stype": "numerical"},
                        "rating_avg": {"dtype": "float64", "stype": "numerical"},
                        "review_count": {"dtype": "float64", "stype": "numerical"},
                        "stock_quantity": {"dtype": "float64", "stype": "numerical"},
                        "is_active": {"dtype": "bool", "stype": "categorical"}
                    },
                    "primary_key": ["instance_id", "product_id"]
                },
                "sessions": {
                    "columns": {
                        "instance_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "session_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "user_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "start_time": {"dtype": "timestamp[us]", "stype": "timestamp"},
                        "device_type": {"dtype": "string", "stype": "categorical"},
                        "referrer_channel": {"dtype": "string", "stype": "categorical"},
                        "is_converted": {"dtype": "string", "stype": "categorical"}
                    },
                    "primary_key": ["instance_id", "session_id"]
                },
                "interactions": {
                    "columns": {
                        "instance_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "interaction_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "session_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "product_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "timestamp": {"dtype": "timestamp[us]", "stype": "timestamp"},
                        "action_type": {"dtype": "string", "stype": "categorical"},
                        "dwell_time_ms": {"dtype": "float64", "stype": "numerical"}
                    },
                    "primary_key": ["instance_id", "interaction_id"]
                },
                "purchases": {
                    "columns": {
                        "instance_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "purchase_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "session_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "product_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "timestamp": {"dtype": "timestamp[us]", "stype": "timestamp"},
                        "quantity": {"dtype": "float64", "stype": "numerical"},
                        "unit_price": {"dtype": "float64", "stype": "numerical"},
                        "total_amount": {"dtype": "float64", "stype": "numerical"}
                    },
                    "primary_key": ["instance_id", "purchase_id"]
                },
                "reviews": {
                    "columns": {
                        "instance_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "review_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "user_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "product_id": {"dtype": "int64", "stype": "ID", "nullable": False},
                        "timestamp": {"dtype": "timestamp[us]", "stype": "timestamp"},
                        "rating": {"dtype": "float64", "stype": "numerical"},
                        "review_text": {"dtype": "string", "stype": "text"}
                    },
                    "primary_key": ["instance_id", "review_id"]
                }
            },
            "relationships": [
                {
                    "source_columns": ["instance_id", "user_id"],
                    "target_table": "users",
                    "target_columns": ["instance_id", "user_id"]
                },
                {
                    "source_columns": ["instance_id", "product_id"],
                    "target_table": "products",
                    "target_columns": ["instance_id", "product_id"]
                },
                {
                    "source_columns": ["instance_id", "user_id"],
                    "source_table": "sessions",
                    "target_table": "users",
                    "target_columns": ["instance_id", "user_id"]
                },
                {
                    "source_columns": ["instance_id", "session_id"],
                    "source_table": "interactions",
                    "target_table": "sessions",
                    "target_columns": ["instance_id", "session_id"]
                },
                {
                    "source_columns": ["instance_id", "product_id"],
                    "source_table": "interactions",
                    "target_table": "products",
                    "target_columns": ["instance_id", "product_id"]
                },
                {
                    "source_columns": ["instance_id", "session_id"],
                    "source_table": "purchases",
                    "target_table": "sessions",
                    "target_columns": ["instance_id", "session_id"]
                },
                {
                    "source_columns": ["instance_id", "product_id"],
                    "source_table": "purchases",
                    "target_table": "products",
                    "target_columns": ["instance_id", "product_id"]
                },
                {
                    "source_columns": ["instance_id", "user_id"],
                    "source_table": "reviews",
                    "target_table": "users",
                    "target_columns": ["instance_id", "user_id"]
                },
                {
                    "source_columns": ["instance_id", "product_id"],
                    "source_table": "reviews",
                    "target_table": "products",
                    "target_columns": ["instance_id", "product_id"]
                }
            ]
        },
        "context": {
            "instance_table": {
                "format": "arrays",
                "columns": ["instance_id", "anchor_time", "user_id", "product_id", "label"],
                "rows": c_inst_rows
            },
            "related_tables": {
                "users": {"format": "arrays", "columns": u_cols, "rows": c_users},
                "products": {"format": "arrays", "columns": p_cols, "rows": c_prods},
                "sessions": {"format": "arrays", "columns": s_cols, "rows": c_sess},
                "interactions": {"format": "arrays", "columns": i_cols, "rows": c_inters},
                "purchases": {"format": "arrays", "columns": pu_cols, "rows": c_purch},
                "reviews": {"format": "arrays", "columns": r_cols, "rows": c_revs}
            }
        },
        "predict": {
            "instance_table": {
                "format": "arrays",
                "columns": ["instance_id", "anchor_time", "user_id", "product_id"],
                "rows": p_inst_rows
            },
            "related_tables": {
                "users": {"format": "arrays", "columns": u_cols, "rows": p_users},
                "products": {"format": "arrays", "columns": p_cols, "rows": p_prods},
                "sessions": {"format": "arrays", "columns": s_cols, "rows": p_sess},
                "interactions": {"format": "arrays", "columns": i_cols, "rows": p_inters},
                "purchases": {"format": "arrays", "columns": pu_cols, "rows": p_purch},
                "reviews": {"format": "arrays", "columns": r_cols, "rows": p_revs}
            }
        },
        "output": {"fields": ["prediction", "probabilities"]}
    }

    import os
    import numpy as np
    
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super(NpEncoder, self).default(obj)

    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/kumo_payload.json', 'w') as f:
        json.dump(payload, f, cls=NpEncoder)
        
    print("Payload generated.")

if __name__ == "__main__":
    main()