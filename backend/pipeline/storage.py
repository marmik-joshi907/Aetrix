"""
Data Storage Module.

Persistence layer using NumPy .npz files for raster arrays 
and JSON for metadata. Supports save/load of processed grids 
with spatial bounds and timestamps.

For production: replace with Zarr + PostGIS.
"""
import numpy as np
import json
import os
import logging

import config

logger = logging.getLogger(__name__)


def _get_dataset_path(city_name):
    """Get storage paths for a city's dataset."""
    safe_name = city_name.lower().replace(" ", "_")
    data_path = os.path.join(config.PROCESSED_DIR, f"{safe_name}_data.npz")
    meta_path = os.path.join(config.PROCESSED_DIR, f"{safe_name}_meta.json")
    return data_path, meta_path


def save_dataset(city_name, data_dict, metadata):
    """
    Save processed dataset to disk.
    
    Args:
        city_name: Name of the city
        data_dict: Dict of {parameter_name: numpy_array}
        metadata: Dict of metadata
    """
    data_path, meta_path = _get_dataset_path(city_name)
    
    # Save numpy arrays
    np.savez_compressed(data_path, **data_dict)
    logger.info(f"Saved data to {data_path}")
    
    # Save metadata as JSON
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata to {meta_path}")


def load_dataset(city_name):
    """
    Load processed dataset from disk.
    
    Returns:
        Dict with 'data' and 'metadata' keys, or None if not found.
    """
    data_path, meta_path = _get_dataset_path(city_name)
    
    if not os.path.exists(data_path) or not os.path.exists(meta_path):
        logger.warning(f"No cached dataset found for {city_name}")
        return None
    
    # Load numpy arrays
    npz = np.load(data_path)
    data_dict = {key: npz[key] for key in npz.files}
    
    # Load metadata
    with open(meta_path, 'r') as f:
        metadata = json.load(f)
    
    logger.info(f"Loaded dataset for {city_name}: {list(data_dict.keys())}")
    return {"data": data_dict, "metadata": metadata}


def dataset_exists(city_name):
    """Check if a processed dataset exists on disk."""
    data_path, meta_path = _get_dataset_path(city_name)
    return os.path.exists(data_path) and os.path.exists(meta_path)


def delete_dataset(city_name):
    """Remove a cached dataset."""
    data_path, meta_path = _get_dataset_path(city_name)
    for path in [data_path, meta_path]:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Deleted {path}")


def get_grid_as_geojson(data_2d, metadata, parameter_name, value_threshold=None):
    """
    Convert a 2D raster grid to GeoJSON features.
    
    Each grid cell becomes a point feature with its value.
    Optionally filter by a minimum value threshold.
    """
    bounds = metadata["bounds"]
    grid_size = metadata["grid_size"]
    
    lats = np.linspace(bounds["lat_min"], bounds["lat_max"], grid_size)
    lons = np.linspace(bounds["lon_min"], bounds["lon_max"], grid_size)
    
    features = []
    for r in range(grid_size):
        for c in range(grid_size):
            value = float(data_2d[r, c])
            
            if value_threshold is not None and value < value_threshold:
                continue
            
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [round(lons[c], 6), round(lats[r], 6)]
                },
                "properties": {
                    "value": round(value, 4),
                    "parameter": parameter_name,
                    "row": r,
                    "col": c,
                }
            })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }
