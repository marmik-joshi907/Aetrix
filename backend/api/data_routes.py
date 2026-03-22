"""
Data API Routes.

Endpoints for fetching processed satellite data:
- GET /api/get-data - Query data at a specific location
- GET /api/available-layers - List available data layers  
- GET /api/grid-data - Get full grid data for map rendering
- GET /api/time-series - Get time series at a point
- GET /api/cities - List available cities
"""
from fastapi import APIRouter, Query, HTTPException
import numpy as np

router = APIRouter(prefix="/api", tags=["data"])

# Pipeline reference (set by main.py on startup)
pipeline = None


@router.get("/cities")
def get_cities():
    """Get list of available cities."""
    import config
    cities = []
    for name, coords in config.CITIES.items():
        cities.append({
            "name": name,
            "lat": coords["lat"],
            "lon": coords["lon"],
            "loaded": pipeline is not None and name in pipeline.data,
        })
    return {"cities": cities}


@router.get("/available-layers")
def get_available_layers():
    """Get list of available data layers/parameters."""
    import config
    if pipeline is None or not pipeline.is_loaded:
        return {"layers": [], "status": "not_loaded"}
    
    city = config.DEMO_CITY_NAME
    meta = pipeline.get_metadata(city)
    
    if meta is None:
        return {"layers": [], "status": "no_metadata"}
    
    layers = []
    for param_name, param_info in meta.get("parameters", {}).items():
        data = pipeline.data.get(city, {}).get(param_name)
        layers.append({
            "name": param_name,
            "description": param_info.get("description", ""),
            "unit": param_info.get("unit", ""),
            "range": param_info.get("range", []),
            "available": data is not None,
            "shape": list(data.shape) if data is not None else None,
        })
    
    return {"layers": layers, "status": "loaded", "city": city}


@router.get("/get-data")
def get_data(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    parameter: str = Query("temperature", description="Parameter name"),
    week: int = Query(-1, description="Week index (-1 = latest)"),
    city: str = Query(None, description="City name"),
):
    """Get data value at a specific lat/lon for a parameter."""
    import config
    
    if pipeline is None or not pipeline.is_loaded:
        raise HTTPException(status_code=503, detail="Data pipeline not initialized")
    
    if city is None:
        city = config.DEMO_CITY_NAME
    
    if city not in pipeline.data:
        raise HTTPException(status_code=404, detail=f"No data for city: {city}")
    
    value = pipeline.get_grid_value(city, parameter, lat, lon, week)
    
    if value is None:
        raise HTTPException(status_code=404, detail=f"No data for parameter: {parameter}")
    
    meta = pipeline.get_metadata(city)
    timestamps = meta.get("timestamps", [])
    timestamp = timestamps[week] if timestamps and abs(week) <= len(timestamps) else "N/A"
    
    return {
        "lat": lat,
        "lon": lon,
        "parameter": parameter,
        "value": round(value, 4),
        "unit": meta.get("parameters", {}).get(parameter, {}).get("unit", ""),
        "timestamp": timestamp,
        "city": city,
    }


@router.get("/grid-data")
def get_grid_data(
    parameter: str = Query("temperature", description="Parameter name"),
    week: int = Query(-1, description="Week index (-1 = latest)"),
    city: str = Query(None, description="City name"),
    downsample: int = Query(1, description="Downsample factor (1=full, 2=half, etc.)"),
):
    """Get full grid data for map rendering."""
    import config
    
    if pipeline is None or not pipeline.is_loaded:
        raise HTTPException(status_code=503, detail="Data pipeline not initialized")
    
    if city is None:
        city = config.DEMO_CITY_NAME
    
    data = pipeline.data.get(city, {}).get(parameter)
    meta = pipeline.get_metadata(city)
    
    if data is None or meta is None:
        raise HTTPException(status_code=404, detail=f"No data for {parameter} in {city}")
    
    # Get 2D slice
    if data.ndim == 3:
        grid = data[week]
    else:
        grid = data
    
    bounds = meta["bounds"]
    grid_size = meta["grid_size"]
    
    # Downsample if requested
    if downsample > 1:
        grid = grid[::downsample, ::downsample]
    
    rows, cols = grid.shape
    lats = np.linspace(bounds["lat_min"], bounds["lat_max"], rows)
    lons = np.linspace(bounds["lon_min"], bounds["lon_max"], cols)
    
    # Convert to list of points for Leaflet heatmap
    points = []
    for r in range(rows):
        for c in range(cols):
            val = float(grid[r, c])
            if not np.isnan(val):
                points.append([round(float(lats[r]), 6), round(float(lons[c]), 6), round(val, 4)])
    
    timestamps = meta.get("timestamps", [])
    timestamp = timestamps[week] if timestamps and abs(week) <= len(timestamps) else "N/A"
    
    return {
        "parameter": parameter,
        "city": city,
        "timestamp": timestamp,
        "bounds": bounds,
        "grid_size": [rows, cols],
        "points": points,
        "stats": {
            "min": round(float(np.nanmin(grid)), 4),
            "max": round(float(np.nanmax(grid)), 4),
            "mean": round(float(np.nanmean(grid)), 4),
        },
        "unit": meta.get("parameters", {}).get(parameter, {}).get("unit", ""),
    }


@router.get("/time-series")
def get_time_series(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    parameter: str = Query("temperature", description="Parameter name"),
    city: str = Query(None, description="City name"),
):
    """Get time series at a specific point."""
    import config
    
    if pipeline is None or not pipeline.is_loaded:
        raise HTTPException(status_code=503, detail="Data pipeline not initialized")
    
    if city is None:
        city = config.DEMO_CITY_NAME
    
    timestamps, values = pipeline.get_time_series_at_point(city, parameter, lat, lon)
    
    if timestamps is None:
        raise HTTPException(status_code=404, detail=f"No time series for {parameter}")
    
    meta = pipeline.get_metadata(city)
    
    return {
        "lat": lat,
        "lon": lon,
        "parameter": parameter,
        "city": city,
        "timestamps": timestamps,
        "values": [round(v, 4) for v in values],
        "unit": meta.get("parameters", {}).get(parameter, {}).get("unit", ""),
    }


@router.get("/week-count")
def get_week_count(city: str = Query(None)):
    """Get total number of weeks of data available."""
    import config
    
    if city is None:
        city = config.DEMO_CITY_NAME
    
    meta = pipeline.get_metadata(city) if pipeline else None
    timestamps = meta.get("timestamps", []) if meta else []
    
    return {"weeks": len(timestamps), "city": city}
