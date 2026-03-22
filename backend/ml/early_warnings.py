"""
Early Warning System Module.

Generates area-based predictive alerts by analyzing current trends and
projecting future conditions. Uses ARIMA forecasts + threshold-based
rules to issue forward-looking warnings.

Examples:
- "Heatwave expected in next 10 days"
- "Vegetation stress increasing — risk of 20% canopy loss"
- "Drought conditions likely within 2 weeks"
"""
import numpy as np
import logging

logger = logging.getLogger(__name__)


# Warning definitions with thresholds (calibrated to detect real changes)
WARNING_DEFINITIONS = {
    "heatwave": {
        "parameter": "temperature",
        "condition": lambda current, forecast: forecast > 38 or (forecast - current) > 1.5,
        "icon": "🔥",
        "category": "Extreme Heat",
        "color": "#ef4444",
        "get_message": lambda c, f, days: (
            f"Heatwave Alert: Temperature expected to reach {f:.1f}°C within {days} days "
            f"(current: {c:.1f}°C). Risk of heat stroke and infrastructure stress."
        ),
        "actions": [
            "Open cooling centers in vulnerable neighborhoods",
            "Issue public health advisory for outdoor workers",
            "Increase water distribution to affected wards",
            "Pre-position emergency medical teams",
        ],
    },
    "air_quality_emergency": {
        "parameter": "pollution",
        "condition": lambda current, forecast: forecast > 120 or (forecast - current) > 15,
        "icon": "💨",
        "category": "Air Quality Emergency",
        "color": "#f97316",
        "get_message": lambda c, f, days: (
            f"Air Quality Alert: AQI expected to reach {f:.0f} within {days} days "
            f"(current: {c:.0f}). Respiratory health risk for sensitive populations."
        ),
        "actions": [
            "Issue N95 mask advisory for outdoor activities",
            "Restrict construction in affected zones",
            "Increase public transit to reduce vehicular emissions",
            "Deploy mobile air quality monitors",
        ],
    },
    "vegetation_stress": {
        "parameter": "ndvi",
        "condition": lambda current, forecast: forecast < 0.25 or (current - forecast) > 0.01,
        "icon": "🌿",
        "category": "Vegetation Stress",
        "color": "#eab308",
        "get_message": lambda c, f, days: (
            f"Vegetation Alert: NDVI declining to {f:.3f} within {days} days "
            f"(current: {c:.3f}). Risk of canopy loss and increased heat exposure."
        ),
        "actions": [
            "Increase watering frequency for urban plantations",
            "Inspect trees in affected zones for disease/pest damage",
            "Defer any planned tree removal or pruning",
            "Apply organic mulch to retain soil moisture around trees",
        ],
    },
    "drought": {
        "parameter": "soil_moisture",
        "condition": lambda current, forecast: forecast < 0.2 or (current - forecast) > 0.01,
        "icon": "🏜️",
        "category": "Drought Warning",
        "color": "#92400e",
        "get_message": lambda c, f, days: (
            f"Drought Alert: Soil moisture dropping to {f*100:.1f}% within {days} days "
            f"(current: {c*100:.1f}%). Agricultural and water supply impact expected."
        ),
        "actions": [
            "Activate drip irrigation advisories for farmers",
            "Implement water rationing for non-essential use",
            "Monitor groundwater extraction rates",
            "Prepare drought relief supply chain",
        ],
    },
}


def generate_early_warnings(data_dict, metadata, current_week=-1, forecast_days=10):
    """
    Generate area-based early warnings using ARIMA-like trend projection.

    Args:
        data_dict: {parameter: 3D numpy array}
        metadata: dataset metadata
        current_week: current week index
        forecast_days: how many days ahead to forecast

    Returns:
        dict with early warning alerts
    """
    city = metadata.get("city", "Unknown")
    bounds = metadata.get("bounds", {})
    alerts = []
    forecast_weeks = max(1, forecast_days // 7)

    for warning_name, warning_def in WARNING_DEFINITIONS.items():
        param_name = warning_def["parameter"]
        param_data = data_dict.get(param_name)

        if param_data is None or param_data.ndim != 3:
            continue

        num_weeks = param_data.shape[0]
        if num_weeks < 4:
            continue

        # Current values
        current_grid = param_data[current_week]
        current_mean = float(np.nanmean(current_grid))
        current_max = float(np.nanmax(current_grid))

        # Simple linear trend projection
        recent_means = []
        for w in range(min(8, num_weeks)):
            idx = current_week - w
            if idx < -num_weeks:
                break
            recent_means.append(float(np.nanmean(param_data[idx])))

        recent_means.reverse()

        if len(recent_means) < 3:
            continue

        # Linear projection
        x = np.arange(len(recent_means))
        slope = float(np.polyfit(x, recent_means, 1)[0])
        forecast_value = current_mean + slope * forecast_weeks

        # Check if warning condition is met
        try:
            if warning_def["condition"](current_mean, forecast_value):
                # Determine severity
                if param_name in ("temperature", "pollution"):
                    change = forecast_value - current_mean
                else:
                    change = current_mean - forecast_value  # For NDVI/soil, decrease = bad

                if change > 0:
                    change_rate = (change / max(abs(current_mean), 0.001)) * 100
                else:
                    change_rate = (abs(change) / max(abs(current_mean), 0.001)) * 100

                if change_rate > 15:
                    urgency = "critical"
                    urgency_label = "Immediate Action Required"
                elif change_rate > 8:
                    urgency = "warning"
                    urgency_label = "Action Needed Soon"
                else:
                    urgency = "watch"
                    urgency_label = "Monitor Closely"

                # Find affected areas (hotspot locations)
                affected_areas = _find_affected_areas(
                    current_grid, bounds, param_name, warning_name
                )

                alerts.append({
                    "type": warning_name,
                    "category": warning_def["category"],
                    "icon": warning_def["icon"],
                    "color": warning_def["color"],
                    "urgency": urgency,
                    "urgency_label": urgency_label,
                    "message": warning_def["get_message"](
                        current_mean, forecast_value, forecast_days
                    ),
                    "parameter": param_name,
                    "current_value": round(current_mean, 4),
                    "forecast_value": round(forecast_value, 4),
                    "forecast_days": forecast_days,
                    "change_rate": round(change_rate, 1),
                    "trend_data": [round(v, 4) for v in recent_means],
                    "affected_areas": affected_areas,
                    "recommended_actions": warning_def["actions"],
                })
        except Exception as e:
            logger.warning(f"Warning check failed for {warning_name}: {e}")

    # Sort by urgency
    urgency_order = {"critical": 0, "warning": 1, "watch": 2}
    alerts.sort(key=lambda x: urgency_order.get(x["urgency"], 3))

    return {
        "city": city,
        "forecast_days": forecast_days,
        "alert_count": len(alerts),
        "critical_count": sum(1 for a in alerts if a["urgency"] == "critical"),
        "alerts": alerts,
    }


def _find_affected_areas(grid_2d, bounds, param_name, warning_type):
    """Find the most affected sub-areas in the grid."""
    rows, cols = grid_2d.shape
    lat_min = bounds.get("lat_min", 0)
    lat_max = bounds.get("lat_max", 1)
    lon_min = bounds.get("lon_min", 0)
    lon_max = bounds.get("lon_max", 1)

    # Divide into quadrants
    quadrants = [
        {"name": "North-West", "r_range": (0, rows // 2), "c_range": (0, cols // 2)},
        {"name": "North-East", "r_range": (0, rows // 2), "c_range": (cols // 2, cols)},
        {"name": "South-West", "r_range": (rows // 2, rows), "c_range": (0, cols // 2)},
        {"name": "South-East", "r_range": (rows // 2, rows), "c_range": (cols // 2, cols)},
    ]

    areas = []
    for quad in quadrants:
        r_start, r_end = quad["r_range"]
        c_start, c_end = quad["c_range"]
        sub_grid = grid_2d[r_start:r_end, c_start:c_end]
        mean_val = float(np.nanmean(sub_grid))

        # Center lat/lon of quadrant
        lat = lat_min + (lat_max - lat_min) * ((r_start + r_end) / 2) / rows
        lon = lon_min + (lon_max - lon_min) * ((c_start + c_end) / 2) / cols

        areas.append({
            "name": quad["name"],
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "mean_value": round(mean_val, 4),
        })

    # Sort by severity (highest values for temp/pollution, lowest for ndvi/soil)
    if param_name in ("temperature", "pollution"):
        areas.sort(key=lambda x: x["mean_value"], reverse=True)
    else:
        areas.sort(key=lambda x: x["mean_value"])

    return areas[:3]  # Top 3 most affected
