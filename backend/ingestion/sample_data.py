"""
Sample Data Generator for Satellite Environmental Intelligence Platform.

Generates realistic synthetic satellite data for demo purposes.
Simulates spatial patterns that mimic real satellite observations:
- Urban heat island effect (higher temp in city center)
- NDVI gradient (more vegetation at outskirts)
- Pollution concentrated around industrial/traffic zones
- Soil moisture variation based on land cover
"""
import numpy as np
from datetime import datetime, timedelta
import json
import os

def _create_urban_heat_island(grid_size, center_intensity=45, edge_temp=30):
    """Create a temperature grid with urban heat island effect."""
    y, x = np.mgrid[0:grid_size, 0:grid_size]
    center = grid_size / 2
    distance = np.sqrt((x - center)**2 + (y - center)**2)
    max_dist = np.sqrt(2) * center
    # Temperature decreases with distance from center
    temp = center_intensity - (center_intensity - edge_temp) * (distance / max_dist)
    return temp

def _create_ndvi_gradient(grid_size, center_ndvi=0.15, edge_ndvi=0.75):
    """Create NDVI grid - low in urban core, high at vegetated outskirts."""
    y, x = np.mgrid[0:grid_size, 0:grid_size]
    center = grid_size / 2
    distance = np.sqrt((x - center)**2 + (y - center)**2)
    max_dist = np.sqrt(2) * center
    # NDVI increases with distance from center (more vegetation outside city)
    ndvi = center_ndvi + (edge_ndvi - center_ndvi) * (distance / max_dist)
    # Add some parks (random patches of high NDVI in the city)
    num_parks = 5
    rng = np.random.RandomState(42)
    for _ in range(num_parks):
        px, py = rng.randint(10, grid_size-10, 2)
        park_radius = rng.randint(2, 5)
        park_mask = ((x - px)**2 + (y - py)**2) < park_radius**2
        ndvi[park_mask] = rng.uniform(0.55, 0.75)
    return np.clip(ndvi, 0, 1)

def _create_pollution_map(grid_size):
    """Create pollution (AQI) map with industrial and traffic hotspots."""
    y, x = np.mgrid[0:grid_size, 0:grid_size]
    center = grid_size / 2
    
    # Base pollution - moderate everywhere
    pollution = np.full((grid_size, grid_size), 80.0)
    
    # Industrial zone (northeast)
    ind_x, ind_y = int(center * 1.4), int(center * 0.6)
    ind_dist = np.sqrt((x - ind_x)**2 + (y - ind_y)**2)
    pollution += 150 * np.exp(-ind_dist**2 / 50)
    
    # Traffic corridor (through center)
    traffic_mask = np.abs(y - center) < 3
    pollution[traffic_mask] += 60
    
    # Another traffic corridor (vertical)
    traffic_mask2 = np.abs(x - center) < 3
    pollution[traffic_mask2] += 40
    
    # City center elevated
    center_dist = np.sqrt((x - center)**2 + (y - center)**2)
    pollution += 40 * np.exp(-center_dist**2 / 100)
    
    return np.clip(pollution, 20, 350)

def _create_soil_moisture(grid_size):
    """Create soil moisture map (m³/m³)."""
    y, x = np.mgrid[0:grid_size, 0:grid_size]
    center = grid_size / 2
    distance = np.sqrt((x - center)**2 + (y - center)**2)
    max_dist = np.sqrt(2) * center
    
    # Lower moisture in urban areas (impervious surfaces), higher outside
    moisture = 0.15 + 0.25 * (distance / max_dist)
    
    # Add some variation
    rng = np.random.RandomState(123)
    moisture += rng.normal(0, 0.03, (grid_size, grid_size))
    
    return np.clip(moisture, 0.05, 0.50)

def generate_time_series(grid_size=50, num_weeks=52, city_name="Ahmedabad"):
    """
    Generate a complete time-series of synthetic satellite data.
    
    Returns dict with keys: ndvi, temperature, pollution, soil_moisture
    Each value is a numpy array of shape (num_weeks, grid_size, grid_size)
    """
    rng = np.random.RandomState(hash(city_name) % 2**31)
    
    # Base spatial patterns
    base_temp = _create_urban_heat_island(grid_size)
    base_ndvi = _create_ndvi_gradient(grid_size)
    base_pollution = _create_pollution_map(grid_size)
    base_moisture = _create_soil_moisture(grid_size)
    
    # Generate time series with seasonal variation
    data = {
        "ndvi": np.zeros((num_weeks, grid_size, grid_size)),
        "temperature": np.zeros((num_weeks, grid_size, grid_size)),
        "pollution": np.zeros((num_weeks, grid_size, grid_size)),
        "soil_moisture": np.zeros((num_weeks, grid_size, grid_size)),
    }
    
    for week in range(num_weeks):
        # Seasonal factor (peak summer at week 20, peak winter at week 46)
        season = np.sin(2 * np.pi * (week - 8) / 52)  # peaks around May
        monsoon = max(0, np.sin(2 * np.pi * (week - 22) / 52))  # monsoon July-Sept
        
        # Temperature: hotter in summer, cooler in winter
        temp_variation = season * 8  # ±8°C seasonal swing
        noise = rng.normal(0, 1.5, (grid_size, grid_size))
        data["temperature"][week] = base_temp + temp_variation + noise
        
        # NDVI: higher after monsoon, lower in dry season
        ndvi_seasonal = monsoon * 0.15  # greenery boost during monsoon
        ndvi_noise = rng.normal(0, 0.03, (grid_size, grid_size))
        data["ndvi"][week] = np.clip(base_ndvi + ndvi_seasonal + ndvi_noise, 0, 1)
        
        # Pollution: higher in winter (inversions), lower in monsoon (rain washout)
        pollution_seasonal = -season * 30 + (1 - monsoon) * 20
        poll_noise = rng.normal(0, 10, (grid_size, grid_size))
        data["pollution"][week] = np.clip(base_pollution + pollution_seasonal + poll_noise, 20, 400)
        
        # Soil moisture: higher in monsoon
        moisture_seasonal = monsoon * 0.12
        moisture_noise = rng.normal(0, 0.02, (grid_size, grid_size))
        data["soil_moisture"][week] = np.clip(base_moisture + moisture_seasonal + moisture_noise, 0.05, 0.55)
    
    return data

def generate_metadata(city_name="Ahmedabad", city_lat=23.0225, city_lon=72.5714,
                      grid_size=50, resolution_km=0.5, num_weeks=52):
    """Generate metadata for the sample dataset."""
    # Calculate grid bounds
    km_to_deg_lat = 1 / 111.0
    km_to_deg_lon = 1 / (111.0 * np.cos(np.radians(city_lat)))
    extent_km = grid_size * resolution_km / 2
    
    lat_min = city_lat - extent_km * km_to_deg_lat
    lat_max = city_lat + extent_km * km_to_deg_lat
    lon_min = city_lon - extent_km * km_to_deg_lon
    lon_max = city_lon + extent_km * km_to_deg_lon
    
    # Generate weekly timestamps (last 52 weeks)
    end_date = datetime(2026, 3, 21)
    timestamps = [(end_date - timedelta(weeks=num_weeks-1-i)).strftime("%Y-%m-%d")
                  for i in range(num_weeks)]
    
    return {
        "city": city_name,
        "center_lat": city_lat,
        "center_lon": city_lon,
        "grid_size": grid_size,
        "resolution_km": resolution_km,
        "crs": "EPSG:4326",
        "bounds": {
            "lat_min": round(lat_min, 6),
            "lat_max": round(lat_max, 6),
            "lon_min": round(lon_min, 6),
            "lon_max": round(lon_max, 6),
        },
        "timestamps": timestamps,
        "parameters": {
            "ndvi": {"unit": "index", "range": [0, 1], "description": "Normalized Difference Vegetation Index"},
            "temperature": {"unit": "°C", "range": [20, 55], "description": "Land Surface Temperature"},
            "pollution": {"unit": "AQI", "range": [0, 500], "description": "Air Quality Index (proxy)"},
            "soil_moisture": {"unit": "m³/m³", "range": [0, 0.55], "description": "Volumetric Soil Moisture"},
        },
        "sources": [
            "Synthetic (MODIS-like thermal)",
            "Synthetic (Sentinel-2-like NDVI)",
            "Synthetic (Ground station-calibrated AQI)",
            "Synthetic (SMAP-like soil moisture)",
        ],
    }


def get_lat_lon_arrays(metadata):
    """Generate latitude and longitude arrays for each grid cell."""
    bounds = metadata["bounds"]
    grid_size = metadata["grid_size"]
    
    lats = np.linspace(bounds["lat_min"], bounds["lat_max"], grid_size)
    lons = np.linspace(bounds["lon_min"], bounds["lon_max"], grid_size)
    
    return lats, lons
