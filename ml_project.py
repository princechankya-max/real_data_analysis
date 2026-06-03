import os
import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, RobustScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings

warnings.filterwarnings('ignore')

# Setup directories
os.makedirs('./models', exist_ok=True)
os.makedirs('./charts', exist_ok=True)
os.makedirs('./outputs', exist_ok=True)

print("=" * 80)
print("OLIST ML PROJECT - COMPREHENSIVE ANALYSIS")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD ALL 9 CSVs
# ============================================================================
print("\n[STEP 1] Loading all 9 CSV files...")

def load_csv(filename):
    try:
        return pd.read_csv(filename, encoding='utf-8')
    except:
        return pd.read_csv(filename, encoding='latin-1')

df_orders = load_csv('olist_orders_dataset.csv')
df_items = load_csv('olist_order_items_dataset.csv')
df_payments = load_csv('olist_order_payments_dataset.csv')
df_reviews = load_csv('olist_order_reviews_dataset.csv')
df_customers = load_csv('olist_customers_dataset.csv')
df_products = load_csv('olist_products_dataset.csv')
df_sellers = load_csv('olist_sellers_dataset.csv')
df_geolocation = load_csv('olist_geolocation_dataset.csv')
df_category_translation = load_csv('product_category_name_translation.csv')

print(f"[OK] Loaded {len(df_orders)} orders")
print(f"[OK] Loaded {len(df_items)} order items")
print(f"[OK] Loaded {len(df_payments)} payments")
print(f"[OK] Loaded {len(df_reviews)} reviews")
print(f"[OK] Loaded {len(df_customers)} customers")

# Parse datetime columns
datetime_cols_orders = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
for col in datetime_cols_orders:
    if col in df_orders.columns:
        df_orders[col] = pd.to_datetime(df_orders[col], errors='coerce')

datetime_cols_reviews = ['review_creation_date', 'review_answer_timestamp']
for col in datetime_cols_reviews:
    if col in df_reviews.columns:
        df_reviews[col] = pd.to_datetime(df_reviews[col], errors='coerce')

datetime_cols_items = ['shipping_limit_date']
for col in datetime_cols_items:
    if col in df_items.columns:
        df_items[col] = pd.to_datetime(df_items[col], errors='coerce')

# ============================================================================
# STEP 2: AGGREGATE ORDER ITEMS
# ============================================================================
print("\n[STEP 2] Aggregating order items...")

items_agg = df_items.groupby('order_id').agg({
    'price': ['sum', 'mean', 'count'],
    'freight_value': 'sum',
    'seller_id': 'nunique'
}).reset_index()

items_agg.columns = ['order_id', 'total_price', 'avg_item_price', 'num_items', 'total_freight', 'unique_sellers']
items_agg['freight_ratio'] = items_agg['total_freight'] / (items_agg['total_price'] + 0.01)

print(f"[OK] Aggregated {len(items_agg)} orders with item data")

# ============================================================================
# STEP 3: AGGREGATE PAYMENTS
# ============================================================================
print("\n[STEP 3] Aggregating payments...")

payment_agg = df_payments.groupby('order_id').agg({
    'payment_value': 'sum',
    'payment_installments': 'max',
    'payment_type': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'credit_card'
}).reset_index()

payment_agg.columns = ['order_id', 'total_payment', 'max_installments', 'payment_type_mode']

print(f"[OK] Aggregated {len(payment_agg)} orders with payment data")

# ============================================================================
# STEP 4: DEDUPLICATE REVIEWS (keep last)
# ============================================================================
print("\n[STEP 4] Processing reviews...")

reviews_latest = df_reviews.sort_values('review_creation_date').drop_duplicates('order_id', keep='last')
reviews_latest = reviews_latest[['order_id', 'review_score']].copy()

print(f"[OK] Deduplicated to {len(reviews_latest)} unique orders with reviews")

# ============================================================================
# STEP 5: MERGE INTO MASTER DATAFRAME
# ============================================================================
print("\n[STEP 5] Merging into master dataframe...")

df_master = df_orders.copy()
df_master = df_master.merge(items_agg, on='order_id', how='left')
df_master = df_master.merge(payment_agg, on='order_id', how='left')
df_master = df_master.merge(reviews_latest, on='order_id', how='left')
df_master = df_master.merge(df_customers[['customer_id', 'customer_unique_id', 'customer_state']], on='customer_id', how='left')

print(f"[OK] Master dataframe: {df_master.shape[0]} rows × {df_master.shape[1]} columns")

# ============================================================================
# STEP 6: FEATURE ENGINEERING (25 FEATURES)
# ============================================================================
print("\n[STEP 6] Engineering 25 ML features...")

df_features = df_master.copy()

# TEMPORAL FEATURES
df_features['order_month'] = df_features['order_purchase_timestamp'].dt.month
df_features['order_quarter'] = df_features['order_purchase_timestamp'].dt.quarter
df_features['order_dayofweek'] = df_features['order_purchase_timestamp'].dt.dayofweek
df_features['order_hour'] = df_features['order_purchase_timestamp'].dt.hour
df_features['is_weekend'] = (df_features['order_dayofweek'] >= 5).astype(int)
df_features['is_q4'] = (df_features['order_month'] >= 10).astype(int)

# DELIVERY FEATURES
df_features['delivery_time_days'] = (df_features['order_delivered_customer_date'] - df_features['order_purchase_timestamp']).dt.days
df_features['estimated_days'] = (df_features['order_estimated_delivery_date'] - df_features['order_purchase_timestamp']).dt.days
df_features['approval_hours'] = (df_features['order_approved_at'] - df_features['order_purchase_timestamp']).dt.total_seconds() / 3600
df_features['delivery_efficiency'] = df_features['estimated_days'] - df_features['delivery_time_days']

# PAYMENT FEATURES
df_features['has_installments'] = (df_features['max_installments'] > 1).astype(int)

# TARGETS
df_features['is_late'] = (df_features['order_delivered_customer_date'] > df_features['order_estimated_delivery_date']).astype(int)
df_features['review_positive'] = (df_features['review_score'] >= 4).astype(int)

print("[OK] Created temporal, delivery, price, and payment features")

# ============================================================================
# STEP 7: ENCODING & PREPROCESSING
# ============================================================================
print("\n[STEP 7] Encoding categorical features...")

le_payment = LabelEncoder()
df_features['payment_type_encoded'] = le_payment.fit_transform(df_features['payment_type_mode'].fillna('credit_card'))

le_state = LabelEncoder()
df_features['customer_state_encoded'] = le_state.fit_transform(df_features['customer_state'].fillna('SP'))

# Fill missing values
numeric_cols = ['order_month', 'order_quarter', 'order_dayofweek', 'order_hour', 'is_weekend', 'is_q4',
                'approval_hours', 'estimated_days', 'delivery_time_days', 'delivery_efficiency',
                'total_price', 'total_freight', 'num_items', 'avg_item_price', 'freight_ratio', 'unique_sellers',
                'total_payment', 'max_installments', 'has_installments', 'payment_type_encoded', 'customer_state_encoded']

for col in numeric_cols:
    if col in df_features.columns:
        df_features[col] = df_features[col].fillna(df_features[col].median())

# Filter: only delivered orders for training
df_features = df_features[df_features['order_status'] == 'delivered'].copy()
print(f"[OK] Filtered to {len(df_features)} delivered orders for training")

# ============================================================================
# MODEL 1: LATE DELIVERY CLASSIFIER
# ============================================================================
print("\n" + "=" * 80)
print("MODEL 1: LATE DELIVERY CLASSIFIER")
print("=" * 80)

features_delay = ['order_month', 'order_quarter', 'order_hour', 'is_weekend', 'is_q4',
                  'approval_hours', 'estimated_days', 'total_price', 'total_freight',
                  'num_items', 'freight_ratio', 'max_installments',
                  'customer_state_encoded', 'payment_type_encoded']

X_delay = df_features[features_delay].copy()
y_delay = df_features['is_late'].copy()

# Remove any remaining NaN
X_delay = X_delay.fillna(X_delay.median())
valid_idx = y_delay.notna()
X_delay = X_delay[valid_idx]
y_delay = y_delay[valid_idx]

print(f"\nTarget distribution: {y_delay.value_counts().to_dict()}")

X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(X_delay, y_delay, test_size=0.2, random_state=42, stratify=y_delay)

models_delay = {}
results_delay = {}

# Model 1a: Logistic Regression
print("\n[Training] Logistic Regression...")
lr_model = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
lr_model.fit(X_train_d, y_train_d)
y_pred_lr = lr_model.predict(X_test_d)

acc_lr = accuracy_score(y_test_d, y_pred_lr)
prec_lr = precision_score(y_test_d, y_pred_lr, average='weighted', zero_division=0)
rec_lr = recall_score(y_test_d, y_pred_lr, average='weighted')
f1_lr = f1_score(y_test_d, y_pred_lr, average='weighted')

models_delay['LogisticRegression'] = lr_model
results_delay['LogisticRegression'] = {'Accuracy': acc_lr, 'Precision': prec_lr, 'Recall': rec_lr, 'F1': f1_lr, 'predictions': y_pred_lr}

print(f"  Accuracy: {acc_lr:.4f} | Precision: {prec_lr:.4f} | Recall: {rec_lr:.4f} | F1: {f1_lr:.4f}")

# Model 1b: Random Forest
print("[Training] Random Forest...")
rf_model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train_d, y_train_d)
y_pred_rf = rf_model.predict(X_test_d)

acc_rf = accuracy_score(y_test_d, y_pred_rf)
prec_rf = precision_score(y_test_d, y_pred_rf, average='weighted', zero_division=0)
rec_rf = recall_score(y_test_d, y_pred_rf, average='weighted')
f1_rf = f1_score(y_test_d, y_pred_rf, average='weighted')

models_delay['RandomForest'] = rf_model
results_delay['RandomForest'] = {'Accuracy': acc_rf, 'Precision': prec_rf, 'Recall': rec_rf, 'F1': f1_rf, 'predictions': y_pred_rf}

print(f"  Accuracy: {acc_rf:.4f} | Precision: {prec_rf:.4f} | Recall: {rec_rf:.4f} | F1: {f1_rf:.4f}")

# Model 1c: XGBoost or GradientBoosting
print("[Training] XGBoost/GradientBoosting...")
try:
    from xgboost import XGBClassifier
    xgb_model = XGBClassifier(n_estimators=200, max_depth=6, random_state=42, eval_metric='logloss', verbosity=0)
    xgb_model.fit(X_train_d, y_train_d)
    y_pred_xgb = xgb_model.predict(X_test_d)

    acc_xgb = accuracy_score(y_test_d, y_pred_xgb)
    prec_xgb = precision_score(y_test_d, y_pred_xgb, average='weighted', zero_division=0)
    rec_xgb = recall_score(y_test_d, y_pred_xgb, average='weighted')
    f1_xgb = f1_score(y_test_d, y_pred_xgb, average='weighted')

    models_delay['XGBoost'] = xgb_model
    results_delay['XGBoost'] = {'Accuracy': acc_xgb, 'Precision': prec_xgb, 'Recall': rec_xgb, 'F1': f1_xgb, 'predictions': y_pred_xgb}

    print(f"  Accuracy: {acc_xgb:.4f} | Precision: {prec_xgb:.4f} | Recall: {rec_xgb:.4f} | F1: {f1_xgb:.4f}")
except ImportError:
    gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    gb_model.fit(X_train_d, y_train_d)
    y_pred_gb = gb_model.predict(X_test_d)

    acc_gb = accuracy_score(y_test_d, y_pred_gb)
    prec_gb = precision_score(y_test_d, y_pred_gb, average='weighted', zero_division=0)
    rec_gb = recall_score(y_test_d, y_pred_gb, average='weighted')
    f1_gb = f1_score(y_test_d, y_pred_gb, average='weighted')

    models_delay['GradientBoosting'] = gb_model
    results_delay['GradientBoosting'] = {'Accuracy': acc_gb, 'Precision': prec_gb, 'Recall': rec_gb, 'F1': f1_gb, 'predictions': y_pred_gb}

    print(f"  Accuracy: {acc_gb:.4f} | Precision: {prec_gb:.4f} | Recall: {rec_gb:.4f} | F1: {f1_gb:.4f}")

# Best model for delay
best_model_name_delay = max(results_delay.items(), key=lambda x: x[1]['F1'])[0]
best_model_delay = models_delay[best_model_name_delay]
best_f1_delay = results_delay[best_model_name_delay]['F1']

print(f"\n[OK] Best Model: {best_model_name_delay} (F1: {best_f1_delay:.4f})")

# Cross-validation
cv_scores_delay = cross_val_score(best_model_delay, X_delay, y_delay, cv=5, scoring='f1_weighted')
print(f"[OK] Cross-validation F1: {cv_scores_delay.mean():.4f} ± {cv_scores_delay.std():.4f}")

# Save model
joblib.dump(best_model_delay, 'models/delay_classifier.pkl')
print("[OK] Saved to models/delay_classifier.pkl")

# ============================================================================
# MODEL 2: REVIEW SCORE CLASSIFIER
# ============================================================================
print("\n" + "=" * 80)
print("MODEL 2: REVIEW SCORE CLASSIFIER")
print("=" * 80)

features_review = ['delivery_time_days', 'estimated_days', 'delivery_efficiency', 'is_late',
                   'total_price', 'avg_item_price', 'freight_ratio', 'num_items',
                   'total_payment', 'max_installments', 'order_month', 'is_weekend',
                   'approval_hours', 'customer_state_encoded']

X_review = df_features[features_review].copy()
y_review = df_features['review_positive'].copy()

# Remove any remaining NaN
X_review = X_review.fillna(X_review.median())
valid_idx_r = y_review.notna()
X_review = X_review[valid_idx_r]
y_review = y_review[valid_idx_r]

print(f"\nTarget distribution: {y_review.value_counts().to_dict()}")

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_review, y_review, test_size=0.2, random_state=42, stratify=y_review)

models_review = {}
results_review = {}

# Model 2a: Logistic Regression
print("\n[Training] Logistic Regression...")
lr_model_r = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
lr_model_r.fit(X_train_r, y_train_r)
y_pred_lr_r = lr_model_r.predict(X_test_r)

acc_lr_r = accuracy_score(y_test_r, y_pred_lr_r)
prec_lr_r = precision_score(y_test_r, y_pred_lr_r, average='weighted', zero_division=0)
rec_lr_r = recall_score(y_test_r, y_pred_lr_r, average='weighted')
f1_lr_r = f1_score(y_test_r, y_pred_lr_r, average='weighted')

models_review['LogisticRegression'] = lr_model_r
results_review['LogisticRegression'] = {'Accuracy': acc_lr_r, 'Precision': prec_lr_r, 'Recall': rec_lr_r, 'F1': f1_lr_r, 'predictions': y_pred_lr_r}

print(f"  Accuracy: {acc_lr_r:.4f} | Precision: {prec_lr_r:.4f} | Recall: {rec_lr_r:.4f} | F1: {f1_lr_r:.4f}")

# Model 2b: Random Forest
print("[Training] Random Forest...")
rf_model_r = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
rf_model_r.fit(X_train_r, y_train_r)
y_pred_rf_r = rf_model_r.predict(X_test_r)

acc_rf_r = accuracy_score(y_test_r, y_pred_rf_r)
prec_rf_r = precision_score(y_test_r, y_pred_rf_r, average='weighted', zero_division=0)
rec_rf_r = recall_score(y_test_r, y_pred_rf_r, average='weighted')
f1_rf_r = f1_score(y_test_r, y_pred_rf_r, average='weighted')

models_review['RandomForest'] = rf_model_r
results_review['RandomForest'] = {'Accuracy': acc_rf_r, 'Precision': prec_rf_r, 'Recall': rec_rf_r, 'F1': f1_rf_r, 'predictions': y_pred_rf_r}

print(f"  Accuracy: {acc_rf_r:.4f} | Precision: {prec_rf_r:.4f} | Recall: {rec_rf_r:.4f} | F1: {f1_rf_r:.4f}")

# Model 2c: XGBoost or GradientBoosting
print("[Training] XGBoost/GradientBoosting...")
try:
    from xgboost import XGBClassifier
    xgb_model_r = XGBClassifier(n_estimators=200, max_depth=6, random_state=42, eval_metric='logloss', verbosity=0)
    xgb_model_r.fit(X_train_r, y_train_r)
    y_pred_xgb_r = xgb_model_r.predict(X_test_r)

    acc_xgb_r = accuracy_score(y_test_r, y_pred_xgb_r)
    prec_xgb_r = precision_score(y_test_r, y_pred_xgb_r, average='weighted', zero_division=0)
    rec_xgb_r = recall_score(y_test_r, y_pred_xgb_r, average='weighted')
    f1_xgb_r = f1_score(y_test_r, y_pred_xgb_r, average='weighted')

    models_review['XGBoost'] = xgb_model_r
    results_review['XGBoost'] = {'Accuracy': acc_xgb_r, 'Precision': prec_xgb_r, 'Recall': rec_xgb_r, 'F1': f1_xgb_r, 'predictions': y_pred_xgb_r}

    print(f"  Accuracy: {acc_xgb_r:.4f} | Precision: {prec_xgb_r:.4f} | Recall: {rec_xgb_r:.4f} | F1: {f1_xgb_r:.4f}")
except ImportError:
    gb_model_r = GradientBoostingClassifier(n_estimators=100, random_state=42)
    gb_model_r.fit(X_train_r, y_train_r)
    y_pred_gb_r = gb_model_r.predict(X_test_r)

    acc_gb_r = accuracy_score(y_test_r, y_pred_gb_r)
    prec_gb_r = precision_score(y_test_r, y_pred_gb_r, average='weighted', zero_division=0)
    rec_gb_r = recall_score(y_test_r, y_pred_gb_r, average='weighted')
    f1_gb_r = f1_score(y_test_r, y_pred_gb_r, average='weighted')

    models_review['GradientBoosting'] = gb_model_r
    results_review['GradientBoosting'] = {'Accuracy': acc_gb_r, 'Precision': prec_gb_r, 'Recall': rec_gb_r, 'F1': f1_gb_r, 'predictions': y_pred_gb_r}

    print(f"  Accuracy: {acc_gb_r:.4f} | Precision: {prec_gb_r:.4f} | Recall: {rec_gb_r:.4f} | F1: {f1_gb_r:.4f}")

# Best model for review
best_model_name_review = max(results_review.items(), key=lambda x: x[1]['F1'])[0]
best_model_review = models_review[best_model_name_review]
best_f1_review = results_review[best_model_name_review]['F1']

print(f"\n[OK] Best Model: {best_model_name_review} (F1: {best_f1_review:.4f})")

# Cross-validation
cv_scores_review = cross_val_score(best_model_review, X_review, y_review, cv=5, scoring='f1_weighted')
print(f"[OK] Cross-validation F1: {cv_scores_review.mean():.4f} ± {cv_scores_review.std():.4f}")

# Save model
joblib.dump(best_model_review, 'models/review_classifier.pkl')
print("[OK] Saved to models/review_classifier.pkl")

# ============================================================================
# GENERATE REPORTS & VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("GENERATING REPORTS & VISUALIZATIONS")
print("=" * 80)

# Generate report
report_text = "=" * 80 + "\n"
report_text += "ML RESULTS REPORT - OLIST PROJECT\n"
report_text += "=" * 80 + "\n\n"

report_text += "MODEL 1: LATE DELIVERY CLASSIFIER\n"
report_text += "-" * 80 + "\n"

for model_name, metrics in results_delay.items():
    report_text += f"\n{model_name}:\n"
    report_text += f"  Accuracy:  {metrics['Accuracy']:.4f}\n"
    report_text += f"  Precision: {metrics['Precision']:.4f}\n"
    report_text += f"  Recall:    {metrics['Recall']:.4f}\n"
    report_text += f"  F1 Score:  {metrics['F1']:.4f}\n"
    report_text += f"\nClassification Report:\n"
    report_text += classification_report(y_test_d, metrics['predictions'], target_names=['On-time', 'Late'], zero_division=0)
    report_text += "\n"

report_text += f"\nBest Model: {best_model_name_delay} (F1: {best_f1_delay:.4f})\n"
report_text += f"Cross-validation F1: {cv_scores_delay.mean():.4f} ± {cv_scores_delay.std():.4f}\n"

report_text += "\n" + "=" * 80 + "\n"
report_text += "MODEL 2: REVIEW SCORE CLASSIFIER\n"
report_text += "-" * 80 + "\n"

for model_name, metrics in results_review.items():
    report_text += f"\n{model_name}:\n"
    report_text += f"  Accuracy:  {metrics['Accuracy']:.4f}\n"
    report_text += f"  Precision: {metrics['Precision']:.4f}\n"
    report_text += f"  Recall:    {metrics['Recall']:.4f}\n"
    report_text += f"  F1 Score:  {metrics['F1']:.4f}\n"
    report_text += f"\nClassification Report:\n"
    report_text += classification_report(y_test_r, metrics['predictions'], target_names=['Negative', 'Positive'], zero_division=0)
    report_text += "\n"

report_text += f"\nBest Model: {best_model_name_review} (F1: {best_f1_review:.4f})\n"
report_text += f"Cross-validation F1: {cv_scores_review.mean():.4f} ± {cv_scores_review.std():.4f}\n"

with open('outputs/ml_results_report.txt', 'w') as f:
    f.write(report_text)

print("[OK] Saved ml_results_report.txt")

# Feature Importance - Delay Model
print("\n[Visualizations] Generating feature importance charts...")

if hasattr(best_model_delay, 'feature_importances_'):
    importances_delay = best_model_delay.feature_importances_
    indices_delay = np.argsort(importances_delay)[-15:]

    plt.figure(figsize=(10, 6))
    plt.barh(range(len(indices_delay)), importances_delay[indices_delay])
    plt.yticks(range(len(indices_delay)), [features_delay[i] for i in indices_delay])
    plt.xlabel('Importance')
    plt.title('Top 15 Features - Late Delivery Classifier')
    plt.tight_layout()
    plt.savefig('charts/ml_delay_importance.png', dpi=100, bbox_inches='tight')
    plt.close()
    print("[OK] Saved ml_delay_importance.png")

# Feature Importance - Review Model
if hasattr(best_model_review, 'feature_importances_'):
    importances_review = best_model_review.feature_importances_
    indices_review = np.argsort(importances_review)[-15:]

    plt.figure(figsize=(10, 6))
    plt.barh(range(len(indices_review)), importances_review[indices_review])
    plt.yticks(range(len(indices_review)), [features_review[i] for i in indices_review])
    plt.xlabel('Importance')
    plt.title('Top 15 Features - Review Score Classifier')
    plt.tight_layout()
    plt.savefig('charts/ml_review_importance.png', dpi=100, bbox_inches='tight')
    plt.close()
    print("[OK] Saved ml_review_importance.png")

# Confusion Matrices
y_pred_best_delay = best_model_delay.predict(X_test_d)
cm_delay = confusion_matrix(y_test_d, y_pred_best_delay)

plt.figure(figsize=(8, 6))
sns.heatmap(cm_delay, annot=True, fmt='d', cmap='Blues', xticklabels=['On-time', 'Late'], yticklabels=['On-time', 'Late'])
plt.title(f'Confusion Matrix - Late Delivery ({best_model_name_delay})')
plt.ylabel('True')
plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig('charts/ml_delay_cm.png', dpi=100, bbox_inches='tight')
plt.close()
print("[OK] Saved ml_delay_cm.png")

y_pred_best_review = best_model_review.predict(X_test_r)
cm_review = confusion_matrix(y_test_r, y_pred_best_review)

plt.figure(figsize=(8, 6))
sns.heatmap(cm_review, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
plt.title(f'Confusion Matrix - Review Score ({best_model_name_review})')
plt.ylabel('True')
plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig('charts/ml_review_cm.png', dpi=100, bbox_inches='tight')
plt.close()
print("[OK] Saved ml_review_cm.png")

# ============================================================================
# RFM + CUSTOMER SEGMENTATION
# ============================================================================
print("\n" + "=" * 80)
print("RFM CUSTOMER SEGMENTATION")
print("=" * 80)

df_rfm = df_master[['customer_unique_id', 'order_purchase_timestamp', 'order_id', 'total_price']].copy()
df_rfm = df_rfm[df_rfm['customer_unique_id'].notna()].copy()

reference_date = df_rfm['order_purchase_timestamp'].max() + timedelta(days=1)
print(f"Reference date: {reference_date}")

rfm_data = df_rfm.groupby('customer_unique_id', as_index=False).agg({
    'order_purchase_timestamp': lambda x: (reference_date - x.max()).days,
    'order_id': 'count',
    'total_price': 'sum'
})

rfm_data.columns = ['customer_unique_id', 'R', 'F', 'M']
rfm_data = rfm_data[(rfm_data['M'] > 0) & (rfm_data['F'] > 0)].copy()

print(f"[OK] RFM data: {len(rfm_data)} customers")

# Scale RFM
scaler = RobustScaler()
rfm_scaled = scaler.fit_transform(rfm_data[['R', 'F', 'M']])

# Elbow Method
print("\n[Segmentation] Finding optimal clusters via Elbow method...")

inertias = []

for k in range(2, 9):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(rfm_scaled)
    inertias.append(kmeans.inertia_)

plt.figure(figsize=(10, 6))
plt.plot(range(2, 9), inertias, 'bo-', linewidth=2, markersize=8)
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia')
plt.title('Elbow Method for Optimal Clusters')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('charts/ml_rfm_elbow.png', dpi=100, bbox_inches='tight')
plt.close()
print("[OK] Saved ml_rfm_elbow.png")

# Apply KMeans with k=4
kmeans_final = KMeans(n_clusters=4, random_state=42, n_init=10)
rfm_data['segment_id'] = kmeans_final.fit_predict(rfm_scaled)

# Auto-label segments
segment_stats = rfm_data.groupby('segment_id')[['R', 'F', 'M']].mean()

segment_labels = {}
for cluster_id in range(4):
    r = segment_stats.loc[cluster_id, 'R']
    f = segment_stats.loc[cluster_id, 'F']
    m = segment_stats.loc[cluster_id, 'M']

    if r < segment_stats['R'].median() and f > segment_stats['F'].median() and m > segment_stats['M'].median():
        segment_labels[cluster_id] = 'Champions'
    elif r < segment_stats['R'].median() and f > segment_stats['F'].quantile(0.25):
        segment_labels[cluster_id] = 'Loyal'
    elif r > segment_stats['R'].median() and m > segment_stats['M'].median():
        segment_labels[cluster_id] = 'At-Risk'
    else:
        segment_labels[cluster_id] = 'Lost'

rfm_data['segment'] = rfm_data['segment_id'].map(segment_labels)

segment_counts = rfm_data['segment'].value_counts()
print(f"\nSegment Distribution:")
for segment, count in segment_counts.items():
    print(f"  {segment}: {count}")

# Save RFM segments
rfm_data.to_csv('outputs/rfm_segments.csv', index=False)
print("\n[OK] Saved rfm_segments.csv")

# RFM Scatter plot
plt.figure(figsize=(12, 8))
colors = {'Champions': 'gold', 'Loyal': 'blue', 'At-Risk': 'orange', 'Lost': 'red'}

for segment in ['Champions', 'Loyal', 'At-Risk', 'Lost']:
    segment_data = rfm_data[rfm_data['segment'] == segment]
    plt.scatter(segment_data['R'], segment_data['M'], label=segment, alpha=0.6, s=50, color=colors.get(segment, 'gray'))

plt.xlabel('Recency (days)')
plt.ylabel('Monetary Value ($)')
plt.title('RFM Customer Segmentation')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('charts/ml_rfm_scatter.png', dpi=100, bbox_inches='tight')
plt.close()
print("[OK] Saved ml_rfm_scatter.png")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("[DONE] PROJECT 2 COMPLETE")
print("=" * 80)
print(f"Delay Model -> Best: {best_model_name_delay}, F1: {best_f1_delay:.4f}")
print(f"Review Model -> Best: {best_model_name_review}, F1: {best_f1_review:.4f}")
print(f"Segments: Champions={segment_counts.get('Champions', 0)}, Loyal={segment_counts.get('Loyal', 0)}, At-Risk={segment_counts.get('At-Risk', 0)}, Lost={segment_counts.get('Lost', 0)}")
print("\nOutput files:")
print("  [OK] models/delay_classifier.pkl")
print("  [OK] models/review_classifier.pkl")
print("  [OK] outputs/ml_results_report.txt")
print("  [OK] outputs/rfm_segments.csv")
print("  [OK] charts/ (6 PNG visualizations)")
print("=" * 80)
