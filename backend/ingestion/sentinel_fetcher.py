"""
Copernicus Sentinel Hub Data Fetcher.

Fetches Sentinel-2 and Sentinel-5P data:
- Sentinel-2: High-resolution optical imagery (10m), NDVI
- Sentinel-5P: Atmospheric composition (NO2, SO2, CO, O3 - pollution proxies)

Requires Copernicus SciHub credentials.
"""
import numpy as np
import requests
import logging

logger = logging.getLogger(__name__)

SCIHUB_BASE = "https://scihub.copernicus.eu/dhus/search"


def search_sentinel2(username, password, lat, lon, start_date, end_date, max_cloud=30):
    """
    Search for Sentinel-2 products in the Copernicus Open Access Hub.
    """
    try:
        # Define footprint (small bounding box)
        delta = 0.15  # ~15km
        footprint = (
            f"POLYGON(({lon-delta} {lat-delta}, {lon+delta} {lat-delta}, "
            f"{lon+delta} {lat+delta}, {lon-delta} {lat+delta}, {lon-delta} {lat-delta}))"
        )
        
        query = (
            f"platformname:Sentinel-2 AND "
            f"cloudcoverpercentage:[0 TO {max_cloud}] AND "
            f"beginposition:[{start_date}T00:00:00.000Z TO {end_date}T23:59:59.999Z] AND "
            f"footprint:\"Intersects({footprint})\""
        )
        
        params = {
            "q": query,
            "format": "json",
            "rows": 10,
            "orderby": "beginposition desc",
        }
        
        response = requests.get(
            SCIHUB_BASE,
            params=params,
            auth=(username, password),
            timeout=30,
        )
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get("feed", {}).get("entry", [])
            if isinstance(entries, dict):
                entries = [entries]
            logger.info(f"Found {len(entries)} Sentinel-2 products")
            return entries
        else:
            logger.warning(f"Sentinel Hub returned {response.status_code}")
            return None
            
    except Exception as e:
        logger.warning(f"Sentinel-2 search failed: {e}")
        return None


def search_sentinel5p(username, password, lat, lon, start_date, end_date, product_type="L2__NO2___"):
    """
    Search for Sentinel-5P atmospheric data.
    
    Product types:
        L2__NO2___  - Nitrogen Dioxide
        L2__SO2___  - Sulphur Dioxide  
        L2__CO____  - Carbon Monoxide
        L2__O3____  - Ozone
    """
    try:
        delta = 0.5  # Larger area for atmospheric data
        footprint = (
            f"POLYGON(({lon-delta} {lat-delta}, {lon+delta} {lat-delta}, "
            f"{lon+delta} {lat+delta}, {lon-delta} {lat+delta}, {lon-delta} {lat-delta}))"
        )
        
        query = (
            f"platformname:Sentinel-5 AND "
            f"producttype:{product_type} AND "
            f"beginposition:[{start_date}T00:00:00.000Z TO {end_date}T23:59:59.999Z] AND "
            f"footprint:\"Intersects({footprint})\""
        )
        
        params = {
            "q": query,
            "format": "json",
            "rows": 10,
        }
        
        response = requests.get(
            SCIHUB_BASE,
            params=params,
            auth=(username, password),
            timeout=30,
        )
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get("feed", {}).get("entry", [])
            if isinstance(entries, dict):
                entries = [entries]
            logger.info(f"Found {len(entries)} Sentinel-5P {product_type} products")
            return entries
        else:
            logger.warning(f"Sentinel-5P search returned {response.status_code}")
            return None
            
    except Exception as e:
        logger.warning(f"Sentinel-5P search failed: {e}")
        return None
