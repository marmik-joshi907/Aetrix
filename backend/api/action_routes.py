"""
Action Plan API Routes.

Endpoints:
- GET /api/action-plan - Generate environmental action plan
"""
from fastapi import APIRouter, Query, HTTPException

router = APIRouter(prefix="/api", tags=["actions"])

# Pipeline reference
pipeline = None


@router.get("/action-plan")
def get_action_plan(
    city: str = Query(None, description="City name"),
    week: int = Query(-1, description="Week index"),
):
    """Generate environmental action plan for a city."""
    import config
    from ml.action_plan import generate_action_plan
    from ml.hotspots import detect_all_hotspots
    from ml.anomaly import detect_anomalies
    
    if pipeline is None or not pipeline.is_loaded:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    if city is None:
        city = config.DEMO_CITY_NAME
    
    data = pipeline.get_data(city)
    meta = pipeline.get_metadata(city)
    
    if data is None or meta is None:
        raise HTTPException(status_code=404, detail=f"No data for {city}")
    
    # Run hotspot detection
    hotspot_results = detect_all_hotspots(data, meta, week)
    
    # Generate action plan
    plan = generate_action_plan(
        data_dict=data,
        metadata=meta,
        hotspot_results=hotspot_results,
        week_index=week,
    )
    
    return plan
