-- 🛰️ SatIntel Environmental Time-Series Database Schema
-- Requires PostGIS extension for spatial queries

-- Enable PostGIS for spatial operations (requires PostgreSQL with PostGIS installed)
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. Locations Table (Grid cells or specific sensor spots)
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom GEOMETRY(Point, 4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)) STORED,
    UNIQUE (city, latitude, longitude)
);

-- Index for fast spatial queries
CREATE INDEX IF NOT EXISTS idx_locations_geom ON locations USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_locations_city ON locations (city);

-- 2. Environmental Time-Series Data Table
CREATE TABLE IF NOT EXISTS environmental_data (
    id BIGSERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id) ON DELETE CASCADE,
    parameter VARCHAR(50) NOT NULL, -- e.g., 'temperature', 'ndvi', 'pollution', 'soil_moisture'
    measurement_time TIMESTAMP WITH TIME ZONE NOT NULL,
    value DOUBLE PRECISION,
    unit VARCHAR(20)
);

-- Composite Index for fast querying by location, parameter, and time
CREATE INDEX IF NOT EXISTS idx_env_data_query 
ON environmental_data (location_id, parameter, measurement_time DESC);

-- Example partition strategy (Optional but recommended for massive datasets)
-- In a real production system, you would partition this by month or year.
