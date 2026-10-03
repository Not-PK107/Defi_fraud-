import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.predictor import predict_fraud_risk

DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / 'blockchain' / 'dataset' / 'transaction_dataset.csv'
)

print('Loading dataset...')
df = pd.read_csv(DATASET_PATH)
df.columns = df.columns.str.strip()
print(f'Dataset loaded: {df.shape[0]} rows x {df.shape[1]} columns')
print()

legitimate_samples = df[df['FLAG'] == 0].sample(3, random_state=42)
fraud_samples      = df[df['FLAG'] == 1].sample(3, random_state=42)
test_rows = pd.concat([legitimate_samples, fraud_samples])

SEP = '=' * 65
print(SEP)
print('PREDICTION MODULE TEST')
print(SEP)

correct = 0
total   = 0

for idx, row in test_rows.iterrows():
    actual_flag  = int(row['FLAG'])
    actual_label = 'FRAUD' if actual_flag == 1 else 'LEGITIMATE'

    # Drop non-feature columns before passing to the model
    drop_cols  = [c for c in row.index if c in ('FLAG', 'Address', 'Index', 'Unnamed: 0')]
    wallet_row = row.drop(labels=drop_cols).to_frame().T

    try:
        result = predict_fraud_risk(wallet_row)
        match  = 'CORRECT' if result['prediction'] == actual_label else 'WRONG'

        print()
        print(f'--- Row index {idx} ---')
        print(f"  Actual label      : {actual_label}")
        print(f"  Predicted label   : {result['prediction']}   [{match}]")
        print(f"  Fraud probability : {result['fraud_probability']:.4f}  "
              f"({result['fraud_probability'] * 100:.2f}%)")
        print(f"  Risk score        : {result['risk_score']} / 100")
        print(f"  Risk level        : {result['risk_level']}")
        print(f"  Recommendation    : {result['recommendation']}")

        if result['prediction'] == actual_label:
            correct += 1
        total += 1

    except Exception as exc:
        print(f'Row {idx} ERROR: {exc}')

print()
print(SEP)
print(f'SUMMARY:  {correct} / {total} predictions correct on this sample')
print(SEP)
