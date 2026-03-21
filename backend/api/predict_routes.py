"""
FastAPI prediction routes for all 4 ML models.
"""
import os
import sys
import traceback

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

router = APIRouter(prefix="/api/predict", tags=["ML Predictions"])


# ── Request models ──

class TempRequest(BaseModel):
    years_ahead: int = 5


class SoilRequest(BaseModel):
    district: str               # e.g. "Ahmedabad"
    sm_level: float             # soil moisture level at 15cm
    sm_agg_pct: float           # aggregate soil moisture %
    sm_vol_pct: float           # volume soil moisture %
    day_of_year: int            # 1-365
    week: int                   # 1-52
    month: int                  # 1-12


class PollutionRequest(BaseModel):
    state: str                  # e.g. "Gujarat"
    latitude: float
    longitude: float
    CO: Optional[float] = None
    NH3: Optional[float] = None
    NO2: Optional[float] = None
    OZONE: Optional[float] = None
    PM10: Optional[float] = None
    PM25: Optional[float] = None   # maps to PM2.5 internally
    SO2: Optional[float] = None


class LanduseRequest(BaseModel):
    latitude: float
    longitude: float
    pm25: float
    no2: float


# ── Endpoints ──

@router.post("/temperature")
def predict_temperature_endpoint(req: TempRequest):
    """Predict next N years of temperature using LSTM model."""
    try:
        from ml.model_temp import predict_temperature
        result = predict_temperature(years_ahead=req.years_ahead)
        return {"status": "success", "predictions": result,
                "model": "LSTM", "unit": "°C"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/soil")
def predict_soil_endpoint(req: SoilRequest):
    """Predict drought risk and 7-day soil moisture forecast."""
    try:
        from ml.model_soil import predict_soil
        result = predict_soil(
            district=req.district,
            sm_level=req.sm_level,
            sm_agg_pct=req.sm_agg_pct,
            sm_vol_pct=req.sm_vol_pct,
            day_of_year=req.day_of_year,
            week=req.week,
            month=req.month,
        )
        return {"status": "success", "result": result, "model": "RandomForest+ARIMA"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pollution")
def predict_pollution_endpoint(req: PollutionRequest):
    """Predict AQI category from pollutant readings."""
    try:
        from ml.model_pollution import predict_pollution
        pollutants = {
            "CO": req.CO, "NH3": req.NH3, "NO2": req.NO2,
            "OZONE": req.OZONE, "PM10": req.PM10,
            "PM2.5": req.PM25, "SO2": req.SO2,
        }
        pollutants = {k: v for k, v in pollutants.items() if v is not None}
        result = predict_pollution(
            state=req.state,
            latitude=req.latitude,
            longitude=req.longitude,
            pollutants=pollutants,
        )
        return {"status": "success", "result": result, "model": "XGBoost"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/landuse")
def predict_landuse_endpoint(req: LanduseRequest):
    """Predict land-use change risk for a given location."""
    try:
        from ml.model_landuse import predict_landuse
        result = predict_landuse(
            latitude=req.latitude,
            longitude=req.longitude,
            pm25=req.pm25,
            no2=req.no2,
        )
        return {"status": "success", "result": result, "model": "KMeans"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hotspots")
def get_hotspots():
    """Return precomputed DBSCAN pollution hotspot clusters."""
    try:
        import pandas as pd
        hotspot_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "processed", "hotspots.csv"
        )
        df = pd.read_csv(hotspot_path)
        hotspots = df[df["hotspot_cluster"] != -1]  # -1 = noise points
        result = hotspots.to_dict(orient="records")
        return {"status": "success", "count": len(result), "hotspots": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def model_health():
    """Check which models are available on disk."""
    models_dir = os.path.join(os.path.dirname(__file__), "..", "models", "saved")
    expected = {
        "temp_mlp": "temp_mlp.pkl",
        "soil_rf": "soil_rf.pkl",
        "pollution_xgb": "pollution_xgb.pkl",
        "landuse_kmeans": "landuse_kmeans.pkl",
    }
    status = {}
    for name, filename in expected.items():
        status[name] = os.path.exists(os.path.join(models_dir, filename))
    return {"models": status, "all_ready": all(status.values())}
