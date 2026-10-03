# Data Dictionary

Dataset: `ApexPlanet_DataAnalytics_Dataset.xlsx` (sheet `Sales_Dataset`) - retail sales transactions, one row per order.
Cleaned file: `data/cleaned/cleaned_sales_dataset.csv` (1,000 rows x 24 columns).

## A. Original columns (12)

| Column | Type | Description | Values / Range | Business relevance |
|--------|------|-------------|----------------|--------------------|
| `Order_ID` | Text | Order identifier, format `ORD######` | `ORD100002`-`ORD101001`; `ORD100050` repeated 9x (data fault) | Identifies a transaction; not unique in raw data |
| `Order_Date` | Date (text in raw) | Date the order was placed | 2025-01-01 to 2026-01-01 | Time-series, seasonality, monthly trends |
| `Customer_ID` | Text | Customer identifier, format `CUST####` | 947 distinct; 52 reused across different names | Customer analysis (use with caution) |
| `Customer_Name` | Text | Anonymised customer name | `Customer_N` | Display label only |
| `Age` | Integer | Customer age in years | 18-65 (20 missing in raw) | Demographic segmentation |
| `Gender` | Categorical | Customer gender | Male, Female | Demographic segmentation |
| `City` | Categorical | City where the order was placed | Patna, Kolkata, Mumbai, Hyderabad, Delhi, Bengaluru, Gaya, Pune, Unknown | Regional performance, logistics |
| `Product` | Categorical | Product purchased | Mobile, Book, Laptop, Chair, Shoes, Rice | Product performance |
| `Category` | Categorical | Product category (each product maps to one) | Electronics, Education, Furniture, Fashion, Grocery | Category-level revenue and mix |
| `Quantity` | Integer | Units in the order | 1-10 | Basket size, volume |
| `Unit_Price` | Decimal | Price per unit | approx. 146-49,998 | Pricing analysis |
| `Total_Sales` | Decimal | Order revenue = `Quantity` x `Unit_Price` | approx. 146-493,678 | Primary revenue metric |

## B. Columns added during cleaning / feature engineering (12)

| Column | Type | Description | How it is derived | Business relevance |
|--------|------|-------------|-------------------|--------------------|
| `Order_Key` | Text | Guaranteed-unique order key | `Order_ID`; for the 9 colliding rows, suffixed `-1` to `-9` | Safe primary key for joins/SQL |
| `Order_ID_Collision` | Boolean | True if the raw `Order_ID` was shared by several orders | Duplicate check on `Order_ID` | Lets analysts trace the data fault |
| `Order_Year` | Integer | Year of order | From `Order_Date` | Yearly grouping |
| `Order_Quarter` | Text | Q1-Q4 | From `Order_Date` | Quarterly reporting |
| `Order_Month` | Integer | Month number 1-12 | From `Order_Date` | Sorting months correctly |
| `Order_Month_Name` | Text | Jan-Dec | From `Order_Date` | Chart labels |
| `Order_Day_Of_Week` | Text | Monday-Sunday | From `Order_Date` | Weekday demand patterns |
| `Is_Weekend` | Boolean | True for Saturday/Sunday | From `Order_Date` | Weekend vs weekday comparison |
| `Age_Imputed` | Boolean | True if `Age` was missing and filled with the median (41) | Missing-value flag | Exclude imputed rows in age-based analysis |
| `Age_Group` | Text | 18-25, 26-35, 36-45, 46-55, 56-65 | Binned `Age` | Customer segmentation |
| `Order_Size` | Text | Small (1-3), Medium (4-7), Large (8-10) | Binned `Quantity` | Basket-size analysis |
| `Is_Sales_Outlier` | Boolean | True if `Total_Sales` exceeds the IQR upper fence (438,707) | Q3 + 1.5 x IQR | Separate very large orders from typical ones |
