"""
Static knowledge documents for the RAG chatbot.

These documents are embedded into a FAISS vector store at startup
so the LLM can ground its answers in domain knowledge about
environmental science, satellite monitoring, and urban planning.
"""

KNOWLEDGE_DOCUMENTS = [
    # === Urban Heat Island ===
    {
        "title": "Urban Heat Island Effect",
        "content": (
            "The Urban Heat Island (UHI) effect occurs when urban areas experience "
            "significantly higher temperatures than surrounding rural areas. This is caused "
            "by dense concentrations of pavement, buildings, and impervious surfaces that "
            "absorb and retain heat. Key factors include: "
            "1) Low vegetation (low NDVI) in city cores reduces evapotranspiration cooling. "
            "2) Dark materials like asphalt absorb solar radiation. "
            "3) Waste heat from vehicles, air conditioning, and industry. "
            "4) Urban canyon geometry traps heat between tall buildings. "
            "Typical UHI intensity ranges from 1-3°C up to 10°C in extreme cases. "
            "Mitigation strategies include: green roofs, urban tree planting, cool pavement "
            "materials, increased park spaces, and reflective building surfaces."
        ),
    },
    # === NDVI Interpretation ===
    {
        "title": "NDVI Vegetation Index Interpretation",
        "content": (
            "Normalized Difference Vegetation Index (NDVI) ranges from -1 to +1 and indicates "
            "vegetation health. NDVI values: "
            "- 0.0 to 0.1: Barren rock, sand, snow, water, or concrete. "
            "- 0.1 to 0.2: Sparse or stressed vegetation, urban areas. "
            "- 0.2 to 0.4: Shrub and grassland, moderate vegetation. "
            "- 0.4 to 0.6: Temperate and tropical forests, healthy cropland. "
            "- 0.6 to 0.9: Dense, healthy vegetation like rainforests. "
            "Declining NDVI over time can indicate deforestation, drought stress, "
            "urbanization, or fire damage. Rising NDVI can indicate reforestation, "
            "monsoon greening, or agricultural growth. "
            "NDVI is derived from satellite imagery comparing near-infrared (NIR) "
            "and visible red reflectance: NDVI = (NIR - Red) / (NIR + Red)."
        ),
    },
    # === Air Quality Index ===
    {
        "title": "Air Quality Index (AQI) Levels and Health Impacts",
        "content": (
            "The Air Quality Index (AQI) measures air pollution levels and health risks. "
            "AQI ranges and health guidance: "
            "- 0-50 (Good): Satisfactory air quality with minimal health risk. "
            "- 51-100 (Moderate): Acceptable but sensitive individuals may be affected. "
            "- 101-150 (Unhealthy for Sensitive Groups): Asthmatics, elderly, children at risk. "
            "- 151-200 (Unhealthy): General population begins to experience health effects. "
            "- 201-300 (Very Unhealthy): Serious health effects for all. "
            "- 301-500 (Hazardous): Emergency health warnings. "
            "Major pollutants: PM2.5 (fine particles), PM10, NO2, SO2, CO, O3. "
            "Sources: vehicle emissions, industrial discharge, construction dust, "
            "crop burning, thermal power plants. "
            "Winter inversions trap pollutants near the ground, causing seasonal spikes. "
            "Monsoon rains help wash out particulates, reducing AQI temporarily."
        ),
    },
    # === Soil Moisture ===
    {
        "title": "Soil Moisture Monitoring and Agriculture",
        "content": (
            "Soil moisture is measured in volumetric water content (m³/m³). "
            "Typical ranges: "
            "- 0.05-0.15 m³/m³: Very dry, drought conditions. Crops under severe stress. "
            "- 0.15-0.25 m³/m³: Dry to moderately dry. Irrigation recommended. "
            "- 0.25-0.35 m³/m³: Optimal range for most crops. "
            "- 0.35-0.50 m³/m³: Wet. Can indicate recent rainfall or waterlogging risk. "
            "Low soil moisture combined with high temperature and low NDVI indicates "
            "drought conditions. High soil moisture after heavy rain can lead to flooding, "
            "especially in urban areas with poor drainage. "
            "Satellite sensors like SMAP and SMOS provide global soil moisture data. "
            "Monitoring helps optimize irrigation scheduling and detect early drought onset."
        ),
    },
    # === Crowd Safety ===
    {
        "title": "Crowd Detection and Safety Management",
        "content": (
            "Satellite-based crowd detection uses environmental proxy indicators to "
            "estimate crowd density in open areas. Key indicators: "
            "- Temperature anomalies: large gatherings create localized heat signatures. "
            "- Pollution spikes: elevated CO2/PM in event areas. "
            "- Vegetation trampling: NDVI drops in park/ground areas during events. "
            "Stampede risk factors: density > 5 persons/m², limited egress routes, "
            "uncontrolled crowd flow, panic triggers. "
            "Safety recommendations: maximum occupancy limits, multiple exit routes, "
            "CCTV monitoring, barrier placement, emergency response teams on standby. "
            "High-risk events: religious gatherings, political rallies, concerts, "
            "festivals, sports events."
        ),
    },
    # === Municipal Planning ===
    {
        "title": "Municipal Urban Planning and Environmental Management",
        "content": (
            "Municipal officers use satellite-derived environmental data to prioritize "
            "urban interventions. Top concern areas: "
            "1) Heat Stress Zones: Areas with temperature > 40°C, low NDVI < 0.2. "
            "   Solutions: tree planting drives, cool roof mandates, public cooling centers. "
            "2) Air Pollution Hotspots: AQI > 150 zones near industrial areas or traffic corridors. "
            "   Solutions: emission monitoring, traffic management, green buffer zones. "
            "3) Water Stress Areas: Soil moisture < 0.15 with declining trend. "
            "   Solutions: rainwater harvesting, irrigation optimization, drought-resistant crops. "
            "4) Vegetation Loss: Rapidly declining NDVI indicating deforestation or land conversion. "
            "   Solutions: urban forest programs, protected green zones, compensatory planting. "
            "Impact tracking: monitor changes in satellite metrics post-intervention "
            "to measure effectiveness of policies."
        ),
    },
    # === Platform Overview ===
    {
        "title": "SatIntel Platform Overview",
        "content": (
            "SatIntel is a Satellite Environmental Intelligence Platform that converts "
            "raw satellite data into actionable environmental insights for smart city planning. "
            "The platform monitors 4 parameters across Indian cities: "
            "1) Temperature (°C): Land Surface Temperature from thermal satellite bands. "
            "2) NDVI (index 0-1): Vegetation health from near-infrared satellite imagery. "
            "3) Pollution (AQI): Air quality proxy combining ground station and satellite data. "
            "4) Soil Moisture (m³/m³): Volumetric water content from microwave sensors. "
            "Available cities: Ahmedabad, Delhi, Bengaluru, Mumbai, Chennai. "
            "Features: interactive heatmaps, hotspot detection (DBSCAN), anomaly detection "
            "(Isolation Forest), ARIMA trend forecasting, explainable predictions, "
            "crowd detection, timeline warnings, early warning system, and municipal dashboard. "
            "Data is processed through an ETL pipeline: Extract → Transform → Load, "
            "with 52 weeks of historical data on a 50×50 grid (~500m resolution per cell)."
        ),
    },
    # === Indian Cities Context ===
    {
        "title": "Indian Cities Environmental Context",
        "content": (
            "Ahmedabad: Located in Gujarat (23.02°N, 72.57°E). Hot semi-arid climate. "
            "Extreme summer temperatures regularly exceed 45°C. Faces severe heat island effects. "
            "First Indian city with a Heat Action Plan. Industrial pollution from textile/chemical industries. "
            "Delhi: Capital (28.61°N, 77.21°E). Severe air pollution, especially in winter. "
            "AQI frequently exceeds 300+ during Nov-Jan due to crop burning, vehicular emissions, "
            "and thermal inversions. Yamuna river pollution is a major concern. "
            "Bengaluru: (12.97°N, 77.59°E). Known as India's IT capital. Rapid urbanization "
            "causing lake destruction and green cover loss. Losing ~2% tree cover annually. "
            "Mumbai: (19.08°N, 72.88°E). Coastal city with monsoon flooding risks. "
            "Mangrove loss, reclamation, and urban flooding are key environmental concerns. "
            "Chennai: (13.08°N, 80.27°E). Prone to both flooding and water scarcity. "
            "2019 water crisis highlighted need for better water management."
        ),
    },
    # === ML Models Used ===
    {
        "title": "Machine Learning Models in SatIntel",
        "content": (
            "SatIntel uses several ML models for environmental analysis: "
            "1) DBSCAN Clustering: Used for spatial hotspot detection. Groups nearby grid cells "
            "with similar extreme values into hotspot clusters. Parameters: eps=0.5, min_samples=5. "
            "2) Isolation Forest: Anomaly detection for both spatial (single timestep) and "
            "temporal (across weeks) patterns. Identifies unusually high/low values. Contamination=0.05. "
            "3) ARIMA (AutoRegressive Integrated Moving Average): Time series forecasting for "
            "predicting parameter trends 4+ weeks ahead at specific locations. "
            "4) XGBoost: Used for soil moisture, pollution, and land-use predictions with "
            "pre-trained models. "
            "5) Linear Regression: Temperature trend prediction over multi-year horizons. "
            "All models process 50×50 spatial grids with 52 weekly timesteps per city."
        ),
    },
]
