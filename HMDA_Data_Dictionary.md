# HMDA 2025 Dataset — Column Guide & Rename Map

**File:** `HMDA_2025_renamed.csv` (same data as `Dataset.csv`, columns renamed to be clean and SQL/Power BI safe)
**Rows:** 1,520,026 · **Year:** 2025 · **States:** PA, WA, CO, SC, MT, ND, AK, VT

The original file has 99 columns. Most of your analysis needs about 20 of them. Below, columns are grouped by purpose. The **⭐ = use these**; the rest are either rarely populated or highly technical and can be ignored for a bootcamp project.

---

## What each rename fixed
- Hyphens removed (`derived_msa-md` → `metro_area_code`, `aus-1` → `underwriting_system_1`) because hyphens break column names in MySQL and Power BI.
- `co-applicant_*` → `coapplicant_*` (same reason).
- `derived_` prefixes dropped for readability (`derived_race` → `race`).
- A few renamed for clarity: `action_taken` → `loan_outcome`, `hoepa_status` → `high_cost_mortgage_status`, `income` → `income_000s` (it's in thousands), `ffiec_msa_md_median_family_income` → `area_median_family_income`.

---

## 1. Identifiers & location
| New name | Original | Meaning | |
|---|---|---|---|
| `year` | activity_year | Data year (2025) | |
| `lender_id` | lei | Legal Entity Identifier of the lender | ⭐ (top lenders) |
| `state` | state_code | Two-letter state | ⭐ |
| `metro_area_code` | derived_msa-md | Metro area (MSA/MD) code | ⭐ (regional) |
| `county_code` | county_code | State-county FIPS code | ⭐ (maps) |
| `census_tract` | census_tract | 11-digit tract | (fine-grained maps) |

## 2. The outcome (your main target)
| New name | Original | Meaning | |
|---|---|---|---|
| `loan_outcome` | action_taken | 1=Originated (approved), 2=Approved not accepted, 3=Denied, 4=Withdrawn, 5=Incomplete, 6=Purchased, 7/8=Preapproval | ⭐⭐ |
| `preapproval` | preapproval | 1=Requested, 2=Not | |
| `purchaser_type` | purchaser_type | Who bought the loan (Fannie/Freddie/etc.) | |

> For an approval-vs-denial study, keep only `loan_outcome` in (1, 3). Codes 4/5/6 aren't decisions.

## 3. Loan characteristics
| New name | Original | Meaning | |
|---|---|---|---|
| `loan_product_type` | derived_loan_product_type | e.g. "Conventional:First Lien" | ⭐ |
| `loan_type` | loan_type | 1=Conventional, 2=FHA, 3=VA, 4=USDA | ⭐ |
| `loan_purpose` | loan_purpose | 1=Purchase, 2=Home improvement, 31=Refi, 32=Cash-out refi, 4=Other | ⭐ |
| `loan_amount` | loan_amount | Amount applied for ($) | ⭐ |
| `loan_term_months` | loan_term | Term in months (e.g. 360) | ⭐ |
| `lien_status` | lien_status | 1=First lien, 2=Subordinate | |
| `interest_rate` | interest_rate | Rate on the loan (%) | ⭐ (~68% filled) |
| `loan_to_value_ratio` | loan_to_value_ratio | LTV % | ⭐ (~67% filled) |
| `rate_spread` | rate_spread | Loan APR minus market rate | (~52% filled) |
| `property_value` | property_value | Property value, rounded | ⭐ (~80% filled) |
| `conforming_loan_limit` | conforming_loan_limit | C=Conforming, NC=Not | |

## 4. Applicant financials
| New name | Original | Meaning | |
|---|---|---|---|
| `income_000s` | income | Gross annual income **in $thousands** | ⭐ (needs cleaning: has negatives/outliers) |
| `dti_ratio` | debt_to_income_ratio | Debt-to-income band (e.g. "36%", "50%-60%") | ⭐ (~66% filled) |
| `applicant_credit_score_model` | applicant_credit_score_type | Which score model (FICO/Vantage). **Note: actual credit score is NOT in HMDA** | |

## 5. Demographics (for the fairness angle) — use the "derived" ones
| New name | Original | Meaning | |
|---|---|---|---|
| `race` | derived_race | Clean single race category | ⭐⭐ |
| `ethnicity` | derived_ethnicity | Hispanic/Latino or not | ⭐ |
| `sex` | derived_sex | Male/Female/Joint | ⭐ |
| `applicant_age` | applicant_age | Age band (<25, 25-34, …) | ⭐ |
| `applicant_age_above_62` | applicant_age_above_62 | Yes/No | |

> Prefer `race`/`ethnicity`/`sex` (already cleaned). The raw `applicant_race_1..5`, `coapplicant_*`, and `*_observed` columns (originals `applicant_race-1` etc.) are detailed/mostly empty — **ignore them.**

## 6. Costs & fees (mostly optional)
`total_loan_costs`, `total_points_and_fees`, `origination_charges`, `discount_points`, `lender_credits` — dollar cost fields. Sparsely filled (many under 50%). Skip unless you want a pricing deep-dive.

## 7. Why applications were denied
| New name | Original | Meaning | |
|---|---|---|---|
| `denial_reason_1` | denial_reason-1 | 1=DTI, 2=Employment, 3=Credit history, 4=Collateral, 5=Insufficient cash, 6=Unverifiable, 7=Incomplete, 8=Mortgage insurance denied, 9=Other, 10=N/A | ⭐⭐ |
| `denial_reason_2..4` | denial_reason-2..4 | Additional reasons (mostly empty) | |

## 8. Property & dwelling
`dwelling_category`, `construction_method`, `occupancy_type` (1=Primary, 2=Second, 3=Investment ⭐), `total_units`, plus manufactured-home fields. `occupancy_type` is worth keeping.

## 9. Loan terms / features (technical flags — mostly ignore)
`reverse_mortgage`, `open_end_line_of_credit`, `business_or_commercial_purpose`, `negative_amortization`, `interest_only_payment`, `balloon_payment`, `other_nonamortizing_features`, `intro_rate_period`, `prepayment_penalty_term`, `high_cost_mortgage_status`. Regulatory flags — safe to skip.

## 10. Underwriting system
`underwriting_system_1..5` (originals `aus-1..5`) — which automated system evaluated the app (Desktop Underwriter, etc.). `underwriting_system_1` could be an interesting secondary angle; 2–5 are mostly empty.

## 11. Area/census context (auto-appended by Census Bureau)
| New name | Meaning | |
|---|---|---|
| `tract_population` | People in the tract | |
| `tract_minority_population_pct` | % minority in the area | ⭐ (regional fairness) |
| `area_median_family_income` | Median family income for the metro ($) | ⭐ (benchmark applicant income) |
| `tract_to_area_income_pct` | Tract income vs. metro income | |
| `tract_owner_occupied_units`, `tract_1_to_4_family_homes`, `tract_median_housing_age` | Housing context | |

---

## Recommended working set (~20 columns)
For your analysis, keep just these and drop the other ~79:

`year, lender_id, state, county_code, metro_area_code, loan_outcome, loan_type, loan_purpose, loan_amount, loan_term_months, interest_rate, loan_to_value_ratio, property_value, income_000s, dti_ratio, race, ethnicity, sex, applicant_age, occupancy_type, denial_reason_1, tract_minority_population_pct, area_median_family_income`

---

## Cleaning notes (for the next step)
1. **Filter states** if the file is too big — e.g. start with SC or CO alone (~290k rows) for Excel-friendliness.
2. **income_000s**: drop negatives and cap extreme outliers (max was 5,000,000 = clearly bad rows).
3. **loan_outcome**: keep 1 & 3 for approval analysis; add an `approved` flag (1 if outcome=1, 0 if outcome=3).
4. **Decode codes → labels** (loan_type, loan_purpose, denial_reason, race, etc.) so charts read in plain English.
5. Numeric-looking text columns (`interest_rate`, `loan_to_value_ratio`, `property_value`) are stored as text with some "Exempt"/blank values — convert to numbers, treating those as null.
