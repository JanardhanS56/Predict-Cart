# Predict-Cart: Recommendation Workbench

> A full-stack demonstration of **NVIDIA Kumo Relational** graph ML for real-time "Next Best Offer" product recommendations.

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-CDN-38bdf8?logo=tailwindcss)](https://tailwindcss.com)
[![NVIDIA Kumo](https://img.shields.io/badge/NVIDIA-Kumo%20Relational-76b900?logo=nvidia)](https://build.nvidia.com)

---

## What It Does

PredictCart takes six relational e-commerce tables (users, products, sessions, interactions, purchases, reviews), builds a **per-user ego-graph**, and posts it to the **NVIDIA Kumo Relational API**. The returned probabilities are served through a FastAPI backend and displayed in a premium, interactive Single Page Application.

---

## Screenshots

**Empty State — Select a User Profile**
![PredictCart empty state with user dropdown](https://github.com/JanardhanS56/Predict-Cart/raw/main/screenshots/1-empty-state.png)

**User Selected — View AI-Ranked Next Best Offers**
![PredictCart showing personalized recommendations grid](https://github.com/JanardhanS56/Predict-Cart/raw/main/screenshots/2-recommendations.png)

**Live Shopping Simulation — Add Interactions & Trigger Prediction**
![PredictCart live simulation with product selection and prediction results](https://github.com/JanardhanS56/Predict-Cart/raw/main/screenshots/3-live-simulation.png)

**Real-Time Predictions — Model Confidence & Product Rankings**
![PredictCart live predictions with confidence scores and detailed product cards](https://github.com/JanardhanS56/Predict-Cart/raw/main/screenshots/4-live-predictions.png)

---

## Architecture

```
┌─────────────────────┐       ┌──────────────────────┐     ┌────────────────────┐
│   Data Pipeline     │────▶  │  FastAPI Backend     │────▶│   Frontend SPA      │
│  scripts/           │       │  backend/main.py     │     │  frontend/          │
│  prepare_payload.py │       │  :8000               │     │  :3000              │
│  predict.py         │       │                      │     │  Vanilla JS +       │
│  eval.py            │       │  /api/users          │     │  TailwindCSS        │
└─────────────────────┘       │  /api/products       │     └────────────────────┘
                              │  /api/recommendations│
                              │  /api/predict_live   │
                              └──────────────────────┘
```

## Project Structure

```
PredictCart Beta/
├── .env                        # NVIDIA_API_KEY (never commit this)
├── .env.example                # Template for the API key
├── .gitignore
├── README.md
├── CHANGELOG.md
├── backend/
│   └── main.py                 # FastAPI server — users, products, recommendations, live prediction
├── frontend/
│   ├── index.html              # SPA layout (Tailwind CSS via CDN)
│   └── app.js                  # All frontend logic (fetch, render, modal, simulation)
├── data/
│   ├── raw/                    # 6 source CSVs (gitignored)
│   └── processed/              # Generated payload & API response (gitignored)
└── scripts/
    ├── prepare_payload.py      # Builds Kumo ego-graph payload from CSVs
    ├── predict.py              # Calls NVIDIA Kumo API, saves response
    ├── eval.py                 # Calculates Hit Rate @ K
    └── requirements.txt        # Python deps
```

---

## Quick Start

```bash
# Clone & setup
git clone https://github.com/JanardhanS56/Predict-Cart.git
cd Predict-Cart
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install deps
pip install -r scripts/requirements.txt
pip install fastapi uvicorn

# Configure API key
cp .env.example .env
# Edit .env and add: NVIDIA_API_KEY="nvapi-xxxx"

# Start backend (Terminal 1)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Start frontend (Terminal 2)
cd frontend
python -m http.server 3000
```

Open **http://localhost:3000** in your browser.

---

## Setup

### 1. Prerequisites
- Python 3.9+
- An [NVIDIA Build](https://build.nvidia.com) API key with access to `kumo-relational`

### 2. Clone & create virtual environment
```bash
git clone https://github.com/YOUR_USERNAME/predictcart-beta.git
cd predictcart-beta
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r scripts/requirements.txt
pip install fastapi uvicorn
```

### 4. Configure API key
```bash
cp .env.example .env
# Edit .env and set: NVIDIA_API_KEY="nvapi-xxxx"
```

### 5. Run the data pipeline *(optional — pre-computed results can be regenerated)*
```bash
python scripts/prepare_payload.py   # builds data/processed/kumo_payload.json
python scripts/predict.py           # calls Kumo API → data/processed/prediction_response.json
python scripts/eval.py              # prints Hit Rate @ 1, 3, 5
```

### 6. Start the backend
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 7. Start the frontend
Open a **second terminal** (keep the backend running):
```bash
cd frontend
python -m http.server 3000
```
Open **http://localhost:3000** in your browser.

---

## Features

| Feature | Description |
|---|---|
| Relational Graph Extraction | Converts flat CSVs into Kumo ego-graph JSON payloads |
| Live API Indicator | Pulsing dot in navbar confirms backend connectivity |
| Personalized Recommendations | Per-user Next Best Offers ranked by Kumo probability |
| Dynamic Confidence Meter | Bar and label update from real model scores (not static) |
| Product Detail Modal | Slide-in panel with name, description, rating, price |
| Live Shopping Simulation | Add View/Cart interactions → trigger real-time prediction |
| Session Graph | Running list of current interactions with clear/reset |
| Staggered Card Animations | Cards fade in sequentially for a polished feel |
| Glassmorphism UI | Mesh gradient background, frosted glass panels |
| Responsive Layout | Works on mobile, tablet, and desktop |

---

## Why This Project Matters

- **Demonstrates Real-World ML Ops**: Not a Jupyter notebook—this is a complete pipeline from raw e-commerce CSVs → relational graph construction → NVIDIA API inference → FastAPI backend → interactive SPA.
- **Shows Product Thinking**: Built a premium UX (glassmorphism, live simulation, confidence meter) to make ML predictions tangible and explorable, not just abstract scores.
- **NVIDIA Kumo Deep-Dive**: Specifically targets the "Next Best Offer" e-commerce use case with proper ego-graph construction and relational feature engineering.
- **Full-Stack Ownership**: Designed the relational schema, scripted the data pipeline, built the FastAPI backend, and crafted a modern Vanilla JS frontend with TailwindCSS.

---

## Model Notes

The NVIDIA Kumo Relational model outputs **per-item probabilities** that sum to 1.0 across the full product catalog. For a catalog of ~1,000+ items, a score of `0.04` (4%) is **extremely high confidence**. The model learns from:

- **User attributes** (age, gender, location)
- **Purchase history** (items, recency, frequency)
- **Browsing behavior** (views, clicks, session length)
- **Product relationships** (category, price, rating, brand)
- **Temporal patterns** (seasonality, trends)

---

## Key Technical Decisions

1. **Relational Graph as ETL**: Why ego-graphs work for recommendation—learned how Kumo expects data shaped vs. raw flat tables. The key insight is that relational patterns (e.g., "users who bought X also viewed Y") matter more than individual attributes.

2. **Live Simulation UX**: Realized static rankings don't sell the model. Added interactive product add-to-cart → live prediction flow to show causality: *user action → updated graph → new predictions*.

3. **Vanilla JS Frontend**: Skipped React/Vue to keep dependencies minimal and demonstrate raw DOM/fetch mastery. TailwindCSS CDN for fast iteration without build tooling.

---

## Future Enhancements

- [ ] Add user segmentation & cohort analysis views
- [ ] Expose Kumo confidence thresholds as interactive sliders
- [ ] Cache API responses to reduce quota burn
- [ ] Multi-user session replay (view others' shopping carts in real-time)
- [ ] Export recommendations as CSV/JSON for downstream analytics
- [ ] A/B testing framework to validate predicted offers vs. random

---

## License

MIT — free to use, fork, and extend.
