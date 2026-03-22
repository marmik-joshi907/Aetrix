"""
Sync Memory Grid Data to PostGIS.

This script extracts the highly detailed 3D numpy arrays from the pipeline
(e.g., NDVI, Temperature, Pollution) and natively converts them into spatial
features using GeoPandas, then pushes them to the new PostgreSQL database.

Requirements: geopandas, geoalchemy2, psycopg2
"""
import sys
import os
import time
import logging

# Add backend dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sqlalchemy import text

import config
from database import engine, SessionLocal
from pipeline.processor import DataPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyncToPostGIS")

def sync_city_data(city_name="Ahmedabad"):
    logger.info(f"Starting synchronization to PostGIS for {city_name}...")
    
    # 1. Initialize Pipeline and Load Data
    pipeline = DataPipeline()
    pipeline.run_pipeline(city_name)
    
    data = pipeline.get_data(city_name)
    meta = pipeline.get_metadata(city_name)
    
    if not data or not meta:
        logger.error("Failed to load data from pipeline.")
        return
        
    bounds = meta["bounds"]
    grid_size = meta["grid_size"]
    timestamps = meta["timestamps"]
    
    logger.info("Generating spatial grid coordinates...")
    lats = np.linspace(bounds["lat_min"], bounds["lat_max"], grid_size)
    lons = np.linspace(bounds["lon_min"], bounds["lon_max"], grid_size)
    
    # 2. Build GeoDataFrame for Locations
    db = SessionLocal()
    try:
        logger.info("Preparing spatial location points...")
        locations = []
        for r, lat in enumerate(lats):
            for c, lon in enumerate(lons):
                locations.append({
                    "city": city_name,
                    "latitude": lat,
                    "longitude": lon,
                    "geometry": Point(lon, lat)  # Note: shapely uses (lon, lat)
                })
        
        gdf_locations = gpd.GeoDataFrame(locations, geometry="geometry", crs="EPSG:4326")
        
        # 3. Save locations to PostgreSQL
        # We don't save 'geometry' directly via pandas to_sql unless using geoalchemy2
        # For simplicity, we drop geometry since our PostGIS init.sql generates it automatically 
        # from latitude/longitude columns using GENERATED ALWAYS AS ... STORED
        df_locations = gdf_locations.drop(columns=['geometry'])
        
        logger.info("Pushing 2,500 grid cells to 'locations' table...")
        try:
            df_locations.to_sql("locations", engine, if_exists="append", index=False)
            logger.info("Locations inserted successfully.")
        except Exception as e:
            if "duplicate key" in str(e).lower() or "uniqueviolation" in str(e).lower():
                logger.info("Locations already exist in the database. Proceeding to fetch their IDs...")
            else:
                raise e
        
        # Fetch the newly created location IDs
        loc_map = pd.read_sql(
            text(f"SELECT id, latitude, longitude FROM locations WHERE city = '{city_name}'"),
            engine
        )
        
        # 4. Process Time-Series Environmental Data
        env_records = []
        logger.info("Extracting time-series arrays for bulk ingestion...")
        
        for parameter, values_3d in data.items():
            logger.info(f"  Processing {parameter}...")
            for w, timestamp in enumerate(timestamps):
                # Flatten the 2D grid for this week into a 1D array
                grid_week = values_3d[w].flatten()
                
                # We need to map these to the location IDs
                for idx, val in enumerate(grid_week):
                    row = idx // grid_size
                    col = idx % grid_size
                    
                    lat_val = lats[row]
                    lon_val = lons[col]
                    
                    # Find corresponding location_id (Approximate match due to float precision)
                    loc_id = loc_map.loc[
                        (np.isclose(loc_map['latitude'], lat_val)) & 
                        (np.isclose(loc_map['longitude'], lon_val)), 'id'
                    ].values[0]
                    
                    env_records.append({
                        "location_id": int(loc_id),
                        "parameter": parameter,
                        "measurement_time": timestamp,
                        "value": float(val),
                        "unit": meta["parameters"][parameter]["unit"]
                    })
                    
        # 5. Bulk insert time-series
        logger.info(f"Bulk inserting {len(env_records)} records into 'environmental_data'. This may take a minute...")
        
        # Chunk the inserts
        chunk_size = 50000
        for i in range(0, len(env_records), chunk_size):
            chunk = env_records[i:i + chunk_size]
            df_env = pd.DataFrame(chunk)
            df_env.to_sql("environmental_data", engine, if_exists="append", index=False)
            logger.info(f"  Inserted {(i + len(chunk)) / len(env_records) * 100:.1f}%")
            
        logger.info("✅ Synchronization Complete!")
        
    except Exception as e:
        logger.error(f"Failed to sync data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_city_data("Ahmedabad")
