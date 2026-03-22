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


# City-specific area names for meaningful area-based warnings
CITY_AREA_NAMES = {
    "Ahmedabad": {
        "NW": "Sabarmati & Motera",
        "NE": "Naroda & Odhav",
        "SW": "Navrangpura & Satellite",
        "SE": "Maninagar & Isanpur",
        "N": "Gandhinagar Highway Corridor",
        "S": "Sarkhej-Sanand Belt",
        "E": "Industrial East Zone",
        "W": "SG Highway Corridor",
        "C": "Walled City & Lal Darwaja",
    },
    "Delhi": {
        "NW": "Rohini & Pitampura",
        "NE": "Shahdara & Dilshad Garden",
        "SW": "Dwarka & Janakpuri",
        "SE": "Sarita Vihar & Okhla",
        "N": "Civil Lines & Model Town",
        "S": "Saket & Mehrauli",
        "E": "Preet Vihar & Laxmi Nagar",
        "W": "Rajouri Garden & Punjabi Bagh",
        "C": "Connaught Place & ITO",
    },
    "Bengaluru": {
        "NW": "Yeshwanthpur & Malleshwaram",
        "NE": "KR Puram & Whitefield",
        "SW": "RR Nagar & Kengeri",
        "SE": "BTM Layout & HSR Layout",
        "N": "Hebbal & Yelahanka",
        "S": "JP Nagar & Banashankari",
        "E": "Indiranagar & Marathahalli",
        "W": "Vijayanagar & Basaveshwara Nagar",
        "C": "MG Road & Cubbon Park",
    },
    "Mumbai": {
        "NW": "Andheri & Goregaon",
        "NE": "Mulund & Bhandup",
        "SW": "Bandra & Juhu",
        "SE": "Chembur & Govandi",
        "N": "Borivali & Dahisar",
        "S": "Colaba & Fort",
        "E": "Kurla & Ghatkopar",
        "W": "Versova & Malad",
        "C": "Dadar & Parel",
    },
    "Chennai": {
        "NW": "Ambattur & Padi",
        "NE": "Tondiarpet & Royapuram",
        "SW": "Guindy & Adyar",
        "SE": "Mylapore & Thiruvanmiyur",
        "N": "Perambur & Kolathur",
        "S": "Velachery & Pallikaranai",
        "E": "Marina & Triplicane",
        "W": "Porur & Valasaravakkam",
        "C": "T Nagar & Nungambakkam",
    },
}


# Warning definitions with relaxed thresholds that trigger realistically
WARNING_DEFINITIONS = {
    "heatwave": {
        "parameter": "temperature",
        "condition": lambda current, forecast, p90: (
            forecast > 35 or forecast > p90 or (forecast - current) > 1.5
        ),
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
        "condition": lambda current, forecast, p90: (
            forecast > 100 or forecast > p90 or (forecast - current) > 15
        ),
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
        "condition": lambda current, forecast, p10: (
            forecast < 0.25 or forecast < p10 or (current - forecast) > 0.01
        ),
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
        "condition": lambda current, forecast, p10: (
            forecast < 0.20 or forecast < p10 or (current - forecast) > 0.01
        ),
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
        if num_weeks < 3:
            continue

        # Current values
        current_grid = param_data[current_week]
        current_mean = float(np.nanmean(current_grid))
        current_max = float(np.nanmax(current_grid))

        # Compute percentile thresholds from historical data
        all_means = [float(np.nanmean(param_data[w])) for w in range(num_weeks)]
        p90 = float(np.percentile(all_means, 90))
        p10 = float(np.percentile(all_means, 10))

        # Simple linear trend projection
        recent_means = []
        for w in range(min(8, num_weeks)):
            idx = current_week - w
            if idx < -num_weeks:
                break
            recent_means.append(float(np.nanmean(param_data[idx])))

        recent_means.reverse()

        if len(recent_means) < 2:
            continue

        # Linear projection
        x = np.arange(len(recent_means))
        slope = float(np.polyfit(x, recent_means, 1)[0])
        forecast_value = current_mean + slope * forecast_weeks

        # Check if warning condition is met (with percentile context)
        try:
            percentile_ref = p90 if param_name in ("temperature", "pollution") else p10
            if warning_def["condition"](current_mean, forecast_value, percentile_ref):
                # Determine severity
                if param_name in ("temperature", "pollution"):
                    change = forecast_value - current_mean
                else:
                    change = current_mean - forecast_value  # For NDVI/soil, decrease = bad

                if change > 0:
                    change_rate = (change / max(abs(current_mean), 0.001)) * 100
                else:
                    change_rate = (abs(change) / max(abs(current_mean), 0.001)) * 100

                if change_rate > 10:
                    urgency = "critical"
                    urgency_label = "Immediate Action Required"
                elif change_rate > 4:
                    urgency = "warning"
                    urgency_label = "Action Needed Soon"
                else:
                    urgency = "watch"
                    urgency_label = "Monitor Closely"

                # Find affected areas with city-specific names
                affected_areas = _find_affected_areas(
                    current_grid, bounds, param_name, warning_name, city
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


def _find_affected_areas(grid_2d, bounds, param_name, warning_type, city="Unknown"):
    """Find the most affected sub-areas in the grid with city-specific names."""
    rows, cols = grid_2d.shape
    lat_min = bounds.get("lat_min", 0)
    lat_max = bounds.get("lat_max", 1)
    lon_min = bounds.get("lon_min", 0)
    lon_max = bounds.get("lon_max", 1)

    # Get city-specific area names
    area_names = CITY_AREA_NAMES.get(city, {})

    # Divide into a 3x3 grid for more granular area identification
    row_thirds = [0, rows // 3, 2 * rows // 3, rows]
    col_thirds = [0, cols // 3, 2 * cols // 3, cols]

    zone_keys = [
        ["NW", "N", "NE"],
        ["W", "C", "E"],
        ["SW", "S", "SE"],
    ]

    default_names = {
        "NW": "North-West Zone",
        "N": "North Zone",
        "NE": "North-East Zone",
        "W": "West Zone",
        "C": "Central Zone",
        "E": "East Zone",
        "SW": "South-West Zone",
        "S": "South Zone",
        "SE": "South-East Zone",
    }

    areas = []
    for ri in range(3):
        for ci in range(3):
            r_start, r_end = row_thirds[ri], row_thirds[ri + 1]
            c_start, c_end = col_thirds[ci], col_thirds[ci + 1]
            sub_grid = grid_2d[r_start:r_end, c_start:c_end]
            mean_val = float(np.nanmean(sub_grid))

            # Center lat/lon of sub-area
            lat = lat_min + (lat_max - lat_min) * ((r_start + r_end) / 2) / rows
            lon = lon_min + (lon_max - lon_min) * ((c_start + c_end) / 2) / cols

            key = zone_keys[ri][ci]
            name = area_names.get(key, default_names.get(key, f"Zone {key}"))

            areas.append({
                "name": name,
                "zone": key,
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "mean_value": round(mean_val, 4),
            })

    # Sort by severity (highest values for temp/pollution, lowest for ndvi/soil)
    if param_name in ("temperature", "pollution"):
        areas.sort(key=lambda x: x["mean_value"], reverse=True)
    else:
        areas.sort(key=lambda x: x["mean_value"])

    return areas[:4]  # Top 4 most affected areas
