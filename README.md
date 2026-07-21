# HMDA Mortgage Approval Prediction

Predicting whether a U.S. residential mortgage application is **approved or denied**, using real
government lending data — and examining the drivers behind lending decisions.

## Problem
Lenders (and regulators) care about who gets approved, who gets denied, and why. This project builds
a clean, analysis-ready dataset from raw HMDA filings and works toward a model that predicts loan
approval from applicant, loan, property and location features — while flagging fairness patterns
across demographic groups.

## Data
- **Source:** U.S. HMDA (Home Mortgage Disclosure Act) loan-level data, from the free public
  [FFIEC / CFPB HMDA Data Browser](https://ffiec.cfpb.gov/data-browser/).
- **Scope:** 2025 filings across 8 states (PA, WA, CO, SC, MT, ND, VT, AK).
- **Size:** ~1.04 million loan decisions, 29 working columns (reduced from the original 99).
- **Target:** `approved` (1 = originated, 0 = denied). Class balance ≈ 78% approved / 22% denied.

> The raw CSVs are large (hundreds of MB) and are **not** stored in this repo — they can be pulled
> directly from the HMDA Data Browser. See `HMDA_Data_Dictionary.md` for the column guide.

## Approach
1. **Cleaning** — removed impossible/junk values (e.g. loan-to-value in the hundreds of millions,
   property values in the billions), filled missing values (median for numeric, mode for
   categorical; no column exceeded 40% missing), and dropped 1,854 duplicate rows.
2. **Exploration** — per-column analysis, box plots, and approval-rate breakdowns by segment.
3. **Feature selection with statistical tests**
   - **Chi-square** for categorical features vs approval — strongest: `dti_ratio`, `loan_purpose`, `race`.
   - **ANOVA F-test** for numeric features vs approval — strongest: `income`, `property_value`.
   - **VIF** for multicollinearity — all features < 2 (well under the 5 threshold), none redundant.
   - Correlation heatmap confirmed only mild feature-to-feature overlap (max ≈ 0.51).
4. **Leakage control** — excluded columns that reveal the outcome (`loan_outcome`, `denial_reason_*`).
5. **Modelling** *(in progress)* — comparing Logistic Regression, Random Forest and XGBoost,
   evaluated on F1 given the class imbalance.

## Key findings so far
- No single numeric feature strongly predicts approval on its own (best is income, r ≈ 0.12);
  the decision is driven by **categorical factors and combinations**, favouring tree-based models.
- **Debt-to-income** is the single strongest signal in the categorical tests.
- Approval rates differ notably by **race, sex, ethnicity and age** — the classic HMDA fairness
  angle (association only; not evidence of cause, since income and other factors overlap).

## Repository contents
| File | What it is |
|---|---|
| `HMDA_Model.ipynb` | Main notebook: cleaning, EDA, statistical tests, findings |
| `HMDA_Data_Dictionary.md` | Column-by-column guide and rename map |
| `HMDA_Mortgage_Project_Plan.md` | Full project plan and business questions |
| `hmda_clean.py` | Data cleaning script |
| `hmda_feature_tests.py` | Statistical feature tests |

## Tools
Python (pandas, numpy, matplotlib, scipy, statsmodels) · Jupyter

## Status
🚧 In progress — data cleaning, EDA and feature selection complete; modelling and dashboard next.
