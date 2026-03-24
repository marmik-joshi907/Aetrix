"""
Action Plan Generator.

Converts environmental insights into actionable recommendations 
for city planners and municipal corporations.

Uses rule-based logic + ML severity scoring to generate:
- Urban greening suggestions for heat islands
- Vegetation recovery plans for NDVI decline
- Traffic/industrial control for pollution hotspots
- Irrigation advisories for soil moisture depletion

Outputs structured JSON reports.
"""
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# === Rule Definitions ===
ACTION_RULES = {
    "temperature": [
        {
            "condition": lambda val: val > 45,
            "severity": "critical",
            "category": "Urban Heat Mitigation",
            "icon": "🔴",
            "actions": [
                "Deploy emergency cooling centers in affected zones",
                "Issue heat advisory for outdoor workers",
                "Activate water misting systems in public areas",
                "Mandate cool-roof installation for new construction",
            ],
        },
        {
            "condition": lambda val: val > 40,
            "severity": "high",
            "category": "Urban Greening",
            "icon": "🟠",
            "actions": [
                "Plant heat-resistant tree species (Neem, Peepal, Banyan)",
                "Install green roofs on government buildings",
                "Create shaded pedestrian corridors",
                "Deploy reflective road surface coatings",
            ],
        },
        {
            "condition": lambda val: val > 35,
            "severity": "moderate",
            "category": "Preventive Measures",
            "icon": "🟡",
            "actions": [
                "Increase urban tree canopy coverage",
                "Plan water features and fountains in public spaces",
                "Promote cool materials in building codes",
            ],
        },
    ],
    "pollution": [
        {
            "condition": lambda val: val > 250,
            "severity": "critical",
            "category": "Emergency Pollution Control",
            "icon": "🔴",
            "actions": [
                "Implement odd-even traffic restrictions immediately",
                "Halt construction activities in affected zones",
                "Issue health advisory: recommend N95 masks",
                "Shutdown non-essential industrial operations",
                "Deploy air purification units in schools/hospitals",
            ],
        },
        {
            "condition": lambda val: val > 150,
            "severity": "high",
            "category": "Traffic & Industrial Control",
            "icon": "🟠",
            "actions": [
                "Increase public transit frequency in affected areas",
                "Enforce stricter emission checks for commercial vehicles",
                "Inspect industrial emission compliance",
                "Deploy mobile air quality monitoring stations",
            ],
        },
        {
            "condition": lambda val: val > 100,
            "severity": "moderate",
            "category": "Air Quality Improvement",
            "icon": "🟡",
            "actions": [
                "Plant pollution-absorbing trees along major roads",
                "Promote electric vehicle adoption with charging stations",
                "Increase dust suppression on unpaved roads",
            ],
        },
    ],
    "ndvi": [
        {
            "condition": lambda val: val < 0.15,
            "severity": "critical",
            "category": "Emergency Vegetation Recovery",
            "icon": "🔴",
            "actions": [
                "Launch immediate reforestation program",
                "Investigate causes of vegetation loss (deforestation, fire, drought)",
                "Implement soil stabilization measures",
                "Create protected green buffer zones",
            ],
        },
        {
            "condition": lambda val: val < 0.25,
            "severity": "high",
            "category": "Green Cover Restoration",
            "icon": "🟠",
            "actions": [
                "Establish community-managed nurseries",
                "Plant native drought-resistant species",
                "Create urban food forests in underutilized spaces",
                "Enforce green zone regulations in development plans",
            ],
        },
        {
            "condition": lambda val: val < 0.35,
            "severity": "moderate",
            "category": "Vegetation Monitoring",
            "icon": "🟡",
            "actions": [
                "Increase monitoring frequency in degraded areas",
                "Plan seasonal plantation drives",
                "Promote rooftop gardens in residential areas",
            ],
        },
    ],
    "soil_moisture": [
        {
            "condition": lambda val: val < 0.1,
            "severity": "critical",
            "category": "Drought Emergency Response",
            "icon": "🔴",
            "actions": [
                "Activate emergency water supply for agriculture",
                "Implement strict water rationing for non-essential use",
                "Deploy rainwater harvesting systems",
                "Provide drought-relief to affected farmers",
            ],
        },
        {
            "condition": lambda val: val < 0.2,
            "severity": "high",
            "category": "Irrigation Advisory",
            "icon": "🟠",
            "actions": [
                "Switch to drip irrigation in agricultural zones",
                "Promote mulching to reduce evaporation",
                "Construct farm ponds for water storage",
                "Plant drought-resistant crop varieties",
            ],
        },
        {
            "condition": lambda val: val < 0.3,
            "severity": "moderate",
            "category": "Water Conservation",
            "icon": "🟡",
            "actions": [
                "Monitor groundwater levels weekly",
                "Promote efficient irrigation scheduling",
                "Create awareness on water conservation practices",
            ],
        },
    ],
}


def generate_action_plan(data_dict, metadata, hotspot_results=None, anomaly_results=None, week_index=-1):
    """
    Generate a comprehensive action plan from environmental data.
    
    Args:
        data_dict: {parameter: 3D array}
        metadata: dataset metadata
        hotspot_results: output from hotspot detection
        anomaly_results: output from anomaly detection
        week_index: which week to analyze
    
    Returns:
        Structured action plan dict
    """
    import config

    city = metadata.get("city", "Unknown City")
    timestamp = metadata.get("timestamps", ["N/A"])[week_index] if metadata.get("timestamps") else "N/A"
    total_area_km2 = (config.GRID_SIZE * config.GRID_RESOLUTION_KM) ** 2  # e.g. 625 km²
    total_cells = config.GRID_SIZE * config.GRID_SIZE
    
    recommendations = []
    summary_stats = {}
    
    for param_name, param_data in data_dict.items():
        if param_data is None:
            continue
        
        # Get current week's data
        if param_data.ndim == 3:
            current = param_data[week_index]
        else:
            current = param_data
        
        mean_val = float(np.nanmean(current))
        max_val = float(np.nanmax(current))
        min_val = float(np.nanmin(current))
        std_val = float(np.nanstd(current))
        p25 = float(np.nanpercentile(current, 25))
        p50 = float(np.nanpercentile(current, 50))
        p75 = float(np.nanpercentile(current, 75))
        p95 = float(np.nanpercentile(current, 95))

        # Week-over-week (WoW) delta
        wow_delta = None
        wow_direction = "stable"
        if param_data.ndim == 3 and abs(week_index) < param_data.shape[0]:
            prev_week = week_index - 1 if week_index != 0 else 0
            if prev_week != week_index:
                prev_mean = float(np.nanmean(param_data[prev_week]))
                wow_delta = round(mean_val - prev_mean, 3)
                if param_name in ("temperature", "pollution"):
                    wow_direction = "worsening" if wow_delta > 0 else ("improving" if wow_delta < 0 else "stable")
                else:
                    wow_direction = "worsening" if wow_delta < 0 else ("improving" if wow_delta > 0 else "stable")
        
        unit = metadata.get("parameters", {}).get(param_name, {}).get("unit", "")
        summary_stats[param_name] = {
            "mean": round(mean_val, 2),
            "max": round(max_val, 2),
            "min": round(min_val, 2),
            "std_dev": round(std_val, 3),
            "p25": round(p25, 2),
            "p50_median": round(p50, 2),
            "p75": round(p75, 2),
            "p95": round(p95, 2),
            "wow_delta": wow_delta,
            "wow_direction": wow_direction,
            "unit": unit,
        }
        
        # Apply rules
        rules = ACTION_RULES.get(param_name, [])
        for rule in rules:
            # Check if mean or max triggers the rule
            if rule["condition"](mean_val) or rule["condition"](max_val):
                # Count affected cells
                affected = sum(1 for r in range(current.shape[0]) 
                             for c in range(current.shape[1])
                             if rule["condition"](current[r, c]))
                affected_percent = affected / total_cells * 100
                affected_km2 = round(affected / total_cells * total_area_km2, 1)

                # Severity distribution across entire grid
                sev_dist = _compute_severity_distribution(current, param_name)
                
                recommendation = {
                    "parameter": param_name,
                    "severity": rule["severity"],
                    "category": rule["category"],
                    "icon": rule["icon"],
                    "trigger_value": round(mean_val, 2),
                    "peak_value": round(max_val, 2) if param_name in ("temperature", "pollution") else round(min_val, 2),
                    "std_dev": round(std_val, 3),
                    "p95": round(p95, 2),
                    "affected_area_percent": round(affected_percent, 1),
                    "affected_area_km2": affected_km2,
                    "wow_delta": wow_delta,
                    "wow_direction": wow_direction,
                    "severity_distribution": sev_dist,
                    "actions": rule["actions"],
                }
                
                # Add hotspot info if available
                if hotspot_results and param_name in hotspot_results:
                    hs = hotspot_results[param_name]
                    recommendation["hotspot_count"] = hs.get("num_clusters", 0)
                    recommendation["hotspot_type"] = hs.get("hotspot_type", "")
                    # Average hotspot severity
                    clusters = hs.get("clusters", [])
                    if clusters:
                        recommendation["hotspot_avg_severity"] = round(
                            sum(c.get("severity", 0) for c in clusters) / len(clusters), 3
                        )
                
                recommendations.append(recommendation)
                break  # Only apply most severe matching rule per parameter
    
    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3}
    recommendations.sort(key=lambda x: severity_order.get(x["severity"], 4))
    
    # Generate overall risk assessment
    if any(r["severity"] == "critical" for r in recommendations):
        overall_risk = "CRITICAL"
        risk_color = "#ef4444"
    elif any(r["severity"] == "high" for r in recommendations):
        overall_risk = "HIGH"
        risk_color = "#f97316"
    elif any(r["severity"] == "moderate" for r in recommendations):
        overall_risk = "MODERATE"
        risk_color = "#eab308"
    else:
        overall_risk = "LOW"
        risk_color = "#22c55e"
    
    action_plan = {
        "title": f"Environmental Action Plan: {city}",
        "generated_at": datetime.now().isoformat(),
        "analysis_date": timestamp,
        "city": city,
        "overall_risk": overall_risk,
        "risk_color": risk_color,
        "summary_stats": summary_stats,
        "recommendations": recommendations,
        "total_recommendations": len(recommendations),
        "total_area_km2": total_area_km2,
        "report_footer": f"Generated by Satellite Environmental Intelligence Platform | "
                        f"Analysis based on {len(data_dict)} environmental parameters",
    }
    
    logger.info(f"Generated action plan for {city}: {overall_risk} risk, "
                f"{len(recommendations)} recommendations")
    
    return action_plan


def _compute_severity_distribution(grid_2d, param_name):
    """Compute cell counts in critical/high/moderate/normal bands."""
    flat = grid_2d.flatten()
    flat = flat[~np.isnan(flat)]
    total = len(flat)
    if total == 0:
        return {"critical": 0, "high": 0, "moderate": 0, "normal": 0}

    if param_name == "temperature":
        return {
            "critical": int(np.sum(flat > 45)),
            "high": int(np.sum((flat > 40) & (flat <= 45))),
            "moderate": int(np.sum((flat > 35) & (flat <= 40))),
            "normal": int(np.sum(flat <= 35)),
        }
    elif param_name == "pollution":
        return {
            "critical": int(np.sum(flat > 250)),
            "high": int(np.sum((flat > 150) & (flat <= 250))),
            "moderate": int(np.sum((flat > 100) & (flat <= 150))),
            "normal": int(np.sum(flat <= 100)),
        }
    elif param_name == "ndvi":
        return {
            "critical": int(np.sum(flat < 0.15)),
            "high": int(np.sum((flat >= 0.15) & (flat < 0.25))),
            "moderate": int(np.sum((flat >= 0.25) & (flat < 0.35))),
            "normal": int(np.sum(flat >= 0.35)),
        }
    elif param_name == "soil_moisture":
        return {
            "critical": int(np.sum(flat < 0.1)),
            "high": int(np.sum((flat >= 0.1) & (flat < 0.2))),
            "moderate": int(np.sum((flat >= 0.2) & (flat < 0.3))),
            "normal": int(np.sum(flat >= 0.3)),
        }
    return {"critical": 0, "high": 0, "moderate": 0, "normal": 0}
