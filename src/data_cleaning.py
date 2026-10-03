"""
Task 1 - Data Immersion & Wrangling
ApexPlanet Data Analytics Internship

Reads the raw sales dataset, profiles data quality, cleans it, engineers
features and writes an analysis-ready dataset plus a data-quality report.

Run from the repository root:
    python src/data_cleaning.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "raw" / "ApexPlanet_DataAnalytics_Dataset.xlsx"
OUT_DIR = ROOT / "data" / "cleaned"
DOCS_DIR = ROOT / "docs"

OUT_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# 1. LOAD
# --------------------------------------------------------------------------
raw = pd.read_excel(RAW_FILE)
df = raw.copy()
rows_raw = len(raw)

# --------------------------------------------------------------------------
# 2. DATA QUALITY ASSESSMENT (profiling of the RAW data)
# --------------------------------------------------------------------------
q1, q3 = raw["Total_Sales"].quantile([0.25, 0.75])
iqr = q3 - q1
upper_fence = q3 + 1.5 * iqr
lower_fence = q1 - 1.5 * iqr

profile = {
    "rows": rows_raw,
    "columns": raw.shape[1],
    "missing_age": int(raw["Age"].isna().sum()),
    "missing_city": int(raw["City"].isna().sum()),
    "fully_duplicated_rows": int(raw.duplicated().sum()),
    "duplicated_order_ids": int(raw["Order_ID"].duplicated().sum()),
    "order_ids_affected": int(raw["Order_ID"][raw["Order_ID"].duplicated(keep=False)].nunique()),
    "date_dtype": str(raw["Order_Date"].dtype),
    "total_sales_mismatch": int(
        ((raw["Quantity"] * raw["Unit_Price"] - raw["Total_Sales"]).abs() > 0.01).sum()
    ),
    "total_sales_outliers": int(
        ((raw["Total_Sales"] > upper_fence) | (raw["Total_Sales"] < lower_fence)).sum()
    ),
    "customer_ids_reused_with_diff_names": int(
        (raw.groupby("Customer_ID")["Customer_Name"].nunique() > 1).sum()
    ),
}

# --------------------------------------------------------------------------
# 3. CLEANING
# --------------------------------------------------------------------------
# 3.1 Standardise text columns (trim whitespace, consistent casing)
for col in ["Customer_Name", "Gender", "City", "Product", "Category"]:
    df[col] = df[col].astype("string").str.strip()
for col in ["Gender", "City", "Product", "Category"]:
    df[col] = df[col].str.title()
df["Order_ID"] = df["Order_ID"].str.strip().str.upper()
df["Customer_ID"] = df["Customer_ID"].str.strip().str.upper()

# 3.2 Remove exact duplicate rows (none expected - kept for reproducibility)
df = df.drop_duplicates().reset_index(drop=True)

# 3.3 Dates: text -> datetime
df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="%Y-%m-%d", errors="coerce")
assert df["Order_Date"].notna().all(), "Unparseable dates found"

# 3.4 Order_ID collisions: same ID, different transactions -> give each a unique key.
#     Rows are NOT dropped because every colliding row is a distinct transaction.
dup_mask = df["Order_ID"].duplicated(keep=False)
seq = df.groupby("Order_ID").cumcount() + 1
df["Order_Key"] = df["Order_ID"].where(~dup_mask, df["Order_ID"] + "-" + seq.astype(str))
df["Order_ID_Collision"] = dup_mask
assert df["Order_Key"].is_unique

# 3.5 Missing Age -> median imputation, flagged so analysts can exclude them
df["Age_Imputed"] = df["Age"].isna()
age_median = df["Age"].median()
df["Age"] = df["Age"].fillna(age_median).astype(int)

# 3.6 Missing City -> explicit 'Unknown' category (no reliable way to infer it)
df["City"] = df["City"].fillna("Unknown")

# 3.7 Integrity check: Total_Sales must equal Quantity x Unit_Price
df["Unit_Price"] = df["Unit_Price"].round(2)
df["Total_Sales"] = df["Total_Sales"].round(2)
mismatch = ((df["Quantity"] * df["Unit_Price"]).round(2) - df["Total_Sales"]).abs() > 0.01
assert not mismatch.any(), "Total_Sales does not reconcile"

# 3.8 Outliers: flagged, NOT removed (large orders are valid Quantity x Price results)
df["Is_Sales_Outlier"] = df["Total_Sales"] > upper_fence

# --------------------------------------------------------------------------
# 4. FEATURE ENGINEERING
# --------------------------------------------------------------------------
df["Order_Year"] = df["Order_Date"].dt.year
df["Order_Quarter"] = "Q" + df["Order_Date"].dt.quarter.astype(str)
df["Order_Month"] = df["Order_Date"].dt.month
df["Order_Month_Name"] = df["Order_Date"].dt.strftime("%b")
df["Order_Day_Of_Week"] = df["Order_Date"].dt.day_name()
df["Is_Weekend"] = df["Order_Date"].dt.dayofweek >= 5

df["Age_Group"] = pd.cut(
    df["Age"],
    bins=[17, 25, 35, 45, 55, 65],
    labels=["18-25", "26-35", "36-45", "46-55", "56-65"],
).astype("string")

df["Order_Size"] = pd.cut(
    df["Quantity"], bins=[0, 3, 7, 10], labels=["Small (1-3)", "Medium (4-7)", "Large (8-10)"]
).astype("string")

# --------------------------------------------------------------------------
# 5. OUTPUT
# --------------------------------------------------------------------------
column_order = [
    "Order_Key", "Order_ID", "Order_ID_Collision", "Order_Date", "Order_Year",
    "Order_Quarter", "Order_Month", "Order_Month_Name", "Order_Day_Of_Week",
    "Is_Weekend", "Customer_ID", "Customer_Name", "Age", "Age_Imputed",
    "Age_Group", "Gender", "City", "Product", "Category", "Quantity",
    "Order_Size", "Unit_Price", "Total_Sales", "Is_Sales_Outlier",
]
df = df[column_order].sort_values("Order_Date").reset_index(drop=True)

df.to_csv(OUT_DIR / "cleaned_sales_dataset.csv", index=False, date_format="%Y-%m-%d")

with pd.ExcelWriter(OUT_DIR / "cleaned_sales_dataset.xlsx", engine="openpyxl") as xw:
    df.to_excel(xw, sheet_name="Cleaned_Sales", index=False)
    ws = xw.sheets["Cleaned_Sales"]
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions
    for col_cells in ws.columns:
        width = max(len(str(c.value)) if c.value is not None else 0 for c in col_cells[:200])
        ws.column_dimensions[col_cells[0].column_letter].width = min(width + 3, 28)

# --------------------------------------------------------------------------
# 6. DATA QUALITY REPORT (auto-generated from the numbers above)
# --------------------------------------------------------------------------
report = f"""# Data Quality Report

Generated by `src/data_cleaning.py` from `data/raw/ApexPlanet_DataAnalytics_Dataset.xlsx`.

**Raw shape:** {profile['rows']:,} rows x {profile['columns']} columns
**Cleaned shape:** {len(df):,} rows x {df.shape[1]} columns

## 1. Issues found and how each was handled

| # | Issue | Count | Treatment | Rationale |
|---|-------|-------|-----------|-----------|
| 1 | Missing `Age` | {profile['missing_age']} ({profile['missing_age']/rows_raw:.1%}) | Filled with median ({age_median:.0f}); flagged in `Age_Imputed` | Small share, roughly symmetric distribution; the flag lets analysts exclude imputed rows |
| 2 | Missing `City` | {profile['missing_city']} ({profile['missing_city']/rows_raw:.1%}) | Set to `Unknown` | City cannot be inferred from other columns; keeps these rows' sales in totals |
| 3 | Repeated `Order_ID` | {profile['duplicated_order_ids']} extra rows (`ORD100050` appears {profile['duplicated_order_ids']+1}x) | New unique `Order_Key` (e.g. `ORD100050-3`); `Order_ID_Collision` flag added; rows kept | Every colliding row has a different customer, product and amount, so they are separate transactions with a faulty ID, not duplicates |
| 4 | Fully duplicated rows | {profile['fully_duplicated_rows']} | None needed | - |
| 5 | `Order_Date` stored as text ({profile['date_dtype']}) | {rows_raw:,} | Converted to datetime (`YYYY-MM-DD`) | Required for time-series work |
| 6 | Outliers in `Total_Sales` (IQR rule, upper fence = {upper_fence:,.0f}) | {profile['total_sales_outliers']} | Flagged in `Is_Sales_Outlier`; not removed | Values equal Quantity x Unit_Price, so they are genuine large orders |
| 7 | `Total_Sales` vs Quantity x Unit_Price | {profile['total_sales_mismatch']} mismatches | None needed | Integrity check passes |
| 8 | `Customer_ID` reused with different names | {profile['customer_ids_reused_with_diff_names']} of {raw['Customer_ID'].nunique()} IDs | Documented only; not merged | See "Known limitations" |

## 2. Feature engineering

The dataset has no Date of Birth column, so `Age` was used directly. New columns:
`Order_Key`, `Order_ID_Collision`, `Age_Imputed`, `Age_Group`, `Order_Size`,
`Order_Year`, `Order_Quarter`, `Order_Month`, `Order_Month_Name`,
`Order_Day_Of_Week`, `Is_Weekend`, `Is_Sales_Outlier`.

## 3. Post-cleaning checks

- Missing values remaining: {int(df.isna().sum().sum())}
- `Order_Key` unique: {df['Order_Key'].is_unique}
- Date range: {df['Order_Date'].min():%Y-%m-%d} to {df['Order_Date'].max():%Y-%m-%d}
- Total revenue: {df['Total_Sales'].sum():,.2f} (raw: {raw['Total_Sales'].sum():,.2f})
- Outlier orders flagged: {int(df['Is_Sales_Outlier'].sum())}

## 4. Known limitations (worth stating in the analysis)

- **`Customer_ID` is not a reliable customer key.** {profile['customer_ids_reused_with_diff_names']} IDs map to more than one name, and many to different ages or genders. Treat customer-level analysis (retention, lifetime value) with caution.
- **Unit prices look synthetic.** Every product, including Rice and Book, has prices spread across roughly 150-50,000, so product-level price comparisons will not reflect real-world pricing.
- **Coverage:** {(df['Order_Date'] == '2026-01-01').sum()} orders fall on 2026-01-01, just outside calendar 2025.
"""
(DOCS_DIR / "data_quality_report.md").write_text(report, encoding="utf-8")

print("Cleaning complete.")
print(f"Raw rows: {rows_raw:,} -> Cleaned rows: {len(df):,}")
print(f"Outputs written to: {OUT_DIR}")
