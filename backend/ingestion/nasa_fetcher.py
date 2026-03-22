"""
NASA API Data Fetcher.

Fetches data from NASA's CMR (Common Metadata Repository) API:
- MODIS data products
- SMAP soil moisture

Requires NASA Earthdata API key.
"""
import numpy as np
import requests
import logging

logger = logging.getLogger(__name__)

NASA_CMR_BASE = "https://cmr.earthdata.nasa.gov/search"
NASA_EARTHDATA_BASE = "https://ladsweb.modaps.eosdis.nasa.gov/api/v2"


def fetch_modis_data(api_key, lat, lon, product="MOD11A2", start_date=None, end_date=None):
    """
    Fetch MODIS data via NASA CMR API.
    
    Products:
        MOD11A2 - Land Surface Temperature (8-day)
        MOD13A2 - NDVI (16-day)
        MOD09GA - Surface Reflectance (daily)
    """
    try:
        # Search for granules
        params = {
            "short_name": product,
            "point": f"{lon},{lat}",
            "temporal": f"{start_date},{end_date}" if start_date else None,
            "page_size": 10,
            "sort_key": "-start_date",
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        headers = {"Authorization": f"Bearer {api_key}"}
        
        response = requests.get(
            f"{NASA_CMR_BASE}/granules.json",
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            granules = data.get("feed", {}).get("entry", [])
            logger.info(f"Found {len(granules)} {product} granules")
            return granules
        else:
            logger.warning(f"NASA API returned {response.status_code}: {response.text[:200]}")
            return None
            
    except Exception as e:
        logger.warning(f"NASA MODIS fetch failed: {e}")
        return None


def fetch_smap_soil_moisture(api_key, lat, lon, start_date=None, end_date=None):
    """
    Fetch SMAP soil moisture data via NASA CMR.
    
    Product: SPL3SMP_E (Enhanced L3 Radiometer Soil Moisture, 9km)
    """
    try:
        params = {
            "short_name": "SPL3SMP_E",
            "version": "005",
            "point": f"{lon},{lat}",
            "temporal": f"{start_date},{end_date}" if start_date else None,
            "page_size": 10,
            "sort_key": "-start_date",
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        headers = {"Authorization": f"Bearer {api_key}"}
        
        response = requests.get(
            f"{NASA_CMR_BASE}/granules.json",
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            granules = data.get("feed", {}).get("entry", [])
            logger.info(f"Found {len(granules)} SMAP granules")
            return granules
        else:
            logger.warning(f"NASA SMAP API returned {response.status_code}")
            return None
            
    except Exception as e:
        logger.warning(f"NASA SMAP fetch failed: {e}")
        return None


def download_granule(url, api_key, output_path):
    """Download a data granule file."""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers, stream=True, timeout=120)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Downloaded granule to {output_path}")
            return True
        else:
            logger.warning(f"Download failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"Granule download failed: {e}")
        return False
