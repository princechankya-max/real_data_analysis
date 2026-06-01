#!/usr/bin/env python3
"""Comprehensive E-Commerce Data Analysis Report Generator"""

import pandas as pd
import numpy as np
import sys

try:
    # Read the CSV file
    df = pd.read_csv('real_project.csv')
    
    # Generate analysis report
    report = []
    report.append("\n" + "="*120)
    report.append("COMPREHENSIVE E-COMMERCE DATA ANALYSIS REPORT")
    report.append("="*120 + "\n")
    
    # ==================== SECTION 1: OVERVIEW ====================
    report.append("1. DATASET OVERVIEW")
    report.append("-" * 120)
    report.append(f"Total Records:              {len(df):>12,}")
    report.append(f"Total Columns:              {len(df.columns):>12}")
    report.append(f"Memory Usage:               {df.memory_usage(deep=True).sum() / 1024**2:>12.2f} MB")
    report.append(f"Date Range:                 {df['order_date'].min()} to {df['order_date'].max()}")
    report.append("")
    
    # ==================== SECTION 2: COLUMN INFO ====================
    report.append("2. COLUMN DETAILS & DATA QUALITY")
    report.append("-" * 120)
    for col in df.columns:
        null_ct = df[col].isna().sum()
        null_pct = (null_ct / len(df) * 100)
        unique = df[col].nunique()
        dtype = str(df[col].dtype)
        report.append(f"  {col:<30} Type: {dtype:<8} Non-Null: {df[col].notna().sum():>6,} Null: {null_ct:>5} ({null_pct:>5.2f}%) Unique: {unique:>6}")
    report.append("")
    
    # ==================== SECTION 3: MISSING DATA ====================
    report.append("3. MISSING DATA ANALYSIS")
    report.append("-" * 120)
    missing = df.isnull().sum()
    if missing.sum() == 0:
        report.append("✓ No missing values - Dataset is COMPLETE and CLEAN")
    else:
        for col in missing[missing > 0].index:
            pct = (missing[col] / len(df) * 100)
            report.append(f"  {col}: {missing[col]:,} missing ({pct:.2f}%)")
    report.append("")
    
    # ==================== SECTION 4: DUPLICATES ====================
    report.append("4. DUPLICATE ANALYSIS")
    report.append("-" * 120)
    total_dup = df.duplicated().sum()
    unique_orders = df['order_id'].nunique()
    dup_orders = len(df) - unique_orders
    report.append(f"Total Duplicate Rows:       {total_dup:>12,} ({total_dup/len(df)*100:>6.2f}%)")
    report.append(f"Unique Order IDs:           {unique_orders:>12,}")
    report.append(f"Duplicate Order IDs:        {dup_orders:>12,}")
    report.append("")
    
    # ==================== SECTION 5: CATEGORICAL DATA ====================
    report.append("5. CATEGORICAL DATA DISTRIBUTION")
    report.append("-" * 120)
    
    categorical_cols = ['country', 'device_type', 'traffic_source', 'payment_method', 'product_category', 'risk_label']
    for col in categorical_cols:
        report.append(f"\n► {col.upper()} ({df[col].nunique()} unique values)")
        counts = df[col].value_counts()
        for val, cnt in counts.items():
            pct = (cnt / len(df) * 100)
            bar_len = int(pct / 2)
            bar = "█" * bar_len
            report.append(f"  {val:<25} {cnt:>8,} ({pct:>6.2f}%) {bar}")
    report.append("")
    
    # ==================== SECTION 6: BINARY FEATURES ====================
    report.append("6. BINARY FEATURES ANALYSIS")
    report.append("-" * 120)
    binary_cols = ['late_delivery_risk', 'address_mismatch', 'high_risk_ip', 'is_returned', 'is_fraud']
    for col in binary_cols:
        zero_ct = (df[col] == 0).sum()
        one_ct = (df[col] == 1).sum()
        zero_pct = (zero_ct / len(df) * 100)
        one_pct = (one_ct / len(df) * 100)
        report.append(f"\n{col}:")
        report.append(f"  No/Normal:  {zero_ct:>10,} ({zero_pct:>6.2f}%) {'█' * int(zero_pct/2)}")
        report.append(f"  Yes/Risk:   {one_ct:>10,} ({one_pct:>6.2f}%) {'█' * int(one_pct/2)}")
    report.append("")
    
    # ==================== SECTION 7: NUMERIC STATISTICS ====================
    report.append("7. NUMERIC COLUMNS - DETAILED STATISTICS")
    report.append("-" * 120)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        data = df[col].dropna()
        Q1, Q3 = data.quantile([0.25, 0.75])
        IQR = Q3 - Q1
        outliers = len(data[(data < Q1 - 1.5*IQR) | (data > Q3 + 1.5*IQR)])
        
        report.append(f"\n{col}:")
        report.append(f"  Count: {len(data):,} | Mean: {data.mean():.2f} | Median: {data.median():.2f} | Std: {data.std():.2f}")
        report.append(f"  Min: {data.min():.2f} | Q1: {Q1:.2f} | Q3: {Q3:.2f} | Max: {data.max():.2f} | IQR: {IQR:.2f}")
        report.append(f"  Outliers (IQR method): {outliers} ({outliers/len(data)*100:.2f}%)")
    report.append("")
    
    # ==================== SECTION 8: GEOGRAPHIC ANALYSIS ====================
    report.append("8. GEOGRAPHIC ANALYSIS")
    report.append("-" * 120)
    report.append(f"{'Country':<20} {'Orders':>10} {'Revenue (€)':>15} {'Avg Value':>12} {'Fraud %':>10} {'Return %':>10}")
    report.append("-" * 120)
    for country in sorted(df['country'].unique()):
        c_data = df[df['country'] == country]
        total = len(c_data)
        revenue = c_data['order_value_eur'].sum()
        avg_val = c_data['order_value_eur'].mean()
        fraud_pct = (c_data['is_fraud'].sum() / total * 100)
        return_pct = (c_data['is_returned'].sum() / total * 100)
        report.append(f"{country:<20} {total:>10,} {revenue:>15,.2f} {avg_val:>12.2f} {fraud_pct:>10.2f} {return_pct:>10.2f}")
    report.append("")
    
    # ==================== SECTION 9: RISK ASSESSMENT ====================
    report.append("9. RISK & FRAUD ASSESSMENT")
    report.append("-" * 120)
    fraud_ct = df['is_fraud'].sum()
    fraud_pct = (fraud_ct / len(df) * 100)
    return_ct = df['is_returned'].sum()
    return_pct = (return_ct / len(df) * 100)
    
    report.append(f"\nFRAUD ANALYSIS:")
    report.append(f"  Total Fraud Cases:         {fraud_ct:>12,} ({fraud_pct:>6.2f}%)")
    report.append(f"  High Risk IP Present:      {df['high_risk_ip'].sum():>12,} cases")
    report.append(f"  Address Mismatch:          {df['address_mismatch'].sum():>12,} cases")
    report.append(f"  Customer Support Contact:  {(df['customer_support_contacts'] > 0).sum():>12,} cases")
    
    if fraud_ct > 0:
        fraud_data = df[df['is_fraud'] == 1]
        report.append(f"\n  In fraud cases:")
        report.append(f"    - High Risk IP:        {fraud_data['high_risk_ip'].sum()/fraud_ct*100:>8.2f}%")
        report.append(f"    - Address Mismatch:    {fraud_data['address_mismatch'].sum()/fraud_ct*100:>8.2f}%")
        report.append(f"    - Support Contacts:    {(fraud_data['customer_support_contacts'] > 0).sum()/fraud_ct*100:>8.2f}%")
    
    report.append(f"\nRETURN ANALYSIS:")
    report.append(f"  Total Returns:             {return_ct:>12,} ({return_pct:>6.2f}%)")
    report.append(f"  Late Delivery Risk:        {df['late_delivery_risk'].sum():>12,} cases")
    
    report.append(f"\nRISK LABEL DISTRIBUTION:")
    for label in df['risk_label'].unique():
        ct = (df['risk_label'] == label).sum()
        pct = (ct / len(df) * 100)
        report.append(f"  {label:<25} {ct:>10,} ({pct:>6.2f}%)")
    report.append("")
    
    # ==================== SECTION 10: PAYMENT METHODS ====================
    report.append("10. PAYMENT METHOD PERFORMANCE")
    report.append("-" * 120)
    report.append(f"{'Payment Method':<20} {'Orders':>10} {'Avg Value':>12} {'Fraud %':>10} {'Return %':>10}")
    report.append("-" * 120)
    for method in sorted(df['payment_method'].unique()):
        m_data = df[df['payment_method'] == method]
        ct = len(m_data)
        avg_val = m_data['order_value_eur'].mean()
        fraud_pct = (m_data['is_fraud'].sum() / ct * 100) if ct > 0 else 0
        return_pct = (m_data['is_returned'].sum() / ct * 100) if ct > 0 else 0
        report.append(f"{method:<20} {ct:>10,} {avg_val:>12.2f} {fraud_pct:>10.2f} {return_pct:>10.2f}")
    report.append("")
    
    # ==================== SECTION 11: PRODUCT CATEGORIES ====================
    report.append("11. PRODUCT CATEGORY PERFORMANCE")
    report.append("-" * 120)
    report.append(f"{'Category':<25} {'Orders':>10} {'Avg Value':>12} {'Fraud %':>10} {'Return %':>10} {'Avg Review':>12}")
    report.append("-" * 120)
    for cat in sorted(df['product_category'].unique()):
        cat_data = df[df['product_category'] == cat]
        ct = len(cat_data)
        avg_val = cat_data['order_value_eur'].mean()
        fraud_pct = (cat_data['is_fraud'].sum() / ct * 100) if ct > 0 else 0
        return_pct = (cat_data['is_returned'].sum() / ct * 100) if ct > 0 else 0
        avg_review = cat_data['review_score'].mean()
        report.append(f"{cat:<25} {ct:>10,} {avg_val:>12.2f} {fraud_pct:>10.2f} {return_pct:>10.2f} {avg_review:>12.2f}")
    report.append("")
    
    # ==================== SECTION 12: TRAFFIC SOURCES ====================
    report.append("12. TRAFFIC SOURCE ANALYSIS")
    report.append("-" * 120)
    report.append(f"{'Traffic Source':<20} {'Orders':>10} {'Avg Value':>12} {'Fraud %':>10} {'Return %':>10}")
    report.append("-" * 120)
    for source in sorted(df['traffic_source'].unique()):
        s_data = df[df['traffic_source'] == source]
        ct = len(s_data)
        avg_val = s_data['order_value_eur'].mean()
        fraud_pct = (s_data['is_fraud'].sum() / ct * 100) if ct > 0 else 0
        return_pct = (s_data['is_returned'].sum() / ct * 100) if ct > 0 else 0
        report.append(f"{source:<20} {ct:>10,} {avg_val:>12.2f} {fraud_pct:>10.2f} {return_pct:>10.2f}")
    report.append("")
    
    # ==================== SECTION 13: DEVICE TYPE ====================
    report.append("13. DEVICE TYPE ANALYSIS")
    report.append("-" * 120)
    report.append(f"{'Device Type':<20} {'Orders':>10} {'Avg Value':>12} {'Fraud %':>10} {'Return %':>10}")
    report.append("-" * 120)
    for device in sorted(df['device_type'].unique()):
        d_data = df[df['device_type'] == device]
        ct = len(d_data)
        avg_val = d_data['order_value_eur'].mean()
        fraud_pct = (d_data['is_fraud'].sum() / ct * 100) if ct > 0 else 0
        return_pct = (d_data['is_returned'].sum() / ct * 100) if ct > 0 else 0
        report.append(f"{device:<20} {ct:>10,} {avg_val:>12.2f} {fraud_pct:>10.2f} {return_pct:>10.2f}")
    report.append("")
    
    # ==================== SECTION 14: CUSTOMER BEHAVIOR ====================
    report.append("14. CUSTOMER BEHAVIOR ANALYSIS")
    report.append("-" * 120)
    new_cust = df[df['previous_orders'] == 0]
    repeat_cust = df[df['previous_orders'] > 0]
    loyal_cust = df[df['previous_orders'] >= 5]
    
    report.append(f"\nCUSTOMER SEGMENTS:")
    report.append(f"  New Customers (0 orders):     {len(new_cust):>10,} ({len(new_cust)/len(df)*100:>6.2f}%)")
    report.append(f"    Fraud Rate:                 {new_cust['is_fraud'].sum()/len(new_cust)*100:>10.2f}%")
    report.append(f"    Return Rate:                {new_cust['is_returned'].sum()/len(new_cust)*100:>10.2f}%")
    
    report.append(f"\n  Repeat Customers (>0 orders): {len(repeat_cust):>10,} ({len(repeat_cust)/len(df)*100:>6.2f}%)")
    report.append(f"    Fraud Rate:                 {repeat_cust['is_fraud'].sum()/len(repeat_cust)*100:>10.2f}%")
    report.append(f"    Return Rate:                {repeat_cust['is_returned'].sum()/len(repeat_cust)*100:>10.2f}%")
    
    report.append(f"\n  Loyal Customers (5+ orders): {len(loyal_cust):>10,} ({len(loyal_cust)/len(df)*100:>6.2f}%)")
    report.append(f"    Fraud Rate:                 {loyal_cust['is_fraud'].sum()/len(loyal_cust)*100:>10.2f}%")
    report.append(f"    Return Rate:                {loyal_cust['is_returned'].sum()/len(loyal_cust)*100:>10.2f}%")
    
    report.append(f"\nCUSTOMER AGE DISTRIBUTION:")
    report.append(f"  Average Customer Age:         {df['customer_age_days'].mean():>10.0f} days")
    report.append(f"  Median Customer Age:          {df['customer_age_days'].median():>10.0f} days")
    report.append("")
    
    # ==================== SECTION 15: DELIVERY ====================
    report.append("15. DELIVERY & SHIPPING ANALYSIS")
    report.append("-" * 120)
    report.append(f"Estimated Delivery Days:    {df['delivery_days_estimated'].mean():>12.2f} days (avg)")
    report.append(f"Shipping Distance:          {df['shipping_distance_km'].mean():>12.2f} km (avg)")
    report.append(f"Max Shipping Distance:      {df['shipping_distance_km'].max():>12.2f} km")
    report.append(f"Late Delivery Risk Cases:   {df['late_delivery_risk'].sum():>12,} ({df['late_delivery_risk'].sum()/len(df)*100:>6.2f}%)")
    report.append(f"\nDelivery Time Distribution:")
    for days in sorted(df['delivery_days_estimated'].unique()):
        ct = (df['delivery_days_estimated'] == days).sum()
        pct = (ct / len(df) * 100)
        report.append(f"  {int(days)} days: {ct:>10,} orders ({pct:>6.2f}%)")
    report.append("")
    
    # ==================== SECTION 16: REVIEW SCORES ====================
    report.append("16. CUSTOMER REVIEW SCORE ANALYSIS")
    report.append("-" * 120)
    report.append(f"Average Review Score:       {df['review_score'].mean():>12.2f} / 5.0")
    report.append(f"Median Review Score:        {df['review_score'].median():>12.2f}")
    report.append(f"Distribution:")
    for score in sorted(df['review_score'].unique()):
        ct = (df['review_score'] == score).sum()
        pct = (ct / len(df) * 100)
        report.append(f"  {score}/5: {ct:>10,} reviews ({pct:>6.2f}%)")
    report.append("")
    
    # ==================== SECTION 17: PRICING ====================
    report.append("17. PRICING & DISCOUNT ANALYSIS")
    report.append("-" * 120)
    report.append(f"Total Revenue Generated:    {df['order_value_eur'].sum():>12,.2f}€")
    report.append(f"Average Order Value:        {df['order_value_eur'].mean():>12.2f}€")
    report.append(f"Median Order Value:         {df['order_value_eur'].median():>12.2f}€")
    report.append(f"Average Quantity per Order: {df['quantity'].mean():>12.2f} items")
    report.append(f"Average Discount Rate:      {df['discount_rate'].mean()*100:>12.2f}%")
    report.append(f"Max Discount Rate:          {df['discount_rate'].max()*100:>12.2f}%")
    report.append(f"Orders with No Discount:    {(df['discount_rate'] == 0).sum():>12,} ({(df['discount_rate'] == 0).sum()/len(df)*100:>6.2f}%)")
    report.append("")
    
    # ==================== SECTION 18: KEY INSIGHTS ====================
    report.append("18. KEY INSIGHTS & RECOMMENDATIONS")
    report.append("="*120)
    
    report.append("\n⚠️  CRITICAL FINDINGS:\n")
    
    # Most fraudulent countries
    fraud_by_country = df.groupby('country')['is_fraud'].agg(['sum', 'count'])
    fraud_by_country['rate'] = (fraud_by_country['sum'] / fraud_by_country['count'] * 100).round(2)
    high_fraud = fraud_by_country[fraud_by_country['rate'] > 0].sort_values('rate', ascending=False).head(3)
    
    report.append("1. GEOGRAPHIC RISK HOTSPOTS:")
    if len(high_fraud) > 0:
        for country, row in high_fraud.iterrows():
            report.append(f"   ► {country}: {row['rate']:.2f}% fraud rate ({int(row['sum'])} cases)")
    else:
        report.append("   ► No significant geographic fraud patterns detected")
    
    # Payment method risk
    fraud_by_payment = df.groupby('payment_method')['is_fraud'].agg(['sum', 'count'])
    fraud_by_payment['rate'] = (fraud_by_payment['sum'] / fraud_by_payment['count'] * 100).round(2)
    high_fraud_payment = fraud_by_payment[fraud_by_payment['rate'] > 0].sort_values('rate', ascending=False).head(3)
    
    report.append("\n2. RISKY PAYMENT METHODS:")
    if len(high_fraud_payment) > 0:
        for method, row in high_fraud_payment.iterrows():
            report.append(f"   ► {method}: {row['rate']:.2f}% fraud rate ({int(row['sum'])} cases)")
    
    # Traffic source quality
    report.append("\n3. TRAFFIC SOURCE QUALITY:")
    for source in sorted(df['traffic_source'].unique()):
        s_data = df[df['traffic_source'] == source]
        fraud_pct = (s_data['is_fraud'].sum() / len(s_data) * 100)
        return_pct = (s_data['is_returned'].sum() / len(s_data) * 100)
        avg_review = s_data['review_score'].mean()
        report.append(f"   ► {source:<20} Fraud: {fraud_pct:>6.2f}% | Returns: {return_pct:>6.2f}% | Avg Review: {avg_review:>4.2f}")
    
    # High-value order patterns
    high_value = df[df['order_value_eur'] > df['order_value_eur'].quantile(0.75)]
    report.append(f"\n4. HIGH-VALUE ORDER PATTERNS (>75th percentile: {df['order_value_eur'].quantile(0.75):.2f}€):")
    report.append(f"   ► Count: {len(high_value):,}")
    report.append(f"   ► Fraud Rate: {high_value['is_fraud'].sum()/len(high_value)*100:.2f}%")
    report.append(f"   ► Return Rate: {high_value['is_returned'].sum()/len(high_value)*100:.2f}%")
    report.append(f"   ► Avg Review: {high_value['review_score'].mean():.2f}")
    
    # New vs repeat customer insights
    report.append(f"\n5. CUSTOMER ACQUISITION vs RETENTION:")
    report.append(f"   ► New customers: {len(new_cust)/len(df)*100:.2f}% of base (Fraud: {new_cust['is_fraud'].sum()/len(new_cust)*100:.2f}%)")
    report.append(f"   ► Loyal customers: {len(loyal_cust)/len(df)*100:.2f}% of base (Fraud: {loyal_cust['is_fraud'].sum()/len(loyal_cust)*100:.2f}%)")
    
    # Product category risk
    high_return_cat = df.groupby('product_category')['is_returned'].apply(lambda x: (x.sum()/len(x)*100)).sort_values(ascending=False).head(3)
    report.append(f"\n6. HIGH-RETURN PRODUCT CATEGORIES:")
    for cat, rate in high_return_cat.items():
        report.append(f"   ► {cat}: {rate:.2f}% return rate")
    
    # Address mismatch correlation
    mismatch_data = df[df['address_mismatch'] == 1]
    if len(mismatch_data) > 0:
        report.append(f"\n7. ADDRESS MISMATCH ALERTS:")
        report.append(f"   ► {len(mismatch_data)} cases ({len(mismatch_data)/len(df)*100:.2f}%)")
        report.append(f"   ► Fraud rate in mismatches: {mismatch_data['is_fraud'].sum()/len(mismatch_data)*100:.2f}%")
    
    report.append("\n" + "="*120)
    report.append("END OF COMPREHENSIVE ANALYSIS REPORT")
    report.append("="*120 + "\n")
    
    # Print and save report
    report_text = "\n".join(report)
    print(report_text)
    
    # Save to file
    with open('analysis_results.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print("\n✓ Report saved to: analysis_results.txt")
    
except Exception as e:
    print(f"Error during analysis: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
