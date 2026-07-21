"""
HMDA 2025 cleaning script.
Run this in your notebook (or as a script) in the same folder as Dataset.csv.
It renames all columns, keeps the useful ones, decodes codes to labels,
cleans income, and creates an 'approved' flag. Outputs hmda_ready.csv.
"""
import pandas as pd
import numpy as np

# 1) LOAD -----------------------------------------------------------
df = pd.read_csv("Dataset.csv", low_memory=False)

# 2) RENAME ALL COLUMNS (clean, SQL/Power BI safe) ------------------
rename = {
    "activity_year": "year", "lei": "lender_id", "derived_msa-md": "metro_area_code",
    "state_code": "state", "derived_loan_product_type": "loan_product_type",
    "derived_dwelling_category": "dwelling_category", "derived_ethnicity": "ethnicity",
    "derived_race": "race", "derived_sex": "sex", "action_taken": "loan_outcome",
    "open-end_line_of_credit": "open_end_line_of_credit", "hoepa_status": "high_cost_mortgage_status",
    "loan_term": "loan_term_months", "income": "income_000s", "debt_to_income_ratio": "dti_ratio",
    "ffiec_msa_md_median_family_income": "area_median_family_income",
    "tract_minority_population_percent": "tract_minority_population_pct",
    "denial_reason-1": "denial_reason_1",
}
# also fix any remaining hyphens / co-applicant automatically
df = df.rename(columns=rename)
df.columns = [c.replace("-", "_").replace("co_applicant", "coapplicant") for c in df.columns]

# 3) KEEP THE USEFUL COLUMNS ---------------------------------------
keep = ["year", "lender_id", "state", "county_code", "metro_area_code",
        "loan_outcome", "loan_type", "loan_purpose", "loan_amount", "loan_term_months",
        "interest_rate", "loan_to_value_ratio", "property_value", "income_000s", "dti_ratio",
        "race", "ethnicity", "sex", "applicant_age", "occupancy_type", "denial_reason_1",
        "tract_minority_population_pct", "area_median_family_income"]
df = df[keep]

# 4) DECODE CODES TO LABELS ----------------------------------------
outcome_map = {1: "Approved", 2: "Approved not accepted", 3: "Denied",
               4: "Withdrawn", 5: "Incomplete", 6: "Purchased",
               7: "Preapproval denied", 8: "Preapproval not accepted"}
loan_type_map = {1: "Conventional", 2: "FHA", 3: "VA", 4: "USDA"}
purpose_map = {1: "Home purchase", 2: "Home improvement", 31: "Refinance",
               32: "Cash-out refinance", 4: "Other", 5: "Not applicable"}
occupancy_map = {1: "Principal residence", 2: "Second residence", 3: "Investment"}
denial_map = {1: "Debt-to-income", 2: "Employment history", 3: "Credit history",
              4: "Collateral", 5: "Insufficient cash", 6: "Unverifiable info",
              7: "Incomplete application", 8: "Mortgage insurance denied",
              9: "Other", 10: "Not applicable"}

df["loan_outcome_label"] = df["loan_outcome"].map(outcome_map)
df["loan_type_label"] = df["loan_type"].map(loan_type_map)
df["loan_purpose_label"] = df["loan_purpose"].map(purpose_map)
df["occupancy_label"] = df["occupancy_type"].map(occupancy_map)
df["denial_reason_label"] = df["denial_reason_1"].map(denial_map)

# 5) FIX NUMERIC TEXT COLUMNS (blank / "Exempt" -> NaN) ------------
for col in ["interest_rate", "loan_to_value_ratio", "property_value"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 6) CLEAN INCOME (remove negatives and extreme outliers) ----------
df.loc[df["income_000s"] <= 0, "income_000s"] = np.nan
df.loc[df["income_000s"] > 2000, "income_000s"] = np.nan   # >$2M/yr = bad rows

# 7) APPROVAL FLAG + FILTER TO DECISIONS ---------------------------
# keep only real decisions (approved / denied) for approval analysis
decisions = df[df["loan_outcome"].isin([1, 3])].copy()
decisions["approved"] = (decisions["loan_outcome"] == 1).astype(int)

# 8) SAVE ----------------------------------------------------------
df.to_csv("hmda_ready_all.csv", index=False)          # all outcomes, cleaned
decisions.to_csv("hmda_ready_decisions.csv", index=False)  # approved/denied only

print("All rows:", df.shape, "| Decisions only:", decisions.shape)
print("Approval rate: {:.1%}".format(decisions["approved"].mean()))
print("Saved hmda_ready_all.csv and hmda_ready_decisions.csv")

# TIP: for Excel / one-state work, filter first, e.g.:
#   sc = decisions[decisions["state"] == "SC"]
#   sc.to_csv("hmda_SC.csv", index=False)
