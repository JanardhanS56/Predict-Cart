
```markdown
# DESIGN.md — Recommendation Workbench

> This file is the single source of truth for the visual and UX system.
> Claude Code MUST read this before writing any UI.
> Do not invent fonts, colors, spacing, or components outside this spec.

## Product direction

**Primary audience:** Casual evaluator (recruiter, professor, classmate).
**Secondary audience:** Technical reviewer.

Position as a **Recommendation Workbench**: a usable product that shows the
model working, with the ability to dig deeper into the relational evidence.

One-line pitch:
> Select a user. See what the relational model predicts next. Investigate the
> evidence around that prediction.

Distinguish **prediction** ("72% predicted probability") from **evidence**
("viewed running shoes twice, purchased sportswear recently").
Never claim the model explained *why* — only show observed relationships.

## Information architecture — 4 screens

1. `/` — **Recommendations** (hero). User picker + ranked next-best offers.
2. `/recommendation/:id` — **Recommendation Detail**. Evidence for one prediction.
3. `/data-model` — **Data & Model**. Relational pipeline explanation.
4. `/evaluation` — **Evaluation**. Precision@K, Recall@K, NDCG@K, limitations.

Nav: left rail or narrow top bar. Items: Recommendations · Data & Model ·
Evaluation. Detail is contextual, not a nav item. About lives at bottom.

## Screen 1 — Recommendations

- User picker (search + select), prominent but not oversized
- User summary line: `User 10482 · Female · 24 · Bengaluru`
- Prediction window label: `Next 30 days`
- Section header: `NEXT BEST OFFERS`
- Ranked list (not a card grid):
  - `01  Product Name                          78%`
  - `    Electronics · ₹4,999`
  - `    Short contextual signal`
- Show probability as `78% predicted probability`, never "AI confidence"
- Empty state (no user selected): "Select a user to generate recommendations."
- Empty state (user has no predictions): "No predictions available for this user."

## Screen 2 — Recommendation Detail

Layout:
- Product identity block (name, category, price)
- Large probability value
- Prediction window + rank
- Section: `RELEVANT USER ACTIVITY`
  - Views / clicks / cart adds / purchases / reviews
  - Recency, frequency
  - Product context

Use "Relevant user activity" — never "because you...".
Empty state: "Limited context available."

## Screen 3 — Data & Model

Hero: horizontal relational diagram (SVG, documentation style).

```
USERS
  ├── SESSIONS ── INTERACTIONS
  ├── PURCHASES
  └── REVIEWS
        ▼
  RELATIONAL MODEL
        ▼
  FUTURE PREDICTION (next 30 days)
        ▼
  NEXT BEST OFFERS
```

Below: entity descriptions table, input → model → output flow, glossary.
No empty state needed.

## Screen 4 — Evaluation

Top: 3–4 metric cards only.
- Precision@K
- Recall@K
- NDCG@K
- Evaluation set size

Then: one primary chart + a `LIMITATIONS` section (bullet list).
If metrics missing: "Evaluation data unavailable." — never fake numbers.

## Typography

- UI sans: **IBM Plex Sans**
- Mono: **IBM Plex Mono** (only for IDs, probabilities, timestamps, stats)
- Bundle locally via `@fontsource`. No Google Fonts CDN.
- Mono is NEVER used for paragraphs or large headings.

## Color tokens (Tailwind theme)

| Token        | Hex       | Usage                    |
|--------------|-----------|--------------------------|
| paper        | #F5F3EE   | Main background          |
| surface      | #FBFAF7   | Raised / content areas   |
| ink          | #242522   | Primary text             |
| ink-soft     | #555750   | Secondary text           |
| gray         | #858780   | Metadata / placeholders  |
| border       | #D8D6CF   | Dividers / borders       |
| border-soft  | #E7E5DE   | Subtle table separators  |
| sage         | #71866F   | Primary accent           |
| sage-dark    | #526751   | Hover / active           |
| sage-pale    | #E6ECE4   | Subtle highlighted state |

Semantic (muted only): success = sage, warning = ochre, error = brick.
No saturated blue. Sage must occupy a SMALL percentage of the screen.

## Spacing

8px base unit. Scale: 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96.

## Border radius

Small only. Inputs/buttons 4–6px. Cards 6–8px. Badges 4px.
No large rounded containers. Borders carry hierarchy. Shadows rare/absent.

## Components

- Button: primary, secondary, ghost, destructive. Compact, rectangular.
- Card: only when grouping truly related info. Prefer section + divider.
- Table: generous row height, strong typographic hierarchy.
- Badge: sparingly for category, interaction type, status. Never decorative.
- Tooltip: only for technical terms (e.g. NDCG@10).
- Charts: line, horizontal bar, small distributions. No 3D, no radar, no donut overload.
- Empty states: what's missing, why it matters, what action resolves it. No illustrations.

## Signature moment

One 60-second sequence:
```
SELECT USER → SEE RANKED PRODUCTS → CLICK TOP RECOMMENDATION
→ SEE PROBABILITY + USER/PRODUCT CONTEXT
→ UNDERSTAND THE RELATIONAL CONNECTION
```

The design principle: **show the prediction first. Explain the relational
complexity second.**

## Hard bans (do not use)

- Purple/blue gradients
- Glassmorphism, backdrop-blur cards
- rounded-2xl on every surface, shadow-xl
- Gradient text
- Hero sections with floating orbs / mesh gradients
- Emoji in UI chrome
- Inter as the only font
- Lucide icons scattered "just because"
- Fake AI-startup aesthetic

## Anti-scope (do NOT build)

1. Full user-management CRUD
2. Product marketplace / cart / checkout / wishlist
3. Real-time analytics dashboard with dozens of KPIs
4. "AI explanation" prose generator or chatbot
5. Exposing model hyperparameters or infra config

## Position statement

The first screen must NOT say "Welcome to our AI-powered recommendation platform."
It should say:

> **Next Best Offers**
> *Predicted products a user is most likely to engage with in the next 30 days.*

Then immediately show the user selector.
```

---
