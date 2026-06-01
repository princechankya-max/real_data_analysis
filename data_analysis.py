import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load the data
df = pd.read_csv('real_project.csv')

print("\n" + "="*100)
print("COMPREHENSIVE E-COMMERCE DATA ANALYSIS REPORT")
print("="*100 + "\n")

# ============================================================================
# 1. DATASET OVERVIEW
# ============================================================================
print("1. DATASET OVERVIEW")
print("-" * 100)
print(f"Total Records: {len(df):,}")
print(f"Total Columns: {len(df.columns)}")
print(f"Dataset Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print(f"Date Range: {df['order_date'].min()} to {df['order_date'].max()}")
print()

# ============================================================================
# 2. COLUMN-BY-COLUMN ANALYSIS
# ============================================================================
print("2. COLUMN INFORMATION & DATA QUALITY")
print("-" * 100)
for col in df.columns:
    null_count = df[col].isna().sum()
    null_pct = (null_count / len(df) * 100)
    unique = df[col].nunique()
    dtype = df[col].dtype
    print(f"► {col}")
    print(f"  Type: {dtype} | Non-Null: {df[col].notna().sum():,} | Null: {null_count} ({null_pct:.2f}%) | Unique: {unique}")
print()

# ============================================================================
# 3. MISSING DATA ANALYSIS
# ============================================================================
print("3. MISSING DATA ANALYSIS")
print("-" * 100)
missing_data = df.isnull().sum()
if missing_data.sum() == 0:
    print("✓ No missing values found - Dataset is complete!")
else:
    missing_summary = pd.DataFrame({
        'Column': missing_data.index,
        'Missing_Count': missing_data.values,
        'Missing_Percentage': (missing_data.values / len(df) * 100).round(2)
    })
    missing_summary = missing_summary[missing_summary['Missing_Count'] > 0].sort_values('Missing_Percentage', ascending=False)
    for idx, row in missing_summary.iterrows():
        print(f"  {row['Column']}: {row['Missing_Count']:,} missing ({row['Missing_Percentage']}%)")
print()

# ============================================================================
# 4. DUPLICATE ANALYSIS
# ============================================================================
print("4. DUPLICATE ANALYSIS")
print("-" * 100)
total_duplicates = df.duplicated().sum()
print(f"Total Duplicate Rows: {total_duplicates:,} ({(total_duplicates/len(df)*100):.2f}%)")
print(f"Unique order_ids: {df['order_id'].nunique():,}")
print(f"Duplicate order_ids: {len(df) - df['order_id'].nunique()}")
print()

# ============================================================================
# 5. CATEGORICAL DATA ANALYSIS
# ============================================================================
print("5. CATEGORICAL DATA ANALYSIS")
print("-" * 100)

categorical_cols = ['country', 'device_type', 'traffic_source', 'payment_method', 'product_category', 'risk_label']
for col in categorical_cols:
    print(f"\n► {col.upper()}")
    counts = df[col].value_counts()
    for val, cnt in counts.head(10).items():
        pct = (cnt / len(df) * 100)
        print(f"  {val}: {cnt:,} ({pct:.2f}%)")
    if len(counts) > 10:
        print(f"  ... and {len(counts) - 10} more categories")

print()

# ============================================================================
# 6. BINARY/BOOLEAN ANALYSIS
# ============================================================================
print("6. BINARY FEATURES ANALYSIS")
print("-" * 100)
binary_cols = ['late_delivery_risk', 'address_mismatch', 'high_risk_ip', 'is_returned', 'is_fraud']
for col in binary_cols:
    zero_count = (df[col] == 0).sum()
    one_count = (df[col] == 1).sum()
    zero_pct = (zero_count / len(df) * 100)
    one_pct = (one_count / len(df) * 100)
    print(f"► {col}")
    print(f"  0 (No/Normal): {zero_count:,} ({zero_pct:.2f}%)")
    print(f"  1 (Yes/Risk): {one_count:,} ({one_pct:.2f}%)")
print()

# ============================================================================
# 7. NUMERIC STATISTICS
# ============================================================================
print("7. NUMERIC COLUMNS - DESCRIPTIVE STATISTICS")
print("-" * 100)
numeric_cols = df.select_dtypes(include=[np.number]).columns
numeric_stats = df[numeric_cols].describe().round(2)
print(numeric_stats.to_string())
print()

# ============================================================================
# 8. DETAILED NUMERIC ANALYSIS
# ============================================================================
print("8. DETAILED NUMERIC ANALYSIS")
print("-" * 100)
for col in numeric_cols:
    print(f"\n► {col.upper()}")
    data = df[col].dropna()
    print(f"  Mean: {data.mean():.2f}")
    print(f"  Median: {data.median():.2f}")
    print(f"  Std Dev: {data.std():.2f}")
    print(f"  Min: {data.min():.2f}")
    print(f"  Max: {data.max():.2f}")
    print(f"  Q1 (25%): {data.quantile(0.25):.2f}")
    print(f"  Q3 (75%): {data.quantile(0.75):.2f}")
    print(f"  IQR: {data.quantile(0.75) - data.quantile(0.25):.2f}")
    
    # Outlier detection using IQR method
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    outliers = data[(data < Q1 - 1.5*IQR) | (data > Q3 + 1.5*IQR)]
    print(f"  Outliers (IQR method): {len(outliers)} ({(len(outliers)/len(data)*100):.2f}%)")
    
    # Skewness and Kurtosis
    skewness = stats.skew(data)
    kurtosis = stats.kurtosis(data)
    print(f"  Skewness: {skewness:.2f} {'(Right-skewed)' if skewness > 0 else '(Left-skewed)' if skewness < 0 else '(Symmetric)'}")
    print(f"  Kurtosis: {kurtosis:.2f}")

print()

# ============================================================================
# 9. CORRELATION ANALYSIS
# ============================================================================
print("9. CORRELATION ANALYSIS")
print("-" * 100)
correlation_matrix = df[numeric_cols].corr()
print("\nCorrelation Matrix (Top correlations with Target variables):")

# Find strong correlations with fraud and returns
for target in ['is_fraud', 'is_returned']:
    print(f"\nCorrelations with {target}:")
    correlations = correlation_matrix[target].drop(target).abs().sort_values(ascending=False)
    for var, corr_val in correlations.head(5).items():
        actual_corr = correlation_matrix.loc[var, target]
        print(f"  {var}: {actual_corr:.3f}")

print()

# ============================================================================
# 10. GEOGRAPHIC ANALYSIS
# ============================================================================
print("10. GEOGRAPHIC ANALYSIS")
print("-" * 100)
print("Top Countries by Order Volume:")
country_stats = df.groupby('country').agg({
    'order_id': 'count',
    'order_value_eur': ['sum', 'mean'],
    'is_fraud': ['sum', lambda x: (x.sum()/len(x)*100)],
    'is_returned': ['sum', lambda x: (x.sum()/len(x)*100)]
}).round(2)
country_stats.columns = ['Total_Orders', 'Total_Revenue', 'Avg_Order_Value', 'Fraud_Count', 'Fraud_Rate_%', 'Return_Count', 'Return_Rate_%']
country_stats = country_stats.sort_values('Total_Orders', ascending=False)
for country, row in country_stats.iterrows():
    print(f"  {country}: Orders={row['Total_Orders']:.0f}, Revenue={row['Total_Revenue']:.2f}€, Avg_Order={row['Avg_Order_Value']:.2f}€, Fraud_Rate={row['Fraud_Rate_%']:.2f}%, Return_Rate={row['Return_Rate_%']:.2f}%")

print()

# ============================================================================
# 11. RISK ASSESSMENT
# ============================================================================
print("11. RISK ASSESSMENT ANALYSIS")
print("-" * 100)
print("\n► Fraud Analysis:")
fraud_rate = (df['is_fraud'].sum() / len(df) * 100)
print(f"  Total Fraud Cases: {df['is_fraud'].sum():,} ({fraud_rate:.2f}%)")

fraud_by_risk = pd.crosstab(df['risk_label'], df['is_fraud'], margins=True)
print("\n  Fraud Distribution by Risk Label:")
for risk_label in fraud_by_risk.index[:-1]:
    total = fraud_by_risk.loc[risk_label].sum()
    fraud_count = fraud_by_risk.loc[risk_label, 1]
    print(f"    {risk_label}: {fraud_count} frauds out of {total:.0f} ({fraud_count/total*100:.2f}%)")

print("\n► Return Risk Analysis:")
return_rate = (df['is_returned'].sum() / len(df) * 100)
print(f"  Total Returns: {df['is_returned'].sum():,} ({return_rate:.2f}%)")

returns_by_risk = pd.crosstab(df['risk_label'], df['is_returned'], margins=True)
print("\n  Returns Distribution by Risk Label:")
for risk_label in returns_by_risk.index[:-1]:
    total = returns_by_risk.loc[risk_label].sum()
    return_count = returns_by_risk.loc[risk_label, 1]
    print(f"    {risk_label}: {return_count} returns out of {total:.0f} ({return_count/total*100:.2f}%)")

print("\n► Risk Factors:")
risk_factors = ['late_delivery_risk', 'address_mismatch', 'high_risk_ip', 'customer_support_contacts']
for factor in risk_factors:
    count = df[factor].sum()
    pct = (count / len(df) * 100)
    print(f"  {factor}: {count:,} ({pct:.2f}%)")

print()

# ============================================================================
# 12. PAYMENT METHOD ANALYSIS
# ============================================================================
print("12. PAYMENT METHOD ANALYSIS")
print("-" * 100)
payment_stats = df.groupby('payment_method').agg({
    'order_id': 'count',
    'order_value_eur': 'mean',
    'is_fraud': lambda x: (x.sum()/len(x)*100),
    'is_returned': lambda x: (x.sum()/len(x)*100)
}).round(2)
payment_stats.columns = ['Count', 'Avg_Value_EUR', 'Fraud_Rate_%', 'Return_Rate_%']
payment_stats = payment_stats.sort_values('Count', ascending=False)
print(payment_stats.to_string())
print()

# ============================================================================
# 13. PRODUCT CATEGORY ANALYSIS
# ============================================================================
print("13. PRODUCT CATEGORY ANALYSIS")
print("-" * 100)
category_stats = df.groupby('product_category').agg({
    'order_id': 'count',
    'order_value_eur': 'mean',
    'is_fraud': lambda x: (x.sum()/len(x)*100),
    'is_returned': lambda x: (x.sum()/len(x)*100),
    'review_score': 'mean'
}).round(2)
category_stats.columns = ['Count', 'Avg_Value_EUR', 'Fraud_Rate_%', 'Return_Rate_%', 'Avg_Review']
category_stats = category_stats.sort_values('Count', ascending=False)
print(category_stats.to_string())
print()

# ============================================================================
# 14. TRAFFIC SOURCE ANALYSIS
# ============================================================================
print("14. TRAFFIC SOURCE ANALYSIS")
print("-" * 100)
traffic_stats = df.groupby('traffic_source').agg({
    'order_id': 'count',
    'order_value_eur': 'mean',
    'is_fraud': lambda x: (x.sum()/len(x)*100),
    'is_returned': lambda x: (x.sum()/len(x)*100)
}).round(2)
traffic_stats.columns = ['Count', 'Avg_Value_EUR', 'Fraud_Rate_%', 'Return_Rate_%']
traffic_stats = traffic_stats.sort_values('Count', ascending=False)
print(traffic_stats.to_string())
print()

# ============================================================================
# 15. DEVICE TYPE ANALYSIS
# ============================================================================
print("15. DEVICE TYPE ANALYSIS")
print("-" * 100)
device_stats = df.groupby('device_type').agg({
    'order_id': 'count',
    'order_value_eur': 'mean',
    'is_fraud': lambda x: (x.sum()/len(x)*100),
    'is_returned': lambda x: (x.sum()/len(x)*100)
}).round(2)
device_stats.columns = ['Count', 'Avg_Value_EUR', 'Fraud_Rate_%', 'Return_Rate_%']
device_stats = device_stats.sort_values('Count', ascending=False)
print(device_stats.to_string())
print()

# ============================================================================
# 16. CUSTOMER BEHAVIOR ANALYSIS
# ============================================================================
print("16. CUSTOMER BEHAVIOR ANALYSIS")
print("-" * 100)
print(f"\n► Customer Age (Days):")
print(f"  New Customers (0-30 days): {(df['customer_age_days'] <= 30).sum():,} ({(df['customer_age_days'] <= 30).sum()/len(df)*100:.2f}%)")
print(f"  Regular Customers (31-365 days): {((df['customer_age_days'] > 30) & (df['customer_age_days'] <= 365)).sum():,} ({((df['customer_age_days'] > 30) & (df['customer_age_days'] <= 365)).sum()/len(df)*100:.2f}%)")
print(f"  Loyal Customers (>365 days): {(df['customer_age_days'] > 365).sum():,} ({(df['customer_age_days'] > 365).sum()/len(df)*100:.2f}%)")

print(f"\n► Previous Orders Distribution:")
for i in range(0, int(df['previous_orders'].max()) + 1):
    if i == int(df['previous_orders'].max()):
        count = (df['previous_orders'] >= i).sum()
        label = f"{i}+"
    else:
        count = (df['previous_orders'] == i).sum()
        label = str(i)
    if count > 0:
        print(f"  Customers with {label} previous orders: {count:,} ({count/len(df)*100:.2f}%)")

print(f"\n► Purchase Frequency Impact on Fraud/Returns:")
new_customers = df[df['previous_orders'] == 0]
repeat_customers = df[df['previous_orders'] > 0]
print(f"  New Customers - Fraud Rate: {(new_customers['is_fraud'].sum()/len(new_customers)*100):.2f}%, Return Rate: {(new_customers['is_returned'].sum()/len(new_customers)*100):.2f}%")
print(f"  Repeat Customers - Fraud Rate: {(repeat_customers['is_fraud'].sum()/len(repeat_customers)*100):.2f}%, Return Rate: {(repeat_customers['is_returned'].sum()/len(repeat_customers)*100):.2f}%")

print()

# ============================================================================
# 17. DELIVERY ANALYSIS
# ============================================================================
print("17. DELIVERY ANALYSIS")
print("-" * 100)
print(f"\nDelivery Performance:")
late_delivery_rate = (df['late_delivery_risk'].sum() / len(df) * 100)
print(f"  Late Delivery Risk: {df['late_delivery_risk'].sum():,} ({late_delivery_rate:.2f}%)")
print(f"  Average Estimated Delivery Days: {df['delivery_days_estimated'].mean():.2f}")
print(f"  Median Estimated Delivery Days: {df['delivery_days_estimated'].median():.2f}")
print(f"  Max Estimated Delivery Days: {df['delivery_days_estimated'].max():.0f}")
print(f"  Average Shipping Distance: {df['shipping_distance_km'].mean():.2f} km")

print("\n  Delivery Time Distribution:")
for days in sorted(df['delivery_days_estimated'].unique()):
    count = (df['delivery_days_estimated'] == days).sum()
    print(f"    {int(days)} days: {count:,} orders")

print()

# ============================================================================
# 18. REVIEW SCORE ANALYSIS
# ============================================================================
print("18. REVIEW SCORE ANALYSIS")
print("-" * 100)
print(f"Average Review Score: {df['review_score'].mean():.2f}")
print(f"Median Review Score: {df['review_score'].median():.2f}")
print(f"Std Dev: {df['review_score'].std():.2f}")
print(f"\nReview Score Distribution:")
for score in sorted(df['review_score'].unique()):
    count = (df['review_score'] == score).sum()
    pct = (count / len(df) * 100)
    print(f"  {score}: {count:,} ({pct:.2f}%)")

print()

# ============================================================================
# 19. DISCOUNT & PRICING ANALYSIS
# ============================================================================
print("19. DISCOUNT & PRICING ANALYSIS")
print("-" * 100)
print(f"Average Order Value: {df['order_value_eur'].mean():.2f}€")
print(f"Median Order Value: {df['order_value_eur'].median():.2f}€")
print(f"Total Revenue: {df['order_value_eur'].sum():,.2f}€")
print(f"Average Discount Rate: {(df['discount_rate'].mean()*100):.2f}%")
print(f"Max Discount Rate: {(df['discount_rate'].max()*100):.2f}%")
print(f"Orders with No Discount: {(df['discount_rate'] == 0).sum():,} ({(df['discount_rate'] == 0).sum()/len(df)*100:.2f}%)")
print(f"Average Quantity per Order: {df['quantity'].mean():.2f} items")

print("\n► Price Segmentation:")
price_segments = [0, 50, 100, 200, float('inf')]
labels = ['<50€', '50-100€', '100-200€', '>200€']
df['price_segment'] = pd.cut(df['order_value_eur'], bins=price_segments, labels=labels, include_lowest=True)
for segment in labels:
    count = (df['price_segment'] == segment).sum()
    if count > 0:
        avg_return = (df[df['price_segment'] == segment]['is_returned'].sum() / count * 100)
        avg_fraud = (df[df['price_segment'] == segment]['is_fraud'].sum() / count * 100)
        print(f"  {segment}: {count:,} orders, Return Rate: {avg_return:.2f}%, Fraud Rate: {avg_fraud:.2f}%")

print()

# ============================================================================
# 20. KEY INSIGHTS & PATTERNS
# ============================================================================
print("20. KEY INSIGHTS & RECOMMENDATIONS")
print("-" * 100)

print("\n► HIGH IMPACT FINDINGS:")

# Risk Label Distribution
risk_distribution = df['risk_label'].value_counts()
print(f"\n  1. Risk Distribution:")
for risk, count in risk_distribution.items():
    print(f"     {risk}: {count:,} ({count/len(df)*100:.2f}%)")

# Fraud hotspots
fraud_data = df[df['is_fraud'] == 1]
if len(fraud_data) > 0:
    print(f"\n  2. Fraud Detection Patterns:")
    print(f"     Total Frauds: {len(fraud_data)} ({fraud_data.shape[0]/len(df)*100:.2f}% of orders)")
    print(f"     Common traits in fraud cases:")
    print(f"     - High Risk IP present: {(fraud_data['high_risk_ip'].sum()/len(fraud_data)*100):.2f}%")
    print(f"     - Address Mismatch: {(fraud_data['address_mismatch'].sum()/len(fraud_data)*100):.2f}%")
    print(f"     - Support Contacts > 0: {(fraud_data['customer_support_contacts'] > 0).sum()/len(fraud_data)*100:.2f}%")
    print(f"     - High Discount Applied: {(fraud_data['discount_rate'] > 0.2).sum()/len(fraud_data)*100:.2f}%")

# Returns Analysis
returns_data = df[df['is_returned'] == 1]
if len(returns_data) > 0:
    print(f"\n  3. Return Risk Patterns:")
    print(f"     Total Returns: {len(returns_data)} ({returns_data.shape[0]/len(df)*100:.2f}% of orders)")
    print(f"     Marked as 'Return Risk': {(df['risk_label'] == 'Return Risk').sum():,} ({(df['risk_label'] == 'Return Risk').sum()/len(df)*100:.2f}% of total)")
    print(f"     Actual Returns (is_returned=1): {len(returns_data)} ({len(returns_data)/len(df)*100:.2f}% of total)")

# Traffic Source Performance
print(f"\n  4. Traffic Source Performance:")
traffic_performance = df.groupby('traffic_source').agg({
    'order_value_eur': 'mean',
    'is_fraud': lambda x: (x.sum()/len(x)*100),
    'review_score': 'mean'
}).round(2).sort_values('order_value_eur', ascending=False)
for traffic, row in traffic_performance.iterrows():
    print(f"     {traffic}: Avg Value={row['order_value_eur']:.2f}€, Fraud Rate={row['is_fraud']:.2f}%, Avg Review={row['review_score']:.2f}")

# Country Risk Profile
print(f"\n  5. Geographic Risk Profile:")
country_fraud_risk = df.groupby('country')['is_fraud'].apply(lambda x: (x.sum()/len(x)*100)).sort_values(ascending=False)
print(f"     Highest Fraud Risk Countries:")
for country, fraud_rate in country_fraud_risk.head(3).items():
    print(f"       {country}: {fraud_rate:.2f}%")

# Device Type Insights
print(f"\n  6. Device Type Insights:")
device_insights = df.groupby('device_type').agg({
    'order_value_eur': 'mean',
    'is_fraud': lambda x: (x.sum()/len(x)*100)
}).round(2).sort_values('order_value_eur', ascending=False)
for device, row in device_insights.iterrows():
    print(f"     {device}: Avg Value={row['order_value_eur']:.2f}€, Fraud Rate={row['is_fraud']:.2f}%")

print("\n" + "="*100)
print("END OF REPORT")
print("="*100 + "\n")
