# Task 1 - Data Immersion & Wrangling

ApexPlanet Software Pvt. Ltd. | Data Analytics Internship (60 days) | Author: Mahesh R

## Objective
Get familiar with the provided sales dataset, assess its quality, clean it, and produce an analysis-ready dataset.

## Dataset
`ApexPlanet_DataAnalytics_Dataset.xlsx`: 1,000 retail orders (Jan 2025 - Jan 2026) across 8 cities, 6 products and 5 categories.

## What was done
1. **Data dictionary** for every column: [`docs/data_dictionary.md`](docs/data_dictionary.md)
2. **Data quality assessment:** [`docs/data_quality_report.md`](docs/data_quality_report.md)
3. **Cleaning and transformation script (Python/pandas):** [`src/data_cleaning.py`](src/data_cleaning.py)
4. **Analysis-ready dataset:** [`data/cleaned/cleaned_sales_dataset.csv`](data/cleaned/cleaned_sales_dataset.csv) (also `.xlsx`)

## Key findings

| Issue | Count | Treatment |
|-------|-------|-----------|
| Missing `Age` | 20 | Median imputation + `Age_Imputed` flag |
| Missing `City` | 13 | Filled with `Unknown` |
| Repeated `Order_ID` (`ORD100050`) | 9 rows | Unique `Order_Key` created; rows kept (distinct transactions) |
| `Order_Date` stored as text | 1,000 | Converted to datetime |
| `Total_Sales` outliers (IQR) | 19 | Flagged, not removed |
| Exact duplicate rows | 0 | - |
| `Total_Sales` != Quantity x Unit_Price | 0 | - |

Result: 1,000 rows x 24 columns, 0 missing values, total revenue unchanged.

## How to run
```bash
pip install -r requirements.txt
python src/data_cleaning.py
```

## Repository structure
```
Task1-Data-Wrangling/
├── data/
│   ├── raw/ApexPlanet_DataAnalytics_Dataset.xlsx
│   └── cleaned/cleaned_sales_dataset.(csv|xlsx)
├── docs/
│   ├── data_dictionary.md
│   ├── data_quality_report.md
│   └── video_walkthrough_script.md
├── src/data_cleaning.py
├── requirements.txt
└── README.md
```
