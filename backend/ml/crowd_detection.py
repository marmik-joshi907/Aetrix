"""
Crowd Detection Module (Simulated).

Uses satellite-derived temperature and pollution anomaly patterns to infer
crowd density in public spaces. High localized temperature combined with
pollution spikes can indicate large gatherings.

In practice, this would use high-resolution satellite imagery with ML
object detection. Here we simulate it using environmental anomaly patterns.
"""
import numpy as np
import logging

logger = logging.getLogger(__name__)


# Known gathering-prone location types (simulated)
GATHERING_ZONES = {
    "Ahmedabad": [
        {"name": "Sabarmati Riverfront", "lat": 23.0350, "lon": 72.5800, "type": "public_space", "capacity": 50000},
        {"name": "Kankaria Lake", "lat": 23.0070, "lon": 72.6060, "type": "recreation", "capacity": 30000},
        {"name": "Manek Chowk", "lat": 23.0258, "lon": 72.5873, "type": "market", "capacity": 15000},
        {"name": "Gujarat University Ground", "lat": 23.0350, "lon": 72.5450, "type": "ground", "capacity": 40000},
        {"name": "Motera Stadium Area", "lat": 23.0916, "lon": 72.5953, "type": "stadium", "capacity": 132000},
    ],
    "Delhi": [
        {"name": "India Gate", "lat": 28.6129, "lon": 77.2295, "type": "landmark", "capacity": 100000},
        {"name": "Ramlila Maidan", "lat": 28.6377, "lon": 77.2393, "type": "ground", "capacity": 50000},
        {"name": "Connaught Place", "lat": 28.6315, "lon": 77.2167, "type": "market", "capacity": 40000},
        {"name": "Red Fort", "lat": 28.6562, "lon": 77.2410, "type": "landmark", "capacity": 30000},
        {"name": "Jantar Mantar", "lat": 28.6271, "lon": 77.2166, "type": "protest_site", "capacity": 20000},
    ],
    "Bengaluru": [
        {"name": "Cubbon Park", "lat": 12.9763, "lon": 77.5929, "type": "park", "capacity": 25000},
        {"name": "Freedom Park", "lat": 12.9646, "lon": 77.5773, "type": "protest_site", "capacity": 15000},
        {"name": "Kanteerava Stadium", "lat": 12.9575, "lon": 77.5920, "type": "stadium", "capacity": 30000},
    ],
    "Mumbai": [
        {"name": "Azad Maidan", "lat": 18.9389, "lon": 72.8325, "type": "ground", "capacity": 40000},
        {"name": "Shivaji Park", "lat": 19.0285, "lon": 72.8380, "type": "park", "capacity": 50000},
        {"name": "Gateway of India", "lat": 18.9220, "lon": 72.8347, "type": "landmark", "capacity": 30000},
    ],
    "Chennai": [
        {"name": "Marina Beach", "lat": 13.0500, "lon": 80.2824, "type": "beach", "capacity": 80000},
        {"name": "Island Grounds", "lat": 13.1060, "lon": 80.2860, "type": "ground", "capacity": 50000},
        {"name": "Valluvar Kottam", "lat": 13.0500, "lon": 80.2417, "type": "landmark", "capacity": 20000},
    ],
}


def detect_crowds(data_dict, metadata, week_index=-1, city="Ahmedabad"):
    """
    Simulate crowd detection by analyzing environmental patterns at known
    gathering locations.

    Uses temperature anomalies (localized heat from body heat) and pollution
    spikes (CO2/PM from vehicles) as proxy indicators.

    Returns:
        dict with detected gatherings, risk assessment, and recommendations
    """
    zones = GATHERING_ZONES.get(city, GATHERING_ZONES.get("Ahmedabad"))
    bounds = metadata.get("bounds", {})
    grid_size = metadata.get("grid_size", 50)

    temp_data = data_dict.get("temperature")
    poll_data = data_dict.get("pollution")

    detections = []
    np.random.seed(int(week_index) + hash(city) % 1000)

    for zone in zones:
        lat, lon = zone["lat"], zone["lon"]

        # Get environmental values at this location
        temp_val = _get_value_at_point(temp_data, bounds, grid_size, lat, lon, week_index)
        poll_val = _get_value_at_point(poll_data, bounds, grid_size, lat, lon, week_index)

        # Simulate crowd detection based on environmental anomalies
        # Higher temp anomaly + pollution spike = more likely crowd
        base_crowd_prob = np.random.uniform(0.05, 0.35)

        if temp_val is not None and temp_val > 38:
            base_crowd_prob += 0.15
        if poll_val is not None and poll_val > 120:
            base_crowd_prob += 0.1

        # Zone type affects probability
        type_boost = {
            "ground": 0.15, "stadium": 0.2, "protest_site": 0.2,
            "market": 0.1, "landmark": 0.08, "recreation": 0.05,
            "park": 0.05, "public_space": 0.1, "beach": 0.1,
        }
        base_crowd_prob += type_boost.get(zone["type"], 0)

        crowd_prob = min(base_crowd_prob, 0.95)

        # Only report if probability is above threshold
        if crowd_prob > 0.25:
            estimated_count = int(zone["capacity"] * crowd_prob * np.random.uniform(0.3, 0.7))
            density = estimated_count / zone["capacity"]

            # Stampede risk assessment
            if density > 0.7:
                stampede_risk = "high"
                risk_color = "#ef4444"
            elif density > 0.4:
                stampede_risk = "moderate"
                risk_color = "#f59e0b"
            else:
                stampede_risk = "low"
                risk_color = "#22c55e"

            detections.append({
                "location": zone["name"],
                "lat": lat,
                "lon": lon,
                "type": zone["type"],
                "capacity": zone["capacity"],
                "estimated_crowd": estimated_count,
                "density_percent": round(density * 100, 1),
                "crowd_probability": round(crowd_prob, 2),
                "stampede_risk": stampede_risk,
                "risk_color": risk_color,
                "environmental_indicators": {
                    "temperature": round(temp_val, 1) if temp_val is not None else None,
                    "pollution_aqi": round(poll_val, 0) if poll_val is not None else None,
                },
                "recommendations": _get_crowd_recommendations(stampede_risk, estimated_count, zone),
            })

    # Sort by stampede risk severity
    risk_order = {"high": 0, "moderate": 1, "low": 2}
    detections.sort(key=lambda x: risk_order.get(x["stampede_risk"], 3))

    # Overall assessment
    high_risk_count = sum(1 for d in detections if d["stampede_risk"] == "high")
    total_estimated = sum(d["estimated_crowd"] for d in detections)

    return {
        "city": city,
        "total_detections": len(detections),
        "total_estimated_crowd": total_estimated,
        "high_risk_zones": high_risk_count,
        "detections": detections,
        "methodology": "Environmental anomaly patterns (temperature + pollution proxy)",
        "disclaimer": "Crowd estimates are simulated using environmental proxy data. "
                      "Actual crowd detection requires high-resolution satellite imagery.",
    }


def _get_value_at_point(data_3d, bounds, grid_size, lat, lon, week_index):
    """Get value from 3D data array at a lat/lon point."""
    if data_3d is None:
        return None

    try:
        lat_min = bounds.get("lat_min", 0)
        lat_max = bounds.get("lat_max", 1)
        lon_min = bounds.get("lon_min", 0)
        lon_max = bounds.get("lon_max", 1)

        if data_3d.ndim == 3:
            _, rows, cols = data_3d.shape
            data_2d = data_3d[week_index]
        else:
            rows, cols = data_3d.shape
            data_2d = data_3d

        row = int((lat - lat_min) / (lat_max - lat_min) * (rows - 1))
        col = int((lon - lon_min) / (lon_max - lon_min) * (cols - 1))

        row = max(0, min(row, rows - 1))
        col = max(0, min(col, cols - 1))

        val = float(data_2d[row, col])
        return val if not np.isnan(val) else None
    except Exception:
        return None


def _get_crowd_recommendations(risk_level, estimated_count, zone):
    """Generate crowd management recommendations based on risk level."""
    recommendations = []

    if risk_level == "high":
        recommendations = [
            f"Deploy crowd control barriers at {zone['name']} immediately",
            f"Station emergency medical teams (est. {estimated_count:,} people)",
            "Open alternate exit routes to prevent bottlenecks",
            "Activate CCTV monitoring and real-time crowd flow analysis",
            "Alert local police for crowd management reinforcement",
        ]
    elif risk_level == "moderate":
        recommendations = [
            f"Monitor crowd density at {zone['name']} closely",
            "Pre-position crowd control equipment nearby",
            "Ensure all emergency exits are clear and accessible",
            "Deploy crowd management volunteers at key choke points",
        ]
    else:
        recommendations = [
            f"Standard monitoring at {zone['name']}",
            "Maintain awareness of crowd growth patterns",
            "Ensure basic safety infrastructure is operational",
        ]

    return recommendations
