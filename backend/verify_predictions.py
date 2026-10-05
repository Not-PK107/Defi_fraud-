"""
verify_predictions.py
=====================
Validates and benchmarks the ML model predictions against the real
Ethereum ground truth dataset (transaction_dataset.csv).

Compares:
  Actual Label (FLAG = 1 -> FRAUD, FLAG = 0 -> LEGITIMATE)
  vs.
  Predicted Label (XGBoost Classifier Inference)

Usage:
    python backend/verify_predictions.py
"""

import sys
from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.predictor import predict_fraud_risk

DATASET_PATH = PROJECT_ROOT / "blockchain" / "dataset" / "transaction_dataset.csv"

def run_verification(sample_size_per_class: int = 25):
    print("=" * 68)
    print("  AEGIS DEFI FRAUD DETECTION - GROUND TRUTH ACCURACY BENCHMARK")
    print("=" * 68)
    
    print(f"\n[1/3] Loading ground-truth blockchain dataset from:\n      {DATASET_PATH}")
    if not DATASET_PATH.exists():
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        return False
        
    df = pd.read_csv(DATASET_PATH)
    df.columns = df.columns.str.strip()
    
    total_records = len(df)
    total_fraud = len(df[df['FLAG'] == 1])
    total_legit = len(df[df['FLAG'] == 0])
    
    print(f"      Total records loaded: {total_records:,}")
    print(f"      - Confirmed Legitimate (FLAG=0): {total_legit:,}")
    print(f"      - Confirmed Fraudulent (FLAG=1): {total_fraud:,}")

    print(f"\n[2/3] Evaluating individual sample wallets (Actual vs Predicted)...")
    print("-" * 68)
    print(f" {'#':<3} | {'Actual':<10} | {'Predicted':<10} | {'Prob':<8} | {'Score':<7} | {'Verdict':<8}")
    print("-" * 68)

    # Sample equal balanced cases
    legit_samples = df[df['FLAG'] == 0].sample(sample_size_per_class, random_state=42)
    fraud_samples = df[df['FLAG'] == 1].sample(sample_size_per_class, random_state=42)
    test_rows = pd.concat([legit_samples, fraud_samples]).sample(frac=1.0, random_state=42).reset_index(drop=True)

    y_true = []
    y_pred = []
    
    correct_count = 0

    for idx, row in test_rows.iterrows():
        actual_flag = int(row['FLAG'])
        actual_label = "FRAUD" if actual_flag == 1 else "LEGITIMATE"
        
        drop_cols = [c for c in row.index if c in ('FLAG', 'Address', 'Index', 'Unnamed: 0')]
        wallet_row = row.drop(labels=drop_cols).to_frame().T

        # Run prediction
        res = predict_fraud_risk(wallet_row)
        pred_label = res['prediction']
        
        is_match = (actual_label == pred_label)
        if is_match:
            correct_count += 1
            verdict_text = "[CORRECT]"
        else:
            verdict_text = "[WRONG]"

        y_true.append(actual_label)
        y_pred.append(pred_label)

        # Show first 15 rows for inspection
        if idx < 15:
            print(f" {idx+1:<3} | {actual_label:<10} | {pred_label:<10} | {res['fraud_probability']:<8.4f} | {res['risk_score']:<7.1f} | {verdict_text:<8}")

    if len(test_rows) > 15:
        print(f" ... ({len(test_rows) - 15} additional test rows processed) ...")

    # Metrics
    acc = accuracy_score(y_true, y_pred)
    
    print("-" * 68)
    print(f"\n[3/3] Final Accuracy Report across {len(test_rows)} test wallets:")
    print("=" * 68)
    print(f"  Accuracy Score : {acc * 100:.2f}% ({correct_count}/{len(test_rows)} correct)")
    print("=" * 68)
    print("\nDetailed Performance Metrics:")
    print(classification_report(y_true, y_pred, digits=4))
    
    print("Confusion Matrix:")
    cm = confusion_matrix(y_true, y_pred, labels=["LEGITIMATE", "FRAUD"])
    print(f"  True Legitimate : {cm[0][0]:<4} | False Fraud (Type I Error)  : {cm[0][1]}")
    print(f"  False Legit     : {cm[1][0]:<4} | True Fraud  (Type II Error) : {cm[1][1]}")
    print("=" * 68)

    return True

if __name__ == "__main__":
    run_verification(sample_size_per_class=25)
