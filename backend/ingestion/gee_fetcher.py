"""
Google Earth Engine Data Fetcher.

Fetches satellite data from GEE:
- MODIS NDVI (MOD13A2)
- Landsat 8 Surface Temperature (LC08/C02/T1_L2)
- Sentinel-2 Imagery

Requires GEE authentication via service account key.
Falls back to sample data if not authenticated.
"""
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def authenticate_gee(service_account_key_path):
    """Authenticate with Google Earth Engine."""
    try:
        import ee
        credentials = ee.ServiceAccountCredentials(
            email=None,
            key_file=service_account_key_path
        )
        ee.Initialize(credentials)
        logger.info("GEE authentication successful")
        return True
    except Exception as e:
        logger.warning(f"GEE authentication failed: {e}")
        return False


def fetch_modis_ndvi(lat, lon, start_date, end_date, grid_size_km=25):
    """
    Fetch MODIS NDVI data from GEE.
    
    Args:
        lat: Center latitude
        lon: Center longitude  
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)
        grid_size_km: Size of area to fetch in km
        
    Returns:
        numpy array of NDVI values, or None if GEE not available
    """
    try:
        import ee
        
        # Define region of interest
        half_size = grid_size_km / 2 * 0.009  # ~degrees
        region = ee.Geometry.Rectangle([
            lon - half_size, lat - half_size,
            lon + half_size, lat + half_size
        ])
        
        # Fetch MODIS NDVI
        collection = (ee.ImageCollection('MODIS/006/MOD13A2')
                     .filterDate(start_date, end_date)
                     .filterBounds(region)
                     .select('NDVI'))
        
        # Get mean composite
        image = collection.mean()
        
        # Scale NDVI values (MODIS stores as int * 10000)
        ndvi = image.multiply(0.0001)
        
        # Sample to numpy array
        result = ndvi.sampleRectangle(region=region)
        ndvi_array = np.array(result.get('NDVI').getInfo())
        
        logger.info(f"Fetched MODIS NDVI: shape={ndvi_array.shape}")
        return ndvi_array
        
    except ImportError:
        logger.warning("earthengine-api not installed. Use: pip install earthengine-api")
        return None
    except Exception as e:
        logger.warning(f"GEE MODIS NDVI fetch failed: {e}")
        return None


def fetch_landsat_temperature(lat, lon, start_date, end_date, grid_size_km=25):
    """
    Fetch Landsat 8 Surface Temperature from GEE.
    
    Returns temperature in Celsius.
    """
    try:
        import ee
        
        half_size = grid_size_km / 2 * 0.009
        region = ee.Geometry.Rectangle([
            lon - half_size, lat - half_size,
            lon + half_size, lat + half_size
        ])
        
        # Landsat 8 Surface Temperature
        collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                     .filterDate(start_date, end_date)
                     .filterBounds(region)
                     .select('ST_B10'))
        
        image = collection.mean()
        
        # Convert to Celsius (scale factor 0.00341802, offset 149.0)
        temp_celsius = image.multiply(0.00341802).add(149.0).subtract(273.15)
        
        result = temp_celsius.sampleRectangle(region=region)
        temp_array = np.array(result.get('ST_B10').getInfo())
        
        logger.info(f"Fetched Landsat temperature: shape={temp_array.shape}")
        return temp_array
        
    except ImportError:
        logger.warning("earthengine-api not installed")
        return None
    except Exception as e:
        logger.warning(f"GEE Landsat temperature fetch failed: {e}")
        return None


def fetch_sentinel2_rgb(lat, lon, start_date, end_date, grid_size_km=25):
    """
    Fetch Sentinel-2 RGB imagery from GEE.
    
    Returns 3-band (R, G, B) numpy array.
    """
    try:
        import ee
        
        half_size = grid_size_km / 2 * 0.009
        region = ee.Geometry.Rectangle([
            lon - half_size, lat - half_size,
            lon + half_size, lat + half_size
        ])
        
        collection = (ee.ImageCollection('COPERNICUS/S2_SR')
                     .filterDate(start_date, end_date)
                     .filterBounds(region)
                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                     .select(['B4', 'B3', 'B2']))
        
        image = collection.median()
        
        result = image.sampleRectangle(region=region)
        r = np.array(result.get('B4').getInfo())
        g = np.array(result.get('B3').getInfo())
        b = np.array(result.get('B2').getInfo())
        
        rgb = np.stack([r, g, b], axis=-1)
        logger.info(f"Fetched Sentinel-2 RGB: shape={rgb.shape}")
        return rgb
        
    except ImportError:
        logger.warning("earthengine-api not installed")
        return None
    except Exception as e:
        logger.warning(f"GEE Sentinel-2 fetch failed: {e}")
        return None
