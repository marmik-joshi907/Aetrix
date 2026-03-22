# 🛰️ Satellite Environmental Intelligence Platform

> Transform raw satellite data into actionable environmental insights for smart city planning and sustainable urban development.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🌟 Overview

Aetrix is a comprehensive environmental monitoring and analysis platform that leverages satellite imagery and machine learning to provide real-time insights into urban environmental conditions. The platform processes multi-spectral satellite data to monitor vegetation health (NDVI), surface temperatures, air pollution levels, and soil moisture across major Indian cities.

### Key Features

- **📊 Multi-Parameter Monitoring**: Track NDVI, temperature, pollution, and soil moisture
- **🔍 ML-Powered Analytics**: Anomaly detection, hotspot clustering, and trend prediction
- **🗺️ Interactive Visualization**: Real-time map rendering with Leaflet.js
- **📈 Predictive Modeling**: ARIMA-based forecasting for environmental trends
- **🎯 Actionable Insights**: Automated municipal action plan generation
- **🏙️ Multi-City Support**: Pre-configured for major Indian metropolitan areas

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend     │    │   Data Sources  │
│   (React)       │◄──►│   (FastAPI)     │◄──►│                 │
│                 │    │                 │    │ • Google Earth  │
│ • Map View      │    │ • API Routes    │    │   Engine        │
│ • Dashboard     │    │ • ML Pipeline   │    │ • NASA CMR      │
│ • Time Controls │    │ • Data Pipeline │    │ • Copernicus    │
│ • Layer Control │    │                 │    │ • Sample Data   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   ML Models     │
                       │                 │
                       │ • Isolation     │
                       │   Forest        │
                       │ • ARIMA         │
                       │ • DBSCAN        │
                       │ • LSTM          │
                       │ • XGBoost       │
                       │ • Random Forest │
                       │ • K-Means       │
                       └─────────────────┘
```

### System Components

#### Backend (Python/FastAPI)
- **Data Ingestion**: Fetches from Google Earth Engine, NASA, and Copernicus APIs
- **ETL Pipeline**: Processes and harmonizes satellite data
- **ML Engine**: Trains and serves predictive models
- **REST API**: Provides data access and analytics endpoints

#### Frontend (React/Leaflet)
- **Interactive Maps**: Real-time visualization of environmental data
- **Time Series Analysis**: Historical trend exploration
- **Dashboard**: Key metrics and insights display
- **Prediction Interface**: Future trend forecasting

#### Data Pipeline
- **Raw Data Sources**: Satellite imagery from multiple providers
- **Processing**: Spatial-temporal harmonization and cleaning
- **Storage**: Optimized NumPy arrays with metadata
- **Caching**: Intelligent data caching for performance

## �️ Technology Stack

### Backend (Python)

#### Core Framework
- **FastAPI**: High-performance async web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **Pydantic**: Data validation and parsing using Python type hints
- **Python-Dotenv**: Environment variable management
- **Python-Multipart**: Multipart form data handling

#### Data Processing & Analysis
- **NumPy**: Fundamental package for array computing
- **Pandas**: Data manipulation and analysis library
- **SciPy**: Scientific computing and technical computing
- **GeoPandas**: Geospatial data manipulation
- **Shapely**: Geometric operations for geospatial data

#### Machine Learning & Statistics
- **Scikit-learn**: Machine learning algorithms (Isolation Forest, Random Forest)
- **Statsmodels**: Statistical modeling (ARIMA, time series analysis)
- **XGBoost**: Gradient boosting framework for pollution modeling
- **Joblib**: Parallel computing and model serialization

#### HTTP & API Clients
- **Requests**: HTTP library for API calls
- **HTTPX**: Async HTTP client for modern Python

### Frontend (JavaScript/React)

#### Core Framework
- **React 18.2+**: User interface library
- **React DOM**: React rendering library
- **React Scripts**: Build scripts and development server

#### Mapping & Visualization
- **Leaflet**: Open-source JavaScript library for mobile-friendly maps
- **React-Leaflet**: React components for Leaflet maps
- **Leaflet.Heat**: Heatmap plugin for Leaflet
- **Chart.js**: Simple yet flexible JavaScript charting library
- **React-ChartJS-2**: React wrapper for Chart.js

#### HTTP & State Management
- **Axios**: Promise-based HTTP client for API requests
- **AJV (Another JSON Schema Validator)**: JSON schema validation

### Data Sources & APIs

#### Satellite Data Providers
- **Google Earth Engine**: Planetary-scale geospatial analysis platform
- **NASA CMR (Common Metadata Repository)**: Earth science data access
- **Copernicus Sentinel Hub**: European Space Agency's satellite data
- **Sample Data Generator**: Fallback synthetic data for demonstrations

#### Mapping & Tiles
- **OpenStreetMap**: Collaborative mapping project
- **CartoDB**: Location intelligence and data visualization platform

### Machine Learning Models

#### Anomaly Detection
- **Isolation Forest**: Unsupervised anomaly detection algorithm

#### Time Series Forecasting
- **ARIMA (AutoRegressive Integrated Moving Average)**: Statistical forecasting method
- **MLPRegressor (Multi-Layer Perceptron)**: Neural network for temperature prediction (scikit-learn implementation)

#### Clustering & Classification
- **DBSCAN (Density-Based Spatial Clustering)**: Spatial clustering algorithm
- **K-Means**: Unsupervised clustering for land use patterns
- **XGBoost**: Gradient boosting for pollution classification

#### Ensemble Methods
- **Random Forest**: Ensemble learning for soil moisture prediction

### Development & Deployment

#### Version Control
- **Git**: Distributed version control system

#### Environment Management
- **Python venv**: Virtual environment for Python dependencies
- **npm**: Package manager for JavaScript

#### Build Tools
- **Create React App**: Build setup for React applications
- **pip**: Package installer for Python

### Infrastructure & Performance

#### Data Storage
- **NumPy Compressed Arrays (.npz)**: Efficient numerical data storage
- **JSON Metadata**: Structured metadata storage
- **File-based Caching**: Local data caching system
- **Geospatial Data Formats**: GeoJSON and shapefile support

#### Asynchronous Processing
- **Async/Await**: Python async programming
- **Concurrent Processing**: Parallel data processing pipelines

#### API Design
- **RESTful APIs**: Representational State Transfer architecture
- **OpenAPI/Swagger**: API documentation and testing
- **CORS (Cross-Origin Resource Sharing)**: Cross-domain request handling

## �🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/aetrix.git
   cd aetrix
   ```

2. **Backend Setup**
   ```bash
   cd backend

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Optional: Set up API keys for live data
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. **Start Backend**
   ```bash
   cd backend
   python main.py
   ```
   Server starts at `http://localhost:8000` with API docs at `/docs`

2. **Start Frontend**
   ```bash
   cd frontend
   npm start
   ```
   App opens at `http://localhost:3000`

### Demo Mode

The application runs in demo mode by default using sample data, requiring no API keys for initial exploration.

## � Deployment

### Prerequisites for Deployment

- Docker and Docker Compose
- PostgreSQL with PostGIS (or use Docker)
- Node.js 16+ (for building frontend)
- Python 3.8+ (for backend)

### Local Deployment with Docker

1. **Clone and navigate to the project**
   ```bash
   git clone https://github.com/your-org/Satintel.git
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and run with Docker Compose**
   ```bash
   # Build the services
   docker-compose build

   # Start all services
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

### Production Deployment

#### Option 1: Docker Compose (Recommended)

Create a `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: aetrix
      POSTGRES_USER: aetrix_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://aetrix_user:your_password@db:5432/aetrix
      - USE_SAMPLE_DATA=true
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"

volumes:
  postgres_data:
```

#### Option 2: Cloud Deployment (Azure)

1. **Azure Container Registry**
   ```bash
   # Build and push images
   az acr build --registry myregistry --image backend:latest ./backend
   az acr build --registry myregistry --image frontend:latest ./frontend
   ```

2. **Azure Database for PostgreSQL**
   ```bash
   az postgres flexible-server create \
     --name aetrix-db \
     --resource-group myResourceGroup \
     --location eastus \
     --admin-user aetrixadmin \
     --admin-password myPassword \
     --sku-name Standard_B1ms \
     --tier Burstable \
     --public-access 0.0.0.0
   ```

3. **Azure Container Apps**
   ```bash
   # Deploy backend
   az containerapp create \
     --name aetrix-backend \
     --resource-group myResourceGroup \
     --environment myEnvironment \
     --image myregistry.azurecr.io/backend:latest \
     --target-port 8000 \
     --ingress external

   # Deploy frontend
   az containerapp create \
     --name aetrix-frontend \
     --resource-group myResourceGroup \
     --environment myEnvironment \
     --image myregistry.azurecr.io/frontend:latest \
     --target-port 80 \
     --ingress external
   ```

#### Option 3: Heroku Deployment

1. **Backend Deployment**
   ```bash
   # Create Heroku app
   heroku create aetrix-backend

   # Set environment variables
   heroku config:set DATABASE_URL=your_postgres_url
   heroku config:set USE_SAMPLE_DATA=true

   # Deploy
   git push heroku main
   ```

2. **Frontend Deployment**
   ```bash
   # Build the app
   cd frontend
   npm run build

   # Deploy to Netlify, Vercel, or similar
   # For static hosting
   ```

### Dockerfiles

#### Backend Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
FROM node:16-alpine as build

WORKDIR /app

COPY package*.json .
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Environment Configuration

Create a `.env` file with:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aetrix

# API Keys (optional for demo mode)
GOOGLE_EARTH_ENGINE_PROJECT=your-gee-project
NASA_CMR_TOKEN=your-nasa-token
SENTINEL_HUB_CLIENT_ID=your-sentinel-id
SENTINEL_HUB_CLIENT_SECRET=your-sentinel-secret

# Application Settings
USE_SAMPLE_DATA=true
DEMO_CITY=Ahmedabad
```

### Monitoring and Scaling

- **Health Checks**: Backend includes `/health` endpoint
- **Logging**: Structured logging with JSON format
- **Metrics**: Prometheus-compatible metrics (optional)
- **Scaling**: Horizontal scaling with load balancer

## �📊 Data Sources & Parameters

### Satellite Data Sources

| Source | Parameters | Resolution | Temporal Coverage |
|--------|------------|------------|-------------------|
| **Google Earth Engine** | NDVI, Temperature | 500m-1km | 2000-Present |
| **NASA CMR** | Soil Moisture | 25km | 2015-Present |
| **Copernicus Sentinel** | Pollution (NO₂, CO) | 10km | 2018-Present |
| **Sample Data** | All parameters | 500m | 52 weeks |

### Environmental Parameters

- **NDVI (Normalized Difference Vegetation Index)**: Vegetation health and density
- **Temperature**: Land surface temperature in °C
- **Pollution**: Air quality indicators (NO₂, CO levels)
- **Soil Moisture**: Soil water content percentage

### Supported Cities

- Ahmedabad (Demo City)
- Delhi
- Bengaluru
- Mumbai
- Chennai

## 🤖 Machine Learning Models

### Model Architecture

| Parameter | Model Type | Purpose | Algorithm |
|-----------|------------|---------|-----------|
| **Temperature** | Time Series | Trend prediction | LSTM + ARIMA |
| **Soil Moisture** | Regression | Spatial prediction | Random Forest + ARIMA |
| **Pollution** | Classification | Hotspot detection | XGBoost + DBSCAN |
| **Land Use** | Clustering | Pattern recognition | K-Means |

### ML Features

#### Anomaly Detection
- **Algorithm**: Isolation Forest
- **Purpose**: Identify unusual environmental conditions
- **Output**: Anomaly scores and spatial locations

#### Hotspot Clustering
- **Algorithm**: DBSCAN
- **Purpose**: Group high-concentration pollution areas
- **Output**: Cluster centroids and boundaries

#### Trend Prediction
- **Algorithm**: ARIMA (AutoRegressive Integrated Moving Average)
- **Purpose**: Forecast future environmental trends
- **Output**: 12-week predictions with confidence intervals

#### Action Plan Generation
- **Method**: Rule-based expert system with ML scoring
- **Purpose**: Convert insights into municipal recommendations
- **Output**: Prioritized action items with severity levels

## 🔌 API Reference

### Core Endpoints

#### Data Retrieval
```http
GET /api/cities
GET /api/available-layers
GET /api/grid-data?parameter=temperature&week=51&city=Ahmedabad
GET /api/get-data?lat=23.0225&lon=72.5714&parameter=temperature
GET /api/time-series?lat=23.0225&lon=72.5714&parameter=temperature
```

#### ML Analytics
```http
GET /api/get-hotspots?parameter=pollution&week=51
GET /api/get-anomalies?parameter=temperature&week=51
GET /api/predict-trend?lat=23.0225&lon=72.5714&parameter=temperature&weeks=12
```

#### Action Planning
```http
GET /api/action-plan?city=Ahmedabad&severity=high
```

### API Documentation

Complete API documentation is available at `http://localhost:8000/docs` when the backend is running.

## 🎨 Frontend Components

### Main Components

- **MapView**: Interactive Leaflet map with heat layers
- **LayerControl**: Parameter and visualization controls
- **TimeSlider**: Temporal navigation through 52-week data
- **Dashboard**: Key metrics and charts
- **ActionPlan**: Municipal recommendations display
- **Prediction**: Future trend forecasting interface

### Visualization Features

- **Heat Maps**: Color-coded environmental data overlay
- **Hotspot Markers**: DBSCAN cluster visualization
- **Time Series Charts**: Historical trend analysis
- **Prediction Graphs**: Forecast visualization with uncertainty
- **Interactive Popups**: Point-specific data inspection

## 🛠️ Development

### Project Structure

```
Satintel/
├── backend/
│   ├── api/                 # FastAPI route handlers
│   │   ├── data_routes.py   # Data retrieval endpoints
│   │   ├── ml_routes.py     # ML analytics endpoints
│   │   ├── action_routes.py # Action plan endpoints
│   │   └── predict_routes.py# Prediction endpoints
│   ├── data/
│   │   ├── raw/            # Raw satellite data
│   │   └── processed/      # Processed datasets
│   ├── ingestion/          # Data fetchers
│   │   ├── gee_fetcher.py  # Google Earth Engine
│   │   ├── nasa_fetcher.py # NASA data
│   │   └── sentinel_fetcher.py # Copernicus
│   ├── ml/                 # Machine learning models
│   │   ├── model_*.py      # Individual model trainers
│   │   ├── hotspots.py     # Hotspot detection
│   │   ├── anomaly.py      # Anomaly detection
│   │   └── action_plan.py  # Recommendation engine
│   ├── pipeline/           # ETL pipeline
│   │   ├── processor.py    # Pipeline orchestrator
│   │   ├── harmonizer.py   # Data harmonization
│   │   └── storage.py      # Data persistence
│   ├── config.py           # Configuration
│   └── main.py             # Application entry point
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   └── utils/          # Constants and helpers
│   ├── public/             # Static assets
│   └── package.json        # Dependencies
└── README.md
```

### Training ML Models

```bash
cd backend
python -m ml.train_all
```

This trains all models sequentially and saves them to `models/saved/`.

### Adding New Cities

1. Add city coordinates to `config.py`
2. Run pipeline: `GET /api/load-city?city=NewCity`
3. Models will be applied automatically

### Data Processing Pipeline

The ETL pipeline runs automatically on startup:

1. **Extract**: Fetch from APIs or generate sample data
2. **Transform**: Harmonize CRS, resample, clean outliers
3. **Load**: Save as compressed NumPy arrays with metadata

## 📈 Performance & Scalability

### Data Optimization

- **Compression**: NumPy arrays stored in compressed NPZ format
- **Caching**: Intelligent caching of processed datasets
- **Spatial Indexing**: Efficient spatial queries on grid data
- **Memory Management**: Lazy loading of large datasets

### API Performance

- **Async Processing**: FastAPI async endpoints
- **Data Chunking**: Large responses streamed in chunks
- **Caching**: Redis-compatible caching layer (configurable)
- **Rate Limiting**: Built-in rate limiting for public endpoints

## 🔒 Security & Privacy

### API Key Management

- Environment-based configuration
- Service account authentication for GEE
- Token-based API access (configurable)
- No sensitive data in client-side code

### Data Privacy

- Satellite data is publicly available
- No personal user data collected
- Local processing and storage
- GDPR/CCPA compliant architecture

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Set up development environment
4. Make changes and add tests
5. Submit a pull request

### Code Standards

- **Backend**: PEP 8, type hints, comprehensive docstrings
- **Frontend**: ESLint, Prettier, React best practices
- **Testing**: pytest for backend, Jest for frontend
- **Documentation**: Sphinx for API docs, JSDoc for components

### Areas for Contribution

- **New Data Sources**: Integration with additional satellite APIs
- **ML Model Improvements**: Enhanced algorithms and accuracy
- **UI/UX Enhancements**: Better visualization and user experience
- **Performance Optimization**: Faster data processing and rendering
- **Mobile Support**: Responsive design for mobile devices

### Acknowledgments

- **Google Earth Engine** for satellite data access
- **NASA** for earth observation data
- **Copernicus Programme** for Sentinel data
- **OpenStreetMap** contributors for base maps
- **CartoDB** for dark theme tiles


**Demo City**: Ahmedabad, India — Showcasing urban heat islands, monsoon NDVI patterns, and industrial pollution hotspots.
