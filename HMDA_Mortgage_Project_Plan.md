# Bootcamp Final Project — Mortgage Lending Analysis (HMDA)

**Tools used:** Python · MySQL · Power BI · Excel
**Data source:** U.S. HMDA (Home Mortgage Disclosure Act) loan-level data — real, free, no login
**Theme:** Banking / mortgage lending

---

## 1. The idea in one sentence

Analyze real U.S. mortgage applications to answer: **who gets approved, who gets denied, why, and are there patterns by income, region, race, or loan type?**

This is a strong final project because the data is *real government regulatory data* (not a toy CSV), it's big enough to justify using a database, it maps beautifully to charts and maps in Power BI, and the business story is one every bank and regulator cares about: fair, profitable lending.

### Business questions you'll answer
- What is the overall **approval vs. denial rate**, and how does it vary by region/county?
- What are the **top reasons applications get denied** (debt-to-income, credit history, collateral…)?
- How do **loan amount, income, and interest rate** relate? Do higher-income applicants get lower rates?
- Are there **differences in approval rates by race, sex, or ethnicity** for similar income levels? (the classic "fairness in lending" angle)
- Which **loan purposes** (home purchase vs. refinance vs. cash-out) dominate, and how has that shifted?
- Which **lenders (LEI)** originate the most loans?

---

## 2. Getting the data (this is your "API / open data" step)

Use the official **HMDA Data Browser** — it lets you filter and export exactly the slice you want, and it also has a documented API.

**Website:** https://ffiec.cfpb.gov/data-browser/
**Field dictionary (bookmark this):** https://ffiec.cfpb.gov/documentation/publications/loan-level-datasets/lar-data-fields

### Recommended scope (keep it manageable)
The full national file is tens of millions of rows. For a bootcamp project, filter down to something that opens fast but still tells a story:

- **1 year** (e.g., 2023 — most recent complete year)
- **1 state** (e.g., your choice — a mid-size state gives ~100k–500k rows)
- **Action taken:** include both *originated (1)* and *denied (3)* so you can compare

Download that as CSV. If it's still huge, filter to a couple of counties or one loan purpose.

### API option (to say "I pulled it via an API")
The Data Browser is backed by a CSV endpoint of the form:
```
https://ffiec.cfpb.gov/v2/data-browser-api/view/csv?states=VA&years=2023&actions_taken=1,3
```
You can call this from Python with `requests`/`pandas` (`pd.read_csv(url)`) to pull the data programmatically instead of clicking download — that satisfies the "receive data via API" requirement cleanly.

---

## 3. Key columns you'll actually use

The file has ~99 columns. You do **not** need all of them. Here's the working set:

| Column | Meaning | Use it for |
|---|---|---|
| `activity_year` | Year | Filtering / trend |
| `state_code`, `county_code`, `census_tract` | Location | Maps, regional analysis |
| `derived_msa-md` | Metro area | Regional grouping |
| `action_taken` | 1=originated, 3=denied, etc. | **Your main outcome** (approved vs denied) |
| `loan_purpose` | 1=purchase, 31=refi, 32=cash-out… | Segment analysis |
| `loan_type` | 1=Conventional, 2=FHA, 3=VA, 4=USDA | Product mix |
| `loan_amount` | Amount applied for | Size analysis, averages |
| `interest_rate` | Rate on the loan | Pricing analysis |
| `income` | Applicant income (in $000s) | Affordability, cross-tabs |
| `debt_to_income_ratio` | DTI band | Risk / denial driver |
| `property_value` | Property value | Loan-to-value context |
| `loan_term` | Months | Product detail |
| `derived_race`, `derived_ethnicity`, `derived_sex` | Demographics (clean, aggregated) | **Fairness analysis** |
| `ageapplicant` | Age band | Demographics |
| `denial_reason-1..4` | Why denied | **Top denial reasons chart** |
| `tract_minority_population_percent` | Area demographics | Regional fairness |
| `ffiec_msa_md_median_family_income` | Area median income | Benchmark income against area |

> Tip: use the **`derived_*`** columns for race/ethnicity/sex — they're pre-cleaned into simple categories, much easier than the raw `applicant_race-1..5` fields.

### Codes worth memorizing
- **action_taken:** 1 = Loan originated (approved), 3 = Application denied
- **loan_purpose:** 1 = Home purchase, 2 = Home improvement, 31 = Refinance, 32 = Cash-out refinance
- **loan_type:** 1 = Conventional, 2 = FHA, 3 = VA, 4 = USDA
- **denial_reason:** 1 = DTI, 2 = Employment history, 3 = Credit history, 4 = Collateral, 5 = Insufficient cash, 6 = Unverifiable info, 7 = Incomplete, 8 = Mortgage insurance denied, 9 = Other

---

## 4. Tool-by-tool workflow

### Step 1 — Python (clean & prep)
- Load the CSV with `pandas`.
- Keep only the ~18 columns above; drop the rest.
- Create readable label columns by mapping codes → words (e.g., `action_taken` → "Approved"/"Denied", `loan_purpose` → text).
- Handle missing/`Exempt`/`NA` values (HMDA uses codes like `1111` for exempt — replace with null).
- Add a simple `approved` flag (1 if `action_taken`==1, 0 if ==3).
- Optionally bucket `income` and `loan_amount` into bands for easier charting.
- Export a clean `hmda_clean.csv` for the next steps.

*Deliverable: a Jupyter notebook showing the cleaning + a few exploratory charts (approval rate, denial reasons, loan amount distribution).*

### Step 2 — MySQL (store & query)
- Create a table `mortgages` and load `hmda_clean.csv` (via `LOAD DATA INFILE` or Python `to_sql`).
- Write the analytical queries that feed your insights, e.g.:
  - Approval rate by county / MSA
  - Top 5 denial reasons overall and by demographic group
  - Average loan amount and interest rate by loan type
  - Approval rate by income band (cross-tab with demographics)
- Save these as a `.sql` file — this is your database deliverable.

*Deliverable: schema (CREATE TABLE) + 6–8 documented queries with their business purpose.*

### Step 3 — Power BI (dashboard)
Connect Power BI to MySQL (or import the clean CSV) and build a 1–2 page dashboard:
- **KPI cards:** total applications, approval rate, avg loan amount, avg interest rate
- **Map:** approval rate by county/state
- **Bar chart:** top denial reasons
- **Clustered bars:** approval rate by loan type / by income band
- **Slicers:** loan purpose, year, demographic group
- One "fairness" visual: approval rate by race/ethnicity held against income band

*Deliverable: `.pbix` file — this is usually the centerpiece of the demo.*

### Step 4 — Excel (exploratory analysis & lookups)
Use Excel to show the specific techniques your bootcamp listed:
- **PivotTables:** approval rate by loan purpose × loan type; average income by outcome
- **VLOOKUP / XLOOKUP:** build a small lookup table that maps code → label (e.g., denial_reason codes to text) and join it onto a sample of the data
- **Conditional formatting:** highlight high denial-rate counties (color scale), flag loans where DTI is high
- A short summary sheet with your top 5 findings

*Deliverable: `.xlsx` workbook with the pivot analysis + a formatted summary.*

---

## 5. Suggested story / conclusion

Frame the final presentation as: *"I analyzed X mortgage applications in [State], 2023. Approval rate was Y%. The top denial reason was Z. Approval rates and pricing varied by [region/income/demographic] — here's what a bank or regulator should look into."* Tie every chart back to a decision someone at a bank would make.

---

## 6. Suggested timeline

1. Download + explore data, lock scope (state/year) — **Day 1**
2. Python cleaning notebook — **Day 2**
3. MySQL load + queries — **Day 3**
4. Power BI dashboard — **Day 4–5**
5. Excel analysis + polish slides — **Day 6**
6. Rehearse the story — **Day 7**

---

## Links
- HMDA Data Browser (download here): https://ffiec.cfpb.gov/data-browser/
- Field definitions: https://ffiec.cfpb.gov/documentation/publications/loan-level-datasets/lar-data-fields
- HMDA program overview: https://www.consumerfinance.gov/data-research/hmda/
