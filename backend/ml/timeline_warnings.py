"""
Timeline Comparison Warnings Module.

Compares current week values against previous weeks to detect
deteriorating conditions. Generates warnings when parameters are
worsening beyond acceptable thresholds, with projections of what
happens if the trend is neglected.
"""
import numpy as np
import logging

logger = logging.getLogger(__name__)


# Deterioration thresholds per parameter (calibrated for real data)
THRESHOLDS = {
    "temperature": {
        "worsening_direction": "increasing",  # higher = worse
        "min_change_pct": 1.0,  # % change to trigger warning
        "unit": "°C",
        "format": lambda v: f"{v:.1f}°C",
    },
    "pollution": {
        "worsening_direction": "increasing",
        "min_change_pct": 2.0,
        "unit": "AQI",
        "format": lambda v: f"AQI {v:.0f}",
    },
    "ndvi": {
        "worsening_direction": "decreasing",  # lower = worse
        "min_change_pct": 1.0,
        "unit": "index",
        "format": lambda v: f"{v:.3f}",
    },
    "soil_moisture": {
        "worsening_direction": "decreasing",
        "min_change_pct": 1.5,
        "unit": "m³/m³",
        "format": lambda v: f"{v*100:.1f}%",
    },
}

# Neglect projections
NEGLECT_PROJECTIONS = {
    "temperature": {
        "moderate": "If neglected, heat stress will intensify. Expect 2-4°C further increase within 3 weeks, endangering outdoor workers and elderly populations.",
        "severe": "CRITICAL: Without intervention, temperatures could reach dangerous levels (>48°C). Risk of heat-related mortality increases 3x. Immediate cooling infrastructure needed.",
    },
    "pollution": {
        "moderate": "Air quality will continue to degrade. Sensitive groups (children, elderly, asthmatics) will face increasing health risks within 1-2 weeks.",
        "severe": "URGENT: Pollution trajectory suggests hazardous levels within days. Hospital admissions for respiratory issues expected to spike 40-60%.",
    },
    "ndvi": {
        "moderate": "Vegetation is declining steadily. If unchecked, expect 15-20% further canopy loss, increasing heat island effect and reducing air filtration.",
        "severe": "CRITICAL: Rapid vegetation loss indicates possible irreversible damage. Land degradation will accelerate soil erosion and worsen flooding risk.",
    },
    "soil_moisture": {
        "moderate": "Soil is drying progressively. Agricultural yields in affected areas will decline 10-30% without irrigation intervention within 2 weeks.",
        "severe": "DROUGHT ALERT: Soil moisture is trending toward critical levels. Crop failure risk is imminent. Emergency water supply and drought-resistant planning needed.",
    },
}


def detect_timeline_warnings(data_dict, metadata, current_week=-1, lookback_weeks=4):
    """
    Compare current week against previous weeks to detect worsening trends.

    Args:
        data_dict: {parameter: 3D numpy array}
        metadata: dataset metadata
        current_week: current week index
        lookback_weeks: how many weeks back to compare

    Returns:
        dict with warnings, trend comparisons, and neglect projections
    """
    city = metadata.get("city", "Unknown")
    timestamps = metadata.get("timestamps", [])
    warnings = []

    for param_name, param_data in data_dict.items():
        if param_data is None or param_data.ndim != 3:
            continue

        num_weeks = param_data.shape[0]
        if num_weeks < lookback_weeks + 1:
            continue

        threshold = THRESHOLDS.get(param_name)
        if threshold is None:
            continue

        # Get current and historical means
        current_grid = param_data[current_week]
        current_mean = float(np.nanmean(current_grid))
        current_max = float(np.nanmax(current_grid))

        # Compare with previous weeks
        week_means = []
        for w in range(lookback_weeks):
            idx = current_week - (w + 1)
            if idx < -num_weeks:
                break
            past_grid = param_data[idx]
            week_means.append(float(np.nanmean(past_grid)))

        if not week_means:
            continue

        past_mean = np.mean(week_means)

        # Calculate change
        if past_mean == 0:
            change_pct = 0
        else:
            change_pct = ((current_mean - past_mean) / abs(past_mean)) * 100

        # Determine if this constitutes worsening
        is_worsening = False
        if threshold["worsening_direction"] == "increasing" and change_pct > threshold["min_change_pct"]:
            is_worsening = True
        elif threshold["worsening_direction"] == "decreasing" and change_pct < -threshold["min_change_pct"]:
            is_worsening = True

        if not is_worsening:
            continue

        abs_change = abs(change_pct)

        # Determine severity
        if abs_change > threshold["min_change_pct"] * 3:
            severity = "critical"
            icon = "🔴"
            projection_key = "severe"
        elif abs_change > threshold["min_change_pct"] * 1.5:
            severity = "high"
            icon = "🟠"
            projection_key = "severe"
        else:
            severity = "moderate"
            icon = "🟡"
            projection_key = "moderate"

        # Get neglect projection
        projections = NEGLECT_PROJECTIONS.get(param_name, {})
        neglect_text = projections.get(projection_key, "Conditions may worsen if not addressed.")

        # Build weekly trend line
        trend_line = []
        for w in range(min(lookback_weeks, len(week_means))):
            idx = current_week - (lookback_weeks - w)
            ts = timestamps[idx] if timestamps and abs(idx) <= len(timestamps) else f"W-{lookback_weeks - w}"
            trend_line.append({
                "week": ts,
                "value": round(week_means[-(w + 1)], 4) if w < len(week_means) else None,
            })

        current_ts = timestamps[current_week] if timestamps and abs(current_week) <= len(timestamps) else "Current"
        trend_line.append({
            "week": current_ts,
            "value": round(current_mean, 4),
        })

        warnings.append({
            "parameter": param_name,
            "severity": severity,
            "icon": icon,
            "title": f"{param_name.replace('_', ' ').title()} is {'Rising' if threshold['worsening_direction'] == 'increasing' else 'Declining'}",
            "current_value": threshold["format"](current_mean),
            "previous_value": threshold["format"](past_mean),
            "change_percent": round(abs_change, 1),
            "direction": threshold["worsening_direction"],
            "weeks_compared": lookback_weeks,
            "trend_line": trend_line,
            "neglect_projection": neglect_text,
            "unit": threshold["unit"],
        })

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "moderate": 2}
    warnings.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return {
        "city": city,
        "current_week": current_week,
        "lookback_weeks": lookback_weeks,
        "warning_count": len(warnings),
        "warnings": warnings,
    }
