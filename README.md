# PredictCart Beta: Recommendation Workbench

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
