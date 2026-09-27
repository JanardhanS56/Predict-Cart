# Recommendation Workbench

A web app that demonstrates NVIDIA's Kumo Relational model generating "Next Best Offer" product recommendations.

## Tech Stack
| Tier | Technology |
|---|---|
| Frontend | React 18, Vite, TypeScript, Tailwind CSS v3 |
| Routing | react-router-dom v6 |
| Charts | recharts |
| Backend | Node + Express (Vercel Serverless) |
| Python (Data Prep) | Python 3.11, pandas, numpy, requests, python-dotenv |

## File Tree
- `api/predict.ts` - Vercel serverless function to get predictions.
- `data/raw/*.csv` - Raw input datasets.
- `data/processed/*` - Processed datasets and predictions.
- `data/sample/predictions_sample.json` - Small sample predictions.
- `scripts/prepare_payload.py` - Prepares payload for NVIDIA Kumo model from 6 CSVs.
- `scripts/predict.py` - Invokes NVIDIA Kumo model for predictions.
- `scripts/evaluate.py` - Evaluates the predictions.
- `src/` - React frontend source code.
- `.env.example` - Example environment variables.
- `DESIGN.md` - Design specifications.

## Data Model
- `users`: Age, gender, country, city, signup_date, income_level, preferred_category, loyalty_tier
- `products`: Category, subcategory, brand, price, rating_avg, review_count, stock_quantity, date_added
- `sessions`: Start_time, device_type, referrer_source, is_converted
- `interactions`: Interaction_type, timestamp, dwell_time_ms
- `purchases`: Quantity, unit_price, total_amount, order_date
- `reviews`: Rating, title, review_text, review_date

## Core Algorithms
- **Payload Build**: `scripts/prepare_payload.py` reads 6 CSVs, constructs consistent UUID->int64 mappings, time-based split (80% context, 20% future). Sets caps on max rows to avoid payload size limit.
- **Evaluation**: `scripts/evaluate.py` loads prediction response, joins with labels, computes Precision@K, Recall@K, NDCG@K, MAP@10, and Coverage. Outputs results and frontend predictions JSON.

## How to run locally
1. Fill `.env` with `NVIDIA_API_KEY`
2. Run data prep: `python scripts/prepare_payload.py`
3. Get predictions: `python scripts/predict.py`
4. Evaluate: `python scripts/evaluate.py`
5. Run frontend: `npm install && npm run dev`

## How to deploy to Vercel
1. Set `NVIDIA_API_KEY` in Vercel environment variables.
2. Deploy via Vercel CLI or GitHub integration.

## Changelog
## 2026-09-27
- Restructured project files and folders.
- Fixed `scripts/predict.py` to use `.env`.
- Created `.gitignore` and `.env.example`.
- Created `FILES.md`.