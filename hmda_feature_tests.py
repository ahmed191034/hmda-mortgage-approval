"""
HMDA feature-selection statistical tests.
Question: which columns are statistically associated with loan APPROVAL?

Run in your notebook after loading + cleaning the data (needs columns renamed).
Works on the raw Dataset.csv too if you map action_taken -> loan_outcome first.

KEY IDEA: with ~500k+ rows, EVERY variable is "significant" (p ~ 0).
So rank by EFFECT SIZE (Cramer's V for categorical, correlation r for numeric),
NOT by p-value.
"""
import pandas as pd, numpy as np
from scipy import stats

# --- load (expects renamed columns; see hmda_clean.py) ---
df = pd.read_csv("Dataset.csv", low_memory=False)
if "action_taken" in df.columns:          # if still raw
    df = df.rename(columns={"action_taken": "loan_outcome",
                            "derived_race": "race", "derived_ethnicity": "ethnicity",
                            "derived_sex": "sex", "income": "income_000s",
                            "debt_to_income_ratio": "dti_ratio", "loan_term": "loan_term_months",
                            "tract_minority_population_percent": "tract_minority_population_pct",
                            "ffiec_msa_md_median_family_income": "area_median_family_income"})

# keep only real decisions: 1 = approved, 3 = denied
d = df[df["loan_outcome"].isin([1, 3])].copy()
d["approved"] = (d["loan_outcome"] == 1).astype(int)
print(f"Decision rows: {len(d):,} | approval rate: {d['approved'].mean():.1%}\n")


def cramers_v(confusion):
    chi2 = stats.chi2_contingency(confusion)[0]
    n = confusion.values.sum()
    r, k = confusion.shape
    return np.sqrt((chi2 / n) / (min(r - 1, k - 1)))


# ---------- CATEGORICAL: Chi-square + Cramer's V ----------
cat_cols = ["race", "ethnicity", "sex", "loan_type", "loan_purpose",
            "occupancy_type", "applicant_age", "dti_ratio", "state"]
print("=== CATEGORICAL (rank by Cramer's V effect size) ===")
res = []
for c in cat_cols:
    if c not in d.columns:
        continue
    t = pd.crosstab(d[c], d["approved"])
    t = t[t.sum(axis=1) >= 50]            # drop tiny groups
    chi2, p, dof, _ = stats.chi2_contingency(t)
    v = cramers_v(t)
    strength = "STRONG" if v >= .15 else "moderate" if v >= .08 else "weak"
    res.append((c, v, p, strength))
for c, v, p, s in sorted(res, key=lambda x: -x[1]):
    print(f"  {c:16s} CramersV={v:.3f}  p={p:.1e}  -> {s}")

# ---------- NUMERIC: point-biserial correlation ----------
num_cols = ["loan_amount", "interest_rate", "loan_to_value_ratio", "property_value",
            "income_000s", "loan_term_months", "tract_minority_population_pct",
            "area_median_family_income"]
print("\n=== NUMERIC (rank by |correlation r|) ===")
nres = []
for c in num_cols:
    if c not in d.columns:
        continue
    x = pd.to_numeric(d[c], errors="coerce")
    m = x.notna()
    if x[m].nunique() < 2:
        print(f"  {c:28s} UNUSABLE (only recorded for approved loans = leakage)")
        continue
    r, p = stats.pointbiserialr(d["approved"][m], x[m])
    nres.append((c, r, p, m.mean()))
for c, r, p, fill in sorted(nres, key=lambda x: -abs(x[1])):
    print(f"  {c:28s} r={r:+.3f}  p={p:.1e}  filled={fill:.0%}")

print("""
NOTES
- Effect size, not p-value, tells you what's useful here.
- interest_rate / some cost fields exist ONLY for approved loans -> leakage, don't use for approval.
- For the fairness angle, re-check race/sex/age gaps WITHIN the same dti_ratio band
  (a raw gap can disappear once you control for debt-to-income).
""")
