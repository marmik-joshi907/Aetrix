"""
Land Use Change Detector
Uses pollution + soil data spatially to cluster land use change risk zones.
Outputs a risk score per geographic cell (lat/lon grid).
K-Means clustering on spatial features → change risk zone classification.
"""
import os
import sys
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "saved")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def train_landuse_model():
    """
    Fuses pollution and soil moisture data spatially.
    Clusters geographic areas into land-use change risk zones.
    """
    poll = pd.read_csv(os.path.join(PROCESSED_DIR, "pollution_clean.csv"))
    soil = pd.read_csv(os.path.join(PROCESSED_DIR, "soil_clean.csv"))

    # Use only Gujarat stations from pollution data
    gujarat_poll = poll[poll["state"].str.lower().str.strip() == "gujarat"].copy()
    print(f"[LANDUSE] Gujarat pollution stations: {len(gujarat_poll)}")

    # Soil: aggregate per district (average over all dates)
    soil_agg = soil.groupby("district").agg(
        sm_level_mean=("sm_level", "mean"),
        sm_agg_pct_mean=("sm_agg_pct", "mean"),
        sm_vol_pct_mean=("sm_vol_pct", "mean"),
        drought_risk_mean=("drought_risk", "mean"),
    ).reset_index()

    # Build feature matrix from pollution data
    if len(gujarat_poll) > 0:
        feature_cols = ["latitude", "longitude"]
        for col in ["PM2.5", "NO2", "PM10"]:
            if col in gujarat_poll.columns:
                feature_cols.append(col)
        X = gujarat_poll[feature_cols].dropna()

        if len(X) < 5:
            print("[LANDUSE] Not enough Gujarat stations. Using all-India data.")
            X = poll[feature_cols].dropna()
    else:
        feature_cols = ["latitude", "longitude", "PM2.5", "NO2"]
        feature_cols = [c for c in feature_cols if c in poll.columns]
        X = poll[feature_cols].dropna()

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # K-Means: 4 clusters = Low/Medium/High/Very High change risk
    n_clusters = min(4, len(X))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    result = X.copy()
    result["landuse_cluster"] = clusters

    # Label clusters by average PM2.5
    pm_col = "PM2.5" if "PM2.5" in result.columns else feature_cols[-1]
    cluster_pm = result.groupby("landuse_cluster")[pm_col].mean().sort_values(ascending=True)
    risk_map = {cluster: i for i, cluster in enumerate(cluster_pm.index)}
    result["change_risk"] = result["landuse_cluster"].map(risk_map)
    result["change_risk_label"] = result["change_risk"].map(
        {0: "Low", 1: "Moderate", 2: "High", 3: "Very High"}
    )

    # Save
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(kmeans, os.path.join(MODELS_DIR, "landuse_kmeans.pkl"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "landuse_scaler.pkl"))
    joblib.dump(feature_cols, os.path.join(MODELS_DIR, "landuse_features.pkl"))
    joblib.dump(risk_map, os.path.join(MODELS_DIR, "landuse_risk_map.pkl"))

    result.to_csv(os.path.join(PROCESSED_DIR, "landuse_clusters.csv"), index=False)
    print(f"[LANDUSE] Saved {n_clusters} clusters.")
    print(result[["latitude", "longitude", pm_col, "change_risk_label"]].head(10))
    return kmeans


def predict_landuse(latitude: float, longitude: float, pm25: float, no2: float):
    """Predict land-use change risk for a given location."""
    kmeans = joblib.load(os.path.join(MODELS_DIR, "landuse_kmeans.pkl"))
    scaler = joblib.load(os.path.join(MODELS_DIR, "landuse_scaler.pkl"))
    feature_cols = joblib.load(os.path.join(MODELS_DIR, "landuse_features.pkl"))
    risk_map = joblib.load(os.path.join(MODELS_DIR, "landuse_risk_map.pkl"))

    row = {
        "latitude": latitude,
        "longitude": longitude,
        "PM2.5": pm25,
        "NO2": no2,
        "PM10": pm25 * 1.5,
    }
    X = pd.DataFrame([[row.get(c, 0) for c in feature_cols]], columns=feature_cols)
    X_scaled = scaler.transform(X)

    cluster = int(kmeans.predict(X_scaled)[0])
    risk = risk_map.get(cluster, 0)
    labels = {0: "Low", 1: "Moderate", 2: "High", 3: "Very High"}

    return {
        "latitude": latitude,
        "longitude": longitude,
        "cluster": cluster,
        "change_risk": risk,
        "change_risk_label": labels.get(risk, "Unknown"),
    }
