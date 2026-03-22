"""
Crowd Detection Module (Satellite-Simulated).

Uses satellite-derived temperature and pollution anomaly patterns to infer
crowd density in public spaces. High localized temperature combined with
pollution spikes can indicate large gatherings.

Includes political rally / meetup detection to help prevent stampedes.

In practice, this would use high-resolution satellite imagery with ML
object detection. Here we simulate it using environmental anomaly patterns.
"""
import numpy as np
import logging

logger = logging.getLogger(__name__)


# Event type definitions with detection characteristics
EVENT_TYPES = {
    "political_rally": {
        "label": "Political Rally / Meetup",
        "icon": "🏛️",
        "description": "Potential political gathering detected via satellite thermal + pollution anomaly patterns",
        "satellite_indicators": [
            "Elevated thermal signature in open ground area",
            "Localized pollution spike from generator/vehicle cluster",
            "Unusual density pattern vs baseline for this time",
        ],
        "stampede_protocols": [
            "Deploy crowd-flow barriers to prevent bottleneck formation",
            "Station emergency medical units within 200m radius",
            "Open at least 4 alternate exit routes in all cardinal directions",
            "Activate real-time CCTV crowd density monitoring",
            "Alert local police rapid-response team for crowd management",
            "Deploy drone surveillance for aerial crowd density analysis",
            "Position water and first-aid stations at entry/exit points",
        ],
    },
    "religious_gathering": {
        "label": "Religious / Festival Gathering",
        "icon": "🛕",
        "description": "Religious or festival event detected via sustained thermal anomaly patterns",
        "satellite_indicators": [
            "Extended thermal signature over multiple hours",
            "Pattern consistent with stationary crowd",
            "Historical correlation with religious calendar events",
        ],
        "stampede_protocols": [
            "Implement one-way pedestrian flow in narrow lanes",
            "Deploy crowd marshals at chokepoints and entry gates",
            "Establish crowd density thresholds with real-time alerts",
            "Ensure VIP/emergency vehicle corridors remain clear",
            "Pre-position ambulances at all major access points",
        ],
    },
    "market_crowd": {
        "label": "Market / Commercial Crowd",
        "icon": "🏪",
        "description": "High commercial zone density detected from thermal patterns",
        "satellite_indicators": [
            "Distributed thermal signatures across market zone",
            "Intermittent crowd density peaks",
        ],
        "stampede_protocols": [
            "Monitor crowd density at market entry points",
            "Maintain clear emergency exit paths",
            "Deploy crowd management volunteers at key intersections",
        ],
    },
    "sports_event": {
        "label": "Sports / Stadium Event",
        "icon": "🏟️",
        "description": "Stadium area crowd detected via concentrated thermal signature",
        "satellite_indicators": [
            "Concentrated thermal anomaly within stadium perimeter",
            "High-density vehicular pollution in parking areas",
        ],
        "stampede_protocols": [
            "Activate stadium crowd management protocol",
            "Stagger exit timing across gates to prevent surge",
            "Monitor crowd flow at all exit points with CCTV",
            "Keep emergency lanes clear for ambulance access",
        ],
    },
    "general_gathering": {
        "label": "General Public Gathering",
        "icon": "👥",
        "description": "Unclassified gathering detected via environmental anomaly patterns",
        "satellite_indicators": [
            "Thermal anomaly above baseline for location",
            "Localized environmental signature change",
        ],
        "stampede_protocols": [
            "Standard crowd monitoring protocols",
            "Maintain awareness of crowd growth patterns",
            "Ensure basic safety infrastructure is operational",
        ],
    },
}

# Known gathering-prone location types (simulated)
GATHERING_ZONES = {
    "Ahmedabad": [
        {"name": "Sabarmati Riverfront", "lat": 23.0350, "lon": 72.5800, "type": "public_space", "capacity": 50000, "event_prone": ["political_rally", "religious_gathering"]},
        {"name": "Kankaria Lake", "lat": 23.0070, "lon": 72.6060, "type": "recreation", "capacity": 30000, "event_prone": ["religious_gathering", "general_gathering"]},
        {"name": "Manek Chowk", "lat": 23.0258, "lon": 72.5873, "type": "market", "capacity": 15000, "event_prone": ["market_crowd"]},
        {"name": "Gujarat University Ground", "lat": 23.0350, "lon": 72.5450, "type": "ground", "capacity": 40000, "event_prone": ["political_rally", "sports_event"]},
        {"name": "Motera Stadium Area", "lat": 23.0916, "lon": 72.5953, "type": "stadium", "capacity": 132000, "event_prone": ["sports_event", "political_rally"]},
        {"name": "Sardar Patel Stadium", "lat": 23.0129, "lon": 72.5620, "type": "ground", "capacity": 25000, "event_prone": ["political_rally", "sports_event"]},
        {"name": "Law Garden", "lat": 23.0300, "lon": 72.5600, "type": "public_space", "capacity": 20000, "event_prone": ["market_crowd", "political_rally"]},
    ],
    "Delhi": [
        {"name": "India Gate", "lat": 28.6129, "lon": 77.2295, "type": "landmark", "capacity": 100000, "event_prone": ["political_rally", "general_gathering"]},
        {"name": "Ramlila Maidan", "lat": 28.6377, "lon": 77.2393, "type": "ground", "capacity": 50000, "event_prone": ["political_rally", "religious_gathering"]},
        {"name": "Connaught Place", "lat": 28.6315, "lon": 77.2167, "type": "market", "capacity": 40000, "event_prone": ["market_crowd", "political_rally"]},
        {"name": "Red Fort", "lat": 28.6562, "lon": 77.2410, "type": "landmark", "capacity": 30000, "event_prone": ["political_rally", "religious_gathering"]},
        {"name": "Jantar Mantar", "lat": 28.6271, "lon": 77.2166, "type": "protest_site", "capacity": 20000, "event_prone": ["political_rally"]},
        {"name": "Jawaharlal Nehru Stadium", "lat": 28.5808, "lon": 77.2337, "type": "stadium", "capacity": 60000, "event_prone": ["sports_event", "political_rally"]},
    ],
    "Bengaluru": [
        {"name": "Cubbon Park", "lat": 12.9763, "lon": 77.5929, "type": "park", "capacity": 25000, "event_prone": ["political_rally", "general_gathering"]},
        {"name": "Freedom Park", "lat": 12.9646, "lon": 77.5773, "type": "protest_site", "capacity": 15000, "event_prone": ["political_rally"]},
        {"name": "Kanteerava Stadium", "lat": 12.9575, "lon": 77.5920, "type": "stadium", "capacity": 30000, "event_prone": ["sports_event", "political_rally"]},
        {"name": "Palace Grounds", "lat": 12.9940, "lon": 77.5810, "type": "ground", "capacity": 50000, "event_prone": ["political_rally", "religious_gathering"]},
    ],
    "Mumbai": [
        {"name": "Azad Maidan", "lat": 18.9389, "lon": 72.8325, "type": "ground", "capacity": 40000, "event_prone": ["political_rally", "sports_event"]},
        {"name": "Shivaji Park", "lat": 19.0285, "lon": 72.8380, "type": "park", "capacity": 50000, "event_prone": ["political_rally", "religious_gathering"]},
        {"name": "Gateway of India", "lat": 18.9220, "lon": 72.8347, "type": "landmark", "capacity": 30000, "event_prone": ["general_gathering", "political_rally"]},
        {"name": "MMRDA Grounds BKC", "lat": 19.0640, "lon": 72.8686, "type": "ground", "capacity": 60000, "event_prone": ["political_rally", "religious_gathering"]},
    ],
    "Chennai": [
        {"name": "Marina Beach", "lat": 13.0500, "lon": 80.2824, "type": "beach", "capacity": 80000, "event_prone": ["political_rally", "general_gathering"]},
        {"name": "Island Grounds", "lat": 13.1060, "lon": 80.2860, "type": "ground", "capacity": 50000, "event_prone": ["political_rally", "religious_gathering"]},
        {"name": "Valluvar Kottam", "lat": 13.0500, "lon": 80.2417, "type": "landmark", "capacity": 20000, "event_prone": ["political_rally"]},
        {"name": "Nehru Indoor Stadium", "lat": 13.0597, "lon": 80.2691, "type": "stadium", "capacity": 40000, "event_prone": ["sports_event", "political_rally"]},
    ],
}


def detect_crowds(data_dict, metadata, week_index=-1, city="Ahmedabad"):
    """
    Simulate crowd detection by analyzing environmental patterns at known
    gathering locations.

    Uses temperature anomalies (localized heat from body heat) and pollution
    spikes (CO2/PM from vehicles) as proxy indicators.

    Returns:
        dict with detected gatherings, risk assessment, event classification,
        and stampede prevention recommendations
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
        base_crowd_prob = np.random.uniform(0.05, 0.35)

        if temp_val is not None and temp_val > 38:
            base_crowd_prob += 0.15
        if poll_val is not None and poll_val > 120:
            base_crowd_prob += 0.1

        # Zone type affects probability
        type_boost = {
            "ground": 0.15, "stadium": 0.2, "protest_site": 0.25,
            "market": 0.1, "landmark": 0.08, "recreation": 0.05,
            "park": 0.05, "public_space": 0.1, "beach": 0.1,
        }
        base_crowd_prob += type_boost.get(zone["type"], 0)
        crowd_prob = min(base_crowd_prob, 0.95)

        # Only report if probability is above threshold
        if crowd_prob > 0.25:
            estimated_count = int(zone["capacity"] * crowd_prob * np.random.uniform(0.3, 0.7))
            density = estimated_count / zone["capacity"]

            # Classify event type
            event_type = _classify_event(zone, crowd_prob, density)
            event_info = EVENT_TYPES.get(event_type, EVENT_TYPES["general_gathering"])

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

            # Use event-specific stampede protocols
            recommendations = event_info["stampede_protocols"][:5] if stampede_risk in ("high", "moderate") else event_info["stampede_protocols"][:3]

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
                "event_type": event_type,
                "event_label": event_info["label"],
                "event_icon": event_info["icon"],
                "event_description": event_info["description"],
                "satellite_indicators": event_info["satellite_indicators"],
                "environmental_indicators": {
                    "temperature": round(temp_val, 1) if temp_val is not None else None,
                    "pollution_aqi": round(poll_val, 0) if poll_val is not None else None,
                },
                "recommendations": recommendations,
            })

    # Sort by stampede risk severity
    risk_order = {"high": 0, "moderate": 1, "low": 2}
    detections.sort(key=lambda x: risk_order.get(x["stampede_risk"], 3))

    # Overall assessment
    high_risk_count = sum(1 for d in detections if d["stampede_risk"] == "high")
    total_estimated = sum(d["estimated_crowd"] for d in detections)
    political_count = sum(1 for d in detections if d["event_type"] == "political_rally")

    return {
        "city": city,
        "total_detections": len(detections),
        "total_estimated_crowd": total_estimated,
        "high_risk_zones": high_risk_count,
        "political_gatherings": political_count,
        "detections": detections,
        "methodology": "Satellite thermal + pollution anomaly pattern analysis for crowd density inference",
        "satellite_capability": (
            "Satellite imagery enables detection of large crowd formations through thermal signatures, "
            "vehicle clustering patterns, and localized pollution anomalies — helping authorities "
            "preemptively deploy stampede prevention measures at political rallies, religious events, "
            "and mass gatherings."
        ),
        "disclaimer": (
            "Crowd estimates are simulated using satellite-derived environmental proxy data. "
            "Actual crowd detection uses high-resolution satellite imagery with ML object detection. "
            "Political event classification is based on location type and historical patterns."
        ),
    }


def _classify_event(zone, crowd_prob, density):
    """Classify the likely event type based on zone characteristics and density."""
    event_prone = zone.get("event_prone", ["general_gathering"])

    # High density at protest sites or grounds → political rally
    if zone["type"] in ("protest_site", "ground") and density > 0.3:
        if "political_rally" in event_prone:
            return "political_rally"

    # Stadiums with high density → sports event
    if zone["type"] == "stadium" and density > 0.4:
        return "sports_event"

    # Markets → market crowd
    if zone["type"] == "market":
        return "market_crowd"

    # High crowd at landmarks/public spaces → could be political
    if density > 0.5 and "political_rally" in event_prone:
        return "political_rally"

    # Default to first event type prone for this zone
    return event_prone[0] if event_prone else "general_gathering"


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
