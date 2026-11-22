"""The 25 studies [4]-[28] cited in the research paper's literature survey.

Everything in `reported` comes from the paper's own Table II and survey text.
No number was added from outside the paper. Where the paper gives no figure,
`reported` says so and the verdict is "none".

verdict keys
  higher   their reported number is higher than ours on the same metric
  similar  same metric, same range as ours
  agree    their qualitative finding matches something we measured
  diff     the number exists but is a different metric or target, so it
           cannot be set beside ours
  none     the paper gives no headline number for this study
"""

VERDICTS = {
    "higher": ("Theirs is higher", "#A81F3D"),
    "similar": ("Similar level", "#C9A227"),
    "agree": ("Agrees with our finding", "#1F7A8C"),
    "diff": ("Different metric, not comparable", "#6B7A8A"),
    "none": ("No headline number in the paper", "#9AA6B3"),
}

KINDS = ["Classical score", "Machine learning", "Deep learning / text",
         "Explainable AI", "Review / survey"]

# ref, cite, kind, setting (only what the paper says), method, reported,
# verdict, vs_ours
STUDIES = [
    (4, "Ohlson, 1980", "Classical score", "Accounting ratios",
     "Logistic regression (O-score)",
     "A probabilistic accounting-ratio model; no figure quoted.",
     "agree",
     "Our logistic regression also beat the Altman Z-score on the same "
     "data: ROC-AUC 0.896 against 0.795 at one year."),
    (5, "Hillegeist et al., 2004", "Classical score", "Accounting vs market",
     "Z-score and O-score against a Black-Scholes-Merton probability",
     "The market-based probability was more informative than either "
     "accounting score.",
     "agree",
     "Same direction in our data: removing the market-value group was the "
     "only change that consistently lowered ROC-AUC (by 0.019 to 0.061 at "
     "one to four years)."),
    (6, "Singh and Mishra, 2016", "Classical score",
     "Indian manufacturing companies",
     "Re-estimated Altman, Ohlson and Zmijewski; new proposed model",
     "98.46% accuracy on the estimation sample.",
     "diff",
     "Accuracy measured on the same sample used to fit the model. Our "
     "numbers are on 2015-2018 years that played no part in fitting, and "
     "accuracy is misleading when failures are rare."),
    (7, "Barboza et al., 2017", "Machine learning", "North American firms",
     "SVM, bagging, boosting and random forest against LDA and logistic "
     "regression",
     "Random forest about 87% accuracy; ML about 10% more accurate than "
     "the traditional models on average.",
     "diff",
     "Accuracy, not AUC. The direction matches ours: machine learning "
     "beat the traditional Altman score by 0.124 ROC-AUC (95% CI "
     "0.095-0.156) at one year."),
    (8, "Shetty et al., 2022", "Machine learning", "3,728 Belgian SMEs",
     "XGBoost, SVM and a deep neural network",
     "82-83% accuracy from only three ratios, with no clear improvement "
     "over simpler models.",
     "diff",
     "Accuracy on a different population. In our data the tree models "
     "clearly beat logistic regression, but not each other."),
    (9, "Nguyen et al., 2024", "Machine learning",
     "Vietnamese listed firms, 2011-2021",
     "SMOTE with seven models including the Merton model",
     "Seven-model comparison; no figure quoted.",
     "none",
     "We handled imbalance with class weights instead of SMOTE."),
    (10, "Deng et al., 2024", "Machine learning",
     "Chinese listed companies",
     "Bagging with LightGBM",
     "An interpretable forewarning model; no figure quoted.",
     "none", "Closest in spirit to our boosted-tree and SHAP approach."),
    (11, "Hosaka, 2019", "Deep learning / text", "Financial ratios as images",
     "Convolutional neural network",
     "Ratios encoded as images; no figure quoted.",
     "none", "We kept plain ratios, which keeps explanations readable."),
    (12, "Hajek and Munk, 2024", "Deep learning / text",
     "2,545 listed companies",
     "BERT text features from annual reports, XGBoost, outlier detection",
     "Beat dictionary-based text features; no figure quoted.",
     "none", "Uses report text as well. We use accounting and market "
     "numbers only."),
    (13, "Fasano et al., 2025", "Deep learning / text", "Corporate crises",
     "Recurrent neural network with explainable AI",
     "High accuracy reported; no figure quoted.",
     "none", "We did not test sequence models."),
    (14, "Yang and Sun, 2026", "Deep learning / text", "Bankruptcy early warning",
     "Hierarchical deep model with risk attribution",
     "ROC-AUC 0.9286 on one validation split; 0.894-0.914 under repeated "
     "cross-validation.",
     "similar",
     "Our static XGBoost reached 0.919 (95% CI 0.895-0.940) on a "
     "time-based test. That sits inside their one-split figure and just "
     "above their cross-validated range. They too did not claim to beat "
     "conventional ML."),
    (15, "Park et al., 2021", "Explainable AI", "Bankruptcy prediction",
     "Tree models explained with LIME",
     "LIME importances were consistent with the models' built-in "
     "importances.",
     "none", "We used exact TreeSHAP for XGBoost instead of LIME."),
    (16, "Zhang et al., 2022", "Explainable AI", "Financial distress",
     "Two-stage ensemble with SHAP, PDP and counterfactuals",
     "Explanations designed for external stakeholders; no figure quoted.",
     "none", "Our website explains each company in plain language but has "
     "no counterfactuals."),
    (17, "Tran et al., 2022", "Explainable AI",
     "Vietnamese listed companies, 2010-2021",
     "ML models with SHAP",
     "Leverage and valuation ratios were the most influential.",
     "agree",
     "Valuation ratios also led in our data: market value to total "
     "liabilities alone carried 23.2% of the SHAP share one year before "
     "failure."),
    (18, "Nguyen et al., 2025", "Explainable AI", "French firms, 1-5 years ahead",
     "Random forest, LightGBM, XGBoost, NGBoost with SHAP",
     "Horizons of one to five years; no figure quoted in the paper.",
     "none",
     "Closest in design to ours. We report ROC-AUC with intervals at each "
     "lead time: 0.920 at one year down to 0.705 at five."),
    (19, "Le Nam and Phan Huy, 2026", "Explainable AI", "Vietnamese firms",
     "ML classifiers against a logistic benchmark, with SHAP",
     "Deeper retained-earnings deficits went with higher predicted "
     "distress.",
     "agree",
     "In our data the median retained earnings to total assets of failed "
     "companies falls from -0.24 three years before the last row to -0.96 "
     "in the last row."),
    (20, "Akbarlou and Mastchaman, 2027", "Explainable AI",
     "Corporate financial distress",
     "Stack of LR, SVM, RF, XGBoost and ANN with time-aware validation "
     "and SHAP",
     "ROC-AUC 0.938, PR-AUC 0.684, balanced accuracy 0.875.",
     "higher",
     "Their ROC-AUC is above our 0.919, though our 95% interval "
     "(0.895-0.940) contains it. Their PR-AUC cannot be set beside ours "
     "because PR-AUC rises with the share of failures in the data, and "
     "that share is not given."),
    (21, "Maktum et al., 2025", "Explainable AI", "Kaggle US company data",
     "Random forest with Altman Z-score, ratios and SHAP",
     "A framework paper; no figure quoted.",
     "none", "Also drew on a Kaggle US company bankruptcy dataset."),
    (22, "Chatterjee, 2018", "Classical score",
     "Large-cap Indian companies, 2000-2013",
     "Altman against Ohlson",
     "Ohlson identified distressed firms better; Altman did better on "
     "overall and non-distressed classification.",
     "none", "We tested only the original Altman score."),
    (23, "Dhingra et al., 2024", "Classical score", "Jet Airways, 2011-2018",
     "Altman, Zmijewski, Pilarski, Springate",
     "All four signalled the decline; Springate was weakest.",
     "none",
     "A single-company case. Across all firms we found the Altman distress "
     "zone caught 80.3% of firm-years one year before failure but also "
     "35.3% of companies that never failed."),
    (24, "Ahamed and Ahammed, 2024", "Classical score",
     "41 NSE logistics firms, 2019-2023",
     "Altman Z-score",
     "Z-score analysis; no figure quoted.",
     "none", "Our Altman baseline reached ROC-AUC 0.795 at one year."),
    (25, "Kaur et al., 2024", "Machine learning",
     "Indian manufacturers after the IBC",
     "RF, decision tree, neural network, logistic regression",
     "Random forest was the most accurate.",
     "agree",
     "Random forest was also top tier for us (ROC-AUC 0.917 at one "
     "year), level with XGBoost."),
    (26, "Ramesh Kannan and Bashir, 2025", "Machine learning",
     "1,938 listed Indian companies, 7,705 observations",
     "LR, decision tree, KNN, random forest",
     "Random forest 93% accuracy with Altman-based labels and 99% with "
     "Fich-Slezak and Zmijewski labels.",
     "diff",
     "Accuracy, and the labels come from distress scores rather than "
     "observed bankruptcies. Our target is real failure, where a model "
     "that predicts nobody fails would already score 99.0% accuracy."),
    (27, "Shi and Li, 2019", "Review / survey", "Studies from 1968 to 2017",
     "Systematic literature review",
     "Logistic regression and neural networks were the most studied.",
     "none", "Logistic regression is one of our four models."),
    (28, "Zhao et al., 2024", "Review / survey", "Bankruptcy literature",
     "Survey of definitions, features and evaluation practice",
     "No model results; covers definitions and evaluation practice.",
     "none", "Background for the definitions and evaluation choices we "
     "state in our methodology."),
]

FIELDS = ["ref", "cite", "kind", "setting", "method", "reported",
          "verdict", "vs_ours"]
ROWS = [dict(zip(FIELDS, r)) for r in STUDIES]
