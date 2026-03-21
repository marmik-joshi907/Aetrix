"""
ETL Pipeline Orchestrator.

Manages the full Extract → Transform → Load lifecycle:
- Extract: Fetch from all data sources (or generate sample data)
- Transform: Harmonize (CRS, resample, align, clean)
- Load: Persist to storage
"""
import numpy as np
import logging
import time
from datetime import datetime

from ingestion.sample_data import generate_time_series, generate_metadata, get_lat_lon_arrays
from pipeline.harmonizer import harmonize_dataset
from pipeline.storage import save_dataset, load_dataset, dataset_exists
import config

logger = logging.getLogger(__name__)


class DataPipeline:
    """Orchestrates the ETL pipeline for satellite data processing."""
    
    def __init__(self):
        self.data = {}      # {city_name: {parameter: np.array}}
        self.metadata = {}  # {city_name: metadata_dict}
        self.is_loaded = False
    
    def run_pipeline(self, city_name=None, force_refresh=False):
        """
        Run the full ETL pipeline for a city.
        
        Args:
            city_name: City to process (default: demo city from config)
            force_refresh: If True, re-fetch even if cached
        """
        if city_name is None:
            city_name = config.DEMO_CITY_NAME
        
        city_info = config.CITIES.get(city_name, {
            "lat": config.DEMO_CITY_LAT,
            "lon": config.DEMO_CITY_LON
        })
        
        logger.info(f"=== Running ETL Pipeline for {city_name} ===")
        start_time = time.time()
        
        # Check cache
        if not force_refresh and dataset_exists(city_name):
            logger.info(f"Loading cached data for {city_name}")
            cached = load_dataset(city_name)
            if cached is not None:
                self.data[city_name] = cached["data"]
                self.metadata[city_name] = cached["metadata"]
                self.is_loaded = True
                logger.info(f"Loaded from cache in {time.time()-start_time:.2f}s")
                return
        
        # === EXTRACT ===
        logger.info("Phase 1: EXTRACT")
        raw_data = self._extract(city_name, city_info)
        
        # === TRANSFORM ===
        logger.info("Phase 2: TRANSFORM (Harmonize)")
        processed_data = self._transform(raw_data)
        
        # === LOAD ===
        logger.info("Phase 3: LOAD (Persist)")
        meta = generate_metadata(
            city_name=city_name,
            city_lat=city_info["lat"],
            city_lon=city_info["lon"],
            grid_size=config.GRID_SIZE,
            resolution_km=config.GRID_RESOLUTION_KM,
            num_weeks=config.TIME_STEPS
        )
        
        self.data[city_name] = processed_data
        self.metadata[city_name] = meta
        self.is_loaded = True
        
        # Persist
        save_dataset(city_name, processed_data, meta)
        
        elapsed = time.time() - start_time
        logger.info(f"=== Pipeline complete for {city_name} in {elapsed:.2f}s ===")
    
    def _extract(self, city_name, city_info):
        """Extract data from sources."""
        if config.use_sample_data():
            logger.info("Using sample data generator (no API keys configured)")
            raw_data = generate_time_series(
                grid_size=config.GRID_SIZE,
                num_weeks=config.TIME_STEPS,
                city_name=city_name
            )
        else:
            # Try real data sources
            logger.info("Attempting to fetch from real satellite sources...")
            raw_data = self._fetch_real_data(city_info)
            
            if raw_data is None:
                logger.warning("Real data fetch failed, falling back to sample data")
                raw_data = generate_time_series(
                    grid_size=config.GRID_SIZE,
                    num_weeks=config.TIME_STEPS,
                    city_name=city_name
                )
        
        return raw_data
    
    def _fetch_real_data(self, city_info):
        """Attempt to fetch from GEE, NASA, Sentinel APIs."""
        try:
            from ingestion.gee_fetcher import authenticate_gee, fetch_modis_ndvi, fetch_landsat_temperature
            
            if config.GEE_SERVICE_ACCOUNT_KEY:
                if authenticate_gee(config.GEE_SERVICE_ACCOUNT_KEY):
                    ndvi = fetch_modis_ndvi(
                        city_info["lat"], city_info["lon"],
                        "2025-01-01", "2026-03-21"
                    )
                    temp = fetch_landsat_temperature(
                        city_info["lat"], city_info["lon"],
                        "2025-01-01", "2026-03-21"
                    )
                    if ndvi is not None and temp is not None:
                        return {
                            "ndvi": ndvi,
                            "temperature": temp,
                            "pollution": None,
                            "soil_moisture": None,
                        }
        except Exception as e:
            logger.warning(f"Real data extraction failed: {e}")
        
        return None
    
    def _transform(self, raw_data):
        """Apply harmonization pipeline."""
        processed = {}
        target_shape = (config.GRID_SIZE, config.GRID_SIZE)
        
        for param_name, param_data in raw_data.items():
            if param_data is not None:
                processed[param_name] = harmonize_dataset(
                    param_data, 
                    target_shape=target_shape,
                    smooth_sigma=0.8
                )
                logger.info(f"  Harmonized {param_name}: shape={processed[param_name].shape}")
            else:
                logger.warning(f"  Skipping {param_name} (no data)")
        
        return processed
    
    def get_data(self, city_name=None):
        """Get processed data for a city."""
        if city_name is None:
            city_name = config.DEMO_CITY_NAME
        return self.data.get(city_name)
    
    def get_metadata(self, city_name=None):
        """Get metadata for a city."""
        if city_name is None:
            city_name = config.DEMO_CITY_NAME
        return self.metadata.get(city_name)
    
    def get_grid_value(self, city_name, parameter, lat, lon, week_index=-1):
        """Get value at a specific lat/lon for a parameter."""
        meta = self.metadata.get(city_name)
        data = self.data.get(city_name, {}).get(parameter)
        
        if meta is None or data is None:
            return None
        
        bounds = meta["bounds"]
        grid_size = meta["grid_size"]
        
        # Convert lat/lon to grid indices
        row = int((lat - bounds["lat_min"]) / (bounds["lat_max"] - bounds["lat_min"]) * grid_size)
        col = int((lon - bounds["lon_min"]) / (bounds["lon_max"] - bounds["lon_min"]) * grid_size)
        
        row = np.clip(row, 0, grid_size - 1)
        col = np.clip(col, 0, grid_size - 1)
        
        if data.ndim == 3:
            return float(data[week_index, row, col])
        return float(data[row, col])
    
    def get_time_series_at_point(self, city_name, parameter, lat, lon):
        """Get full time series at a lat/lon point."""
        meta = self.metadata.get(city_name)
        data = self.data.get(city_name, {}).get(parameter)
        
        if meta is None or data is None or data.ndim != 3:
            return None, None
        
        bounds = meta["bounds"]
        grid_size = meta["grid_size"]
        
        row = int((lat - bounds["lat_min"]) / (bounds["lat_max"] - bounds["lat_min"]) * grid_size)
        col = int((lon - bounds["lon_min"]) / (bounds["lon_max"] - bounds["lon_min"]) * grid_size)
        
        row = np.clip(row, 0, grid_size - 1)
        col = np.clip(col, 0, grid_size - 1)
        
        values = data[:, row, col].tolist()
        timestamps = meta.get("timestamps", list(range(len(values))))
        
        return timestamps, values
