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

## Architecture

```
┌─────────────────────┐       ┌──────────────----────┐     ┌─────────────────────┐
│   Data Pipeline      │────▶│  FastAPI Backend     │────▶│   Frontend SPA      │
│  scripts/            │      │  backend/main.py     │     │  frontend/          │
│  prepare_payload.py  │      │  :8000               │     │  :3000              │
│  predict.py          │      │                      │     │  Vanilla JS +       │
│  eval.py             │      │  /api/users          │     │  TailwindCSS        │
└─────────────────────┘       │  /api/products       │     └─────────────────────┘
                              │  /api/recommendations│
                              │  /api/predict_live   │
                              └──────────────----────┘
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

## Model Notes

The NVIDIA Kumo Relational model outputs **per-item probabilities** that sum to 1.0 across the full product catalog. For a catalog of ~1,000+ items, a score of `0.04` (4%) is **extremely high confidence** — it means the model ranks that product among the top 1–2% of all items. The confidence meter is scaled accordingly (≥4% = High, 1–4% = Medium, <1% = Low).

---

## License

MIT — free to use, fork, and extend.


A full-stack demonstration of NVIDIA's Kumo Relational model for predicting "Next Best Offer" product recommendations. This project builds a relational graph from raw e-commerce CSVs (users, products, sessions, interactions, purchases, reviews), queries the NVIDIA Kumo Relational API, and displays the personalized recommendations in a beautiful, premium Single Page Application (SPA).

## Architecture & Phases

1. **Data Pipeline (`scripts/`)**
   - **`prepare_payload.py`**: Extracts per-user ego-graphs from the relational CSVs and packs them into the exact JSON schema required by the Kumo Relational model.
   - **`predict.py`**: Posts the payload to the NVIDIA API and saves the inference results.
   - **`eval.py`**: Calculates the Mock Hit Rate of the model's predictions.
2. **Backend API (`backend/main.py`)**
   - A FastAPI application that serves the mock users, the product catalog, and the pre-computed Kumo recommendations to the frontend.
3. **Frontend UI (`frontend/`)**
   - A modern, responsive SPA built with Vanilla JS, HTML, and TailwindCSS (via CDN).

## Project Structure

```text
PredictCart Beta/
├── .env                  # NVIDIA_API_KEY
├── README.md             # Setup & run instructions
├── backend/
│   └── main.py           # FastAPI server
├── frontend/
│   ├── index.html        # SPA layout with Tailwind
│   └── app.js            # Frontend logic
├── data/
│   ├── raw/              # The 6 CSV files
│   └── processed/        # Generated payload & API response
└── scripts/
    ├── prepare_payload.py
    ├── predict.py
    ├── eval.py
    └── requirements.txt
```

## Setup Instructions

1. **Install Python Dependencies**
   Ensure you have Python 3.9+ installed, then install the dependencies:
   ```bash
   pip install -r scripts/requirements.txt
   pip install fastapi uvicorn
   ```

2. **Configure API Key**
   Create a `.env` file in the root directory (copy `.env.example` if available) and add your NVIDIA API key:
   ```env
   NVIDIA_API_KEY="nvapi-your-key-here"
   ```

3. **Run the Data Pipeline (Optional, pre-computed data is saved)**
   To regenerate the payload and fetch new predictions from the NVIDIA API:
   ```bash
   python scripts/prepare_payload.py
   python scripts/predict.py
   python scripts/eval.py
   ```

4. **Start the Backend API**
   Run the FastAPI server from the root directory:
   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

5. **Start the Frontend UI**
   In a new terminal window, serve the frontend directory using a simple HTTP server:
   ```bash
   cd frontend
   python -m http.server 3000
   ```
   Open `http://localhost:3000` in your browser.

## Features

- **Relational Graph Extraction**: Converts flat tables into the ego-graph format required by Kumo.
- **Robust Data Handling**: Handles complex datatypes, timestamps, and schema validations to prevent `422 Unprocessable Entity` errors from the API.
- **Premium UI**: Uses a glassmorphism design, subtle mesh gradients, and smooth CSS transitions.
- **Color-coded Confidence**: The Next Best Offer score is visually represented (Green for high, Yellow for medium, Gray for low).
