"""
Anomaly Detection Module.

Uses Isolation Forest to detect unusual spatial patterns in:
- Temperature (heat spikes)
- Pollution (AQI spikes)
- NDVI (vegetation loss)
- Soil Moisture (drought indicators)

Returns anomaly locations with severity scores.
"""
import numpy as np
from sklearn.ensemble import IsolationForest
import logging

logger = logging.getLogger(__name__)


def detect_anomalies(data_2d, contamination=0.05, parameter_name="unknown"):
    """
    Detect spatial anomalies in a 2D grid using Isolation Forest.
    
    Args:
        data_2d: 2D numpy array (single timestep)
        contamination: Expected fraction of anomalies (0.01 to 0.1)
        parameter_name: Name of the parameter for logging
    
    Returns:
        dict with:
            'anomaly_mask': boolean 2D array (True = anomaly)
            'scores': 2D array of anomaly scores (-1=anomaly, 1=normal)
            'anomaly_points': list of {row, col, value, severity}
    """
    rows, cols = data_2d.shape
    
    # Flatten for sklearn
    flat_data = data_2d.flatten().reshape(-1, 1)
    
    # Remove NaN for fitting
    valid_mask = ~np.isnan(flat_data.flatten())
    valid_data = flat_data[valid_mask]
    
    if len(valid_data) < 10:
        logger.warning(f"Not enough valid data for anomaly detection ({len(valid_data)} points)")
        return _empty_result(rows, cols)
    
    # Fit Isolation Forest
    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,
        n_jobs=-1
    )
    
    predictions = np.ones(len(flat_data))  # default normal
    scores = np.zeros(len(flat_data))
    
    predictions[valid_mask] = model.fit_predict(valid_data)
    scores[valid_mask] = model.decision_function(valid_data)
    
    # Reshape back to 2D
    anomaly_mask = (predictions.reshape(rows, cols) == -1)
    score_grid = scores.reshape(rows, cols)
    
    # Extract anomaly points
    anomaly_points = []
    anomaly_indices = np.where(anomaly_mask)
    for r, c in zip(anomaly_indices[0], anomaly_indices[1]):
        severity = abs(float(score_grid[r, c]))
        anomaly_points.append({
            "row": int(r),
            "col": int(c),
            "value": round(float(data_2d[r, c]), 4),
            "severity": round(severity, 4),
        })
    
    # Sort by severity (most anomalous first)
    anomaly_points.sort(key=lambda x: x["severity"], reverse=True)
    
    num_anomalies = int(anomaly_mask.sum())
    logger.info(f"Detected {num_anomalies} anomalies in {parameter_name} "
                f"({num_anomalies/(rows*cols)*100:.1f}%)")
    
    return {
        "anomaly_mask": anomaly_mask,
        "scores": score_grid,
        "anomaly_points": anomaly_points,
        "count": num_anomalies,
        "parameter": parameter_name,
    }


def detect_temporal_anomalies(time_series_3d, contamination=0.05, parameter_name="unknown"):
    """
    Detect anomalies across time by comparing each timestep's mean to the series.
    
    Identifies weeks with unusually high or low values.
    """
    num_weeks = time_series_3d.shape[0]
    weekly_means = [float(np.nanmean(time_series_3d[t])) for t in range(num_weeks)]
    weekly_stds = [float(np.nanstd(time_series_3d[t])) for t in range(num_weeks)]
    
    # Use Isolation Forest on weekly statistics
    features = np.column_stack([weekly_means, weekly_stds])
    
    model = IsolationForest(contamination=contamination, random_state=42)
    predictions = model.fit_predict(features)
    scores = model.decision_function(features)
    
    anomalous_weeks = []
    for i in range(num_weeks):
        if predictions[i] == -1:
            anomalous_weeks.append({
                "week_index": i,
                "mean_value": round(weekly_means[i], 4),
                "severity": round(abs(float(scores[i])), 4),
            })
    
    anomalous_weeks.sort(key=lambda x: x["severity"], reverse=True)
    
    logger.info(f"Detected {len(anomalous_weeks)} anomalous weeks in {parameter_name}")
    
    return {
        "anomalous_weeks": anomalous_weeks,
        "weekly_means": weekly_means,
        "parameter": parameter_name,
    }


def _empty_result(rows, cols):
    return {
        "anomaly_mask": np.zeros((rows, cols), dtype=bool),
        "scores": np.zeros((rows, cols)),
        "anomaly_points": [],
        "count": 0,
        "parameter": "unknown",
    }
