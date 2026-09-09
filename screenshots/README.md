# Screenshots

This folder is where dashboard screenshots referenced from the main
`README.md` should live.

To generate them:

1. Run the dashboard locally: `streamlit run dashboard/app.py`
2. Capture the following views and save them here with these exact
   filenames:
   - `overview.png` — the Overview tab (KPI cards + risk distribution)
   - `customers_risk.png` — the Customers & Risk tab (high-risk table + lookup)
   - `campaign_planner_assumptions.png` — Campaign Planner assumptions and KPI summary
   - `campaign_planner_thresholds.png` — Campaign Planner threshold/value charts
   - `campaign_planner_outreach.png` — Campaign Planner ranked outreach table
   - `explainability.png` — the Explainability tab (SHAP waterfall)
   - `business_insights.png` — the Business Insights tab

The campaign planner screenshots are included from a local Streamlit
run. Refresh them whenever the planner layout changes materially.
