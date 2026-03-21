"""
ML Analytics API Routes.

Endpoints for ML-powered analysis:
- GET /api/get-hotspots - DBSCAN hotspot clusters
- GET /api/get-anomalies - Isolation Forest anomalies
- GET /api/predict-trend - ARIMA forecast
"""
from fastapi import APIRouter, Query, HTTPException
import numpy as np

router = APIRouter(prefix="/api", tags=["ml"])

# Pipeline reference (set by main.py)
pipeline = None


@router.get("/get-hotspots")
def get_hotspots(
    parameter: str = Query(None, description="Specific parameter, or all if None"),
    week: int = Query(-1, description="Week index"),
    city: str = Query(None, description="City name"),
):
    """Detect spatial hotspots using DBSCAN clustering."""
    import config
    from ml.hotspots import detect_hotspots, detect_all_hotspots
    
    if pipeline is None or not pipeline.is_loaded:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    if city is None:
        city = config.DEMO_CITY_NAME
    
    data = pipeline.get_data(city)
    meta = pipeline.get_metadata(city)
    
    if data is None or meta is None:
        raise HTTPException(status_code=404, detail=f"No data for {city}")
    
    if parameter:
        # Single parameter
        param_data = data.get(parameter)
        if param_data is None:
            raise HTTPException(status_code=404, detail=f"No data for {parameter}")
        
        if param_data.ndim == 3:
            data_2d = param_data[week]
        else:
            data_2d = param_data
        
        result = detect_hotspots(data_2d, meta, parameter)
        return {"city": city, "week": week, "results": {parameter: result}}
    else:
        # All parameters
        results = detect_all_hotspots(data, meta, week)
        return {"city": city, "week": week, "results": results}


@router.get("/get-anomalies")
def get_anomalies(
    parameter: str = Query(None, description="Specific parameter"),
    week: int = Query(-1, description="Week index"),
    city: str = Query(None, description="City name"),
    contamination: float = Query(0.05, description="Expected anomaly fraction"),
):
    """Detect anomalies using Isolation Forest."""
    import config
    from ml.anomaly import detect_anomalies, detect_temporal_anomalies
    
    if pipeline is None or not pipeline.is_loaded:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    if city is None:
        city = config.DEMO_CITY_NAME
    
    data = pipeline.get_data(city)
    meta = pipeline.get_metadata(city)
    
    if data is None:
        raise HTTPException(status_code=404, detail=f"No data for {city}")
    
    results = {}
    params_to_analyze = [parameter] if parameter else list(data.keys())
    
    for param_name in params_to_analyze:
        param_data = data.get(param_name)
        if param_data is None:
            continue
        
        # Spatial anomalies for the given week
        if param_data.ndim == 3:
            data_2d = param_data[week]
        else:
            data_2d = param_data
        
        spatial = detect_anomalies(data_2d, contamination, param_name)
        
        # Temporal anomalies
        temporal = None
        if param_data.ndim == 3:
            temporal = detect_temporal_anomalies(param_data, contamination, param_name)
        
        # Convert anomaly_mask to serializable format
        spatial_result = {
            "count": spatial["count"],
            "parameter": spatial["parameter"],
            "anomaly_points": spatial["anomaly_points"][:30],  # Top 30
        }
        
        results[param_name] = {
            "spatial": spatial_result,
            "temporal": temporal,
        }
    
    return {"city": city, "week": week, "results": results}


@router.get("/predict-trend")
def predict_trend(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    parameter: str = Query("temperature", description="Parameter name"),
    forecast_weeks: int = Query(4, description="Weeks to forecast"),
    city: str = Query(None, description="City name"),
):
    """Predict trend at a specific location using ARIMA."""
    import config
    from ml.trends import predict_trend_arima
    
    if pipeline is None or not pipeline.is_loaded:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    if city is None:
        city = config.DEMO_CITY_NAME
    
    timestamps, values = pipeline.get_time_series_at_point(city, parameter, lat, lon)
    
    if values is None:
        raise HTTPException(status_code=404, detail=f"No time series for {parameter}")
    
    result = predict_trend_arima(
        np.array(values), 
        forecast_weeks=forecast_weeks,
        parameter_name=parameter
    )
    
    result["timestamps"] = timestamps
    result["lat"] = lat
    result["lon"] = lon
    result["city"] = city
    
    meta = pipeline.get_metadata(city)
    result["unit"] = meta.get("parameters", {}).get(parameter, {}).get("unit", "")
    
    return result
