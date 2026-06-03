"""
Olist Brazilian E-commerce Complete Data Analysis + SQL Project
Analyzes 9 CSV files with feature engineering, SQLite database, 20 SQL queries, 12 visualizations
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Create output directories
os.makedirs('./charts', exist_ok=True)
os.makedirs('./outputs', exist_ok=True)

print("\n" + "="*80)
print("OLIST BRAZILIAN E-COMMERCE DATA ANALYSIS PROJECT")
print("="*80 + "\n")

# ============================================================================
# STEP 1: DATA LOADING
# ============================================================================
print("STEP 1: LOADING DATA FILES\n")

def load_csv(filename):
    """Load CSV with fallback encoding"""
    try:
        df = pd.read_csv(f'./{filename}', encoding='utf-8', on_bad_lines='skip')
    except:
        df = pd.read_csv(f'./{filename}', encoding='latin-1', on_bad_lines='skip')
    return df

# Load all datasets
df_orders = load_csv('olist_orders_dataset.csv')
df_items = load_csv('olist_order_items_dataset.csv')
df_products = load_csv('olist_products_dataset.csv')
df_sellers = load_csv('olist_sellers_dataset.csv')
df_customers = load_csv('olist_customers_dataset.csv')
df_reviews = load_csv('olist_order_reviews_dataset.csv')
df_payments = load_csv('olist_order_payments_dataset.csv')
df_geolocation = load_csv('olist_geolocation_dataset.csv')
df_category_trans = load_csv('product_category_name_translation.csv')

# Store for later reference
dataframes = {
    'orders': df_orders,
    'order_items': df_items,
    'products': df_products,
    'sellers': df_sellers,
    'customers': df_customers,
    'reviews': df_reviews,
    'payments': df_payments,
    'geolocation': df_geolocation,
    'category_translation': df_category_trans
}

# Print data info
for name, df in dataframes.items():
    print(f"\n[*] {name.upper()}")
    print(f"  Shape: {df.shape}")
    print(f"  Null counts: {df.isnull().sum().sum()}")
    null_per_col = df.isnull().sum()
    if null_per_col.sum() > 0:
        print(f"    {dict(null_per_col[null_per_col > 0])}")
    print(f"  Duplicates: {df.duplicated().sum()}")

# ============================================================================
# STEP 2: FEATURE ENGINEERING
# ============================================================================
print("\n\nSTEP 2: FEATURE ENGINEERING\n")

# Parse datetime columns for orders
df_orders['order_purchase_timestamp'] = pd.to_datetime(
    df_orders['order_purchase_timestamp'], errors='coerce'
)
df_orders['order_approved_at'] = pd.to_datetime(
    df_orders['order_approved_at'], errors='coerce'
)
df_orders['order_delivered_customer_date'] = pd.to_datetime(
    df_orders['order_delivered_customer_date'], errors='coerce'
)
df_orders['order_estimated_delivery_date'] = pd.to_datetime(
    df_orders['order_estimated_delivery_date'], errors='coerce'
)

# Feature engineering on orders
df_orders['delivery_time_days'] = (
    df_orders['order_delivered_customer_date'] - df_orders['order_purchase_timestamp']
).dt.days
df_orders['estimated_days'] = (
    df_orders['order_estimated_delivery_date'] - df_orders['order_purchase_timestamp']
).dt.days
df_orders['approval_hours'] = (
    df_orders['order_approved_at'] - df_orders['order_purchase_timestamp']
).dt.total_seconds() / 3600
df_orders['is_late'] = (
    df_orders['order_delivered_customer_date'] > df_orders['order_estimated_delivery_date']
).astype(int)
df_orders['order_year'] = df_orders['order_purchase_timestamp'].dt.year
df_orders['order_month'] = df_orders['order_purchase_timestamp'].dt.month
df_orders['order_dayofweek'] = df_orders['order_purchase_timestamp'].dt.dayofweek
df_orders['order_hour'] = df_orders['order_purchase_timestamp'].dt.hour
df_orders['is_weekend'] = (df_orders['order_dayofweek'] >= 5).astype(int)

print("[+] Orders features engineered")

# Aggregate order items by order_id
df_items_agg = df_items.groupby('order_id').agg({
    'order_item_id': 'count',
    'price': ['sum', 'mean'],
    'freight_value': 'sum',
    'seller_id': 'nunique',
    'product_id': 'nunique'
}).reset_index()

df_items_agg.columns = [
    'order_id', 'num_items', 'total_price', 'avg_item_price',
    'total_freight', 'unique_sellers', 'unique_products'
]
df_items_agg['total_revenue'] = df_items_agg['total_price'] + df_items_agg['total_freight']
df_items_agg['freight_ratio'] = df_items_agg['total_freight'] / (df_items_agg['total_price'] + 1)

print("[+] Order items aggregated")

# Sentiment analysis on reviews
df_reviews['sentiment'] = df_reviews['review_score'].apply(
    lambda x: 'Positive' if x >= 4 else ('Neutral' if x == 3 else 'Negative')
)
print("[+] Review sentiment classified\n")

# ============================================================================
# STEP 3: CREATE SQLITE DATABASE
# ============================================================================
print("STEP 3: CREATING SQLITE DATABASE\n")

db_path = './outputs/olist_database.db'
conn = sqlite3.connect(db_path)

for table_name, df in dataframes.items():
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"[+] Table '{table_name}' created ({len(df)} rows)")

print(f"\n[+] Database saved to: {db_path}\n")

# ============================================================================
# STEP 4: 20 SQL BUSINESS QUERIES
# ============================================================================
print("STEP 4: RUNNING 20 SQL BUSINESS QUERIES\n")

query_results = {}
query_count = 0

# Q01: Total orders by status
try:
    q = """
    SELECT order_status as status, COUNT(*) as count,
           ROUND(COUNT(*)*100.0 / (SELECT COUNT(*) FROM orders), 2) as percentage
    FROM orders
    GROUP BY order_status
    ORDER BY count DESC
    """
    query_results['Q01_OrdersByStatus'] = pd.read_sql_query(q, conn)
    print("[+] Q01: Total orders by status")
    query_count += 1
except Exception as e:
    print(f"[x] Q01 Error: {e}")

# Q02: Monthly order volume + revenue trend
try:
    q = """
    SELECT
        o.order_year,
        o.order_month,
        COUNT(o.order_id) as num_orders,
        ROUND(SUM(COALESCE(oi.total_price, 0)), 2) as total_price,
        ROUND(SUM(COALESCE(oi.total_freight, 0)), 2) as total_freight,
        ROUND(SUM(COALESCE(oi.total_revenue, 0)), 2) as total_revenue
    FROM orders o
    LEFT JOIN (
        SELECT order_id, SUM(price) as total_price, SUM(freight_value) as total_freight,
                SUM(price + freight_value) as total_revenue
        FROM order_items
        GROUP BY order_id
    ) oi ON o.order_id = oi.order_id
    WHERE o.order_year IS NOT NULL AND o.order_month IS NOT NULL
    GROUP BY o.order_year, o.order_month
    ORDER BY o.order_year, o.order_month
    """
    query_results['Q02_MonthlyTrend'] = pd.read_sql_query(q, conn)
    print("[+] Q02: Monthly order volume and revenue trend")
    query_count += 1
except Exception as e:
    print(f"[x] Q02 Error: {e}")

# Q03: Top 10 customer states by order count + avg delivery days
try:
    q = """
    SELECT
        c.customer_state,
        COUNT(DISTINCT o.order_id) as num_orders,
        ROUND(AVG(o.delivery_time_days), 2) as avg_delivery_days,
        COUNT(DISTINCT c.customer_id) as num_customers
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.delivery_time_days IS NOT NULL
    GROUP BY c.customer_state
    ORDER BY num_orders DESC
    LIMIT 10
    """
    query_results['Q03_TopCustomerStates'] = pd.read_sql_query(q, conn)
    print("[+] Q03: Top 10 customer states by order count")
    query_count += 1
except Exception as e:
    print(f"[x] Q03 Error: {e}")

# Q04: Top 10 seller states by number of sellers + avg price
try:
    q = """
    SELECT
        s.seller_state,
        COUNT(DISTINCT s.seller_id) as num_sellers,
        ROUND(AVG(oi.price), 2) as avg_price,
        COUNT(oi.order_item_id) as num_items_sold,
        ROUND(SUM(oi.price), 2) as total_revenue
    FROM sellers s
    JOIN order_items oi ON s.seller_id = oi.seller_id
    GROUP BY s.seller_state
    ORDER BY num_sellers DESC
    LIMIT 10
    """
    query_results['Q04_TopSellerStates'] = pd.read_sql_query(q, conn)
    print("[+] Q04: Top 10 seller states")
    query_count += 1
except Exception as e:
    print(f"[x] Q04 Error: {e}")

# Q05: Average delivery_time_days by order_status
try:
    q = """
    SELECT
        order_status as status,
        COUNT(*) as count,
        ROUND(AVG(delivery_time_days), 2) as avg_delivery_days,
        MIN(delivery_time_days) as min_days,
        MAX(delivery_time_days) as max_days
    FROM orders
    WHERE delivery_time_days IS NOT NULL
    GROUP BY order_status
    ORDER BY avg_delivery_days DESC
    """
    query_results['Q05_DeliveryByStatus'] = pd.read_sql_query(q, conn)
    print("[+] Q05: Average delivery time by status")
    query_count += 1
except Exception as e:
    print(f"[x] Q05 Error: {e}")

# Q06: Overall late delivery % and count
try:
    q = """
    SELECT
        COUNT(*) as total_orders,
        SUM(is_late) as late_count,
        ROUND(SUM(is_late)*100.0/COUNT(*), 2) as late_percentage
    FROM orders
    WHERE delivery_time_days IS NOT NULL
    """
    query_results['Q06_LateDeliveryRate'] = pd.read_sql_query(q, conn)
    print("[+] Q06: Overall late delivery percentage")
    query_count += 1
except Exception as e:
    print(f"[x] Q06 Error: {e}")

# Q07: Top 10 most sold product categories
try:
    q = """
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
    """
    query_results['Q07_TopCategories'] = pd.read_sql_query(q, conn)
    print("[+] Q07: Top 10 most sold product categories")
    query_count += 1
except Exception as e:
    print(f"[x] Q07 Error: {e}")

# Q08: Revenue by product category (top 10)
try:
    q = """
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
    LIMIT 10
    """
    query_results['Q08_RevenueByCategory'] = pd.read_sql_query(q, conn)
    print("[+] Q08: Revenue by product category")
    query_count += 1
except Exception as e:
    print(f"[x] Q08 Error: {e}")

# Q09: Payment type distribution with avg order value
try:
    q = """
    SELECT
        payment_type,
        COUNT(*) as count,
        ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM payments), 2) as percentage,
        ROUND(AVG(payment_value), 2) as avg_value,
        ROUND(SUM(payment_value), 2) as total_value
    FROM payments
    GROUP BY payment_type
    ORDER BY count DESC
    """
    query_results['Q09_PaymentTypes'] = pd.read_sql_query(q, conn)
    print("[+] Q09: Payment type distribution")
    query_count += 1
except Exception as e:
    print(f"[x] Q09 Error: {e}")

# Q10: Average payment installments by payment type
try:
    q = """
    SELECT
        payment_type,
        ROUND(AVG(payment_installments), 2) as avg_installments,
        MAX(payment_installments) as max_installments,
        COUNT(*) as num_payments
    FROM payments
    WHERE payment_installments > 0
    GROUP BY payment_type
    ORDER BY avg_installments DESC
    """
    query_results['Q10_Installments'] = pd.read_sql_query(q, conn)
    print("[+] Q10: Average installments by payment type")
    query_count += 1
except Exception as e:
    print(f"[x] Q10 Error: {e}")

# Q11: Review score distribution
try:
    q = """
    SELECT
        review_score,
        COUNT(*) as count,
        ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM reviews), 2) as percentage
    FROM reviews
    WHERE review_score IS NOT NULL
    GROUP BY review_score
    ORDER BY review_score
    """
    query_results['Q11_ReviewScores'] = pd.read_sql_query(q, conn)
    print("[+] Q11: Review score distribution")
    query_count += 1
except Exception as e:
    print(f"[x] Q11 Error: {e}")

# Q12: Average review score by month
try:
    q = """
    SELECT
        SUBSTR(review_creation_date, 1, 7) as year_month,
        ROUND(AVG(review_score), 2) as avg_score,
        COUNT(*) as num_reviews
    FROM reviews
    WHERE review_creation_date IS NOT NULL
    GROUP BY year_month
    ORDER BY year_month
    """
    query_results['Q12_ReviewTrend'] = pd.read_sql_query(q, conn)
    print("[+] Q12: Average review score by month")
    query_count += 1
except Exception as e:
    print(f"[x] Q12 Error: {e}")

# Q13: Top 10 states with highest late delivery rate
try:
    q = """
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
    LIMIT 10
    """
    query_results['Q13_LatestByState'] = pd.read_sql_query(q, conn)
    print("[+] Q13: Top 10 states with highest late delivery rate")
    query_count += 1
except Exception as e:
    print(f"[x] Q13 Error: {e}")

# Q14: Avg freight_value vs avg price per category (top 10 by freight ratio)
try:
    q = """
    SELECT
        COALESCE(ct.product_category_name_english, p.product_category_name) as category,
        COUNT(oi.order_item_id) as num_items,
        ROUND(AVG(oi.price), 2) as avg_price,
        ROUND(AVG(oi.freight_value), 2) as avg_freight,
        ROUND(SUM(oi.freight_value) / (SUM(oi.price) + 1), 4) as freight_ratio
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
    GROUP BY category
    ORDER BY freight_ratio DESC
    LIMIT 10
    """
    query_results['Q14_FreightAnalysis'] = pd.read_sql_query(q, conn)
    print("[+] Q14: Freight vs price analysis")
    query_count += 1
except Exception as e:
    print(f"[x] Q14 Error: {e}")

# Q15: Top 10 sellers by total revenue
try:
    q = """
    SELECT
        s.seller_id,
        s.seller_state,
        COUNT(DISTINCT oi.order_id) as num_orders,
        COUNT(oi.order_item_id) as num_items,
        ROUND(SUM(oi.price), 2) as total_revenue,
        ROUND(AVG(oi.price), 2) as avg_price
    FROM sellers s
    JOIN order_items oi ON s.seller_id = oi.seller_id
    GROUP BY s.seller_id
    ORDER BY total_revenue DESC
    LIMIT 10
    """
    query_results['Q15_TopSellers'] = pd.read_sql_query(q, conn)
    print("[+] Q15: Top 10 sellers by revenue")
    query_count += 1
except Exception as e:
    print(f"[x] Q15 Error: {e}")

# Q16: Multi-item order analysis
try:
    q = """
    SELECT
        CASE
            WHEN num_items = 1 THEN '1 item'
            WHEN num_items = 2 THEN '2 items'
            WHEN num_items = 3 THEN '3 items'
            WHEN num_items = 4 THEN '4 items'
            ELSE '5+ items'
        END as items_category,
        COUNT(*) as num_orders,
        ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM (
            SELECT COUNT(*) as cnt FROM order_items GROUP BY order_id
        )), 2) as percentage
    FROM (
        SELECT order_id, COUNT(*) as num_items FROM order_items GROUP BY order_id
    )
    GROUP BY items_category
    ORDER BY items_category
    """
    query_results['Q16_MultiItemOrders'] = pd.read_sql_query(q, conn)
    print("[+] Q16: Multi-item order analysis")
    query_count += 1
except Exception as e:
    print(f"[x] Q16 Error: {e}")

# Q17: Peak ordering hours
try:
    q = """
    SELECT
        order_hour,
        COUNT(*) as num_orders,
        ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM orders WHERE order_hour IS NOT NULL), 2) as percentage
    FROM orders
    WHERE order_hour IS NOT NULL
    GROUP BY order_hour
    ORDER BY order_hour
    """
    query_results['Q17_HourlyOrders'] = pd.read_sql_query(q, conn)
    print("[+] Q17: Peak ordering hours")
    query_count += 1
except Exception as e:
    print(f"[x] Q17 Error: {e}")

# Q18: Day of week with most orders
try:
    q = """
    SELECT
        CASE order_dayofweek
            WHEN 0 THEN 'Monday'
            WHEN 1 THEN 'Tuesday'
            WHEN 2 THEN 'Wednesday'
            WHEN 3 THEN 'Thursday'
            WHEN 4 THEN 'Friday'
            WHEN 5 THEN 'Saturday'
            WHEN 6 THEN 'Sunday'
        END as day_of_week,
        order_dayofweek,
        COUNT(*) as num_orders,
        ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM orders WHERE order_dayofweek IS NOT NULL), 2) as percentage
    FROM orders
    WHERE order_dayofweek IS NOT NULL
    GROUP BY order_dayofweek
    ORDER BY order_dayofweek
    """
    query_results['Q18_WeekdayOrders'] = pd.read_sql_query(q, conn)
    print("[+] Q18: Day of week analysis")
    query_count += 1
except Exception as e:
    print(f"[x] Q18 Error: {e}")

# Q19: Customer repeat purchase rate
try:
    q = """
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
        WHERE c.customer_unique_id IS NOT NULL
        GROUP BY customer_unique_id
    )
    GROUP BY purchase_category
    """
    query_results['Q19_RepeatPurchases'] = pd.read_sql_query(q, conn)
    print("[+] Q19: Customer repeat purchase analysis")
    query_count += 1
except Exception as e:
    print(f"[x] Q19 Error: {e}")

# Q20: Full business KPI summary
try:
    q = """
    SELECT
        COUNT(DISTINCT o.order_id) as total_orders,
        ROUND(SUM(COALESCE(oi.price, 0)), 2) as total_revenue,
        ROUND(AVG(o.delivery_time_days), 2) as avg_delivery_days,
        ROUND(SUM(o.is_late)*100.0/COUNT(*), 2) as late_delivery_pct,
        ROUND(AVG(r.review_score), 2) as avg_review_score,
        COUNT(DISTINCT o.customer_id) as num_customers,
        COUNT(DISTINCT oi.seller_id) as num_sellers
    FROM orders o
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    WHERE o.delivery_time_days IS NOT NULL
    """
    query_results['Q20_KPISummary'] = pd.read_sql_query(q, conn)
    print("[+] Q20: Business KPI summary")
    query_count += 1
except Exception as e:
    print(f"[x] Q20 Error: {e}")

print(f"\n[+] {query_count}/20 queries executed successfully\n")

# ============================================================================
# STEP 5: SAVE SQL RESULTS TO EXCEL
# ============================================================================
print("STEP 5: SAVING SQL RESULTS TO EXCEL\n")

excel_path = './outputs/sql_results.xlsx'
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    for sheet_name, df in query_results.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"[+] Sheet '{sheet_name}' saved")

print(f"\n[+] All results saved to: {excel_path}\n")

# ============================================================================
# STEP 6: 12 VISUALIZATIONS
# ============================================================================
print("STEP 6: CREATING 12 VISUALIZATIONS\n")

# Set style
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    plt.style.use('ggplot')

chart_count = 0

# Chart 01: Monthly orders
try:
    df_monthly = query_results['Q02_MonthlyTrend'].copy()
    df_monthly['date'] = pd.to_datetime(
        df_monthly['order_year'].astype(str) + '-' + df_monthly['order_month'].astype(str).str.zfill(2)
    )

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df_monthly['date'], df_monthly['num_orders'], marker='o', linewidth=2, color='#1f77b4')
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Number of Orders', fontsize=11)
    ax.set_title('Monthly Order Volume Trend (2017-2018)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('./charts/chart_01_monthly_orders.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] chart_01_monthly_orders.png")
    chart_count += 1
except Exception as e:
    print(f"[x] Chart 01 Error: {e}")

# Chart 02: Monthly revenue
try:
    df_monthly = query_results['Q02_MonthlyTrend'].copy()
    df_monthly['date'] = pd.to_datetime(
        df_monthly['order_year'].astype(str) + '-' + df_monthly['order_month'].astype(str).str.zfill(2)
    )

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(df_monthly['date'].astype(str), df_monthly['total_revenue'], color='#2ca02c', alpha=0.8)
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Total Revenue (R$)', fontsize=11)
    ax.set_title('Monthly Total Revenue Trend', fontsize=13, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('./charts/chart_02_monthly_revenue.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] chart_02_monthly_revenue.png")
    chart_count += 1
except Exception as e:
    print(f"[x] Chart 02 Error: {e}")

# Chart 03: Order status
try:
    df_status = query_results['Q01_OrdersByStatus'].copy()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df_status['status'], df_status['count'], color='#ff7f0e', alpha=0.8)
    ax.set_xlabel('Count', fontsize=11)
    ax.set_ylabel('Order Status', fontsize=11)
    ax.set_title('Order Status Distribution', fontsize=13, fontweight='bold')

    for i, v in enumerate(df_status['count']):
        ax.text(v + 100, i, str(v), va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig('./charts/chart_03_order_status.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] chart_03_order_status.png")
    chart_count += 1
except Exception as e:
    print(f"[x] Chart 03 Error: {e}")

# Chart 04: Delivery time histogram
try:
    delivery_times = df_orders['delivery_time_days'].dropna()
    delivery_times = delivery_times[(delivery_times >= 0) & (delivery_times <= 60)]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.hist(delivery_times, bins=30, color='#d62728', alpha=0.7, edgecolor='black')
    ax.set_xlabel('Delivery Time (Days)', fontsize=11)
    ax.set_ylabel('Frequency', fontsize=11)
    ax.set_title('Distribution of Delivery Time (0-60 Days)', fontsize=13, fontweight='bold')
    ax.axvline(delivery_times.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {delivery_times.mean():.1f}')
    ax.legend()
    plt.tight_layout()
    plt.savefig('./charts/chart_04_delivery_time_hist.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] chart_04_delivery_time_hist.png")
    chart_count += 1
except Exception as e:
    print(f"[x] Chart 04 Error: {e}")

# Chart 05: Review scores
try:
    df_reviews_dist = query_results['Q11_ReviewScores'].copy()

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#d62728', '#ff7f0e', '#ffdd00', '#90ee90', '#2ca02c']
    ax.bar(df_reviews_dist['review_score'], df_reviews_dist['count'], color=colors[:len(df_reviews_dist)], alpha=0.8)
    ax.set_xlabel('Review Score', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Review Score Distribution', fontsize=13, fontweight='bold')
    ax.set_xticks([1, 2, 3, 4, 5])

    for i, v in enumerate(df_reviews_dist['count']):
        ax.text(df_reviews_dist['review_score'].iloc[i], v + 100, str(int(v)), ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig('./charts/chart_05_review_scores.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] chart_05_review_scores.png")
    chart_count += 1
except Exception as e:
    print(f"[x] Chart 05 Error: {e}")

# Chart 06: Top categories
try:
    df_cat = query_results['Q07_TopCategories'].copy().head(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(range(len(df_cat)), df_cat['num_items_sold'], color='#9467bd', alpha=0.8)
    ax.set_yticks(range(len(df_cat)))
    ax.set_yticklabels(df_cat['category'])
    ax.set_xlabel('Items Sold', fontsize=11)
    ax.set_title('Top 10 Product Categories by Items Sold', fontsize=13, fontweight='bold')

    for i, v in enumerate(df_cat['num_items_sold']):
        ax.text(v + 50, i, str(int(v)), va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig('./charts/chart_06_top_categories.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] chart_06_top_categories.png")
    chart_count += 1
except Exception as e:
    print(f"[x] Chart 06 Error: {e}")

# Chart 07: Payment types
try:
    df_pay = query_results['Q09_PaymentTypes'].copy()

    fig, ax = plt.subplots(figsize=(10, 6))
    colors_pie = plt.cm.Set3(range(len(df_pay)))
    wedges, texts, autotexts = ax.pie(df_pay['count'], labels=df_pay['payment_type'], autopct='%1.1f%%',
                                       colors=colors_pie, startangle=90)
    ax.set_title('Payment Type Distribution', fontsize=13, fontweight='bold')

    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')

    plt.tight_layout()
    plt.savefig('./charts/chart_07_payment_types.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] chart_07_payment_types.png")
    chart_count += 1
except Exception as e:
    print(f"[x] Chart 07 Error: {e}")

# Chart 08: Late delivery by state
try:
    df_late = query_results['Q13_LatestByState'].copy()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(range(len(df_late)), df_late['late_percentage'], color='#e377c2', alpha=0.8)
    ax.set_xticks(range(len(df_late)))
    ax.set_xticklabels(df_late['customer_state'], rotation=45)
    ax.set_ylabel('Late Delivery %', fontsize=11)
    ax.set_title('Top 10 States with Highest Late Delivery Rate', fontsize=13, fontweight='bold')

    for i, v in enumerate(df_late['late_percentage']):
        ax.text(i, v + 0.5, f'{v:.1f}%', ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig('./charts/chart_08_late_by_state.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] chart_08_late_by_state.png")
    chart_count += 1
except Exception as e:
    print(f"[x] Chart 08 Error: {e}")

# Chart 09: Hourly orders
try:
    df_hourly = query_results['Q17_HourlyOrders'].copy()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(df_hourly['order_hour'], df_hourly['num_orders'], color='#1f77b4', alpha=0.8)
    ax.set_xlabel('Hour of Day', fontsize=11)
    ax.set_ylabel('Number of Orders', fontsize=11)
    ax.set_title('Orders by Hour of Day', fontsize=13, fontweight='bold')
    ax.set_xticks(range(0, 24, 2))

    plt.tight_layout()
    plt.savefig('./charts/chart_09_hourly_orders.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] chart_09_hourly_orders.png")
    chart_count += 1
except Exception as e:
    print(f"[x] Chart 09 Error: {e}")

# Chart 10: Weekday orders
try:
    df_weekday = query_results['Q18_WeekdayOrders'].copy()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(df_weekday['day_of_week'], df_weekday['num_orders'], color='#2ca02c', alpha=0.8)
    ax.set_ylabel('Number of Orders', fontsize=11)
    ax.set_title('Orders by Day of Week', fontsize=13, fontweight='bold')
    plt.xticks(rotation=45)

    for i, v in enumerate(df_weekday['num_orders']):
        ax.text(i, v + 100, str(int(v)), ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig('./charts/chart_10_weekday_orders.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] chart_10_weekday_orders.png")
    chart_count += 1
except Exception as e:
    print(f"[x] Chart 10 Error: {e}")

# Chart 11: Price distribution by top 5 categories
try:
    df_cat_top = query_results['Q07_TopCategories'].copy().head(5)['category'].tolist()

    # Filter items for top categories
    df_items_for_chart = df_items.copy()
    df_items_for_chart = df_items_for_chart.merge(df_products[['product_id', 'product_category_name']], on='product_id')
    df_items_for_chart = df_items_for_chart[df_items_for_chart['product_category_name'].isin(df_cat_top)]

    if len(df_items_for_chart) > 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        category_data = [df_items_for_chart[df_items_for_chart['product_category_name'] == cat]['price'].values
                         for cat in df_cat_top]
        ax.boxplot(category_data, labels=df_cat_top)
        ax.set_ylabel('Price (R$)', fontsize=11)
        ax.set_title('Price Distribution by Top 5 Product Categories', fontsize=13, fontweight='bold')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('./charts/chart_11_price_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("[+] chart_11_price_distribution.png")
        chart_count += 1
    else:
        print("[x] Chart 11: No data available")
except Exception as e:
    print(f"[x] Chart 11 Error: {e}")

# Chart 12: Items per order distribution
try:
    df_multi = query_results['Q16_MultiItemOrders'].copy()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(range(len(df_multi)), df_multi['num_orders'], color='#ff7f0e', alpha=0.8)
    ax.set_xticks(range(len(df_multi)))
    ax.set_xticklabels(df_multi['items_category'], rotation=0)
    ax.set_ylabel('Number of Orders', fontsize=11)
    ax.set_title('Distribution of Items per Order', fontsize=13, fontweight='bold')

    for i, v in enumerate(df_multi['num_orders']):
        ax.text(i, v + 500, str(int(v)), ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig('./charts/chart_12_items_per_order.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] chart_12_items_per_order.png")
    chart_count += 1
except Exception as e:
    print(f"[x] Chart 12 Error: {e}")

# ============================================================================
# COMPLETION SUMMARY
# ============================================================================
print("\n" + "="*80)
print(f"[SUCCESS] PROJECT 1 COMPLETE")
print("="*80)
print(f"\n[DATA] RESULTS SUMMARY:")
print(f"   • {query_count} SQL queries executed")
print(f"   • {chart_count} visualizations saved to ./charts/")
print(f"   • SQL results saved to: {excel_path}")
print(f"   • Database saved to: {db_path}")
print(f"\n[FILES] OUTPUT FILES:")
print(f"   • eda_sql_analysis.py (this script)")
print(f"   • ./outputs/olist_database.db (SQLite database with 9 tables)")
print(f"   • ./outputs/sql_results.xlsx (20 query results, 20 sheets)")
print(f"   • ./charts/ (12 PNG visualizations)")
print("\n" + "="*80 + "\n")

conn.close()