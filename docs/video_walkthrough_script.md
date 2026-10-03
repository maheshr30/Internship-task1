# LinkedIn Video Script (3-5 min)

Screen-record while walking through the files. Suggested timing:

| Time | What to show | What to say |
|------|--------------|-------------|
| 0:00-0:30 | Title slide / GitHub repo | Who you are, the ApexPlanet Data Analytics internship, Task 1: Data Immersion & Wrangling, and the dataset (1,000 retail orders, 12 columns) |
| 0:30-1:15 | Raw Excel file + `docs/data_dictionary.md` | What each column means; that you documented type, range and business relevance |
| 1:15-2:30 | `docs/data_quality_report.md` (issues table) | Walk through: 20 missing ages, 13 missing cities, `ORD100050` repeated 9 times, dates stored as text, 19 high-value outliers, reused Customer IDs. Explain why you flagged rather than deleted |
| 2:30-3:45 | `src/data_cleaning.py`, then run it in the terminal | Show the steps: standardise text, parse dates, unique `Order_Key`, impute age, fill city, integrity check, feature engineering |
| 3:45-4:30 | `data/cleaned/cleaned_sales_dataset.csv` | 24 columns, zero missing values, revenue unchanged (139.4M) |
| 4:30-5:00 | Wrap-up | Key learning: check the data before trusting it; teaser for Task 2 (EDA and SQL) |
