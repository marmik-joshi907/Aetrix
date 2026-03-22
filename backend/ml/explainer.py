"""
Explainable Predictions Module.

Cross-references all 4 environmental parameters at a point to generate
human-readable causation explanations.

Example output: "High temperature likely due to low vegetation cover (NDVI: 0.12)
and high pollution levels (AQI: 185)"
"""
import numpy as np
import logging

logger = logging.getLogger(__name__)


# === Cross-parameter causation rules ===
CAUSATION_RULES = {
    "high_temp_low_ndvi": {
        "condition": lambda t, n, p, s: t is not None and n is not None and t > 38 and n < 0.25,
        "title": "Urban Heat Island Effect",
        "icon": "🏙️",
        "severity": "high",
        "explanation": lambda t, n, p, s: (
            f"High temperature ({t:.1f}°C) is strongly correlated with low vegetation cover "
            f"(NDVI: {n:.3f}). Areas with sparse greenery absorb more solar radiation, "
            f"creating localized heat islands."
        ),
        "factors": lambda t, n, p, s: [
            {"name": "Low Vegetation", "value": f"NDVI {n:.3f}", "impact": "primary", "icon": "🌿"},
            {"name": "Surface Temperature", "value": f"{t:.1f}°C", "impact": "result", "icon": "🌡️"},
        ],
    },
    "high_temp_high_pollution": {
        "condition": lambda t, n, p, s: t is not None and p is not None and t > 38 and p > 120,
        "title": "Pollution-Amplified Heat Stress",
        "icon": "🏭",
        "severity": "critical",
        "explanation": lambda t, n, p, s: (
            f"Elevated temperature ({t:.1f}°C) combined with high pollution (AQI: {p:.0f}) "
            f"creates dangerous conditions. Pollution traps heat near the surface (greenhouse "
            f"effect), worsening thermal stress on residents."
        ),
        "factors": lambda t, n, p, s: [
            {"name": "Air Pollution", "value": f"AQI {p:.0f}", "impact": "amplifier", "icon": "🏭"},
            {"name": "Temperature", "value": f"{t:.1f}°C", "impact": "result", "icon": "🌡️"},
        ],
    },
    "high_temp_low_soil": {
        "condition": lambda t, n, p, s: t is not None and s is not None and t > 38 and s < 0.15,
        "title": "Drought-Driven Heat Amplification",
        "icon": "🏜️",
        "severity": "high",
        "explanation": lambda t, n, p, s: (
            f"Low soil moisture ({s*100:.1f}%) reduces evaporative cooling, allowing surface "
            f"temperatures to rise to {t:.1f}°C. Dry soil absorbs more heat, creating a "
            f"positive feedback loop."
        ),
        "factors": lambda t, n, p, s: [
            {"name": "Soil Moisture Deficit", "value": f"{s*100:.1f}%", "impact": "primary", "icon": "💧"},
            {"name": "Reduced Evaporation", "value": "Low cooling", "impact": "mechanism", "icon": "♨️"},
        ],
    },
    "low_ndvi_high_pollution": {
        "condition": lambda t, n, p, s: n is not None and p is not None and n < 0.2 and p > 150,
        "title": "Vegetation Decline from Air Pollution",
        "icon": "☠️",
        "severity": "critical",
        "explanation": lambda t, n, p, s: (
            f"Very low vegetation health (NDVI: {n:.3f}) in areas with severe pollution "
            f"(AQI: {p:.0f}). High concentrations of PM2.5 and NO2 damage plant tissues, "
            f"reducing photosynthesis and causing canopy die-off."
        ),
        "factors": lambda t, n, p, s: [
            {"name": "Severe Pollution", "value": f"AQI {p:.0f}", "impact": "primary", "icon": "🏭"},
            {"name": "Vegetation Loss", "value": f"NDVI {n:.3f}", "impact": "result", "icon": "🍂"},
        ],
    },
    "low_ndvi_low_soil": {
        "condition": lambda t, n, p, s: n is not None and s is not None and n < 0.2 and s < 0.15,
        "title": "Desertification Risk",
        "icon": "🏜️",
        "severity": "critical",
        "explanation": lambda t, n, p, s: (
            f"Both vegetation (NDVI: {n:.3f}) and soil moisture ({s*100:.1f}%) are critically "
            f"low, indicating active desertification. Without intervention, this area will "
            f"lose productive capacity within 2-3 seasons."
        ),
        "factors": lambda t, n, p, s: [
            {"name": "Vegetation Collapse", "value": f"NDVI {n:.3f}", "impact": "primary", "icon": "🌿"},
            {"name": "Soil Desiccation", "value": f"{s*100:.1f}%", "impact": "amplifier", "icon": "💧"},
        ],
    },
    "high_pollution_low_soil": {
        "condition": lambda t, n, p, s: p is not None and s is not None and p > 150 and s < 0.2,
        "title": "Compound Environmental Stress",
        "icon": "⚠️",
        "severity": "high",
        "explanation": lambda t, n, p, s: (
            f"High pollution (AQI: {p:.0f}) combined with low soil moisture ({s*100:.1f}%) "
            f"indicates multiple stressors. Dry conditions amplify dust and particulate matter, "
            f"further degrading air quality in a vicious cycle."
        ),
        "factors": lambda t, n, p, s: [
            {"name": "Dry Soil → Dust", "value": f"SM {s*100:.1f}%", "impact": "amplifier", "icon": "💨"},
            {"name": "Air Quality", "value": f"AQI {p:.0f}", "impact": "result", "icon": "🏭"},
        ],
    },
    "all_bad": {
        "condition": lambda t, n, p, s: (
            t is not None and n is not None and p is not None and s is not None
            and t > 40 and n < 0.2 and p > 150 and s < 0.15
        ),
        "title": "Multi-Factor Environmental Crisis",
        "icon": "🚨",
        "severity": "critical",
        "explanation": lambda t, n, p, s: (
            f"CRITICAL: All 4 parameters are in danger zones — Temperature: {t:.1f}°C, "
            f"NDVI: {n:.3f}, AQI: {p:.0f}, Soil Moisture: {s*100:.1f}%. This area faces "
            f"compounding environmental collapse requiring immediate multi-agency intervention."
        ),
        "factors": lambda t, n, p, s: [
            {"name": "Extreme Heat", "value": f"{t:.1f}°C", "impact": "critical", "icon": "🌡️"},
            {"name": "No Vegetation", "value": f"NDVI {n:.3f}", "impact": "critical", "icon": "🌿"},
            {"name": "Toxic Air", "value": f"AQI {p:.0f}", "impact": "critical", "icon": "🏭"},
            {"name": "No Water", "value": f"SM {s*100:.1f}%", "impact": "critical", "icon": "💧"},
        ],
    },
}

# Single-parameter explanations (fallback when no cross-parameter matches)
SINGLE_PARAM_EXPLANATIONS = {
    "temperature": [
        {"condition": lambda v: v > 45, "severity": "critical", "icon": "🔥",
         "title": "Extreme Heat Zone",
         "text": lambda v: f"Temperature has reached {v:.1f}°C — well above the 45°C danger threshold. Likely caused by dense built-up area, lack of green cover, and heat-trapping concrete surfaces."},
        {"condition": lambda v: v > 40, "severity": "high", "icon": "🌡️",
         "title": "Heat Stress Zone",
         "text": lambda v: f"Temperature at {v:.1f}°C indicates significant heat stress. Contributing factors include reduced tree canopy, dark rooftop surfaces, and limited water bodies."},
        {"condition": lambda v: v > 35, "severity": "moderate", "icon": "☀️",
         "title": "Elevated Temperature",
         "text": lambda v: f"Temperature at {v:.1f}°C is above comfort levels. Local factors like building density and paved surface ratio influence the microclimate."},
    ],
    "ndvi": [
        {"condition": lambda v: v < 0.1, "severity": "critical", "icon": "🏜️",
         "title": "Barren / No Vegetation",
         "text": lambda v: f"NDVI of {v:.3f} indicates near-zero vegetation. This is likely a built-up, industrial, or severely degraded area."},
        {"condition": lambda v: v < 0.2, "severity": "high", "icon": "🍂",
         "title": "Severe Vegetation Stress",
         "text": lambda v: f"NDVI of {v:.3f} shows severe vegetation decline. Possible causes: drought, deforestation, overgrazing, or land-use conversion."},
        {"condition": lambda v: v < 0.3, "severity": "moderate", "icon": "🌿",
         "title": "Moderate Vegetation Decline",
         "text": lambda v: f"NDVI of {v:.3f} indicates moderate stress. Seasonal changes or gradual urbanization may be contributing."},
    ],
    "pollution": [
        {"condition": lambda v: v > 250, "severity": "critical", "icon": "☣️",
         "title": "Hazardous Air Quality",
         "text": lambda v: f"AQI of {v:.0f} is hazardous. Likely causes: industrial emissions, vehicular traffic congestion, construction dust, and crop burning."},
        {"condition": lambda v: v > 150, "severity": "high", "icon": "🏭",
         "title": "Very Poor Air Quality",
         "text": lambda v: f"AQI of {v:.0f} is very unhealthy. Contributing factors include vehicle exhaust, industrial activity, and poor wind dispersal."},
        {"condition": lambda v: v > 100, "severity": "moderate", "icon": "💨",
         "title": "Moderate Pollution",
         "text": lambda v: f"AQI of {v:.0f} is moderately polluted. Local traffic patterns and industrial zones likely contribute."},
    ],
    "soil_moisture": [
        {"condition": lambda v: v < 0.1, "severity": "critical", "icon": "🏜️",
         "title": "Severe Drought Conditions",
         "text": lambda v: f"Soil moisture at {v*100:.1f}% is critically low. Causes include prolonged dry spell, over-extraction of groundwater, and reduced rainfall."},
        {"condition": lambda v: v < 0.2, "severity": "high", "icon": "💧",
         "title": "Water Stress",
         "text": lambda v: f"Soil moisture at {v*100:.1f}% indicates water stress. Reduced rainfall, high evapotranspiration, or poor water management may be factors."},
        {"condition": lambda v: v < 0.3, "severity": "moderate", "icon": "🌊",
         "title": "Below-Average Moisture",
         "text": lambda v: f"Soil moisture at {v*100:.1f}% is below optimal. Seasonal drying or land-use changes could be contributing."},
    ],
}


def generate_explanation(temp_val, ndvi_val, poll_val, soil_val, lat, lon):
    """
    Generate human-readable explanations for environmental conditions at a point.

    Args:
        temp_val: Temperature value (°C) or None
        ndvi_val: NDVI value (0-1) or None
        poll_val: Pollution AQI value or None
        soil_val: Soil moisture value (0-1) or None
        lat: Latitude of the point
        lon: Longitude of the point

    Returns:
        dict with explanations, factors, and severity
    """
    explanations = []

    # 1. Check cross-parameter causation rules (most valuable)
    for rule_name, rule in CAUSATION_RULES.items():
        try:
            if rule["condition"](temp_val, ndvi_val, poll_val, soil_val):
                explanations.append({
                    "type": "cross_parameter",
                    "rule": rule_name,
                    "title": rule["title"],
                    "icon": rule["icon"],
                    "severity": rule["severity"],
                    "explanation": rule["explanation"](temp_val, ndvi_val, poll_val, soil_val),
                    "factors": rule["factors"](temp_val, ndvi_val, poll_val, soil_val),
                })
        except Exception as e:
            logger.warning(f"Rule {rule_name} failed: {e}")

    # 2. Add single-parameter explanations for context
    param_values = {
        "temperature": temp_val,
        "ndvi": ndvi_val,
        "pollution": poll_val,
        "soil_moisture": soil_val,
    }

    for param_name, value in param_values.items():
        if value is None:
            continue
        rules = SINGLE_PARAM_EXPLANATIONS.get(param_name, [])
        for rule in rules:
            if rule["condition"](value):
                explanations.append({
                    "type": "single_parameter",
                    "parameter": param_name,
                    "title": rule["title"],
                    "icon": rule["icon"],
                    "severity": rule["severity"],
                    "explanation": rule["text"](value),
                })
                break  # Only most severe per parameter

    # Sort: cross-parameter first, then by severity
    severity_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3}
    explanations.sort(key=lambda x: (
        0 if x["type"] == "cross_parameter" else 1,
        severity_order.get(x["severity"], 4),
    ))

    # Overall severity
    if any(e["severity"] == "critical" for e in explanations):
        overall = "critical"
    elif any(e["severity"] == "high" for e in explanations):
        overall = "high"
    elif any(e["severity"] == "moderate" for e in explanations):
        overall = "moderate"
    else:
        overall = "normal"

    result = {
        "lat": lat,
        "lon": lon,
        "overall_severity": overall,
        "explanation_count": len(explanations),
        "explanations": explanations,
        "values": {
            "temperature": round(temp_val, 2) if temp_val is not None else None,
            "ndvi": round(ndvi_val, 4) if ndvi_val is not None else None,
            "pollution": round(poll_val, 1) if poll_val is not None else None,
            "soil_moisture": round(soil_val, 4) if soil_val is not None else None,
        },
    }

    logger.info(f"Generated {len(explanations)} explanations at ({lat:.4f}, {lon:.4f}), "
                f"overall: {overall}")

    return result
