# Early Detection of Financial Distress (demo)

A web page for the course project "Early Detection of Financial Distress in
Companies Using Explainable ML". Give it a company's financial statements and
it shows the risk of bankruptcy within 1, 2 and 3 years, and why.

## Run (Windows cmd, in this folder)
    python -m pip install streamlit openpyxl
    python -m streamlit run app.py
Use the same Python as the notebooks (it already has xgboost, pandas,
scikit-learn, joblib).

## How the page works
- It opens on a real example (a company that failed a year later), so there
  is something to read straight away.
- Sidebar, "Company data": pick an example, type the 16 statement values
  (USD millions), or upload a CSV/Excel file with many companies. Columns are
  matched automatically (X1..X18, common names, Compustat tickers) and can be
  corrected by hand.
- Main page: a risk verdict with a ranked bar for each horizon; then "Why
  this result?" in plain language: a summary sentence, the five business
  areas that push risk up or down, and each top factor drawn against the range
  of healthy companies. The SHAP/log-odds details sit in one expander.
- "All the detail": all 25 ratios with formulas and the raw inputs.

## Files
- app.py        Streamlit page
- ui.py         theme (CSS) and HTML components: risk bars, factor strips
- analysis.py   column matching, batch scoring, explanations
- scoring.py    model loading, TreeSHAP contributions, percentiles, tiers
- features.py   ratio construction (same as Step 3, static features)
- selftest.py   checks without xgboost/streamlit: python selftest.py
- .streamlit/config.toml   colours and font settings
- assets/       models, calibration, reference stats, example companies

## Notes
- Models: XGBoost, static features (one year of statements).
- Trained on US-listed companies 1999-2011. Scores are ranking scores, not
  probabilities; calibration.json maps them to failure rates seen in 2015-2018.
