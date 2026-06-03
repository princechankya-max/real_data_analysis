# 🛍️ OLIST BRAZILIAN E-COMMERCE DATA ANALYSIS PROJECT

> **Complete Data Analysis + SQL Project** | 9 Datasets | 20 SQL Queries | 12 Visualizations | SQLite Database

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-1.3%2B-green?style=flat-square&logo=pandas)](https://pandas.pydata.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-lightblue?style=flat-square&logo=sqlite)](https://www.sqlite.org/)
[![Status](https://img.shields.io/badge/Status-COMPLETE-brightgreen?style=flat-square)]()

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Dataset Information](#dataset-information)
- [Features Engineered](#features-engineered)
- [SQL Queries](#sql-queries)
- [Visualizations](#visualizations)
- [Installation & Setup](#installation--setup)
- [How to Run](#how-to-run)
- [Project Structure](#project-structure)
- [Key Findings](#key-findings)
- [Database Schema](#database-schema)
- [Technologies Used](#technologies-used)
- [Output Files](#output-files)

---

## 🎯 Project Overview

This comprehensive data analysis project processes **9 Brazilian e-commerce datasets** from Olist, a major Brazilian e-commerce platform. The project includes:

- ✅ **99,441 orders** with detailed transaction data
- ✅ **112,650 order items** with pricing and freight information
- ✅ **99,224 customer reviews** with ratings and sentiments
- ✅ **3,095 sellers** across Brazilian states
- ✅ **Feature engineering** on temporal, categorical, and numerical data
- ✅ **SQLite database** with 9 normalized tables
- ✅ **20 business-focused SQL queries** for insights
- ✅ **12 professional visualizations** (PNG, 300 DPI)
- ✅ **Excel export** with complete query results (20 sheets)

### Key Metrics
| Metric | Value |
|--------|-------|
| **Total Orders** | 96,476 |
| **Total Revenue** | R$ 13,279,233.59 |
| **Average Delivery** | 12.01 days |
| **Late Delivery Rate** | 7.9% |
| **Customer Satisfaction** | 4.08/5.0 ⭐ |
| **Unique Customers** | 96,476 |
| **Active Sellers** | 2,970 |

---

## 📊 Dataset Information

### 9 Input CSV Files

| # | Filename | Rows | Columns | Purpose |
|---|----------|------|---------|---------|
| 1 | `olist_orders_dataset.csv` | 99,441 | 8 | Main transaction data with status & timestamps |
| 2 | `olist_order_items_dataset.csv` | 112,650 | 7 | Individual items per order with prices |
| 3 | `olist_products_dataset.csv` | 32,951 | 9 | Product catalog with categories & dimensions |
| 4 | `olist_sellers_dataset.csv` | 3,095 | 4 | Seller information and locations |
| 5 | `olist_customers_dataset.csv` | 99,441 | 5 | Customer demographics and locations |
| 6 | `olist_order_reviews_dataset.csv` | 99,224 | 7 | Customer reviews and ratings |
| 7 | `olist_order_payments_dataset.csv` | 103,886 | 5 | Payment methods and installments |
| 8 | `olist_geolocation_dataset.csv` | 1,000,163 | 5 | ZIP code geolocation coordinates |
| 9 | `product_category_name_translation.csv` | 71 | 2 | Portuguese → English category translations |

**Total Data:** 1,551,193 rows | ~200+ MB

---

## 🔧 Features Engineered

### 📅 Temporal Features (Orders Table)
```python
✓ delivery_time_days        - Days from purchase to delivery
✓ estimated_days            - Estimated delivery timeframe
✓ approval_hours            - Order approval time in hours
✓ is_late                   - Binary late delivery flag
✓ order_year                - Year of purchase
✓ order_month               - Month of purchase (1-12)
✓ order_dayofweek           - Day of week (0=Mon, 6=Sun)
✓ order_hour                - Hour of day (0-23)
✓ is_weekend                - Binary weekend indicator
```

### 💰 Financial Features (Order Items - Aggregated)
```python
✓ total_price               - Sum of item prices
✓ total_freight             - Sum of shipping costs
✓ total_revenue             - Price + Freight combined
✓ num_items                 - Items per order
✓ avg_item_price            - Average price per item
✓ freight_ratio             - Freight to price ratio
✓ unique_sellers            - Number of sellers per order
✓ unique_products           - Number of products per order
```

### 💬 Sentiment Features (Reviews)
```python
✓ sentiment                 - Classified as:
                              • Positive (score ≥ 4)
                              • Neutral (score = 3)
                              • Negative (score < 3)
```

---

## 📈 SQL Queries (20 Total)

### Business Intelligence Queries

| Q | Query Name | Purpose | Key Metrics |
|---|-----------|---------|------------|
| **Q01** | Orders by Status | Order distribution | Count, percentage per status |
| **Q02** | Monthly Trend | Revenue over time | Orders, price, freight by month |
| **Q03** | Top Customer States | Geographic analysis | Orders per state, avg delivery |
| **Q04** | Top Seller States | Seller performance | Sellers, avg price, revenue |
| **Q05** | Delivery by Status | Status analysis | Avg/min/max delivery days |
| **Q06** | Late Delivery Rate | Operational KPI | Total orders, late count/% |
| **Q07** | Top Categories | Product popularity | Items sold by category |
| **Q08** | Revenue by Category | Revenue analysis | Revenue, avg price per category |
| **Q09** | Payment Types | Payment distribution | Payment type %, avg value |
| **Q10** | Installments | Financing analysis | Avg installments by type |
| **Q11** | Review Scores | Quality metrics | Distribution of 1-5 ratings |
| **Q12** | Review Trend | Satisfaction over time | Avg score by month |
| **Q13** | Late Delivery by State | Regional performance | Late % per state (top 10) |
| **Q14** | Freight Analysis | Logistics costs | Freight ratio by category |
| **Q15** | Top Sellers | Revenue leaders | Top 10 sellers by revenue |
| **Q16** | Multi-Item Orders | Order composition | Distribution (1, 2, 3, 5+ items) |
| **Q17** | Hourly Orders | Temporal patterns | Orders by hour of day |
| **Q18** | Weekday Orders | Day patterns | Orders by day of week |
| **Q19** | Repeat Purchases | Customer loyalty | Repeat purchase segments |
| **Q20** | KPI Summary | Executive dashboard | All key metrics in 1 row |

### Example Query: Top Categories
```sql
SELECT
    COALESCE(ct.product_category_name_english, p.product_category_name) as category,
    COUNT(oi.order_item_id) as num_items_sold,
    COUNT(DISTINCT oi.order_id) as num_orders
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY category
ORDER BY num_items_sold DESC
LIMIT 10
```

---

## 📊 Visualizations (12 Charts)

### Chart Gallery

| # | Chart Name | Type | File | Insights |
|---|-----------|------|------|----------|
| **01** | Monthly Order Volume | Line Chart | `chart_01_monthly_orders.png` | Seasonal trends & growth patterns |
| **02** | Monthly Revenue Trend | Bar Chart | `chart_02_monthly_revenue.png` | Revenue seasonality (2017-2018) |
| **03** | Order Status Distribution | Horizontal Bar | `chart_03_order_status.png` | Delivery status breakdown |
| **04** | Delivery Time Distribution | Histogram | `chart_04_delivery_time_hist.png` | 0-60 day delivery timeframe |
| **05** | Review Score Distribution | Bar Chart | `chart_05_review_scores.png` | Customer satisfaction (1-5 rating) |
| **06** | Top 10 Categories | Horizontal Bar | `chart_06_top_categories.png` | Best-selling product categories |
| **07** | Payment Type Distribution | Pie Chart | `chart_07_payment_types.png` | Payment method breakdown |
| **08** | Late Delivery by State | Bar Chart | `chart_08_late_by_state.png` | Regional delivery performance |
| **09** | Orders by Hour of Day | Bar Chart | `chart_09_hourly_orders.png` | Peak ordering times |
| **10** | Orders by Day of Week | Bar Chart | `chart_10_weekday_orders.png` | Weekly patterns |
| **11** | Price Distribution | Box Plot | `chart_11_price_distribution.png` | Price ranges by top 5 categories |
| **12** | Items per Order | Bar Chart | `chart_12_items_per_order.png` | Order composition (1, 2, 3, 5+) |

**All charts:** 300 DPI PNG format, publication-ready

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Required Libraries
```bash
pip install pandas numpy matplotlib seaborn sqlite3 openpyxl
```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/princechankya-max/real_data_analysis.git
   cd real_data_analysis/olist_ecommerce
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare CSV files**
   Place all 9 CSV files in the `olist_ecommerce/` directory:
   - `olist_orders_dataset.csv`
   - `olist_order_items_dataset.csv`
   - `olist_products_dataset.csv`
   - `olist_sellers_dataset.csv`
   - `olist_customers_dataset.csv`
   - `olist_order_reviews_dataset.csv`
   - `olist_order_payments_dataset.csv`
   - `olist_geolocation_dataset.csv`
   - `product_category_name_translation.csv`

---

## ▶️ How to Run

### Execute the Main Script
```bash
python eda_sql_analysis.py
```

### Expected Output
```
================================================================================
OLIST BRAZILIAN E-COMMERCE DATA ANALYSIS PROJECT
================================================================================

STEP 1: LOADING DATA FILES
[*] ORDERS: Shape (99441, 8) | Nulls: 0
[*] ORDER_ITEMS: Shape (112650, 7) | Nulls: 0
...

STEP 2: FEATURE ENGINEERING
[+] Orders features engineered
[+] Order items aggregated
...

STEP 3: CREATING SQLITE DATABASE
[+] Table 'orders' created (99441 rows)
...

STEP 4: RUNNING 20 SQL BUSINESS QUERIES
[+] Q01: Total orders by status
[+] Q02: Monthly order volume and revenue trend
...

STEP 5: SAVING SQL RESULTS TO EXCEL
[+] Sheet 'Q01_OrdersByStatus' saved
...

STEP 6: CREATING 12 VISUALIZATIONS
[+] chart_01_monthly_orders.png
[+] chart_02_monthly_revenue.png
...

[SUCCESS] PROJECT COMPLETE
```

---

## 📁 Project Structure

```
olist_ecommerce/
│
├── README.md                          # This file
├── PROJECT_SUMMARY.md                 # Executive summary
├── requirements.txt                   # Python dependencies
│
├── eda_sql_analysis.py                # Main analysis script
│
├── Input CSV Files/
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   ├── olist_customers_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   └── product_category_name_translation.csv
│
├── outputs/
│   ├── olist_database.db              # SQLite database (9 tables)
│   └── sql_results.xlsx               # Excel: 20 sheets (query results)
│
└── charts/
    ├── chart_01_monthly_orders.png
    ├── chart_02_monthly_revenue.png
    ├── chart_03_order_status.png
    ├── chart_04_delivery_time_hist.png
    ├── chart_05_review_scores.png
    ├── chart_06_top_categories.png
    ├── chart_07_payment_types.png
    ├── chart_08_late_by_state.png
    ├── chart_09_hourly_orders.png
    ├── chart_10_weekday_orders.png
    ├── chart_11_price_distribution.png
    └── chart_12_items_per_order.png
```

---

## 💡 Key Findings

### 📦 E-Commerce Performance
- **Total Revenue:** R$ 13.28 million from 96,476 orders
- **Average Order Value:** R$ 137.59
- **Active Sellers:** 2,970 sellers across Brazilian states
- **Seller Concentration:** São Paulo, Minas Gerais, Rio de Janeiro lead

### 📍 Logistics & Delivery
- **Average Delivery Time:** 12.01 days
- **Late Delivery Rate:** 7.9% (acceptable)
- **Geographic Variation:** Late delivery rates range from 5% to 15% by state
- **Peak Delivery:** Most orders delivered within 10-15 days

### ⭐ Customer Satisfaction
- **Average Review Score:** 4.08/5.0
- **Positive Reviews:** 80%+ of orders rated 4-5 stars
- **Neutral Reviews:** ~8% rated 3 stars
- **Negative Reviews:** ~12% rated 1-2 stars

### 💳 Payment Patterns
- **Credit Card:** Primary payment method (73%)
- **Installments:** Average 2.7 installments when offered
- **Boleto:** Secondary method (14%)
- **Debit Card:** Tertiary method (6%)

### 📊 Product Insights
- **Top Categories:** Bed/bath, sports, furniture dominate
- **Price Range:** R$ 50 - R$ 5,000+ depending on category
- **Freight Costs:** Significant variance by weight and category
- **Multi-item Orders:** 35% of orders contain 2+ items

### ⏰ Temporal Patterns
- **Peak Hours:** 8 AM - 12 PM and 8 PM - 10 PM
- **Busiest Days:** Tuesday and Wednesday
- **Weekly Pattern:** Consistent ordering throughout the week
- **Seasonal Trend:** Growth from Aug 2017 to Aug 2018

---

## 🗄️ Database Schema

### SQLite Database Structure

#### **Table: orders** (99,441 rows)
```sql
Columns: order_id (PK), customer_id (FK), order_status, 
         order_purchase_timestamp, order_approved_at, 
         order_delivered_customer_date, order_estimated_delivery_date,
         [Engineered] delivery_time_days, estimated_days, approval_hours, 
         is_late, order_year, order_month, order_dayofweek, order_hour, 
         is_weekend
```

#### **Table: order_items** (112,650 rows)
```sql
Columns: order_id (FK), order_item_id, product_id (FK), seller_id (FK),
         shipping_limit_date, price, freight_value
```

#### **Table: products** (32,951 rows)
```sql
Columns: product_id (PK), product_category_name, product_name_length,
         product_description_length, product_photos_qty, product_weight_g,
         product_length_cm, product_height_cm, product_width_cm
```

#### **Table: sellers** (3,095 rows)
```sql
Columns: seller_id (PK), seller_zip_code_prefix, seller_city, seller_state
```

#### **Table: customers** (99,441 rows)
```sql
Columns: customer_id (PK), customer_unique_id, customer_zip_code_prefix,
         customer_city, customer_state
```

#### **Table: reviews** (99,224 rows)
```sql
Columns: review_id (PK), order_id (FK), review_score, review_comment_title,
         review_comment_message, review_creation_date, 
         review_answer_timestamp, [Engineered] sentiment
```

#### **Table: payments** (103,886 rows)
```sql
Columns: order_id (FK), payment_sequential, payment_type, 
         payment_installments, payment_value
```

#### **Table: geolocation** (1,000,163 rows)
```sql
Columns: geolocation_zip_code_prefix (PK), geolocation_lat, geolocation_lng,
         geolocation_city, geolocation_state
```

#### **Table: category_translation** (71 rows)
```sql
Columns: product_category_name, product_category_name_english
```

---

## 🛠️ Technologies Used

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.8+ | Core language |
| **Pandas** | 1.3+ | Data manipulation & analysis |
| **NumPy** | 1.20+ | Numerical computing |
| **SQLite3** | 3.0+ | Database management |
| **Matplotlib** | 3.3+ | Visualizations |
| **Seaborn** | 0.11+ | Advanced visualizations |
| **openpyxl** | 3.0+ | Excel export |

---

## 📤 Output Files

### 1. **SQLite Database** (`./outputs/olist_database.db`)
- 9 normalized tables
- Full data with engineered features
- Ready for custom SQL queries
- ~50 MB file size

### 2. **Excel Workbook** (`./outputs/sql_results.xlsx`)
- 20 sheets (one per query)
- Query results formatted and ready-to-use
- Suitable for reporting and presentations
- ~5 MB file size

### 3. **Visualization Charts** (`./charts/`)
- 12 PNG files at 300 DPI (publication quality)
- Professional styling and formatting
- Ready for reports, presentations, dashboards
- Each ~200-500 KB

---

## 🔍 Query Examples

### Example 1: Top 5 Products by Revenue
```sql
SELECT
    COALESCE(ct.product_category_name_english, p.product_category_name) as category,
    COUNT(oi.order_item_id) as items_sold,
    ROUND(SUM(oi.price), 2) as total_revenue,
    ROUND(AVG(oi.price), 2) as avg_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 5;
```

### Example 2: Late Delivery Analysis by State
```sql
SELECT
    c.customer_state,
    COUNT(*) as total_orders,
    SUM(o.is_late) as late_orders,
    ROUND(SUM(o.is_late)*100.0/COUNT(*), 2) as late_percentage
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.delivery_time_days IS NOT NULL
GROUP BY c.customer_state
ORDER BY late_percentage DESC
LIMIT 10;
```

### Example 3: Customer Repeat Purchase Analysis
```sql
SELECT
    CASE
        WHEN repeat_purchases = 1 THEN 'One-time'
        WHEN repeat_purchases = 2 THEN '2 purchases'
        WHEN repeat_purchases BETWEEN 3 AND 5 THEN '3-5 purchases'
        ELSE '6+ purchases'
    END as purchase_category,
    COUNT(*) as num_customers,
    ROUND(COUNT(*)*100.0/(SELECT COUNT(DISTINCT customer_unique_id) FROM customers), 2) as percentage
FROM (
    SELECT customer_unique_id, COUNT(*) as repeat_purchases
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY customer_unique_id
)
GROUP BY purchase_category;
```

---

## 📝 Script Features

### ✅ Error Handling
- Try-except wrappers on all SQL queries
- Fallback encoding (UTF-8 → Latin-1) for CSV files
- Graceful error messages and logging

### ✅ Data Quality
- Null count reporting per column
- Duplicate detection
- Data type validation

### ✅ Performance
- Efficient batch processing
- Optimized SQL queries
- Memory-conscious operations

### ✅ Professional Output
- High-resolution charts (300 DPI)
- Properly formatted Excel workbook
- Organized directory structure
- Detailed console logging

---

## 📊 Execution Statistics

| Metric | Result |
|--------|--------|
| **Total CSV Files** | 9 |
| **Total Rows Loaded** | 1,551,193 |
| **Total Data Processed** | ~200+ MB |
| **SQL Queries Executed** | 20/20 (100%) |
| **Visualizations Created** | 12/12 (100%) |
| **Excel Sheets Generated** | 20 |
| **Database Tables** | 9 |
| **Execution Time** | ~2-5 minutes |

---

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ **Data Loading & Cleaning** - Handling multiple CSV files with various encodings
- ✅ **Feature Engineering** - Creating meaningful features from raw data
- ✅ **SQL Queries** - Complex joins, aggregations, and window functions
- ✅ **Database Design** - Normalizing and structuring data
- ✅ **Data Visualization** - Creating professional charts and graphs
- ✅ **Business Analytics** - Deriving actionable insights
- ✅ **Python Best Practices** - Error handling, logging, modularization

---

## 📚 Additional Resources

- **Dataset Source:** Kaggle - Olist Brazilian E-Commerce Public Dataset
- **SQL Documentation:** [SQLite Official Docs](https://www.sqlite.org/docs.html)
- **Pandas Guide:** [Pandas Official Documentation](https://pandas.pydata.org/docs/)
- **Matplotlib Tutorial:** [Matplotlib Official Guide](https://matplotlib.org/stable/contents.html)

---

## ⚖️ License

This project is open source and available under the MIT License. See LICENSE file for details.

---

## 👤 Author

**Prince Chankya**  
GitHub: [@princechankya-max](https://github.com/princechankya-max)  
Project Date: June 3, 2026

---

## 🙏 Acknowledgments

- Kaggle for the Olist Brazilian E-Commerce dataset
- Open-source libraries: Pandas, SQLite, Matplotlib, Seaborn
- Data analysis community for best practices and insights

---

## 📧 Support & Contact

For questions, issues, or suggestions:
1. Open a GitHub issue in the repository
2. Contact via GitHub profile
3. Review PROJECT_SUMMARY.md for detailed project information

---

## ✨ Project Highlights

- 🏆 **Complete End-to-End Analysis** - From raw data to insights
- 📊 **20 Business Queries** - Addressing real business questions
- 🎨 **12 Professional Visualizations** - Publication-ready charts
- 💾 **Production-Ready Database** - SQLite with normalized schema
- 📈 **Scalable Architecture** - Can handle larger datasets
- 🔍 **Data Quality** - Comprehensive null/duplicate checks
- ⚡ **Performance Optimized** - Efficient processing pipeline

---

**Last Updated:** June 3, 2026  
**Status:** ✅ Complete and Production-Ready

