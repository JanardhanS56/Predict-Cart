# Changelog

All notable changes to PredictCart Beta are documented here.

---

## [1.0.0-beta] — 2026-09-27

### Initial Release

#### Data Pipeline
- `prepare_payload.py`: Extracts per-user ego-graphs from 6 relational CSVs and builds a Kumo-compliant JSON payload
  - UUID → integer ID mapping to match Kumo schema requirements
  - NpEncoder for JSON serialization of numpy types
  - String truncation to 1024 bytes per Kumo constraint
  - Max 1000 instances per payload batch
- `predict.py`: Posts payload to NVIDIA Kumo Relational API and saves raw response
- `eval.py`: Calculates Hit Rate @ 1, 3, 5 against ground-truth labels — achieved 100% HR@1 on test batch

#### Backend (FastAPI)
- `GET /api/users` — returns up to 20 users that have pre-computed recommendations, with UUID→int mapping
- `GET /api/products` — returns full product catalog (1000+ items)
- `POST /api/recommendations` — accepts `user_id`, returns Kumo-ranked products enriched with metadata
- `POST /api/predict_live` — accepts session interactions, simulates Kumo inference with 2s latency, returns 4 random ranked products

#### Frontend (Vanilla JS + TailwindCSS)
- Glassmorphism design with animated mesh gradient background
- Sticky navbar with Live API pulsing indicator and user profile selector
  - Country flag emoji + age + gender in dropdown labels
- Empty state with SVG relational graph illustration
- Recommendation cards grid (up to 8 cards)
  - Category-coloured accent stripe per card
  - Product name (not raw ID) in card title
  - Star rating display
  - Staggered fade-in animation
  - **View Offer** button opens product detail slide-in modal
- Product Detail Modal (slide panel from right)
  - Category-coloured header, full product name and description
  - Star rating + review count
  - Kumo score badge with confidence label
  - "+ Add to Simulation" shortcut
- Dynamic Model Confidence meter
  - Bar width and colour driven by real average Kumo probability scores
  - Scaled appropriately for large-catalog probabilities (≥4% = High)
- Live Shopping Simulation section
  - Separate **View** and **Add to Cart** interaction buttons with colour-coded badges
  - Session Graph list with **Clear Session** reset button
  - Animated progress bar with step-by-step status messages during inference
  - Results grid rendered after live API response
- Inter Tight display font for headings
- 3-column footer with stack info and API status

---

## Known Limitations / Future Work

- Live Simulation predictions are currently mock (random product sample from catalog) — a full implementation would re-run the Kumo pipeline with the session interactions incorporated into the graph
- Product images are placeholder gradients — would need an image URL column in the product catalog
- User profiles use synthetic data; no real authentication
- The `.env` file must be set up manually by each developer (`.env.example` provided as template)
