"""
Temperature Trend / UHI Predictor
Uses MLPRegressor (Neural Network) to predict next year's annual mean temperature
from a sliding window of past years.

NOTE: Originally designed for LSTM/TensorFlow but adapted to use scikit-learn
MLPRegressor since TensorFlow is not available for Python 3.14+.
The sliding-window approach is preserved — the model still uses 10-year windows
of 5 temperature features to predict the next year's temperatures.
"""
import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "saved")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

WINDOW = 10
FEATURE_COLS = ["ANNUAL", "JAN-FEB", "MAR-MAY", "JUN-SEP", "OCT-DEC"]


def build_sequences(data, window=10):
    """Create sliding window sequences for NN input."""
    X, y = [], []
    for i in range(len(data) - window):
        # Flatten the window into a 1D feature vector
        X.append(data[i : i + window].flatten())
        y.append(data[i + window])
    return np.array(X), np.array(y)


def train_temperature_model(processed_path=None):
    """Train MLPRegressor model on temperature data."""
    if processed_path is None:
        processed_path = os.path.join(PROCESSED_DIR, "temp_clean.csv")

    df = pd.read_csv(processed_path)
    df = df.sort_values("YEAR").reset_index(drop=True)

    # Feature matrix: use all 5 temperature features
    data = df[FEATURE_COLS].values  # shape: (121, 5)

    # Scale to [0,1]
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    # Build sequences with window=10 years
    X, y = build_sequences(data_scaled, window=WINDOW)
    # X shape: (111, 50)  →  111 sequences, 10*5 flattened features
    # y shape: (111, 5)   →  predict all 5 temp values for next year

    # Train / test split (80/20, no shuffle — time-series order matters)
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Build MLPRegressor (multi-layer neural network)
    model = MLPRegressor(
        hidden_layer_sizes=(128, 64, 32),
        activation="relu",
        solver="adam",
        max_iter=1000,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=30,
        random_state=42,
        verbose=True,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred_scaled = model.predict(X_test)
    y_pred = scaler.inverse_transform(y_pred_scaled)
    y_true = scaler.inverse_transform(y_test)

    mae = mean_absolute_error(y_true[:, 0], y_pred[:, 0])
    rmse = np.sqrt(mean_squared_error(y_true[:, 0], y_pred[:, 0]))
    print(f"[TEMP MODEL] MAE: {mae:.4f}°C | RMSE: {rmse:.4f}°C")

    # Save model and scaler
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODELS_DIR, "temp_mlp.pkl"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "temp_scaler.pkl"))
    joblib.dump(
        {"window": WINDOW, "feature_cols": FEATURE_COLS,
         "last_sequence": data_scaled[-WINDOW:]},
        os.path.join(MODELS_DIR, "temp_metadata.pkl"),
    )

    print("[TEMP MODEL] Saved to models/saved/temp_mlp.pkl")
    return model, scaler


def predict_temperature(years_ahead=5):
    """Load saved model and predict next N years of temperatures."""
    model = joblib.load(os.path.join(MODELS_DIR, "temp_mlp.pkl"))
    scaler = joblib.load(os.path.join(MODELS_DIR, "temp_scaler.pkl"))
    meta = joblib.load(os.path.join(MODELS_DIR, "temp_metadata.pkl"))

    sequence = meta["last_sequence"].copy()  # shape: (10, 5)
    predictions = []

    for _ in range(years_ahead):
        x_input = sequence.flatten().reshape(1, -1)  # (1, 50)
        y_pred_scaled = model.predict(x_input)
        y_pred = scaler.inverse_transform(y_pred_scaled.reshape(1, -1))[0]
        predictions.append(y_pred)
        # Slide the window: drop oldest, add new prediction (scaled)
        new_row_scaled = scaler.transform(y_pred.reshape(1, -1))[0]
        sequence = np.vstack([sequence[1:], new_row_scaled])

    # Build result
    df = pd.read_csv(os.path.join(PROCESSED_DIR, "temp_clean.csv"))
    last_year = int(df["YEAR"].max())
    result = []
    for i, pred in enumerate(predictions):
        result.append({
            "year": last_year + i + 1,
            "predicted_annual": round(float(pred[0]), 2),
            "predicted_jan_feb": round(float(pred[1]), 2),
            "predicted_mar_may": round(float(pred[2]), 2),
            "predicted_jun_sep": round(float(pred[3]), 2),
            "predicted_oct_dec": round(float(pred[4]), 2),
        })
    return result
