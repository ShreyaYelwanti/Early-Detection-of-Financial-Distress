# Added: two comparison pages

Existing files (app.py, ui.py, analysis.py, scoring.py, features.py, the
notebooks and all models) are unchanged. Streamlit lists everything in
`pages/` in the sidebar automatically.

- pages/1_Model_comparison.py       five models side by side, curves, paired
                                    tests, and the reasons XGBoost was chosen
- pages/2_Literature_comparison.py  our results beside the 25 cited studies
- compare_ui.py                     shared HTML helpers and extra CSS
- literature_data.py                the 25 studies, taken from the paper
- build_comparison_assets.py        rebuilds assets/model_comparison.json
                                    from the notebook outputs (read only)
- assets/model_comparison.json      numbers used by the pages

Run as before: python -m streamlit run app.py
