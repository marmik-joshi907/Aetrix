"""
Master trainer: Run all 4 ML training pipelines sequentially.

Usage:
    cd backend
    python -m ml.train_all
"""
import sys
import os

# Ensure backend dir is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ml.preprocess import clean_temperature, clean_soil_moisture, clean_pollution
from ml.model_temp import train_temperature_model
from ml.model_soil import train_soil_model
from ml.model_pollution import train_pollution_model
from ml.model_landuse import train_landuse_model

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("STEP 1: Cleaning all datasets")
    print("=" * 60)
    clean_temperature()
    clean_soil_moisture()
    clean_pollution()

    print("\n" + "=" * 60)
    print("STEP 2: Training Temperature LSTM")
    print("=" * 60)
    train_temperature_model()

    print("\n" + "=" * 60)
    print("STEP 3: Training Soil Moisture Random Forest + ARIMA")
    print("=" * 60)
    train_soil_model()

    print("\n" + "=" * 60)
    print("STEP 4: Training Pollution XGBoost + DBSCAN")
    print("=" * 60)
    train_pollution_model()

    print("\n" + "=" * 60)
    print("STEP 5: Training Land Use K-Means")
    print("=" * 60)
    train_landuse_model()

    print("\n" + "=" * 60)
    print("ALL MODELS TRAINED. Files in models/saved/")
    print("=" * 60)
