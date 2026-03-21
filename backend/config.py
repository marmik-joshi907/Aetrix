"""
Configuration module for the Satellite Environmental Intelligence Platform.
Loads settings from environment variables with sensible defaults.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# === API Keys ===
GEE_SERVICE_ACCOUNT_KEY = os.getenv("GEE_SERVICE_ACCOUNT_KEY", "")
NASA_API_KEY = os.getenv("NASA_API_KEY", "")
SENTINEL_USER = os.getenv("SENTINEL_USER", "")
SENTINEL_PASS = os.getenv("SENTINEL_PASS", "")

# === Server ===
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

# === Demo City ===
DEMO_CITY_LAT = float(os.getenv("DEMO_CITY_LAT", "23.0225"))
DEMO_CITY_LON = float(os.getenv("DEMO_CITY_LON", "72.5714"))
DEMO_CITY_NAME = os.getenv("DEMO_CITY_NAME", "Ahmedabad")

# === Database ===
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/satintel_db")

# === Grid Configuration ===
GRID_SIZE = 50  # 50x50 grid cells
GRID_RESOLUTION_KM = 0.5  # ~500m per cell
SPATIAL_EXTENT_KM = GRID_SIZE * GRID_RESOLUTION_KM  # 25km extent

# === Available Cities ===
CITIES = {
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
}

# === Data Parameters ===
PARAMETERS = ["ndvi", "temperature", "pollution", "soil_moisture"]
TIME_STEPS = 52  # 52 weeks of data

# === Data Paths ===
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
CACHE_DIR = os.path.join(DATA_DIR, "cache")

# Create directories
for d in [DATA_DIR, RAW_DIR, PROCESSED_DIR, CACHE_DIR]:
    os.makedirs(d, exist_ok=True)

def use_sample_data():
    """Check if we should use sample data (no API keys configured)."""
    return not (GEE_SERVICE_ACCOUNT_KEY or NASA_API_KEY)
