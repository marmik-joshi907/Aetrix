"""
Data Harmonization Pipeline.

Handles the core challenge of satellite data:
- CRS transformation (reproject to EPSG:4326)
- Spatial resampling (to common 500m grid)
- Temporal alignment (weekly aggregation)
- Missing data handling (interpolation + forward-fill)
- Noise filtering (Gaussian smoothing)
"""
import numpy as np
from scipy import ndimage, interpolate
import logging

logger = logging.getLogger(__name__)


def reproject_to_common_crs(data, source_crs="EPSG:32643", target_crs="EPSG:4326",
                             source_bounds=None, target_bounds=None):
    """
    Reproject raster data from source CRS to target CRS.
    
    For the MVP, this is a conceptual wrapper. With rasterio installed,
    this performs actual reprojection. Without it, returns data as-is
    (sample data is already in EPSG:4326).
    """
    try:
        from rasterio.warp import reproject, Resampling
        from rasterio.crs import CRS
        from rasterio.transform import from_bounds
        
        src_crs = CRS.from_string(source_crs)
        dst_crs = CRS.from_string(target_crs)
        
        if src_crs == dst_crs:
            return data
            
        src_transform = from_bounds(*source_bounds, data.shape[1], data.shape[0])
        dst_transform = from_bounds(*target_bounds, data.shape[1], data.shape[0])
        
        destination = np.zeros_like(data)
        reproject(
            source=data,
            destination=destination,
            src_transform=src_transform,
            src_crs=src_crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            resampling=Resampling.bilinear
        )
        
        logger.info(f"Reprojected from {source_crs} to {target_crs}")
        return destination
        
    except ImportError:
        logger.debug("rasterio not available, skipping CRS transform (sample data is already in EPSG:4326)")
        return data


def resample_spatial(data, target_shape=(50, 50), method='bilinear'):
    """
    Resample a 2D raster to a target grid size.
    
    Args:
        data: 2D numpy array
        target_shape: desired (rows, cols)
        method: 'bilinear', 'nearest', or 'cubic'
    """
    if data.shape == target_shape:
        return data
    
    current_rows, current_cols = data.shape
    target_rows, target_cols = target_shape
    
    # Calculate zoom factors
    row_factor = target_rows / current_rows
    col_factor = target_cols / current_cols
    
    if method == 'nearest':
        order = 0
    elif method == 'bilinear':
        order = 1
    elif method == 'cubic':
        order = 3
    else:
        order = 1
    
    resampled = ndimage.zoom(data, (row_factor, col_factor), order=order)
    
    # Ensure exact target shape (zoom can be off by 1)
    resampled = resampled[:target_rows, :target_cols]
    
    logger.debug(f"Resampled from {data.shape} to {resampled.shape}")
    return resampled


def align_temporal(time_series_data, source_interval_days=8, target_interval_days=7):
    """
    Align time series to a common temporal resolution.
    
    Aggregates irregular time intervals into weekly means.
    
    Args:
        time_series_data: array of shape (num_timesteps, rows, cols)
        source_interval_days: original data interval
        target_interval_days: desired interval (7 = weekly)
    
    Returns:
        Aligned time series array
    """
    num_steps, rows, cols = time_series_data.shape
    
    if source_interval_days == target_interval_days:
        return time_series_data
    
    # Calculate number of target steps
    total_days = num_steps * source_interval_days
    num_target_steps = total_days // target_interval_days
    
    # Interpolate along time axis for each grid cell
    source_times = np.arange(num_steps) * source_interval_days
    target_times = np.arange(num_target_steps) * target_interval_days
    
    aligned = np.zeros((num_target_steps, rows, cols))
    
    for r in range(rows):
        for c in range(cols):
            pixel_series = time_series_data[:, r, c]
            # Linear interpolation
            f = interpolate.interp1d(source_times, pixel_series, 
                                      kind='linear', fill_value='extrapolate')
            aligned[:, r, c] = f(target_times)
    
    logger.info(f"Temporal alignment: {num_steps} steps ({source_interval_days}d) → "
                f"{num_target_steps} steps ({target_interval_days}d)")
    return aligned


def fill_missing_data(data, method='spatial'):
    """
    Handle missing/NaN values in raster data.
    
    Methods:
        'spatial' - Interpolate from neighboring cells
        'temporal' - Forward-fill from previous timestep
        'mean' - Replace with layer mean
    """
    if not np.any(np.isnan(data)):
        return data
    
    filled = data.copy()
    
    if method == 'spatial' and data.ndim == 2:
        # Use nearest-neighbor interpolation for NaN cells
        mask = np.isnan(filled)
        if np.any(mask):
            # Replace NaN with interpolated values from neighbors
            filled[mask] = ndimage.generic_filter(
                filled, np.nanmean, size=5, mode='constant', cval=np.nan
            )[mask]
            # If still NaN, use global mean
            remaining_nan = np.isnan(filled)
            if np.any(remaining_nan):
                filled[remaining_nan] = np.nanmean(data)
                
    elif method == 'temporal' and data.ndim == 3:
        # Forward-fill along time axis
        for t in range(1, data.shape[0]):
            mask = np.isnan(filled[t])
            filled[t][mask] = filled[t-1][mask]
        # Back-fill first frame if needed
        mask = np.isnan(filled[0])
        if np.any(mask):
            for t in range(1, data.shape[0]):
                still_nan = np.isnan(filled[0])
                if not np.any(still_nan):
                    break
                filled[0][still_nan] = filled[t][still_nan]
    
    elif method == 'mean':
        global_mean = np.nanmean(data)
        filled = np.where(np.isnan(filled), global_mean, filled)
    
    num_fixed = np.sum(np.isnan(data)) - np.sum(np.isnan(filled))
    logger.debug(f"Filled {num_fixed} missing values using '{method}' method")
    return filled


def apply_noise_filter(data, sigma=1.0):
    """
    Apply Gaussian smoothing to reduce noise in raster data.
    
    Args:
        data: 2D or 3D numpy array
        sigma: Gaussian kernel standard deviation
    """
    if data.ndim == 2:
        return ndimage.gaussian_filter(data, sigma=sigma)
    elif data.ndim == 3:
        # Apply per-timestep
        filtered = np.zeros_like(data)
        for t in range(data.shape[0]):
            filtered[t] = ndimage.gaussian_filter(data[t], sigma=sigma)
        return filtered
    return data


def harmonize_dataset(data, target_shape=(50, 50), smooth_sigma=0.8):
    """
    Full harmonization pipeline for a single dataset.
    
    Steps:
    1. Resample to common grid
    2. Fill missing values
    3. Apply noise filter
    """
    if data.ndim == 2:
        result = resample_spatial(data, target_shape)
        result = fill_missing_data(result, method='spatial')
        result = apply_noise_filter(result, sigma=smooth_sigma)
    elif data.ndim == 3:
        # Time-series: harmonize each frame
        num_steps = data.shape[0]
        result = np.zeros((num_steps, *target_shape))
        for t in range(num_steps):
            result[t] = resample_spatial(data[t], target_shape)
        result = fill_missing_data(result, method='temporal')
        result = apply_noise_filter(result, sigma=smooth_sigma)
    else:
        result = data
    
    logger.info(f"Harmonized dataset: shape={result.shape}")
    return result
