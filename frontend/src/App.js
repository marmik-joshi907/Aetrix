import React, { useState, useEffect, useCallback } from 'react';
import MapView from './components/MapView';
import LayerControl from './components/LayerControl';
import TimeSlider from './components/TimeSlider';
import Dashboard from './components/Dashboard';
import ActionPlan from './components/ActionPlan';
import CitySelector from './components/CitySelector';
import Prediction from './components/Prediction';
import { 
  getGridData, getHotspots, predictTrend, getActionPlan, loadCity, getWeekCount,
  predictTemperature, predictSoil, predictPollution, predictLanduse
} from './services/api';
import { CITIES, LAYERS } from './utils/constants';

export default function App() {
  // State
  const [currentCity, setCurrentCity] = useState('Ahmedabad');
  const [activeLayer, setActiveLayer] = useState('temperature');
  const [currentWeek, setCurrentWeek] = useState(51);
  const [totalWeeks, setTotalWeeks] = useState(52);
  const [timestamps, setTimestamps] = useState([]);
  const [selectedPoint, setSelectedPoint] = useState(null);
  
  // Data
  const [gridData, setGridData] = useState(null);
  const [hotspots, setHotspots] = useState(null);
  const [trendData, setTrendData] = useState(null);
  const [mlPrediction, setMlPrediction] = useState(null);
  const [actionPlan, setActionPlan] = useState(null);
  
  // UI
  const [activeTab, setActiveTab] = useState('layers');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const cityObj = CITIES.find(c => c.name === currentCity) || CITIES[0];

  // Fetch grid data
  const fetchGridData = useCallback(async () => {
    try {
      const res = await getGridData(activeLayer, currentWeek, currentCity, 2);
      setGridData(res.data);
      if (res.data.timestamp) {
        // Store for display
      }
    } catch (err) {
      console.error('Grid data error:', err);
    }
  }, [activeLayer, currentWeek, currentCity]);

  // Fetch hotspots
  const fetchHotspots = useCallback(async () => {
    try {
      const res = await getHotspots(activeLayer, currentWeek, currentCity);
      const results = res.data.results || {};
      setHotspots(results[activeLayer] || null);
    } catch (err) {
      console.error('Hotspots error:', err);
    }
  }, [activeLayer, currentWeek, currentCity]);

  // Fetch generic trend (kept for Dashboard)
  const fetchTrend = useCallback(async () => {
    try {
      const res = await predictTrend(cityObj.lat, cityObj.lon, activeLayer, 4, currentCity);
      setTrendData(res.data);
    } catch (err) {
      console.error('Trend error:', err);
    }
  }, [activeLayer, currentCity, cityObj]);

  // Fetch Specific ML Prediction
  const fetchMLPrediction = async (lat, lon, layer) => {
    setMlPrediction(null); // loading state
    try {
      let res;
      if (layer === 'temperature') {
        res = await predictTemperature(5); // 5 years ahead
      } else if (layer === 'soil_moisture') {
        // We use dummy/approx values for the point, normally extracted from grid
        res = await predictSoil(currentCity, 0.8, 6.0, 12.0, 180, 26, 6);
      } else if (layer === 'pollution') {
        res = await predictPollution(currentCity, lat, lon, { PM25: 65, NO2: 30 }); // dummy current pollutants
      } else if (layer === 'ndvi') {
        // Land use proxy
        res = await predictLanduse(lat, lon, 65, 30);
      }
      if (res && res.data) {
        setMlPrediction(res.data);
      }
    } catch (err) {
      console.error('ML Prediction error:', err);
    }
  };

  // Fetch action plan
  const fetchActionPlan = useCallback(async () => {
    try {
      const res = await getActionPlan(currentCity, currentWeek);
      setActionPlan(res.data);
    } catch (err) {
      console.error('Action plan error:', err);
    }
  }, [currentCity, currentWeek]);

  // Fetch week count
  const fetchWeekCount = useCallback(async () => {
    try {
      const res = await getWeekCount(currentCity);
      setTotalWeeks(res.data.weeks || 52);
    } catch (err) {
      console.error('Week count error:', err);
    }
  }, [currentCity]);

  // Initial load
  useEffect(() => {
    const init = async () => {
      setLoading(true);
      setError(null);
      try {
        await fetchWeekCount();
        await fetchGridData();
        await Promise.all([fetchHotspots(), fetchTrend(), fetchActionPlan()]);
        await fetchMLPrediction(cityObj.lat, cityObj.lon, activeLayer);
      } catch (err) {
        setError('Failed to connect to backend. Make sure the server is running on port 8000.');
      }
      setLoading(false);
    };
    init();
  }, [currentCity]);

  // Reload on layer or week change
  useEffect(() => {
    if (!loading) {
      fetchGridData();
      fetchHotspots();
    }
  }, [activeLayer, currentWeek]);

  // Reload trend when layer changes
  useEffect(() => {
    if (!loading) {
      fetchTrend();
      const lat = selectedPoint ? selectedPoint[0] : cityObj.lat;
      const lon = selectedPoint ? selectedPoint[1] : cityObj.lon;
      fetchMLPrediction(lat, lon, activeLayer);
    }
  }, [activeLayer]);

  // City change
  const handleCityChange = async (cityName) => {
    setLoading(true);
    setCurrentCity(cityName);
    try {
      await loadCity(cityName);
    } catch (err) {
      // City might already be loaded
    }
  };

  const [clickedSpotData, setClickedSpotData] = useState(null);

  // Map click
  const handleMapClick = async (lat, lon) => {
    setSelectedPoint([lat, lon]);
    setActiveTab('prediction');
    setClickedSpotData(null); // Reset for loading
    try {
      // Fetch generic trend for the chart (if needed)
      const res = await predictTrend(lat, lon, activeLayer, 4, currentCity);
      setTrendData(res.data);
      // Fetch specific ML prediction for UI
      await fetchMLPrediction(lat, lon, activeLayer);

      // Fetch snapshot data for the Popup (using predict endpoints as a fast proxy for current params)
      const [tRes, sRes, pRes, lRes] = await Promise.all([
        predictTemperature(1).catch(() => null),
        predictSoil(currentCity, 0.8, 6.0, 12.0, 180, 26, 6).catch(() => null),
        predictPollution(currentCity, lat, lon, { PM25: 65, NO2: 30 }).catch(() => null),
        predictLanduse(lat, lon, 65, 30).catch(() => null)
      ]);

      setClickedSpotData({
        temperature: tRes?.data?.predictions?.[0]?.predicted_annual || 'N/A',
        soil_moisture: sRes?.data?.result?.forecast_7d_sm_pct?.[0] || 'N/A',
        pollution_aqi: pRes?.data?.result?.aqi_category || 'N/A',
        vegetation_risk: lRes?.data?.result?.change_risk_label || 'N/A',
      });

    } catch (err) {
      console.error('Map click trend error:', err);
    }
  };

  // Week change via slider
  const handleWeekChange = (val) => {
    if (typeof val === 'function') {
      setCurrentWeek(prev => {
        const next = val(prev);
        return next;
      });
    } else {
      setCurrentWeek(val);
    }
  };

  return (
    <div className="app-container">
      {/* Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner" />
          <div className="loading-text">
            Initializing satellite data pipeline...
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
            Processing {currentCity} environmental data
          </div>
        </div>
      )}

      {/* Sidebar */}
      <div className="sidebar">
        {/* Header */}
        <div className="sidebar-header">
          <span className="sidebar-logo">🛰️</span>
          <div>
            <div className="sidebar-title">SatIntel</div>
            <div className="sidebar-subtitle">Environmental Intelligence</div>
          </div>
        </div>

        {/* City Selector */}
        <CitySelector
          currentCity={currentCity}
          onCityChange={handleCityChange}
          loading={loading}
        />

        {/* Navigation Tabs */}
        <div className="nav-tabs">
          <button
            className={`nav-tab ${activeTab === 'layers' ? 'active' : ''}`}
            onClick={() => setActiveTab('layers')}
          >
            Layers
          </button>
          <button
            className={`nav-tab ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            Analytics
          </button>
          <button
            className={`nav-tab ${activeTab === 'actions' ? 'active' : ''}`}
            onClick={() => setActiveTab('actions')}
          >
            Actions
          </button>
          <button
            className={`nav-tab ${activeTab === 'prediction' ? 'active' : ''}`}
            onClick={() => setActiveTab('prediction')}
          >
            Prediction
          </button>
        </div>

        {/* Sidebar Content */}
        <div className="sidebar-content">
          {/* Time Slider (always visible) */}
          <TimeSlider
            totalWeeks={totalWeeks}
            currentWeek={currentWeek}
            timestamps={timestamps}
            onChange={handleWeekChange}
          />

          {/* Tab Content */}
          {activeTab === 'layers' && (
            <LayerControl
              activeLayer={activeLayer}
              onLayerChange={setActiveLayer}
            />
          )}

          {activeTab === 'analytics' && (
            <Dashboard
              gridData={gridData}
              trendData={trendData}
              mlPrediction={mlPrediction}
              activeLayer={activeLayer}
            />
          )}

          {activeTab === 'actions' && (
            <ActionPlan plan={actionPlan} />
          )}

          {activeTab === 'prediction' && (
            <Prediction
              trendData={trendData}
              mlPrediction={mlPrediction}
              activeLayer={activeLayer}
              selectedPoint={selectedPoint}
            />
          )}
        </div>
      </div>

      {/* Map */}
      <div className="map-container">
        <MapView
          gridData={gridData}
          hotspots={hotspots}
          activeLayer={activeLayer}
          city={cityObj}
          selectedPoint={selectedPoint}
          clickedSpotData={clickedSpotData}
          onMapClick={handleMapClick}
        />

        {/* Map Info Overlay */}
        {gridData && (
          <div className="map-info-overlay">
            <div className="map-info-title">
              {LAYERS[activeLayer]?.icon} {LAYERS[activeLayer]?.name}
            </div>
            <div className="map-info-value" style={{
              color: activeLayer === 'temperature' ? 'var(--accent-rose)' :
                     activeLayer === 'ndvi' ? 'var(--accent-emerald)' :
                     activeLayer === 'pollution' ? 'var(--accent-amber)' :
                     'var(--accent-cyan)'
            }}>
              {gridData.stats?.mean?.toFixed(1)} {gridData.unit}
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
              {gridData.city} · {gridData.timestamp}
            </div>
            
            {/* Map Legend Overlay */}
            <div style={{ marginTop: 12 }}>
              <div style={{ fontSize: 9, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>
                Map Legend
              </div>
              <div className="color-legend">
                <span className="legend-label">{LAYERS[activeLayer]?.range[0]}</span>
                <div
                  className="legend-gradient"
                  style={{ background: LAYERS[activeLayer]?.gradient }}
                />
                <span className="legend-label" style={{ textAlign: 'right' }}>
                  {LAYERS[activeLayer]?.range[1]}
                </span>
              </div>
            </div>

          </div>
        )}

        {/* Error Overlay */}
        {error && !loading && (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 900,
            background: 'var(--bg-glass)',
            backdropFilter: 'blur(16px)',
            border: '1px solid var(--accent-rose)',
            borderRadius: 'var(--radius-lg)',
            padding: '24px 32px',
            textAlign: 'center',
            maxWidth: 400,
          }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>⚠️</div>
            <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>
              Connection Error
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
              {error}
            </div>
            <button
              onClick={() => window.location.reload()}
              style={{
                marginTop: 16,
                padding: '8px 20px',
                background: 'var(--accent-emerald)',
                border: 'none',
                borderRadius: 8,
                color: 'white',
                fontWeight: 600,
                cursor: 'pointer',
                fontFamily: 'inherit',
              }}
            >
              Retry
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
