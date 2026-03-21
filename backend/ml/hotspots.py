"""
Hotspot Detection Module.

Uses DBSCAN clustering to identify spatial hotspots:
- Urban Heat Islands (high temperature clusters)
- Pollution Clusters (AQI hotspots)
- Vegetation Loss Zones (low NDVI clusters)
- Drought Zones (low soil moisture clusters)

Returns cluster centroids, sizes, and severity levels.
"""
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


def detect_hotspots(data_2d, metadata, parameter_name, 
                     threshold_percentile=85, eps=3.0, min_samples=5):
    """
    Detect spatial hotspots using DBSCAN clustering.
    
    Args:
        data_2d: 2D numpy array (single timestep)
        metadata: Dataset metadata with bounds
        parameter_name: 'temperature', 'pollution', 'ndvi', 'soil_moisture'
        threshold_percentile: Percentile threshold to consider as extreme
        eps: DBSCAN neighborhood radius (in grid cells)
        min_samples: Minimum points to form a cluster
    
    Returns:
        dict with clusters, centroids, and severity info
    """
    rows, cols = data_2d.shape
    bounds = metadata["bounds"]
    
    # Determine if we're looking for high or low values
    # Temperature/Pollution: high values are hotspots
    # NDVI/Moisture: low values are hotspots (loss zones)
    if parameter_name in ["ndvi", "soil_moisture"]:
        threshold = np.nanpercentile(data_2d, 100 - threshold_percentile)
        extreme_mask = data_2d <= threshold
        severity_multiplier = -1  # Lower = worse
    else:
        threshold = np.nanpercentile(data_2d, threshold_percentile)
        extreme_mask = data_2d >= threshold
        severity_multiplier = 1  # Higher = worse
    
    # Get coordinates of extreme points
    extreme_coords = np.argwhere(extreme_mask)
    
    if len(extreme_coords) < min_samples:
        logger.info(f"Not enough extreme points for clustering in {parameter_name}")
        return _empty_hotspot_result(parameter_name)
    
    # Run DBSCAN on spatial coordinates
    clustering = DBSCAN(eps=eps, min_samples=min_samples)
    labels = clustering.fit_predict(extreme_coords)
    
    # Extract clusters (ignore noise label -1)
    unique_labels = set(labels)
    unique_labels.discard(-1)
    
    clusters = []
    lats = np.linspace(bounds["lat_min"], bounds["lat_max"], rows)
    lons = np.linspace(bounds["lon_min"], bounds["lon_max"], cols)
    
    for label in sorted(unique_labels):
        cluster_mask = labels == label
        cluster_points = extreme_coords[cluster_mask]
        
        # Centroid
        centroid_row = int(np.mean(cluster_points[:, 0]))
        centroid_col = int(np.mean(cluster_points[:, 1]))
        
        # Values in cluster
        cluster_values = [float(data_2d[r, c]) for r, c in cluster_points]
        mean_value = np.mean(cluster_values)
        max_value = np.max(cluster_values) if severity_multiplier > 0 else np.min(cluster_values)
        
        # Severity score (0-1)
        data_range = float(np.nanmax(data_2d) - np.nanmin(data_2d))
        if data_range > 0:
            if severity_multiplier > 0:
                severity = (mean_value - np.nanmean(data_2d)) / data_range
            else:
                severity = (np.nanmean(data_2d) - mean_value) / data_range
        else:
            severity = 0
        severity = min(max(severity, 0), 1)
        
        # Classify severity level
        if severity > 0.6:
            level = "critical"
        elif severity > 0.4:
            level = "high"
        elif severity > 0.2:
            level = "moderate"
        else:
            level = "low"
        
        clusters.append({
            "id": int(label),
            "centroid_lat": round(float(lats[centroid_row]), 6),
            "centroid_lon": round(float(lons[centroid_col]), 6),
            "centroid_row": centroid_row,
            "centroid_col": centroid_col,
            "size": int(len(cluster_points)),
            "mean_value": round(float(mean_value), 4),
            "max_value": round(float(max_value), 4),
            "severity": round(float(severity), 4),
            "level": level,
            "points": [{"row": int(r), "col": int(c)} for r, c in cluster_points[:50]],  # limit points
        })
    
    # Sort by severity
    clusters.sort(key=lambda x: x["severity"], reverse=True)
    
    logger.info(f"Detected {len(clusters)} hotspot clusters in {parameter_name}")
    
    return {
        "parameter": parameter_name,
        "threshold": round(float(threshold), 4),
        "num_clusters": len(clusters),
        "total_hotspot_cells": int(extreme_mask.sum()),
        "clusters": clusters,
        "hotspot_type": _get_hotspot_type(parameter_name),
    }


def detect_all_hotspots(data_dict, metadata, week_index=-1):
    """
    Run hotspot detection on all parameters for a given week.
    
    Returns dict of parameter_name -> hotspot results.
    """
    results = {}
    
    for param_name, param_data in data_dict.items():
        if param_data is None:
            continue
        
        if param_data.ndim == 3:
            data_2d = param_data[week_index]
        else:
            data_2d = param_data
        
        results[param_name] = detect_hotspots(
            data_2d, metadata, param_name
        )
    
    return results


def _get_hotspot_type(parameter_name):
    """Get human-readable hotspot type name."""
    types = {
        "temperature": "Urban Heat Island",
        "pollution": "Pollution Cluster",
        "ndvi": "Vegetation Loss Zone",
        "soil_moisture": "Drought Zone",
    }
    return types.get(parameter_name, "Environmental Hotspot")


def _empty_hotspot_result(parameter_name):
    return {
        "parameter": parameter_name,
        "threshold": 0,
        "num_clusters": 0,
        "total_hotspot_cells": 0,
        "clusters": [],
        "hotspot_type": _get_hotspot_type(parameter_name),
    }
