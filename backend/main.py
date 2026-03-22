"""
Satellite Environmental Intelligence Platform - Backend Server

FastAPI application entry point.
Initializes the data pipeline and mounts all API routes.
"""
import logging
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import config
from pipeline.processor import DataPipeline
from api import data_routes, ml_routes, action_routes, predict_routes, feature_routes, chat_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Global pipeline instance
pipeline = DataPipeline()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # === STARTUP ===
    logger.info("=" * 60)
    logger.info("🛰️  Satellite Environmental Intelligence Platform")
    logger.info("=" * 60)
    logger.info(f"Demo City: {config.DEMO_CITY_NAME} "
                f"({config.DEMO_CITY_LAT}, {config.DEMO_CITY_LON})")
    logger.info(f"Grid: {config.GRID_SIZE}x{config.GRID_SIZE} @ {config.GRID_RESOLUTION_KM}km")
    logger.info(f"Using sample data: {config.use_sample_data()}")
    
    import database
    logger.info("Testing PostgreSQL database connection...")
    database.test_connection()
    
    # Run pipeline for demo city
    logger.info("Initializing data pipeline...")
    pipeline.run_pipeline(config.DEMO_CITY_NAME)
    
    # Share pipeline with route modules
    data_routes.pipeline = pipeline
    ml_routes.pipeline = pipeline
    action_routes.pipeline = pipeline
    feature_routes.pipeline = pipeline
    
    # Initialize RAG chatbot engine
    logger.info("Initializing RAG chatbot engine...")
    try:
        from rag.rag_engine import init_engine
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAjq4GT4LrpeYv0-FxV5NB3EfSVaDiYHr8")
        rag = init_engine(GEMINI_API_KEY)
        rag.set_pipeline(pipeline)
        logger.info("✅ RAG chatbot engine ready")
    except Exception as e:
        logger.warning(f"⚠️ RAG engine init failed (chat will be unavailable): {e}")
    
    logger.info("✅ Pipeline initialized. Server ready!")
    logger.info(f"📊 API docs: http://localhost:{config.BACKEND_PORT}/docs")
    logger.info("=" * 60)
    
    yield
    
    # === SHUTDOWN ===
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Satellite Environmental Intelligence Platform",
    description=(
        "Converts raw satellite data into actionable environmental insights "
        "for smart city planning. Provides NDVI, temperature, pollution, and "
        "soil moisture analysis with ML-powered anomaly detection, trend "
        "prediction, and hotspot clustering."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount route modules
app.include_router(data_routes.router)
app.include_router(ml_routes.router)
app.include_router(action_routes.router)
app.include_router(predict_routes.router)
app.include_router(feature_routes.router)
app.include_router(chat_routes.router)


@app.get("/")
def root():
    """Health check and API info."""
    return {
        "name": "Satellite Environmental Intelligence Platform",
        "version": "1.0.0",
        "status": "running",
        "pipeline_loaded": pipeline.is_loaded,
        "demo_city": config.DEMO_CITY_NAME,
        "endpoints": {
            "docs": "/docs",
            "cities": "/api/cities",
            "layers": "/api/available-layers",
            "data": "/api/get-data?lat=23.0225&lon=72.5714&parameter=temperature",
            "grid": "/api/grid-data?parameter=ndvi",
            "hotspots": "/api/get-hotspots",
            "anomalies": "/api/get-anomalies",
            "trend": "/api/predict-trend?lat=23.0225&lon=72.5714&parameter=temperature",
            "action_plan": "/api/action-plan",
        },
    }


@app.get("/api/load-city")
def load_city(city: str):
    """Load/process data for a new city."""
    if city not in config.CITIES:
        return {"error": f"Unknown city: {city}", "available": list(config.CITIES.keys())}
    
    pipeline.run_pipeline(city)
    
    data_routes.pipeline = pipeline
    ml_routes.pipeline = pipeline
    action_routes.pipeline = pipeline
    feature_routes.pipeline = pipeline
    
    # Update RAG pipeline reference
    try:
        from rag.rag_engine import get_engine
        engine = get_engine()
        if engine:
            engine.set_pipeline(pipeline)
    except Exception:
        pass
    
    return {"status": "loaded", "city": city}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.BACKEND_HOST, port=config.BACKEND_PORT)
