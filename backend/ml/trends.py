"""
Time-Series Trend Analysis Module.

Uses ARIMA for forecasting environmental parameters:
- Temperature trends (heat increase prediction)
- NDVI decline forecasting
- Pollution trend prediction
- Soil moisture depletion

Falls back to linear regression if ARIMA fails.
"""
import numpy as np
from scipy import stats
import logging

logger = logging.getLogger(__name__)


def predict_trend_arima(time_series, forecast_weeks=4, parameter_name="unknown"):
    """
    Predict future values using ARIMA model.
    
    Args:
        time_series: 1D array of values over time
        forecast_weeks: Number of weeks to forecast ahead
        parameter_name: Name for logging
    
    Returns:
        dict with forecast values, confidence intervals, and trend direction
    """
    time_series = np.array(time_series, dtype=float)
    
    # Remove NaN
    valid = time_series[~np.isnan(time_series)]
    if len(valid) < 10:
        return _linear_fallback(time_series, forecast_weeks, parameter_name)
    
    try:
        from statsmodels.tsa.arima.model import ARIMA
        
        # Fit ARIMA(2,1,2) - good general purpose order
        model = ARIMA(valid, order=(2, 1, 2))
        fitted = model.fit()
        
        # Forecast
        forecast_result = fitted.get_forecast(steps=forecast_weeks)
        forecast_values = forecast_result.predicted_mean.tolist()
        conf_int = forecast_result.conf_int()
        
        lower = conf_int.iloc[:, 0].tolist()
        upper = conf_int.iloc[:, 1].tolist()
        
        # Determine trend
        trend = _calculate_trend(valid, forecast_values)
        
        logger.info(f"ARIMA forecast for {parameter_name}: {trend['direction']} "
                    f"({trend['change_percent']:.1f}%)")
        
        return {
            "model": "ARIMA(2,1,2)",
            "historical": valid.tolist(),
            "forecast": forecast_values,
            "confidence_lower": lower,
            "confidence_upper": upper,
            "trend": trend,
            "parameter": parameter_name,
        }
        
    except Exception as e:
        logger.warning(f"ARIMA failed for {parameter_name}: {e}. Using linear fallback.")
        return _linear_fallback(valid, forecast_weeks, parameter_name)


def _linear_fallback(time_series, forecast_weeks, parameter_name):
    """Linear regression fallback when ARIMA fails."""
    valid = time_series[~np.isnan(time_series)] if np.any(np.isnan(time_series)) else time_series
    
    if len(valid) < 3:
        return {
            "model": "insufficient_data",
            "historical": valid.tolist() if len(valid) else [],
            "forecast": [],
            "trend": {"direction": "unknown", "change_percent": 0, "slope": 0},
            "parameter": parameter_name,
        }
    
    x = np.arange(len(valid))
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, valid)
    
    # Forecast
    future_x = np.arange(len(valid), len(valid) + forecast_weeks)
    forecast_values = (slope * future_x + intercept).tolist()
    
    # Confidence interval (simple ±2*std_err)
    margin = 2 * std_err * future_x
    lower = (np.array(forecast_values) - margin).tolist()
    upper = (np.array(forecast_values) + margin).tolist()
    
    trend = _calculate_trend(valid, forecast_values)
    
    logger.info(f"Linear forecast for {parameter_name}: {trend['direction']} "
                f"(R²={r_value**2:.3f})")
    
    return {
        "model": "linear_regression",
        "historical": valid.tolist(),
        "forecast": forecast_values,
        "confidence_lower": lower,
        "confidence_upper": upper,
        "trend": trend,
        "r_squared": round(r_value**2, 4),
        "parameter": parameter_name,
    }


def _calculate_trend(historical, forecast):
    """Calculate trend direction and magnitude."""
    if len(historical) == 0 or len(forecast) == 0:
        return {"direction": "unknown", "change_percent": 0, "slope": 0}
    
    recent_mean = float(np.mean(historical[-4:]))  # last 4 weeks
    forecast_mean = float(np.mean(forecast))
    
    if recent_mean == 0:
        change_percent = 0
    else:
        change_percent = ((forecast_mean - recent_mean) / abs(recent_mean)) * 100
    
    # Slope over entire series
    full_series = np.concatenate([historical, forecast])
    x = np.arange(len(full_series))
    slope = float(np.polyfit(x, full_series, 1)[0])
    
    if change_percent > 2:
        direction = "increasing"
    elif change_percent < -2:
        direction = "decreasing"
    else:
        direction = "stable"
    
    return {
        "direction": direction,
        "change_percent": round(change_percent, 2),
        "slope": round(slope, 6),
        "recent_mean": round(recent_mean, 4),
        "forecast_mean": round(forecast_mean, 4),
    }


def analyze_all_trends(data_3d, metadata, parameter_name, num_points=25, forecast_weeks=4):
    """
    Analyze trends at multiple sample points across the grid.
    
    Returns summary of spatial trend patterns.
    """
    num_weeks, rows, cols = data_3d.shape
    
    # Sample points evenly across the grid
    step_r = max(1, rows // int(np.sqrt(num_points)))
    step_c = max(1, cols // int(np.sqrt(num_points)))
    
    trends = []
    increasing_count = 0
    decreasing_count = 0
    stable_count = 0
    
    for r in range(0, rows, step_r):
        for c in range(0, cols, step_c):
            series = data_3d[:, r, c]
            result = predict_trend_arima(series, forecast_weeks, f"{parameter_name}[{r},{c}]")
            
            direction = result["trend"]["direction"]
            if direction == "increasing":
                increasing_count += 1
            elif direction == "decreasing":
                decreasing_count += 1
            else:
                stable_count += 1
            
            trends.append({
                "row": r,
                "col": c,
                "direction": direction,
                "change_percent": result["trend"]["change_percent"],
            })
    
    total = len(trends)
    
    return {
        "parameter": parameter_name,
        "sample_points": total,
        "increasing": increasing_count,
        "decreasing": decreasing_count,
        "stable": stable_count,
        "dominant_trend": max(
            [("increasing", increasing_count), 
             ("decreasing", decreasing_count), 
             ("stable", stable_count)],
            key=lambda x: x[1]
        )[0],
        "point_trends": trends,
    }
