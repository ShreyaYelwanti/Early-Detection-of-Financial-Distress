# Early Detection of Financial Distress in Companies Using Explainable ML

Course project (ML). Predicts whether a US-listed company will go bankrupt
within 1, 2 or 3 years from its annual financial statements, and explains
which ratios drive the prediction and how that changes with lead time.

## Data
`american_bankruptcy.csv` - American Companies Bankruptcy Prediction dataset
(Lombardo et al., 2022, Future Internet 14(8):244, doi 10.3390/fi14080244).
Columns: company_name, status_label (alive/failed), year, X1..X18 (raw
accounting values, USD millions). Time split used throughout:
train 1999-2011, validation 2012-2014, test 2015-2018.

## How to run
1. Install the packages: `python -m pip install -r requirements.txt`
2. Run the notebooks in order, each from top to bottom, with this folder as
   the working directory:

| Notebook | What it does | Main outputs |
|---|---|---|
| Step1 | Load and inspect the data | failed_per_year.png |
| Step2 | Build the "fails within h years" targets, check label assumptions, make the year split | data/processed/targets.csv, results/step2_* |
| Step3 | Build 25 static ratios and 22 change features, clip at train 1st/99th percentiles, Altman Z baseline | data/processed/features.csv, results/feature_groups.csv, winsor_bounds.json, step3_* |
| Step4 | Train Logistic Regression, Random Forest, XGBoost and EBM for horizons 1-3 (static and full feature sets), evaluate with company-level bootstrap CIs | models/, data/processed/preds.csv, results/step4_* |
| Step5 | Explanations (TreeSHAP / EBM terms / logistic contributions), feature-group shares, lead-time models for 1-5 years before failure, stability across models and periods | results/step5_*, fig_*.png |
| Step6 | Reliability of explanations: seed noise floor, seed-averaged group shares, period retraining, group ablation, paired model comparison | results/step6_*, fig_group_share_seedavg.png |
| Step7 | Random-half control and lead-time AUCs with 95% company-bootstrap CIs | results/step7_* |
| Step8_tables | Prints the summary tables used in the paper | (printed only) |

Some notebooks read the environment variables `B_BOOT` (bootstrap
resamples) and `REPS` (repeats); lower them for a quick test run.

## Folders
- `data/processed/` targets, features and predictions (plain CSV)
- `models/` saved models (xgb_*, rf_*, ebm_*, logreg_*)
- `results/` all tables (CSV) and figures (PNG) used in the paper

## Notes
- Metrics reported: ROC-AUC, PR-AUC, PR-lift, recall in the riskiest 5% and
  10% of firm-years (results/step4b_recall_topk.csv), F2, Brier score.
  Accuracy is not used because failures are rare (about 1-2% of rows).
- Fit steps (clipping bounds, imputation, scaling, class weights, early
  stopping, calibration) use training or validation years only; the
  2015-2018 test years are used for final evaluation.
