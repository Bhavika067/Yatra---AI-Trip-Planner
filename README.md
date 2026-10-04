# Yatra — Explainable AI Trip Planner

A Streamlit travel-planning portfolio project for exploring personalized recommendations with structured data. Choose interests, trip length, traveller count, and a budget to compare Indian destinations and generate a downloadable itinerary.

> **Project scope:** The current recommender is an explainable, rule-based baseline. It is not a trained machine-learning model and does not use live prices, route optimization, booking data, or a generative AI API.

## Features

- Dark, responsive interface with trip planning, destination exploration, and project notes.
- Content-based destination ranking from user interests and budget fit.
- Score explanation: 70% interest-tag match and 30% budget fit.
- Curated activity suggestions grouped into a day-by-day itinerary.
- Expandable place cards with descriptions, general local travel guidance, Google Maps directions, and free/paid notes where available.
- Indicative budget estimate and CSV itinerary download.
- Local CSV dataset that can be extended without changing the recommendation logic.
- No API key required to run the current version.

## Tech stack

- Python
- Streamlit
- pandas
- CSV data

## Run locally

1. Clone the repository and open its folder in VS Code.
2. Create and activate a virtual environment:

   **Windows PowerShell**

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies and start the app:

   ```bash
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
   ```

4. Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Repository layout

```text
.
├── app.py                    # Streamlit interface and recommendation logic
├── destination.csv           # Destination profiles, tags, and indicative costs
├── requirements.txt          # Python dependencies
└── .streamlit/config.toml     # Dark theme and server defaults
```

## Recommendation method

For a destination, the interest-match component is the fraction of the selected interests present in its tags. The budget-fit component is `min(total budget / estimated trip cost, 1)`, where estimated trip cost is average daily cost × trip days × traveller count.

```text
score = 100 × (0.70 × interest_match + 0.30 × budget_fit)
```

This transparent baseline is useful for discussing feature design and explainability in a student project. Destination costs and seasons are illustrative, not live travel quotes. Place details link to visitor information where available; travel guidance is general and is not live routing. Verify current ticket prices, routes, schedules, and availability before making travel decisions.

## AIML portfolio extensions

- Expand and cite the destination dataset; record its source and update date.
- Add unit tests for score calculation, data validation, and itinerary generation.
- Evaluate top-k recommendations with precision@k or NDCG using preference examples.
- Compare the baseline with TF-IDF, collaborative filtering, or embeddings.
- Add optional model-backed itinerary generation using a server-side secret, never a committed key.
- Add geospatial route ordering and compare route distance or travel time.

## Security

Do not commit `.streamlit/secrets.toml`, `.env`, virtual environments, or API keys. If a key was exposed, revoke it with its provider and issue a replacement.

## Author

Student portfolio project · Add your name, course, and institution here before publishing if you want them shown.
