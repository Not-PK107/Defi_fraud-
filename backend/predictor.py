"""
predictor.py
============
Standalone fraud-prediction module for the DeFi Fraud Detection project.

What this file does
-------------------
1. Loads the trained XGBoost model and preprocessing artifacts (once, at import time).
2. Provides predict_fraud_risk() -- the single function you call to get a full
   fraud assessment for any wallet feature record.
3. Is designed so the same processed input can later be passed to a SHAP
   explainer for human-readable explanations.
4. Can be imported by a Flask/FastAPI web app, a CLI script, or any other module.

Pipeline
--------
Raw input dict / DataFrame
    -> strip column name whitespace
    -> create ERC20_data_missing flag  (1 = wallet had no ERC20 activity)
    -> validate all 39 features are present
    -> reindex columns to exact training order
    -> median_imputer.transform()        (fitted on training data -- never refit)
    -> xgb_model.predict_proba()
    -> fraud_probability -> risk_score -> risk_level -> recommendation

Usage
-----
    from backend.predictor import predict_fraud_risk

    result = predict_fraud_risk({"Avg min between sent tnx": 123, ...})
    print(result)
    # {
    #     "prediction":        "FRAUD",
    #     "fraud_probability": 0.9998,
    #     "risk_score":        99.98,
    #     "risk_level":        "HIGH",
    #     "recommendation":    "AVOID TRANSACTION"
    # }
"""

from pathlib import Path

import joblib
import pandas as pd


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# This file lives at  defi/backend/predictor.py
# MODEL_DIR must point to defi/notebooks/models/
_BACKEND_DIR = Path(__file__).resolve().parent          # defi/backend/
_PROJECT_ROOT = _BACKEND_DIR.parent                     # defi/
MODEL_DIR = _PROJECT_ROOT / "notebooks" / "models"


# ---------------------------------------------------------------------------
# Risk-level thresholds  (change these constants, not the logic below)
# ---------------------------------------------------------------------------

LOW_RISK_THRESHOLD = 30    # 0  -- 29  -> LOW
HIGH_RISK_THRESHOLD = 70   # 30 -- 69  -> MEDIUM  |  70 -- 100 -> HIGH


# ---------------------------------------------------------------------------
# Load artifacts once when this module is first imported
# ---------------------------------------------------------------------------
# Loading at import time means the model is in memory for the entire life of
# the application -- no repeated disk reads for every prediction.

_model = joblib.load(MODEL_DIR / "fraud_model.pkl")
_feature_columns = joblib.load(MODEL_DIR / "feature_columns.pkl")
_imputer = joblib.load(MODEL_DIR / "median_imputer.pkl")

# Sanity check -- make sure the three artifacts are consistent with each other
assert len(_feature_columns) == len(_imputer.feature_names_in_), (
    "Mismatch: feature_columns.pkl and median_imputer.pkl have different lengths. "
    "Re-run the training notebook to regenerate consistent artifacts."
)


# ---------------------------------------------------------------------------
# Helper: risk score
# ---------------------------------------------------------------------------

def calculate_risk_score(fraud_probability: float) -> float:
    """
    Convert the model's fraud probability (0.0 - 1.0) to a 0-100 risk score.

    Examples
    --------
    fraud_probability = 0.9998  ->  risk_score = 99.98
    fraud_probability = 0.0012  ->  risk_score =  0.12
    """
    return round(fraud_probability * 100, 2)


# ---------------------------------------------------------------------------
# Helper: risk level
# ---------------------------------------------------------------------------

def get_risk_level(risk_score: float) -> str:
    """
    Classify the risk score into a human-readable level.

    Thresholds (defined as module constants so they are easy to adjust):
        0  -- 29   -> "LOW"
        30 -- 69   -> "MEDIUM"
        70 -- 100  -> "HIGH"
    """
    if risk_score < LOW_RISK_THRESHOLD:
        return "LOW"
    elif risk_score < HIGH_RISK_THRESHOLD:
        return "MEDIUM"
    else:
        return "HIGH"


# ---------------------------------------------------------------------------
# Helper: recommendation
# ---------------------------------------------------------------------------

def get_recommendation(risk_level: str) -> str:
    """
    Return a plain-English recommendation based on the risk level.

    The ML model predicts fraud probability.
    The risk-management layer (this function) interprets it for the user.
    """
    recommendations = {
        "LOW":    "PROCEED",
        "MEDIUM": "PROCEED WITH CAUTION",
        "HIGH":   "AVOID TRANSACTION",
    }
    return recommendations.get(risk_level, "UNKNOWN")


# ---------------------------------------------------------------------------
# Main prediction function
# ---------------------------------------------------------------------------

def predict_fraud_risk(
    wallet_features,
    threshold: float = 0.50,
) -> dict:
    """
    Assess one wallet and return a complete fraud decision.

    Parameters
    ----------
    wallet_features : dict or single-row pd.DataFrame
        Must contain the 38 raw numeric features.
        The 39th feature (ERC20_data_missing) is created automatically
        if it is not already present.

    threshold : float, default 0.50
        Probability cutoff for the FRAUD / LEGITIMATE label.
        The risk_score and risk_level are always computed from the raw
        probability -- only the final label flips at this threshold.

    Returns
    -------
    dict with keys:
        prediction        - "FRAUD" or "LEGITIMATE"
        fraud_probability - raw model probability (0.0000 - 1.0000)
        risk_score        - probability scaled to 0-100
        risk_level        - "LOW", "MEDIUM", or "HIGH"
        recommendation    - "PROCEED", "PROCEED WITH CAUTION", or "AVOID TRANSACTION"
        _processed_input  - the cleaned DataFrame fed to the model
                            (kept so SHAP can use it directly)

    Raises
    ------
    ValueError  - if threshold is out of range or required features are missing
    TypeError   - if wallet_features is not a dict or single-row DataFrame
    """

    # ---- 1. Validate threshold ----
    if not 0 < threshold < 1:
        raise ValueError(
            f"threshold must be between 0 and 1 (exclusive), got {threshold}"
        )

    # ---- 2. Normalise input to a DataFrame ----
    if isinstance(wallet_features, dict):
        wallet_frame = pd.DataFrame([wallet_features])
    elif isinstance(wallet_features, pd.DataFrame):
        if len(wallet_features) != 1:
            raise TypeError(
                "wallet_features must be a dict or a one-row DataFrame, "
                f"got a DataFrame with {len(wallet_features)} rows."
            )
        wallet_frame = wallet_features.copy()
    else:
        raise TypeError(
            "wallet_features must be a dict or a single-row pd.DataFrame, "
            f"got {type(wallet_features)}"
        )

    # ---- 3. Strip whitespace from all column names ----
    # The raw dataset has columns with leading spaces (e.g. " Total ERC20 tnxs").
    # This step makes matching reliable regardless of the source.
    wallet_frame.columns = wallet_frame.columns.str.strip()

    # ---- 4. Create ERC20_data_missing flag ----
    # During training, a wallet with no ERC20 activity had NaN in all ERC20
    # columns. A flag column was created to capture this information before
    # imputation. We must replicate the exact same logic here.
    if "ERC20_data_missing" not in wallet_frame.columns:
        if "Total ERC20 tnxs" not in wallet_frame.columns:
            raise ValueError(
                "Input must contain either 'Total ERC20 tnxs' "
                "(so ERC20_data_missing can be derived) "
                "or 'ERC20_data_missing' itself."
            )
        wallet_frame["ERC20_data_missing"] = (
            wallet_frame["Total ERC20 tnxs"].isna().astype(int)
        )

    # ---- 5. Verify all 39 required features are present ----
    missing = [f for f in _feature_columns if f not in wallet_frame.columns]
    if missing:
        raise ValueError(
            f"Input is missing {len(missing)} required feature(s):\n  "
            + "\n  ".join(missing)
        )

    # Warn about unexpected extra columns (they will be silently ignored below)
    extra = [c for c in wallet_frame.columns if c not in _feature_columns]
    if extra:
        print(
            f"[predictor] Note: {len(extra)} extra column(s) in input will be "
            f"ignored: {extra}"
        )

    # ---- 6. Reorder columns to exactly match training order ----
    # XGBoost (and the imputer) expect columns in the exact order they were
    # seen during fit(). reindex() enforces that order and drops extras.
    model_input = wallet_frame.reindex(columns=_feature_columns)

    # ---- 7. Apply the saved imputer (median fill) ----
    # IMPORTANT: we call .transform() NOT .fit_transform().
    # The imputer was already fitted on the training set.
    # Re-fitting here would cause data leakage.
    model_input = pd.DataFrame(
        _imputer.transform(model_input),
        columns=_feature_columns,
    )

    # ---- 8. Get probability from the XGBoost model ----
    # predict_proba() returns [[prob_class_0, prob_class_1]]
    # We want prob_class_1, which is the fraud probability.
    fraud_probability = float(_model.predict_proba(model_input)[0, 1])

    # ---- 9. Derive risk score, level, recommendation ----
    risk_score     = calculate_risk_score(fraud_probability)
    risk_level     = get_risk_level(risk_score)
    recommendation = get_recommendation(risk_level)

    # ---- 10. Build and return the result ----
    return {
        "prediction":        "FRAUD" if fraud_probability >= threshold else "LEGITIMATE",
        "fraud_probability": round(fraud_probability, 4),
        "risk_score":        risk_score,
        "risk_level":        risk_level,
        "recommendation":    recommendation,
        # _processed_input is kept for SHAP:
        #   explainer = shap.TreeExplainer(_model)
        #   shap_values = explainer.shap_values(result["_processed_input"])
        "_processed_input":  model_input,
    }
