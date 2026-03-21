"""
Data cleaning and preprocessing for all 3 CSV datasets.
Run clean_temperature(), clean_soil_moisture(), clean_pollution() to produce
cleaned CSVs in data/processed/.
"""
import os
import sys
import pandas as pd
import numpy as np

# Ensure backend dir is on path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def clean_temperature(path=None):
    """Clean India national temperature dataset (1901-2021)."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "raw",
                            "TEMP_ANNUAL_SEASONAL_MEAN.csv")

    df = pd.read_csv(path)

    # Drop trailing garbage rows (where YEAR is null or not a 4-digit year)
    df = df.dropna(subset=["YEAR"])
    df = df[pd.to_numeric(df["YEAR"], errors="coerce").notna()]
    df["YEAR"] = df["YEAR"].astype(int)

    # Convert all temp columns from string to float
    for col in ["ANNUAL", "JAN-FEB", "MAR-MAY", "JUN-SEP", "OCT-DEC"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Interpolate any remaining NaN values (there will be 1-2)
    df = df.interpolate(method="linear")
    df = df.reset_index(drop=True)

    # Add a rolling 10-year average column (useful as a feature)
    df["ANNUAL_ROLL10"] = df["ANNUAL"].rolling(window=10, min_periods=1).mean()

    # Add anomaly flag: year where ANNUAL > mean + 1.5*std
    mean_t = df["ANNUAL"].mean()
    std_t = df["ANNUAL"].std()
    df["IS_ANOMALY_YEAR"] = (
        (df["ANNUAL"] > mean_t + 1.5 * std_t)
        | (df["ANNUAL"] < mean_t - 1.5 * std_t)
    ).astype(int)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(os.path.join(out_dir, "temp_clean.csv"), index=False)
    print(f"[TEMP] Cleaned: {len(df)} rows, columns: {list(df.columns)}")
    return df


def clean_soil_moisture(path=None):
    """Clean Gujarat soil moisture dataset (Jun-Dec 2018)."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "raw",
                            "sm_Gujarat_2018.csv")

    df = pd.read_csv(path)

    # Drop the useless volume column (all "-" values)
    if "Average SoilMoisture Volume (at 15cm)" in df.columns:
        df = df.drop(columns=["Average SoilMoisture Volume (at 15cm)"])

    # Parse date
    df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m/%d")

    # Rename columns to short names for easier use
    df = df.rename(columns={
        "Average Soilmoisture Level (at 15cm)":        "sm_level",
        "Aggregate Soilmoisture Percentage (at 15cm)": "sm_agg_pct",
        "Volume Soilmoisture percentage (at 15cm)":    "sm_vol_pct",
        "DistrictName":                                "district",
        "State Name":                                  "state",
    })

    # Normalize district name casing
    df["district"] = df["district"].str.title()

    # Add time features (useful for time-series models)
    df["day_of_year"] = df["Date"].dt.dayofyear
    df["week"] = df["Date"].dt.isocalendar().week.astype(int)
    df["month"] = df["Date"].dt.month

    # Label-encode district for ML (also keep original string)
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    df["district_encoded"] = le.fit_transform(df["district"])

    # Create target: drought risk class based on sm_agg_pct thresholds
    def drought_class(pct):
        if pct < 5:
            return 2   # High drought risk
        elif pct < 15:
            return 1   # Medium risk
        else:
            return 0   # Low risk / adequate moisture

    df["drought_risk"] = df["sm_agg_pct"].apply(drought_class)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(os.path.join(out_dir, "soil_clean.csv"), index=False)
    print(f"[SOIL] Cleaned: {len(df)} rows, districts: {df['district'].nunique()}")
    return df


def clean_pollution(path=None):
    """Clean CPCB India pollutant station snapshot."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "raw",
                            "pollutants_india_live.csv")

    df = pd.read_csv(path)

    # Drop rows where sensor was offline (null readings)
    df["pollutant_avg"] = pd.to_numeric(df["pollutant_avg"], errors="coerce")
    df = df.dropna(subset=["pollutant_avg"])

    # Keep only the columns we need
    df = df[["state", "city", "station", "latitude", "longitude",
             "pollutant_id", "pollutant_avg"]]

    # Clean lat/lon (some have trailing spaces)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])

    # Pivot: one row per station, one column per pollutant
    df_wide = df.pivot_table(
        index=["state", "city", "station", "latitude", "longitude"],
        columns="pollutant_id",
        values="pollutant_avg",
        aggfunc="mean",
    ).reset_index()

    # Flatten column names
    df_wide.columns.name = None

    # Fill missing pollutant readings with median of that pollutant
    for col in ["CO", "NH3", "NO2", "OZONE", "PM10", "PM2.5", "SO2"]:
        if col in df_wide.columns:
            df_wide[col] = df_wide[col].fillna(df_wide[col].median())

    # Compute AQI category from PM2.5 (India CPCB standard)
    def aqi_category(pm25):
        if pd.isna(pm25):
            return 0
        if pm25 <= 30:
            return 0   # Good
        elif pm25 <= 60:
            return 1   # Satisfactory
        elif pm25 <= 90:
            return 2   # Moderate
        elif pm25 <= 120:
            return 3   # Poor
        elif pm25 <= 250:
            return 4   # Very Poor
        else:
            return 5   # Severe

    df_wide["aqi_category"] = df_wide["PM2.5"].apply(aqi_category)
    df_wide["aqi_label"] = df_wide["aqi_category"].map({
        0: "Good", 1: "Satisfactory", 2: "Moderate",
        3: "Poor", 4: "Very Poor", 5: "Severe",
    })

    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
    os.makedirs(out_dir, exist_ok=True)
    df_wide.to_csv(os.path.join(out_dir, "pollution_clean.csv"), index=False)
    print(f"[POLLUTION] Cleaned: {len(df_wide)} station rows after pivot")
    print(f"  Columns: {list(df_wide.columns)}")
    return df_wide


if __name__ == "__main__":
    clean_temperature()
    clean_soil_moisture()
    clean_pollution()
    print("\n✅ All datasets cleaned.")
