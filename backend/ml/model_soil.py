"""
Soil Moisture / Vegetation Drought Predictor
- Random Forest classifier for drought risk per district (Low/Medium/High)
- ARIMA per district for 7-day soil moisture trajectory
"""
import os
import sys
import warnings
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "saved")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def train_soil_model(processed_path=None):
    """Train Random Forest classifier + ARIMA per district."""
    if processed_path is None:
        processed_path = os.path.join(PROCESSED_DIR, "soil_clean.csv")

    df = pd.read_csv(processed_path)

    # Features for Random Forest classifier
    feature_cols = [
        "sm_level", "sm_agg_pct", "sm_vol_pct",
        "day_of_year", "week", "month", "district_encoded",
    ]
    target_col = "drought_risk"  # 0=Low, 1=Medium, 2=High

    X = df[feature_cols]
    y = df[target_col]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Random Forest
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)

    # Evaluate
    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[SOIL RF] Accuracy: {acc:.4f}")
    print(classification_report(
        y_test, y_pred,
        target_names=["Low Risk", "Medium Risk", "High Risk"],
    ))

    # Feature importance
    importances = dict(zip(feature_cols, rf.feature_importances_))
    print("[SOIL RF] Feature importances:", importances)

    # Save Random Forest
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(rf, os.path.join(MODELS_DIR, "soil_rf.pkl"))
    joblib.dump(feature_cols, os.path.join(MODELS_DIR, "soil_features.pkl"))

    # ARIMA: train one per district on sm_agg_pct time series
    train_soil_arima_per_district(df)

    print("[SOIL MODEL] All saved.")
    return rf


def train_soil_arima_per_district(df):
    """Train one ARIMA(2,1,2) model per district for 7-day sm_agg_pct forecast."""
    from statsmodels.tsa.arima.model import ARIMA

    warnings.filterwarnings("ignore")

    arima_models = {}
    df["Date"] = pd.to_datetime(df["Date"])

    for district in df["district"].unique():
        ddf = df[df["district"] == district].sort_values("Date")
        ts = ddf.set_index("Date")["sm_agg_pct"]

        if len(ts) < 30:
            print(f"  [ARIMA] Skipping {district}: too few points ({len(ts)})")
            continue

        try:
            model = ARIMA(ts, order=(2, 1, 2))
            fitted = model.fit()
            arima_models[district] = fitted
            print(f"  [ARIMA] Trained for {district} | AIC: {fitted.aic:.1f}")
        except Exception as e:
            print(f"  [ARIMA] Failed for {district}: {e}")

    joblib.dump(arima_models, os.path.join(MODELS_DIR, "soil_arima_per_district.pkl"))
    print(f"[SOIL ARIMA] Saved {len(arima_models)} district models.")


def predict_soil(district: str, sm_level: float, sm_agg_pct: float,
                 sm_vol_pct: float, day_of_year: int, week: int, month: int):
    """
    Returns:
    - drought_risk: 0/1/2 (Low/Medium/High)
    - drought_label: string
    - forecast_7d: list of 7 daily sm_agg_pct predictions
    """
    rf = joblib.load(os.path.join(MODELS_DIR, "soil_rf.pkl"))
    feature_cols = joblib.load(os.path.join(MODELS_DIR, "soil_features.pkl"))
    arima_models = joblib.load(os.path.join(MODELS_DIR, "soil_arima_per_district.pkl"))

    # Reconstruct district_encoded
    df_ref = pd.read_csv(os.path.join(PROCESSED_DIR, "soil_clean.csv"))
    districts = sorted(df_ref["district"].unique())
    district_encoded = districts.index(district) if district in districts else 0

    row = pd.DataFrame([{
        "sm_level": sm_level,
        "sm_agg_pct": sm_agg_pct,
        "sm_vol_pct": sm_vol_pct,
        "day_of_year": day_of_year,
        "week": week,
        "month": month,
        "district_encoded": district_encoded,
    }])

    risk_class = int(rf.predict(row[feature_cols])[0])
    risk_prob = rf.predict_proba(row[feature_cols])[0].tolist()
    labels = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}

    # ARIMA forecast
    forecast_7d = []
    if district in arima_models:
        try:
            fc = arima_models[district].forecast(steps=7)
            forecast_7d = [round(float(v), 2) for v in fc]
        except Exception:
            forecast_7d = []

    return {
        "district": district,
        "drought_risk": risk_class,
        "drought_label": labels[risk_class],
        "probabilities": {labels[i]: round(p, 3) for i, p in enumerate(risk_prob)},
        "forecast_7d_sm_pct": forecast_7d,
    }
