"""
New Feature API Routes.

Endpoints for the 5 new features:
- GET /api/explain - Explainable predictions
- GET /api/crowd-detection - Crowd density detection
- GET /api/timeline-warnings - Timeline comparison warnings
- GET /api/early-warnings - Early warning system
- GET /api/municipal-dashboard - Municipal officers dashboard
"""
from fastapi import APIRouter, Query, HTTPException

router = APIRouter(prefix="/api", tags=["features"])

# Pipeline reference (set by main.py on startup)
pipeline = None


@router.get("/explain")
def get_explanation(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    week: int = Query(-1, description="Week index"),
    city: str = Query(None, description="City name"),
):
    """Generate explainable predictions at a specific point."""
    import config
    from ml.explainer import generate_explanation

    if pipeline is None or not pipeline.is_loaded:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    if city is None:
        city = config.DEMO_CITY_NAME

    if city not in pipeline.data:
        raise HTTPException(status_code=404, detail=f"No data for city: {city}")

    # Get values for all 4 parameters at this point
    temp_val = pipeline.get_grid_value(city, "temperature", lat, lon, week)
    ndvi_val = pipeline.get_grid_value(city, "ndvi", lat, lon, week)
    poll_val = pipeline.get_grid_value(city, "pollution", lat, lon, week)
    soil_val = pipeline.get_grid_value(city, "soil_moisture", lat, lon, week)

    result = generate_explanation(temp_val, ndvi_val, poll_val, soil_val, lat, lon)
    result["city"] = city
    result["week"] = week

    return result


@router.get("/crowd-detection")
def get_crowd_detection(
    city: str = Query(None, description="City name"),
    week: int = Query(-1, description="Week index"),
):
    """Detect crowd gatherings using environmental proxy data."""
    import config
    from ml.crowd_detection import detect_crowds

    if pipeline is None or not pipeline.is_loaded:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    if city is None:
        city = config.DEMO_CITY_NAME

    data = pipeline.get_data(city)
    meta = pipeline.get_metadata(city)

    if data is None or meta is None:
        raise HTTPException(status_code=404, detail=f"No data for {city}")

    result = detect_crowds(data, meta, week_index=week, city=city)
    return result


@router.get("/timeline-warnings")
def get_timeline_warnings(
    city: str = Query(None, description="City name"),
    week: int = Query(-1, description="Week index"),
    lookback: int = Query(4, description="Weeks to look back for comparison"),
):
    """Detect worsening trends by comparing current vs historical data."""
    import config
    from ml.timeline_warnings import detect_timeline_warnings

    if pipeline is None or not pipeline.is_loaded:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    if city is None:
        city = config.DEMO_CITY_NAME

    data = pipeline.get_data(city)
    meta = pipeline.get_metadata(city)

    if data is None or meta is None:
        raise HTTPException(status_code=404, detail=f"No data for {city}")

    result = detect_timeline_warnings(data, meta, current_week=week, lookback_weeks=lookback)
    return result


@router.get("/early-warnings")
def get_early_warnings(
    city: str = Query(None, description="City name"),
    week: int = Query(-1, description="Week index"),
    forecast_days: int = Query(10, description="Days ahead to forecast"),
):
    """Generate area-based early warning alerts."""
    import config
    from ml.early_warnings import generate_early_warnings

    if pipeline is None or not pipeline.is_loaded:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    if city is None:
        city = config.DEMO_CITY_NAME

    data = pipeline.get_data(city)
    meta = pipeline.get_metadata(city)

    if data is None or meta is None:
        raise HTTPException(status_code=404, detail=f"No data for {city}")

    result = generate_early_warnings(data, meta, current_week=week, forecast_days=forecast_days)
    return result


@router.get("/municipal-dashboard")
def get_municipal_dashboard(
    city: str = Query(None, description="City name"),
    week: int = Query(-1, description="Week index"),
):
    """Generate municipal officers dashboard with top 3 urgent problems."""
    import config
    from ml.municipal_dashboard import generate_municipal_dashboard
    from ml.hotspots import detect_all_hotspots

    if pipeline is None or not pipeline.is_loaded:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    if city is None:
        city = config.DEMO_CITY_NAME

    data = pipeline.get_data(city)
    meta = pipeline.get_metadata(city)

    if data is None or meta is None:
        raise HTTPException(status_code=404, detail=f"No data for {city}")

    # Run hotspot detection for context
    try:
        hotspot_results = detect_all_hotspots(data, meta, week)
    except Exception:
        hotspot_results = None

    result = generate_municipal_dashboard(data, meta, hotspot_results, week_index=week)
    return result
