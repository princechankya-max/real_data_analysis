import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv('real_project.csv')

# Save results to file
with open('analysis_results.txt', 'w', encoding='utf-8') as f:
    f.write("\n" + "="*100 + "\n")
    f.write("COMPREHENSIVE E-COMMERCE DATA ANALYSIS REPORT\n")
    f.write("="*100 + "\n\n")
    
    # 1. DATASET OVERVIEW
    f.write("1. DATASET OVERVIEW\n")
    f.write("-" * 100 + "\n")
    f.write(f"Total Records: {len(df):,}\n")
    f.write(f"Total Columns: {len(df.columns)}\n")
    f.write(f"Dataset Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n")
    f.write(f"Date Range: {df['order_date'].min()} to {df['order_date'].max()}\n\n")
    
    # 2. COLUMN INFO
    f.write("2. COLUMN INFORMATION\n")
    f.write("-" * 100 + "\n")
    for col in df.columns:
        null_count = df[col].isna().sum()
        null_pct = (null_count / len(df) * 100)
        unique = df[col].nunique()
        dtype = df[col].dtype
        f.write(f"• {col}: {dtype} | Non-Null: {df[col].notna().sum():,} | Null: {null_count} ({null_pct:.2f}%) | Unique: {unique}\n")
    f.write("\n")
    
    # 3. MISSING DATA
    f.write("3. MISSING DATA ANALYSIS\n")
    f.write("-" * 100 + "\n")
    missing_data = df.isnull().sum()
    if missing_data.sum() == 0:
        f.write("✓ No missing values found - Dataset is complete!\n")
    else:
        for col in missing_data[missing_data > 0].index:
            pct = (missing_data[col] / len(df) * 100)
            f.write(f"  {col}: {missing_data[col]} missing ({pct:.2f}%)\n")
    f.write("\n")
    
    # 4. DUPLICATES
    f.write("4. DUPLICATE ANALYSIS\n")
    f.write("-" * 100 + "\n")
    total_dup = df.duplicated().sum()
    f.write(f"Total Duplicate Rows: {total_dup:,} ({(total_dup/len(df)*100):.2f}%)\n")
    f.write(f"Unique order_ids: {df['order_id'].nunique():,} (Duplicates: {len(df) - df['order_id'].nunique()})\n\n")
    
    # 5. CATEGORICAL ANALYSIS
    f.write("5. CATEGORICAL DATA ANALYSIS\n")
    f.write("-" * 100 + "\n")
    for col in ['country', 'device_type', 'traffic_source', 'payment_method', 'product_category', 'risk_label']:
        f.write(f"\n▸ {col.upper()}\n")
        counts = df[col].value_counts()
        for val, cnt in counts.items():
            pct = (cnt / len(df) * 100)
            f.write(f"  {val}: {cnt:,} ({pct:.2f}%)\n")
    f.write("\n")
    
    # 6. BINARY FEATURES
    f.write("6. BINARY FEATURES ANALYSIS\n")
    f.write("-" * 100 + "\n")
    for col in ['late_delivery_risk', 'address_mismatch', 'high_risk_ip', 'is_returned', 'is_fraud']:
        zero = (df[col] == 0).sum()
        one = (df[col] == 1).sum()
        f.write(f"• {col}: Yes={one:,} ({one/len(df)*100:.2f}%) | No={zero:,} ({zero/len(df)*100:.2f}%)\n")
    f.write("\n")
    
    # 7. NUMERIC STATISTICS
    f.write("7. NUMERIC COLUMNS - DESCRIPTIVE STATISTICS\n")
    f.write("-" * 100 + "\n")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        data = df[col].dropna()
        f.write(f"\n▸ {col.upper()}\n")
        f.write(f"  Count: {len(data)}\n")
        f.write(f"  Mean: {data.mean():.2f}\n")
        f.write(f"  Median: {data.median():.2f}\n")
        f.write(f"  Std Dev: {data.std():.2f}\n")
        f.write(f"  Min: {data.min():.2f}\n")
        f.write(f"  Max: {data.max():.2f}\n")
        f.write(f"  Q1 (25%): {data.quantile(0.25):.2f}\n")
        f.write(f"  Q3 (75%): {data.quantile(0.75):.2f}\n")
        f.write(f"  IQR: {data.quantile(0.75) - data.quantile(0.25):.2f}\n")
        
        # Outliers
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        outliers = data[(data < Q1 - 1.5*IQR) | (data > Q3 + 1.5*IQR)]
        f.write(f"  Outliers: {len(outliers)} ({(len(outliers)/len(data)*100):.2f}%)\n")
    f.write("\n")
    
    # 8. GEOGRAPHIC ANALYSIS
    f.write("8. GEOGRAPHIC ANALYSIS\n")
    f.write("-" * 100 + "\n")
    country_agg = df.groupby('country').agg({
        'order_id': 'count',
        'order_value_eur': ['sum', 'mean'],
        'is_fraud': 'sum',
        'is_returned': 'sum'
    }).round(2)
    for country in df['country'].unique():
        country_data = df[df['country'] == country]
        total = len(country_data)
        revenue = country_data['order_value_eur'].sum()
        avg_val = country_data['order_value_eur'].mean()
        fraud_rate = (country_data['is_fraud'].sum() / total * 100)
        return_rate = (country_data['is_returned'].sum() / total * 100)
        f.write(f"  {country}: Orders={total}, Revenue={revenue:.2f}€, Avg={avg_val:.2f}€, Fraud={fraud_rate:.2f}%, Returns={return_rate:.2f}%\n")
    f.write("\n")
    
    # 9. RISK & FRAUD ANALYSIS
    f.write("9. RISK & FRAUD ANALYSIS\n")
    f.write("-" * 100 + "\n")
    f.write(f"Total Fraud Cases: {df['is_fraud'].sum():,} ({df['is_fraud'].sum()/len(df)*100:.2f}%)\n")
    f.write(f"Total Returns: {df['is_returned'].sum():,} ({df['is_returned'].sum()/len(df)*100:.2f}%)\n")
    f.write(f"Late Delivery Risk: {df['late_delivery_risk'].sum():,} ({df['late_delivery_risk'].sum()/len(df)*100:.2f}%)\n")
    f.write(f"Address Mismatch: {df['address_mismatch'].sum():,} ({df['address_mismatch'].sum()/len(df)*100:.2f}%)\n")
    f.write(f"High Risk IP: {df['high_risk_ip'].sum():,} ({df['high_risk_ip'].sum()/len(df)*100:.2f}%)\n")
    f.write("\nRisk Label Distribution:\n")
    for label in df['risk_label'].unique():
        count = (df['risk_label'] == label).sum()
        f.write(f"  {label}: {count:,} ({count/len(df)*100:.2f}%)\n")
    f.write("\n")
    
    # 10. PAYMENT METHOD PERFORMANCE
    f.write("10. PAYMENT METHOD ANALYSIS\n")
    f.write("-" * 100 + "\n")
    for method in df['payment_method'].unique():
        method_data = df[df['payment_method'] == method]
        count = len(method_data)
        avg_val = method_data['order_value_eur'].mean()
        fraud_rate = (method_data['is_fraud'].sum() / count * 100)
        return_rate = (method_data['is_returned'].sum() / count * 100)
        f.write(f"  {method}: Count={count:,}, Avg={avg_val:.2f}€, Fraud={fraud_rate:.2f}%, Returns={return_rate:.2f}%\n")
    f.write("\n")
    
    # 11. PRODUCT CATEGORY ANALYSIS
    f.write("11. PRODUCT CATEGORY ANALYSIS\n")
    f.write("-" * 100 + "\n")
    for cat in sorted(df['product_category'].unique()):
        cat_data = df[df['product_category'] == cat]
        count = len(cat_data)
        avg_val = cat_data['order_value_eur'].mean()
        avg_review = cat_data['review_score'].mean()
        fraud_rate = (cat_data['is_fraud'].sum() / count * 100)
        return_rate = (cat_data['is_returned'].sum() / count * 100)
        f.write(f"  {cat}: Count={count:,}, Avg={avg_val:.2f}€, Fraud={fraud_rate:.2f}%, Returns={return_rate:.2f}%, Review={avg_review:.2f}\n")
    f.write("\n")
    
    # 12. TRAFFIC SOURCE
    f.write("12. TRAFFIC SOURCE ANALYSIS\n")
    f.write("-" * 100 + "\n")
    for source in sorted(df['traffic_source'].unique()):
        source_data = df[df['traffic_source'] == source]
        count = len(source_data)
        avg_val = source_data['order_value_eur'].mean()
        fraud_rate = (source_data['is_fraud'].sum() / count * 100)
        return_rate = (source_data['is_returned'].sum() / count * 100)
        f.write(f"  {source}: Count={count:,}, Avg={avg_val:.2f}€, Fraud={fraud_rate:.2f}%, Returns={return_rate:.2f}%\n")
    f.write("\n")
    
    # 13. DEVICE TYPE
    f.write("13. DEVICE TYPE ANALYSIS\n")
    f.write("-" * 100 + "\n")
    for device in sorted(df['device_type'].unique()):
        device_data = df[df['device_type'] == device]
        count = len(device_data)
        avg_val = device_data['order_value_eur'].mean()
        fraud_rate = (device_data['is_fraud'].sum() / count * 100)
        return_rate = (device_data['is_returned'].sum() / count * 100)
        f.write(f"  {device}: Count={count:,}, Avg={avg_val:.2f}€, Fraud={fraud_rate:.2f}%, Returns={return_rate:.2f}%\n")
    f.write("\n")
    
    # 14. CUSTOMER BEHAVIOR
    f.write("14. CUSTOMER BEHAVIOR ANALYSIS\n")
    f.write("-" * 100 + "\n")
    new_cust = df[df['previous_orders'] == 0]
    repeat_cust = df[df['previous_orders'] > 0]
    f.write(f"New Customers (0 previous orders): {len(new_cust):,} ({len(new_cust)/len(df)*100:.2f}%)\n")
    f.write(f"  Fraud Rate: {new_cust['is_fraud'].sum()/len(new_cust)*100:.2f}%\n")
    f.write(f"  Return Rate: {new_cust['is_returned'].sum()/len(new_cust)*100:.2f}%\n")
    f.write(f"Repeat Customers (>0 previous orders): {len(repeat_cust):,} ({len(repeat_cust)/len(df)*100:.2f}%)\n")
    f.write(f"  Fraud Rate: {repeat_cust['is_fraud'].sum()/len(repeat_cust)*100:.2f}%\n")
    f.write(f"  Return Rate: {repeat_cust['is_returned'].sum()/len(repeat_cust)*100:.2f}%\n")
    f.write("\n")
    
    # 15. DELIVERY ANALYSIS
    f.write("15. DELIVERY ANALYSIS\n")
    f.write("-" * 100 + "\n")
    f.write(f"Average Estimated Delivery Days: {df['delivery_days_estimated'].mean():.2f}\n")
    f.write(f"Average Shipping Distance: {df['shipping_distance_km'].mean():.2f} km\n")
    f.write(f"Max Shipping Distance: {df['shipping_distance_km'].max():.2f} km\n")
    f.write("Delivery Days Distribution:\n")
    for days in sorted(df['delivery_days_estimated'].unique()):
        count = (df['delivery_days_estimated'] == days).sum()
        f.write(f"  {int(days)} days: {count:,}\n")
    f.write("\n")
    
    # 16. REVIEW SCORES
    f.write("16. REVIEW SCORE ANALYSIS\n")
    f.write("-" * 100 + "\n")
    f.write(f"Average Review Score: {df['review_score'].mean():.2f}\n")
    f.write(f"Median Review Score: {df['review_score'].median():.2f}\n")
    f.write("Distribution:\n")
    for score in sorted(df['review_score'].unique()):
        count = (df['review_score'] == score).sum()
        f.write(f"  {score}: {count:,}\n")
    f.write("\n")
    
    # 17. PRICING & DISCOUNT
    f.write("17. PRICING & DISCOUNT ANALYSIS\n")
    f.write("-" * 100 + "\n")
    f.write(f"Total Revenue: {df['order_value_eur'].sum():,.2f}€\n")
    f.write(f"Average Order Value: {df['order_value_eur'].mean():.2f}€\n")
    f.write(f"Median Order Value: {df['order_value_eur'].median():.2f}€\n")
    f.write(f"Average Discount Rate: {df['discount_rate'].mean()*100:.2f}%\n")
    f.write(f"Max Discount Rate: {df['discount_rate'].max()*100:.2f}%\n")
    f.write(f"Orders with No Discount: {(df['discount_rate'] == 0).sum():,} ({(df['discount_rate'] == 0).sum()/len(df)*100:.2f}%)\n")
    f.write(f"Average Quantity per Order: {df['quantity'].mean():.2f} items\n")
    f.write("\n")
    
    # 18. CORRELATION ANALYSIS
    f.write("18. CORRELATION WITH KEY METRICS\n")
    f.write("-" * 100 + "\n")
    corr_matrix = df[numeric_cols].corr()
    f.write("Correlations with 'is_fraud':\n")
    fraud_corr = corr_matrix['is_fraud'].drop('is_fraud').abs().sort_values(ascending=False)
    for var, val in fraud_corr.head(5).items():
        actual = corr_matrix.loc[var, 'is_fraud']
        f.write(f"  {var}: {actual:.3f}\n")
    f.write("\nCorrelations with 'is_returned':\n")
    return_corr = corr_matrix['is_returned'].drop('is_returned').abs().sort_values(ascending=False)
    for var, val in return_corr.head(5).items():
        actual = corr_matrix.loc[var, 'is_returned']
        f.write(f"  {var}: {actual:.3f}\n")
    f.write("\n")
    
    # 19. KEY INSIGHTS
    f.write("19. KEY INSIGHTS & FINDINGS\n")
    f.write("-" * 100 + "\n")
    f.write("\n✓ HIGH IMPACT FINDINGS:\n")
    
    f.write("\n1. FRAUD PATTERNS:\n")
    fraud_data = df[df['is_fraud'] == 1]
    if len(fraud_data) > 0:
        f.write(f"   - Total fraud cases: {len(fraud_data)}\n")
        f.write(f"   - High Risk IP present: {fraud_data['high_risk_ip'].sum()/len(fraud_data)*100:.2f}% of frauds\n")
        f.write(f"   - Address Mismatch: {fraud_data['address_mismatch'].sum()/len(fraud_data)*100:.2f}% of frauds\n")
        f.write(f"   - Support Contacts > 0: {(fraud_data['customer_support_contacts'] > 0).sum()/len(fraud_data)*100:.2f}% of frauds\n")
    
    f.write("\n2. RETURN PATTERNS:\n")
    return_data = df[df['is_returned'] == 1]
    if len(return_data) > 0:
        f.write(f"   - Total returns: {len(return_data)}\n")
        f.write(f"   - Avg review of returned items: {return_data['review_score'].mean():.2f}\n")
        f.write(f"   - High discount in returns: {(return_data['discount_rate'] > 0.2).sum()/len(return_data)*100:.2f}%\n")
    
    f.write("\n3. TOP RISK COUNTRIES:\n")
    for country in df['country'].unique():
        c_data = df[df['country'] == country]
        fraud_rate = c_data['is_fraud'].sum() / len(c_data) * 100
        if fraud_rate > 0:
            f.write(f"   - {country}: {fraud_rate:.2f}% fraud rate\n")
    
    f.write("\n4. CUSTOMER VALUE:\n")
    f.write(f"   - New customers contribute to fraud: {new_cust['is_fraud'].sum()/len(new_cust)*100:.2f}%\n")
    f.write(f"   - Repeat customers' fraud rate: {repeat_cust['is_fraud'].sum()/len(repeat_cust)*100:.2f}%\n")
    
    f.write("\n" + "="*100 + "\n")
    f.write("END OF ANALYSIS REPORT\n")
    f.write("="*100 + "\n")

print("Analysis complete! Output saved to analysis_results.txt")
