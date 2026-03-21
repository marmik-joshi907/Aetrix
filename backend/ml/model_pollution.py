"""
Air Quality / Pollution Risk Predictor
- XGBoost classifier for AQI category (0-5: Good to Severe)
- DBSCAN for spatial pollution hotspot clustering
"""
import os
import sys
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.cluster import DBSCAN
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "saved")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def train_pollution_model(processed_path=None):
    """Train XGBoost AQI classifier + DBSCAN spatial clustering."""
    if processed_path is None:
        processed_path = os.path.join(PROCESSED_DIR, "pollution_clean.csv")

    df = pd.read_csv(processed_path)

    # Features: all available pollutants + coordinates
    pollutant_cols = [c for c in ["CO", "NH3", "NO2", "OZONE", "PM10", "PM2.5", "SO2"]
                      if c in df.columns]
    feature_cols = pollutant_cols + ["latitude", "longitude"]
    target_col = "aqi_category"

    # Encode state as label
    le_state = LabelEncoder()
    df["state_enc"] = le_state.fit_transform(df["state"])
    feature_cols.append("state_enc")

    X = df[feature_cols].fillna(df[feature_cols].median())
    y = df[target_col]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # XGBoost
    xgb = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
    )
    xgb.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # Evaluate
    y_pred = xgb.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[POLLUTION XGB] Accuracy: {acc:.4f}")
    labels = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    present = sorted(y.unique())
    print(classification_report(
        y_test, y_pred,
        labels=present,
        target_names=[labels[i] for i in present],
        zero_division=0,
    ))

    # DBSCAN spatial hotspot clustering
    coords = df[["latitude", "longitude"]].values
    coords_rad = np.radians(coords)
    db = DBSCAN(eps=0.5, min_samples=3, metric="haversine")
    cluster_labels = db.fit_predict(coords_rad)
    df["hotspot_cluster"] = cluster_labels
    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    print(f"[POLLUTION DBSCAN] Found {n_clusters} spatial hotspot clusters")

    # Save
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(xgb, os.path.join(MODELS_DIR, "pollution_xgb.pkl"))
    joblib.dump(le_state, os.path.join(MODELS_DIR, "pollution_state_encoder.pkl"))
    joblib.dump(feature_cols, os.path.join(MODELS_DIR, "pollution_features.pkl"))
    joblib.dump(pollutant_cols, os.path.join(MODELS_DIR, "pollution_pollutant_cols.pkl"))

    # Save hotspot data for the map
    hotspot_cols = ["state", "city", "station", "latitude", "longitude",
                    "aqi_category", "aqi_label", "hotspot_cluster"]
    for c in ["PM2.5", "NO2"]:
        if c in df.columns:
            hotspot_cols.append(c)
    hotspot_df = df[hotspot_cols].copy()
    hotspot_df.to_csv(os.path.join(PROCESSED_DIR, "hotspots.csv"), index=False)
    print("[POLLUTION MODEL] All saved.")
    return xgb


def predict_pollution(state: str, latitude: float, longitude: float,
                      pollutants: dict):
    """
    pollutants: dict with any subset of keys: CO, NH3, NO2, OZONE, PM10, PM2.5, SO2
    Returns: AQI category + label + per-pollutant risk flags
    """
    xgb = joblib.load(os.path.join(MODELS_DIR, "pollution_xgb.pkl"))
    le_state = joblib.load(os.path.join(MODELS_DIR, "pollution_state_encoder.pkl"))
    feature_cols = joblib.load(os.path.join(MODELS_DIR, "pollution_features.pkl"))
    pollutant_cols = joblib.load(os.path.join(MODELS_DIR, "pollution_pollutant_cols.pkl"))

    # Build input row
    row = {}
    for p in pollutant_cols:
        row[p] = pollutants.get(p, np.nan)
    row["latitude"] = latitude
    row["longitude"] = longitude

    # Encode state
    try:
        row["state_enc"] = le_state.transform([state])[0]
    except Exception:
        row["state_enc"] = 0

    df_row = pd.DataFrame([row])
    # Fill missing with training medians
    ref = pd.read_csv(os.path.join(PROCESSED_DIR, "pollution_clean.csv"))
    for col in pollutant_cols:
        if col in df_row.columns:
            df_row[col] = df_row[col].fillna(ref[col].median())

    aqi_class = int(xgb.predict(df_row[feature_cols])[0])
    aqi_probs = xgb.predict_proba(df_row[feature_cols])[0]

    labels = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]

    # Per-pollutant WHO threshold flags
    thresholds = {
        "PM2.5": 25, "PM10": 50, "NO2": 40, "SO2": 20,
        "CO": 4000, "OZONE": 100, "NH3": 200,
    }
    risk_flags = {}
    for p, threshold in thresholds.items():
        if p in pollutants and pollutants[p] is not None:
            risk_flags[p] = "EXCEEDS_WHO" if pollutants[p] > threshold else "OK"

    return {
        "aqi_category": aqi_class,
        "aqi_label": labels[aqi_class] if aqi_class < len(labels) else "Unknown",
        "probabilities": {
            labels[i]: round(float(p), 3)
            for i, p in enumerate(aqi_probs) if i < len(labels)
        },
        "pollutant_risk_flags": risk_flags,
    }
