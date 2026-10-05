"""
retrain_model.py
================
Improved model retraining script:
  1. Loads the original dataset
  2. Engineers new features (velocity, ratio, etc.)
  3. Fixes class imbalance using scale_pos_weight
  4. Tunes hyperparameters with RandomizedSearchCV
  5. Saves the new improved model, imputer, and feature columns
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.impute import SimpleImputer
from sklearn.metrics import (classification_report, roc_auc_score,
                              confusion_matrix, accuracy_score)
from xgboost import XGBClassifier

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH  = ROOT / "blockchain" / "dataset" / "transaction_dataset.csv"
MODEL_DIR  = ROOT / "notebooks" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("  DeFi Fraud Detection - Model Retraining")
print("=" * 60)

# ── Step 1: Load Data ────────────────────────────────────────────────────────
print("\n[1/5] Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"      Shape: {df.shape}")

# Strip whitespace from column names
df.columns = df.columns.str.strip()

# Drop non-feature columns
drop_cols = ['Index', 'Unnamed: 0', 'Address',
             'ERC20 most sent token type', 'ERC20_most_rec_token_type']
df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

# ── Step 2: Engineer New Features ───────────────────────────────────────────
print("\n[2/5] Engineering new features...")

# Sent/Received ratio — fraud wallets often only receive, never send
df['sent_recv_ratio'] = df['Sent tnx'] / (df['Received Tnx'] + 1)

# ETH velocity — how fast ETH moves out compared to how much came in
df['eth_velocity'] = df['total Ether sent'] / (df['total ether received'] + 1e-9)

# Balance retention rate — scammers drain their wallets quickly
df['balance_retention'] = df['total ether balance'] / (df['total ether received'] + 1e-9)

# Transaction concentration — are they receiving from very few or very many?
df['recv_concentration'] = df['Unique Received From Addresses'] / (df['Received Tnx'] + 1)

# ERC20 engagement ratio
df['erc20_engagement'] = df['Total ERC20 tnxs'] / (
    df['total transactions (including tnx to create contract'] + 1
)

print(f"      New features added: sent_recv_ratio, eth_velocity,")
print(f"      balance_retention, recv_concentration, erc20_engagement")

# ── Step 3: Prepare X and y ──────────────────────────────────────────────────
print("\n[3/5] Preparing features and labels...")
X = df.drop(columns=['FLAG'])
y = df['FLAG']

feature_columns = list(X.columns)
print(f"      Total features: {len(feature_columns)}")
print(f"      Fraud: {y.sum()} | Legitimate: {(y==0).sum()}")
neg = (y == 0).sum()
pos = y.sum()
scale_pos_weight = neg / pos
print(f"      Class imbalance ratio (scale_pos_weight): {scale_pos_weight:.2f}")

# ── Step 4: Train/Test Split + Imputation ───────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

imputer = SimpleImputer(strategy='median')
X_train_imp = imputer.fit_transform(X_train)
X_test_imp  = imputer.transform(X_test)

# ── Step 5: Hyperparameter Tuning ────────────────────────────────────────────
print("\n[4/5] Running hyperparameter tuning (this may take a few minutes)...")

param_dist = {
    'n_estimators':      [200, 300, 400, 500],
    'max_depth':         [4, 5, 6, 7, 8],
    'learning_rate':     [0.01, 0.05, 0.1, 0.15],
    'subsample':         [0.7, 0.8, 0.9, 1.0],
    'colsample_bytree':  [0.7, 0.8, 0.9, 1.0],
    'min_child_weight':  [1, 3, 5, 7],
    'gamma':             [0, 0.1, 0.2, 0.3],
    'reg_alpha':         [0, 0.01, 0.1, 1],
    'reg_lambda':        [1, 1.5, 2, 5],
}

base_model = XGBClassifier(
    objective='binary:logistic',
    eval_metric='auc',
    scale_pos_weight=scale_pos_weight,   # Fix class imbalance!
    use_label_encoder=False,
    random_state=42,
    n_jobs=-1,
)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

search = RandomizedSearchCV(
    estimator=base_model,
    param_distributions=param_dist,
    n_iter=30,
    scoring='roc_auc',
    cv=cv,
    verbose=1,
    random_state=42,
    n_jobs=-1,
)

search.fit(X_train_imp, y_train)

best_model = search.best_estimator_
print(f"\n      Best AUC (CV): {search.best_score_:.4f}")
print(f"      Best params: {search.best_params_}")

# ── Step 6: Evaluate ─────────────────────────────────────────────────────────
print("\n[5/5] Evaluating on test set...")
y_pred      = best_model.predict(X_test_imp)
y_pred_prob = best_model.predict_proba(X_test_imp)[:, 1]

print(f"\n  Accuracy : {accuracy_score(y_test, y_pred):.4f}")
print(f"  ROC-AUC  : {roc_auc_score(y_test, y_pred_prob):.4f}")
print(f"\n{classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraud'])}")

cm = confusion_matrix(y_test, y_pred)
print(f"  Confusion Matrix:")
print(f"  [[TN={cm[0,0]}  FP={cm[0,1]}]")
print(f"   [FN={cm[1,0]}  TP={cm[1,1]}]]")

# ── Step 7: Save new model artifacts ─────────────────────────────────────────
print("\nSaving new model artifacts...")
joblib.dump(best_model, MODEL_DIR / "fraud_model.pkl")
joblib.dump(imputer,    MODEL_DIR / "median_imputer.pkl")
joblib.dump(feature_columns, MODEL_DIR / "feature_columns.pkl")

print(f"\n  [OK] Model saved to     : {MODEL_DIR / 'fraud_model.pkl'}")
print(f"  [OK] Imputer saved to   : {MODEL_DIR / 'median_imputer.pkl'}")
print(f"  [OK] Features saved to  : {MODEL_DIR / 'feature_columns.pkl'}")
print("\n" + "=" * 60)
print("  Retraining complete! Your new model is ready.")
print("=" * 60)
