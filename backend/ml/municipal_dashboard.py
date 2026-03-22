"""
Municipal Officers Dashboard Module.

Analyzes all environmental parameters, hotspots, and trends to identify
the top 3 most urgent problems with:
- Exact locations (lat/lon)
- Recommended solutions
- Projected impact after 7-10 days of implementation
- Status tracking (Pending / In Progress / Completed)
"""
import numpy as np
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# Solution templates per problem type
SOLUTION_TEMPLATES = {
    "heat_island": {
        "title": "Urban Heat Island",
        "icon": "🌡️",
        "category": "Temperature",
        "solutions": [
            {
                "action": "Deploy reflective cool-roof coatings on buildings",
                "timeline": "3-5 days",
                "cost": "Medium",
                "effectiveness": "Reduces surface temp by 2-5°C",
            },
            {
                "action": "Install shade structures and misting systems",
                "timeline": "5-7 days",
                "cost": "Medium",
                "effectiveness": "Immediate 3-4°C cooling in pedestrian zones",
            },
            {
                "action": "Emergency tree planting drive (50-100 saplings)",
                "timeline": "7-10 days",
                "cost": "Low-Medium",
                "effectiveness": "Long-term 2-8°C cooling once mature",
            },
        ],
        "impact_7d": "Expected 1-2°C reduction in hotspot temperature",
        "impact_10d": "Expected 2-4°C reduction with sustained implementation",
    },
    "air_pollution": {
        "title": "Air Pollution Hotspot",
        "icon": "🏭",
        "category": "Pollution",
        "solutions": [
            {
                "action": "Enforce emission controls on industrial units in zone",
                "timeline": "1-2 days",
                "cost": "Low (enforcement)",
                "effectiveness": "Reduces industrial emissions by 20-40%",
            },
            {
                "action": "Implement traffic diversion and odd-even restriction",
                "timeline": "1-3 days",
                "cost": "Low",
                "effectiveness": "Reduces vehicular pollution by 15-25%",
            },
            {
                "action": "Deploy water sprinklers for dust suppression",
                "timeline": "1-2 days",
                "cost": "Low",
                "effectiveness": "Reduces PM10 by 30-50%",
            },
        ],
        "impact_7d": "Expected 15-25% AQI improvement",
        "impact_10d": "Expected 25-40% AQI improvement with sustained enforcement",
    },
    "vegetation_loss": {
        "title": "Vegetation Degradation",
        "icon": "🌿",
        "category": "NDVI",
        "solutions": [
            {
                "action": "Emergency irrigation for stressed urban trees",
                "timeline": "1-2 days",
                "cost": "Low",
                "effectiveness": "Prevents further 10-15% canopy loss",
            },
            {
                "action": "Apply organic mulch and soil amendments",
                "timeline": "3-5 days",
                "cost": "Low-Medium",
                "effectiveness": "Improves soil water retention by 25-40%",
            },
            {
                "action": "Plant native drought-resistant species",
                "timeline": "7-10 days",
                "cost": "Medium",
                "effectiveness": "Restores green cover gradually over 2-6 months",
            },
        ],
        "impact_7d": "Expected stabilization of NDVI decline",
        "impact_10d": "Expected 5-10% NDVI recovery in treated areas",
    },
    "drought": {
        "title": "Soil Moisture Crisis",
        "icon": "💧",
        "category": "Soil Moisture",
        "solutions": [
            {
                "action": "Deploy mobile water tankers to affected areas",
                "timeline": "1-2 days",
                "cost": "Medium",
                "effectiveness": "Immediate relief for agricultural zones",
            },
            {
                "action": "Install rainwater harvesting systems in public buildings",
                "timeline": "5-7 days",
                "cost": "Medium-High",
                "effectiveness": "Augments groundwater recharge by 15-20%",
            },
            {
                "action": "Switch to drip irrigation in nearby agricultural land",
                "timeline": "5-10 days",
                "cost": "Medium",
                "effectiveness": "Reduces water usage by 40-60%",
            },
        ],
        "impact_7d": "Expected 5-10% soil moisture improvement",
        "impact_10d": "Expected 10-20% soil moisture improvement with sustained supply",
    },
}

# Priority scoring weights
SEVERITY_WEIGHTS = {
    "temperature": {"threshold_bad": 42, "threshold_critical": 46, "weight": 1.0},
    "pollution": {"threshold_bad": 180, "threshold_critical": 300, "weight": 1.2},
    "ndvi": {"threshold_bad": 0.18, "threshold_critical": 0.10, "weight": 0.8},
    "soil_moisture": {"threshold_bad": 0.15, "threshold_critical": 0.08, "weight": 0.9},
}


def generate_municipal_dashboard(data_dict, metadata, hotspot_results=None, week_index=-1):
    """
    Generate a municipal officers dashboard with top 3 urgent problems.

    Args:
        data_dict: {parameter: 3D numpy array}
        metadata: dataset metadata
        hotspot_results: optional hotspot detection results
        week_index: current week index

    Returns:
        dict with prioritized problems, solutions, and impact projections
    """
    city = metadata.get("city", "Unknown")
    bounds = metadata.get("bounds", {})
    timestamps = metadata.get("timestamps", [])
    current_timestamp = timestamps[week_index] if timestamps and abs(week_index) <= len(timestamps) else "N/A"

    problems = []

    for param_name, param_data in data_dict.items():
        if param_data is None:
            continue

        # Get current week's data
        if param_data.ndim == 3:
            current = param_data[week_index]
        else:
            current = param_data

        severity_config = SEVERITY_WEIGHTS.get(param_name)
        if severity_config is None:
            continue

        mean_val = float(np.nanmean(current))
        max_val = float(np.nanmax(current))
        min_val = float(np.nanmin(current))

        # Calculate severity score
        score = _calculate_severity_score(param_name, mean_val, max_val, min_val, severity_config)

        if score <= 0:
            continue

        # Find the worst location (exact lat/lon)
        worst_loc = _find_worst_location(current, bounds, param_name)

        # Get problem template
        problem_type = _get_problem_type(param_name, mean_val, max_val)
        template = SOLUTION_TEMPLATES.get(problem_type)

        if template is None:
            continue

        # Build the problem entry
        unit = metadata.get("parameters", {}).get(param_name, {}).get("unit", "")
        hotspot_count = 0
        if hotspot_results and param_name in hotspot_results:
            hotspot_count = hotspot_results[param_name].get("num_clusters", 0)

        problems.append({
            "priority_score": round(score, 2),
            "parameter": param_name,
            "title": template["title"],
            "icon": template["icon"],
            "category": template["category"],
            "location": worst_loc,
            "current_values": {
                "mean": round(mean_val, 2),
                "max": round(max_val, 2),
                "min": round(min_val, 2),
                "unit": unit,
            },
            "hotspot_clusters": hotspot_count,
            "solutions": template["solutions"],
            "impact_projection": {
                "after_7_days": template["impact_7d"],
                "after_10_days": template["impact_10d"],
            },
            "status": "pending",  # Default status
            "assigned_to": None,
            "created_at": datetime.now().isoformat(),
            "target_completion": (datetime.now() + timedelta(days=10)).isoformat(),
        })

    # Sort by priority score (highest first) and take top 3
    problems.sort(key=lambda x: x["priority_score"], reverse=True)
    top_problems = problems[:3]

    # Assign priority numbers
    for i, problem in enumerate(top_problems):
        problem["priority_rank"] = i + 1

    # Calculate overall city health score (0-100, 100 = best)
    total_score = sum(p["priority_score"] for p in problems)
    max_possible = len(problems) * 100
    health_score = max(0, 100 - (total_score / max(max_possible, 1)) * 100)

    return {
        "title": f"Municipal Dashboard: {city}",
        "city": city,
        "generated_at": datetime.now().isoformat(),
        "analysis_date": current_timestamp,
        "city_health_score": round(health_score, 1),
        "total_issues_detected": len(problems),
        "top_3_urgent": top_problems,
        "all_issues": problems,
        "summary": _generate_summary(top_problems, city),
    }


def _calculate_severity_score(param_name, mean_val, max_val, min_val, config):
    """Calculate 0-100 severity score for a parameter."""
    threshold_bad = config["threshold_bad"]
    threshold_critical = config["threshold_critical"]
    weight = config["weight"]

    if param_name in ("temperature", "pollution"):
        # Higher = worse
        if max_val >= threshold_critical:
            base_score = 80 + min(20, (max_val - threshold_critical) / threshold_critical * 100)
        elif mean_val >= threshold_bad:
            base_score = 50 + (mean_val - threshold_bad) / (threshold_critical - threshold_bad) * 30
        elif max_val >= threshold_bad:
            base_score = 30 + (max_val - threshold_bad) / (threshold_critical - threshold_bad) * 20
        else:
            base_score = 0
    else:
        # Lower = worse (NDVI, soil moisture)
        if min_val <= threshold_critical:
            base_score = 80 + min(20, (threshold_critical - min_val) / max(threshold_critical, 0.01) * 100)
        elif mean_val <= threshold_bad:
            base_score = 50 + (threshold_bad - mean_val) / max(threshold_bad - threshold_critical, 0.01) * 30
        elif min_val <= threshold_bad:
            base_score = 30 + (threshold_bad - min_val) / max(threshold_bad - threshold_critical, 0.01) * 20
        else:
            base_score = 0

    return min(100, base_score * weight)


def _find_worst_location(grid_2d, bounds, param_name):
    """Find the lat/lon of the worst value in the grid."""
    rows, cols = grid_2d.shape
    lat_min = bounds.get("lat_min", 0)
    lat_max = bounds.get("lat_max", 1)
    lon_min = bounds.get("lon_min", 0)
    lon_max = bounds.get("lon_max", 1)

    if param_name in ("temperature", "pollution"):
        # Worst = highest
        idx = np.unravel_index(np.nanargmax(grid_2d), grid_2d.shape)
    else:
        # Worst = lowest
        idx = np.unravel_index(np.nanargmin(grid_2d), grid_2d.shape)

    lat = lat_min + (lat_max - lat_min) * idx[0] / (rows - 1)
    lon = lon_min + (lon_max - lon_min) * idx[1] / (cols - 1)

    return {
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "value": round(float(grid_2d[idx]), 4),
        "area_description": _get_area_description(lat, lon, bounds),
    }


def _get_area_description(lat, lon, bounds):
    """Generate a human-readable area description based on position."""
    lat_min = bounds.get("lat_min", 0)
    lat_max = bounds.get("lat_max", 1)
    lon_min = bounds.get("lon_min", 0)
    lon_max = bounds.get("lon_max", 1)

    lat_pct = (lat - lat_min) / (lat_max - lat_min)
    lon_pct = (lon - lon_min) / (lon_max - lon_min)

    ns = "North" if lat_pct > 0.5 else "South"
    ew = "East" if lon_pct > 0.5 else "West"

    return f"{ns}-{ew} sector ({lat:.4f}°N, {lon:.4f}°E)"


def _get_problem_type(param_name, mean_val, max_val):
    """Map parameter + values to a problem type key."""
    mapping = {
        "temperature": "heat_island",
        "pollution": "air_pollution",
        "ndvi": "vegetation_loss",
        "soil_moisture": "drought",
    }
    return mapping.get(param_name)


def _generate_summary(top_problems, city):
    """Generate a brief executive summary."""
    if not top_problems:
        return f"No critical environmental issues detected in {city}."

    lines = [f"⚡ {len(top_problems)} urgent issue(s) identified in {city}:"]
    for p in top_problems:
        lines.append(
            f"  #{p['priority_rank']}: {p['title']} at {p['location']['area_description']} "
            f"(Score: {p['priority_score']})"
        )

    return "\n".join(lines)
