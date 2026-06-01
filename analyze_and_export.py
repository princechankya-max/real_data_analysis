#!/usr/bin/env python3
"""Complete E-Commerce Data Analysis with HTML Export"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

# Read data
df = pd.read_csv('real_project.csv')

# ============ ANALYSIS ENGINE ============
def analyze_data(df):
    """Perform comprehensive analysis"""
    
    analysis = {}
    
    # 1. Overview
    analysis['overview'] = {
        'total_records': len(df),
        'total_columns': len(df.columns),
        'date_range': f"{df['order_date'].min()} to {df['order_date'].max()}",
        'total_revenue': float(df['order_value_eur'].sum()),
        'avg_order_value': float(df['order_value_eur'].mean()),
        'memory_mb': float(df.memory_usage(deep=True).sum() / 1024**2)
    }
    
    # 2. Data Quality
    analysis['data_quality'] = {
        'total_missing': int(df.isnull().sum().sum()),
        'total_duplicates': int(df.duplicated().sum()),
        'unique_orders': int(df['order_id'].nunique())
    }
    
    # 3. Categorical Distributions
    analysis['categories'] = {}
    for col in ['country', 'device_type', 'traffic_source', 'payment_method', 'product_category']:
        analysis['categories'][col] = df[col].value_counts().to_dict()
    
    # 4. Risk Analysis
    analysis['risk'] = {
        'fraud_count': int(df['is_fraud'].sum()),
        'fraud_rate': float(df['is_fraud'].sum() / len(df) * 100),
        'return_count': int(df['is_returned'].sum()),
        'return_rate': float(df['is_returned'].sum() / len(df) * 100),
        'late_delivery': int(df['late_delivery_risk'].sum()),
        'address_mismatch': int(df['address_mismatch'].sum()),
        'high_risk_ip': int(df['high_risk_ip'].sum()),
        'risk_labels': df['risk_label'].value_counts().to_dict()
    }
    
    # 5. Geographic Performance
    analysis['geography'] = {}
    for country in sorted(df['country'].unique()):
        c_data = df[df['country'] == country]
        analysis['geography'][country] = {
            'orders': int(len(c_data)),
            'revenue': float(c_data['order_value_eur'].sum()),
            'avg_value': float(c_data['order_value_eur'].mean()),
            'fraud_rate': float(c_data['is_fraud'].sum() / len(c_data) * 100),
            'return_rate': float(c_data['is_returned'].sum() / len(c_data) * 100)
        }
    
    # 6. Payment Methods
    analysis['payment_methods'] = {}
    for method in sorted(df['payment_method'].unique()):
        m_data = df[df['payment_method'] == method]
        analysis['payment_methods'][method] = {
            'count': int(len(m_data)),
            'avg_value': float(m_data['order_value_eur'].mean()),
            'fraud_rate': float(m_data['is_fraud'].sum() / len(m_data) * 100),
            'return_rate': float(m_data['is_returned'].sum() / len(m_data) * 100)
        }
    
    # 7. Product Categories
    analysis['categories_performance'] = {}
    for cat in sorted(df['product_category'].unique()):
        cat_data = df[df['product_category'] == cat]
        analysis['categories_performance'][cat] = {
            'count': int(len(cat_data)),
            'avg_value': float(cat_data['order_value_eur'].mean()),
            'fraud_rate': float(cat_data['is_fraud'].sum() / len(cat_data) * 100),
            'return_rate': float(cat_data['is_returned'].sum() / len(cat_data) * 100),
            'avg_review': float(cat_data['review_score'].mean())
        }
    
    # 8. Customer Behavior
    new_cust = df[df['previous_orders'] == 0]
    repeat_cust = df[df['previous_orders'] > 0]
    loyal_cust = df[df['previous_orders'] >= 5]
    
    analysis['customers'] = {
        'new_customers': {
            'count': int(len(new_cust)),
            'percentage': float(len(new_cust) / len(df) * 100),
            'fraud_rate': float(new_cust['is_fraud'].sum() / len(new_cust) * 100),
            'return_rate': float(new_cust['is_returned'].sum() / len(new_cust) * 100)
        },
        'repeat_customers': {
            'count': int(len(repeat_cust)),
            'percentage': float(len(repeat_cust) / len(df) * 100),
            'fraud_rate': float(repeat_cust['is_fraud'].sum() / len(repeat_cust) * 100),
            'return_rate': float(repeat_cust['is_returned'].sum() / len(repeat_cust) * 100)
        },
        'loyal_customers': {
            'count': int(len(loyal_cust)),
            'percentage': float(len(loyal_cust) / len(df) * 100),
            'fraud_rate': float(loyal_cust['is_fraud'].sum() / len(loyal_cust) * 100),
            'return_rate': float(loyal_cust['is_returned'].sum() / len(loyal_cust) * 100)
        }
    }
    
    # 9. Traffic Sources
    analysis['traffic_sources'] = {}
    for source in sorted(df['traffic_source'].unique()):
        s_data = df[df['traffic_source'] == source]
        analysis['traffic_sources'][source] = {
            'count': int(len(s_data)),
            'avg_value': float(s_data['order_value_eur'].mean()),
            'fraud_rate': float(s_data['is_fraud'].sum() / len(s_data) * 100),
            'return_rate': float(s_data['is_returned'].sum() / len(s_data) * 100)
        }
    
    # 10. Device Types
    analysis['devices'] = {}
    for device in sorted(df['device_type'].unique()):
        d_data = df[df['device_type'] == device]
        analysis['devices'][device] = {
            'count': int(len(d_data)),
            'avg_value': float(d_data['order_value_eur'].mean()),
            'fraud_rate': float(d_data['is_fraud'].sum() / len(d_data) * 100),
            'return_rate': float(d_data['is_returned'].sum() / len(d_data) * 100)
        }
    
    # 11. Numeric Statistics
    analysis['numeric_stats'] = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        data = df[col].dropna()
        analysis['numeric_stats'][col] = {
            'mean': float(data.mean()),
            'median': float(data.median()),
            'std': float(data.std()),
            'min': float(data.min()),
            'max': float(data.max()),
            'q1': float(data.quantile(0.25)),
            'q3': float(data.quantile(0.75))
        }
    
    return analysis

# Generate analysis
print("🔄 Analyzing data...")
analysis = analyze_data(df)
print("✓ Analysis complete!")

# ============ HTML GENERATION ============
def generate_html(analysis):
    """Generate professional HTML report"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Commerce Data Analysis Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .content {{
            padding: 40px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .card {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        .card-value {{
            font-size: 2em;
            color: #667eea;
            font-weight: bold;
            margin: 10px 0;
        }}
        .card-label {{
            font-size: 0.9em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .card-pct {{
            font-size: 1.1em;
            color: #764ba2;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover {{ background: #f8f9fa; }}
        .metric {{
            display: inline-block;
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 6px;
            margin: 10px 10px 10px 0;
            border-left: 4px solid #667eea;
        }}
        .metric-label {{
            font-size: 0.85em;
            color: #6c757d;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 1.5em;
            color: #667eea;
            font-weight: bold;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        .risk-high {{ color: #dc3545; }}
        .risk-medium {{ color: #ffc107; }}
        .risk-low {{ color: #28a745; }}
        .progress-bar {{
            background: #e9ecef;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-size: 0.8em;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 E-Commerce Data Analysis Report</h1>
            <p>Comprehensive Analysis of {analysis['overview']['total_records']:,} Orders</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            <!-- OVERVIEW SECTION -->
            <div class="section">
                <h2>📈 Dataset Overview</h2>
                <div class="grid">
                    <div class="card">
                        <div class="card-label">Total Orders</div>
                        <div class="card-value">{analysis['overview']['total_records']:,}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Total Revenue</div>
                        <div class="card-value">€{analysis['overview']['total_revenue']:,.0f}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Average Order Value</div>
                        <div class="card-value">€{analysis['overview']['avg_order_value']:.2f}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Date Range</div>
                        <div class="card-value" style="font-size: 0.8em;">{analysis['overview']['date_range']}</div>
                    </div>
                </div>
            </div>
            
            <!-- DATA QUALITY SECTION -->
            <div class="section">
                <h2>✓ Data Quality</h2>
                <div class="grid">
                    <div class="card">
                        <div class="card-label">Missing Values</div>
                        <div class="card-value risk-low">{analysis['data_quality']['total_missing']}</div>
                        <div class="card-pct">Clean Data</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Duplicate Rows</div>
                        <div class="card-value risk-low">{analysis['data_quality']['total_duplicates']}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Unique Orders</div>
                        <div class="card-value">{analysis['data_quality']['unique_orders']:,}</div>
                    </div>
                </div>
            </div>
            
            <!-- RISK ANALYSIS SECTION -->
            <div class="section">
                <h2>⚠️ Risk & Fraud Analysis</h2>
                <div class="grid">
                    <div class="card">
                        <div class="card-label">Fraud Cases</div>
                        <div class="card-value risk-high">{analysis['risk']['fraud_count']}</div>
                        <div class="card-pct">{analysis['risk']['fraud_rate']:.2f}% of orders</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Returns</div>
                        <div class="card-value risk-medium">{analysis['risk']['return_count']}</div>
                        <div class="card-pct">{analysis['risk']['return_rate']:.2f}% of orders</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Late Delivery Risks</div>
                        <div class="card-value risk-medium">{analysis['risk']['late_delivery']}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Address Mismatches</div>
                        <div class="card-value risk-high">{analysis['risk']['address_mismatch']}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">High Risk IPs</div>
                        <div class="card-value risk-high">{analysis['risk']['high_risk_ip']}</div>
                    </div>
                </div>
                
                <h3 style="margin-top: 30px; color: #333;">Risk Label Distribution</h3>
                <table>
                    <tr>
                        <th>Risk Label</th>
                        <th>Count</th>
                        <th>Percentage</th>
                        <th>Visual</th>
                    </tr>
"""
    
    total_risks = sum(analysis['risk']['risk_labels'].values())
    for label, count in sorted(analysis['risk']['risk_labels'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_risks * 100) if total_risks > 0 else 0
        color_class = 'risk-high' if 'Fraud' in label else 'risk-medium' if 'Return' in label else 'risk-low'
        html += f"""
                    <tr>
                        <td><strong>{label}</strong></td>
                        <td>{count:,}</td>
                        <td class="{color_class}">{pct:.2f}%</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {min(pct*2, 100)}%; background: {'#dc3545' if 'Fraud' in label else '#ffc107' if 'Return' in label else '#28a745'};">
                                    {pct:.0f}%
                                </div>
                            </div>
                        </td>
                    </tr>
"""
    
    html += """
                </table>
            </div>
            
            <!-- GEOGRAPHIC PERFORMANCE -->
            <div class="section">
                <h2>🌍 Geographic Performance</h2>
                <table>
                    <tr>
                        <th>Country</th>
                        <th>Orders</th>
                        <th>Revenue (€)</th>
                        <th>Avg Order Value</th>
                        <th>Fraud Rate</th>
                        <th>Return Rate</th>
                    </tr>
"""
    
    for country in sorted(analysis['geography'].keys()):
        data = analysis['geography'][country]
        html += f"""
                    <tr>
                        <td><strong>{country}</strong></td>
                        <td>{data['orders']:,}</td>
                        <td>€{data['revenue']:,.2f}</td>
                        <td>€{data['avg_value']:.2f}</td>
                        <td><span class="risk-high">{data['fraud_rate']:.2f}%</span></td>
                        <td><span class="risk-medium">{data['return_rate']:.2f}%</span></td>
                    </tr>
"""
    
    html += """
                </table>
            </div>
            
            <!-- PAYMENT METHODS -->
            <div class="section">
                <h2>💳 Payment Method Performance</h2>
                <table>
                    <tr>
                        <th>Payment Method</th>
                        <th>Orders</th>
                        <th>Avg Order Value</th>
                        <th>Fraud Rate</th>
                        <th>Return Rate</th>
                    </tr>
"""
    
    for method in sorted(analysis['payment_methods'].keys()):
        data = analysis['payment_methods'][method]
        html += f"""
                    <tr>
                        <td><strong>{method}</strong></td>
                        <td>{data['count']:,}</td>
                        <td>€{data['avg_value']:.2f}</td>
                        <td>{data['fraud_rate']:.2f}%</td>
                        <td>{data['return_rate']:.2f}%</td>
                    </tr>
"""
    
    html += """
                </table>
            </div>
            
            <!-- PRODUCT CATEGORIES -->
            <div class="section">
                <h2>📦 Product Category Analysis</h2>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Orders</th>
                        <th>Avg Value</th>
                        <th>Fraud %</th>
                        <th>Return %</th>
                        <th>Avg Review</th>
                    </tr>
"""
    
    for cat in sorted(analysis['categories_performance'].keys()):
        data = analysis['categories_performance'][cat]
        html += f"""
                    <tr>
                        <td><strong>{cat}</strong></td>
                        <td>{data['count']:,}</td>
                        <td>€{data['avg_value']:.2f}</td>
                        <td>{data['fraud_rate']:.2f}%</td>
                        <td>{data['return_rate']:.2f}%</td>
                        <td>{'⭐' * int(data['avg_review'])} {data['avg_review']:.2f}</td>
                    </tr>
"""
    
    html += """
                </table>
            </div>
            
            <!-- CUSTOMER ANALYSIS -->
            <div class="section">
                <h2>👥 Customer Behavior Analysis</h2>
"""
    
    for segment_name, segment_data in analysis['customers'].items():
        display_name = segment_name.replace('_', ' ').title()
        html += f"""
                <div style="margin-bottom: 30px;">
                    <h3 style="color: #667eea; margin-bottom: 15px;">{display_name}</h3>
                    <div class="grid">
                        <div class="card">
                            <div class="card-label">Count</div>
                            <div class="card-value">{segment_data['count']:,}</div>
                            <div class="card-pct">{segment_data['percentage']:.2f}% of base</div>
                        </div>
                        <div class="card">
                            <div class="card-label">Fraud Rate</div>
                            <div class="card-value risk-high">{segment_data['fraud_rate']:.2f}%</div>
                        </div>
                        <div class="card">
                            <div class="card-label">Return Rate</div>
                            <div class="card-value risk-medium">{segment_data['return_rate']:.2f}%</div>
                        </div>
                    </div>
                </div>
"""
    
    html += """
            </div>
            
            <!-- TRAFFIC SOURCES -->
            <div class="section">
                <h2>🔗 Traffic Source Analysis</h2>
                <table>
                    <tr>
                        <th>Traffic Source</th>
                        <th>Orders</th>
                        <th>Avg Order Value</th>
                        <th>Fraud Rate</th>
                        <th>Return Rate</th>
                    </tr>
"""
    
    for source in sorted(analysis['traffic_sources'].keys()):
        data = analysis['traffic_sources'][source]
        html += f"""
                    <tr>
                        <td><strong>{source}</strong></td>
                        <td>{data['count']:,}</td>
                        <td>€{data['avg_value']:.2f}</td>
                        <td>{data['fraud_rate']:.2f}%</td>
                        <td>{data['return_rate']:.2f}%</td>
                    </tr>
"""
    
    html += """
                </table>
            </div>
            
            <!-- DEVICE TYPES -->
            <div class="section">
                <h2>📱 Device Type Performance</h2>
                <table>
                    <tr>
                        <th>Device Type</th>
                        <th>Orders</th>
                        <th>Avg Order Value</th>
                        <th>Fraud Rate</th>
                        <th>Return Rate</th>
                    </tr>
"""
    
    for device in sorted(analysis['devices'].keys()):
        data = analysis['devices'][device]
        html += f"""
                    <tr>
                        <td><strong>{device}</strong></td>
                        <td>{data['count']:,}</td>
                        <td>€{data['avg_value']:.2f}</td>
                        <td>{data['fraud_rate']:.2f}%</td>
                        <td>{data['return_rate']:.2f}%</td>
                    </tr>
"""
    
    html += """
                </table>
            </div>
            
            <!-- NUMERIC STATISTICS -->
            <div class="section">
                <h2>📊 Numeric Statistics</h2>
                <div class="grid">
"""
    
    for col, stats in sorted(analysis['numeric_stats'].items()):
        html += f"""
                    <div class="card" style="text-align: left;">
                        <div class="card-label">{col}</div>
                        <div style="font-size: 0.9em; margin: 10px 0;">
                            <div class="metric" style="display: block; margin: 5px 0;">
                                <div class="metric-label">Mean</div>
                                <div class="metric-value">{stats['mean']:.2f}</div>
                            </div>
                            <div class="metric" style="display: block; margin: 5px 0;">
                                <div class="metric-label">Range</div>
                                <div class="metric-value">{stats['min']:.2f} - {stats['max']:.2f}</div>
                            </div>
                        </div>
                    </div>
"""
    
    html += """
                </div>
            </div>
            
        </div>
        
        <div class="footer">
            <p>✓ Analysis Complete | E-Commerce Data Analysis Report</p>
            <p style="font-size: 0.9em; margin-top: 10px;">This report provides comprehensive insights into order data, customer behavior, fraud patterns, and performance metrics.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

# Generate HTML
print("🎨 Generating HTML report...")
html_content = generate_html(analysis)

# Save HTML
with open('analysis_report.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ HTML report saved: analysis_report.html")
print("📄 Opening in your default browser...")

# Also save JSON for data science purposes
with open('analysis_data.json', 'w', encoding='utf-8') as f:
    json.dump(analysis, f, indent=2)

print("📊 JSON data saved: analysis_data.json")

# Print summary to console
print("\n" + "="*80)
print("QUICK SUMMARY")
print("="*80)
print(f"Total Orders: {analysis['overview']['total_records']:,}")
print(f"Total Revenue: €{analysis['overview']['total_revenue']:,.2f}")
print(f"Average Order Value: €{analysis['overview']['avg_order_value']:.2f}")
print(f"\nFraud Rate: {analysis['risk']['fraud_rate']:.2f}%")
print(f"Return Rate: {analysis['risk']['return_rate']:.2f}%")
print(f"Late Delivery Risk: {analysis['risk']['late_delivery']} cases")
print(f"\nTop Country: {max(analysis['geography'], key=lambda k: analysis['geography'][k]['revenue'])}")
print(f"Top Payment Method: {max(analysis['payment_methods'], key=lambda k: analysis['payment_methods'][k]['count'])}")
print("="*80)

# Try to open the HTML file
import sys
import os
import webbrowser
try:
    html_path = os.path.abspath('analysis_report.html')
    webbrowser.open(f'file://{html_path}')
except:
    print(f"Open this file in your browser: {os.path.abspath('analysis_report.html')}")


