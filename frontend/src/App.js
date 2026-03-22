import React, { useState, useEffect, useCallback } from 'react';
import MapView from './components/MapView';
import AnalyticsView from './components/KeplerMapView';
import LayerControl from './components/LayerControl';
import TimeSlider from './components/TimeSlider';
import Dashboard from './components/Dashboard';
import ActionPlan from './components/ActionPlan';
import CitySelector from './components/CitySelector';
import Prediction from './components/Prediction';
import ExplainPanel from './components/ExplainPanel';
import CrowdDetection from './components/CrowdDetection';
import TimelineWarnings from './components/TimelineWarnings';
import EarlyWarnings from './components/EarlyWarnings';
import MunicipalDashboard from './components/MunicipalDashboard';
import { 
  getGridData, getHotspots, getAnomalies, predictTrend, getActionPlan, loadCity, getWeekCount,
  predictTemperature, predictSoil, predictPollution, predictLanduse, getData,
  getExplanation, getCrowdDetection, getTimelineWarnings, getEarlyWarnings, getMunicipalDashboard
} from './services/api';
import { CITIES, LAYERS } from './utils/constants';

export default function App() {
  // === Top-level view ===
  const [activeView, setActiveView] = useState('map'); // 'map' | 'analytics'

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
  const [anomalyData, setAnomalyData] = useState(null);
  const [trendData, setTrendData] = useState(null);
  const [mlPrediction, setMlPrediction] = useState(null);
  const [actionPlan, setActionPlan] = useState(null);
  
  // New feature data
  const [explanationData, setExplanationData] = useState(null);
  const [crowdData, setCrowdData] = useState(null);
  const [crowdLoading, setCrowdLoading] = useState(false);
  const [timelineWarningData, setTimelineWarningData] = useState(null);
  const [earlyWarningData, setEarlyWarningData] = useState(null);
  const [earlyWarningLoading, setEarlyWarningLoading] = useState(false);
  const [municipalData, setMunicipalData] = useState(null);
  const [municipalLoading, setMunicipalLoading] = useState(false);

  // UI
  const [activeTab, setActiveTab] = useState('layers');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pointLoading, setPointLoading] = useState(false);

  // Layer visibility toggles
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showHotspots, setShowHotspots] = useState(true);
  const [showAnomalies, setShowAnomalies] = useState(false);
  const [showDotMatrix, setShowDotMatrix] = useState(true);

  const cityObj = CITIES.find(c => c.name === currentCity) || CITIES[0];

  // Fetch grid data
  const fetchGridData = useCallback(async () => {
    try {
      const res = await getGridData(activeLayer, currentWeek, currentCity, 2);
      setGridData(res.data);
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

  // Fetch anomalies
  const fetchAnomalies = useCallback(async () => {
    try {
      const res = await getAnomalies(activeLayer, currentWeek, currentCity);
      const results = res.data.results || {};
      setAnomalyData(results[activeLayer] || null);
    } catch (err) {
      console.error('Anomalies error:', err);
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
    setMlPrediction(null);
    try {
      let res;
      if (layer === 'temperature') {
        res = await predictTemperature(5);
      } else if (layer === 'soil_moisture') {
        res = await predictSoil(currentCity, 0.8, 6.0, 12.0, 180, 26, 6);
      } else if (layer === 'pollution') {
        res = await predictPollution(currentCity, lat, lon, { PM25: 65, NO2: 30 });
      } else if (layer === 'ndvi') {
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

  // === New Feature Fetchers ===

  // Fetch explanation for a point
  const fetchExplanation = async (lat, lon) => {
    try {
      const res = await getExplanation(lat, lon, currentWeek, currentCity);
      setExplanationData(res.data);
    } catch (err) {
      console.error('Explanation error:', err);
      setExplanationData(null);
    }
  };

  // Fetch crowd detection data
  const fetchCrowdDetection = useCallback(async () => {
    setCrowdLoading(true);
    try {
      const res = await getCrowdDetection(currentCity, currentWeek);
      setCrowdData(res.data);
    } catch (err) {
      console.error('Crowd detection error:', err);
      setCrowdData(null);
    } finally {
      setCrowdLoading(false);
    }
  }, [currentCity, currentWeek]);

  // Fetch timeline warnings
  const fetchTimelineWarnings = useCallback(async () => {
    try {
      const res = await getTimelineWarnings(currentCity, currentWeek);
      setTimelineWarningData(res.data);
    } catch (err) {
      console.error('Timeline warnings error:', err);
      setTimelineWarningData(null);
    }
  }, [currentCity, currentWeek]);

  // Fetch early warnings
  const fetchEarlyWarnings = useCallback(async () => {
    setEarlyWarningLoading(true);
    try {
      const res = await getEarlyWarnings(currentCity, currentWeek);
      setEarlyWarningData(res.data);
    } catch (err) {
      console.error('Early warnings error:', err);
      setEarlyWarningData(null);
    } finally {
      setEarlyWarningLoading(false);
    }
  }, [currentCity, currentWeek]);

  // Fetch municipal dashboard
  const fetchMunicipalDashboard = useCallback(async () => {
    setMunicipalLoading(true);
    try {
      const res = await getMunicipalDashboard(currentCity, currentWeek);
      setMunicipalData(res.data);
    } catch (err) {
      console.error('Municipal dashboard error:', err);
      setMunicipalData(null);
    } finally {
      setMunicipalLoading(false);
    }
  }, [currentCity, currentWeek]);

  // Initial load
  useEffect(() => {
    const init = async () => {
      setLoading(true);
      setError(null);
      setSelectedPoint(null);
      setClickedSpotData(null);
      setMlPrediction(null);
      setExplanationData(null);
      try {
        await fetchWeekCount();
        await fetchGridData();
        await Promise.all([
          fetchHotspots(), fetchAnomalies(), fetchTrend(), fetchActionPlan(),
          fetchTimelineWarnings(), fetchEarlyWarnings(),
        ]);
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
      if (showAnomalies) fetchAnomalies();
    }
  }, [activeLayer, currentWeek]);

  // Reload anomalies when toggle is turned on
  useEffect(() => {
    if (showAnomalies && !anomalyData && !loading) {
      fetchAnomalies();
    }
  }, [showAnomalies]);

  // Reload trend and ML prediction when layer changes
  useEffect(() => {
    if (!loading) {
      fetchTrend();
      if (selectedPoint) {
        fetchMLPrediction(selectedPoint[0], selectedPoint[1], activeLayer);
      }
    }
  }, [activeLayer]);

  // Re-fetch point data when week changes and a point is selected
  useEffect(() => {
    if (!loading && selectedPoint) {
      handleMapClick(selectedPoint[0], selectedPoint[1]);
    }
  }, [currentWeek]);

  // Fetch crowd detection when tab is selected
  useEffect(() => {
    if (activeTab === 'crowd' && !crowdData && !crowdLoading) {
      fetchCrowdDetection();
    }
  }, [activeTab]);

  // Fetch municipal data when view is selected
  useEffect(() => {
    if (activeView === 'municipal' && !municipalData && !municipalLoading) {
      fetchMunicipalDashboard();
    }
  }, [activeView]);

  // City change
  const handleCityChange = async (cityName) => {
    setLoading(true);
    setCurrentCity(cityName);
    setCrowdData(null);
    setMunicipalData(null);
    setEarlyWarningData(null);
    setTimelineWarningData(null);
    try {
      await loadCity(cityName);
    } catch (err) {
      // City might already be loaded
    }
  };

  const [clickedSpotData, setClickedSpotData] = useState(null);

  // Helper to safely extract a value from an API response
  const safeValue = (res) => {
    try {
      if (res && res.data && res.data.value != null && !isNaN(res.data.value)) {
        return res.data.value;
      }
    } catch { /* ignore */ }
    return null;
  };

  // Map click — fetch point-specific analysis
  const handleMapClick = async (lat, lon) => {
    setSelectedPoint([lat, lon]);
    setActiveTab('prediction');
    setClickedSpotData(null);
    setPointLoading(true);
    setExplanationData(null);

    try {
      // 1. Fetch all 4 parameter values at clicked point using getData API
      const paramFetches = ['temperature', 'ndvi', 'pollution', 'soil_moisture'].map(param =>
        getData(lat, lon, param, currentWeek, currentCity).catch(() => null)
      );
      const [tempData, ndviData, pollData, soilData] = await Promise.all(paramFetches);

      const tempVal = safeValue(tempData);
      const ndviVal = safeValue(ndviData);
      const pollVal = safeValue(pollData);
      const soilVal = safeValue(soilData);

      // Build popup data from point-level values
      setClickedSpotData({
        temperature: tempVal != null ? `${tempVal.toFixed(1)}°C` : 'N/A',
        soil_moisture: soilVal != null ? `${(soilVal * 100).toFixed(1)}%` : 'N/A',
        pollution_aqi: pollVal != null ? pollVal.toFixed(0) : 'N/A',
        vegetation: ndviVal != null ? ndviVal.toFixed(3) : 'N/A',
      });

      // 2. Fetch trend for clicked point
      const trendRes = await predictTrend(lat, lon, activeLayer, 4, currentCity).catch(() => null);
      if (trendRes?.data) {
        setTrendData(trendRes.data);
      }

      // 3. Fetch ML prediction for active layer
      await fetchMLPrediction(lat, lon, activeLayer);

      // 4. Fetch explanation (new feature)
      fetchExplanation(lat, lon);

    } catch (err) {
      console.error('Map click error:', err);
      // Still show fallback values so the UI isn't stuck
      setClickedSpotData({
        temperature: 'N/A',
        soil_moisture: 'N/A',
        pollution_aqi: 'N/A',
        vegetation: 'N/A',
      });
    } finally {
      setPointLoading(false);
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

  // Count active early warnings for badge
  const earlyWarningCount = earlyWarningData?.alert_count || 0;

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

      {/* ═══ Top-Level View Switcher ═══ */}
      <div className="view-switcher">
        <button
          className={`view-tab ${activeView === 'map' ? 'active' : ''}`}
          onClick={() => setActiveView('map')}
        >
          <span className="view-tab-icon">🗺️</span>
          Map View
        </button>
        <button
          className={`view-tab ${activeView === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveView('analytics')}
        >
          <span className="view-tab-icon">📊</span>
          Analytics
        </button>
        <button
          className={`view-tab ${activeView === 'municipal' ? 'active' : ''}`}
          onClick={() => setActiveView('municipal')}
        >
          <span className="view-tab-icon">🏛️</span>
          Municipal
        </button>
      </div>

      {/* ═══ MAP VIEW ═══ */}
      {activeView === 'map' && (
        <>
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
              <button
                className={`nav-tab ${activeTab === 'warnings' ? 'active' : ''}`}
                onClick={() => setActiveTab('warnings')}
                style={{ position: 'relative' }}
              >
                Warnings
                {earlyWarningCount > 0 && (
                  <span className="warning-badge-count">{earlyWarningCount}</span>
                )}
              </button>
              <button
                className={`nav-tab ${activeTab === 'crowd' ? 'active' : ''}`}
                onClick={() => setActiveTab('crowd')}
              >
                Crowd
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

              {/* Layer Visibility Toggles */}
              <div className="layer-visibility-panel">
                <div className="card-title" style={{ fontSize: 10, marginBottom: 8 }}>
                  🔲 Map Overlays
                </div>
                <div className="layer-toggle-row" onClick={() => setShowHeatmap(!showHeatmap)}>
                  <button className={`layer-toggle ${showHeatmap ? 'on' : 'off'}`} />
                  <span className="layer-toggle-label">Heatmap</span>
                </div>
                <div className="layer-toggle-row" onClick={() => setShowHotspots(!showHotspots)}>
                  <button className={`layer-toggle ${showHotspots ? 'on' : 'off'}`} />
                  <span className="layer-toggle-label">Hotspots</span>
                </div>
                <div className="layer-toggle-row" onClick={() => setShowAnomalies(!showAnomalies)}>
                  <button className={`layer-toggle ${showAnomalies ? 'on' : 'off'}`} />
                  <span className="layer-toggle-label">Anomalies</span>
                </div>
                <div className="layer-toggle-row" onClick={() => setShowDotMatrix(!showDotMatrix)}>
                  <button className={`layer-toggle ${showDotMatrix ? 'on' : 'off'}`} />
                  <span className="layer-toggle-label">Dot Matrix</span>
                </div>
              </div>

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
                <>
                  <Prediction
                    trendData={trendData}
                    mlPrediction={mlPrediction}
                    activeLayer={activeLayer}
                    selectedPoint={selectedPoint}
                    pointLoading={pointLoading}
                    clickedSpotData={clickedSpotData}
                  />
                  <ExplainPanel explanationData={explanationData} />
                  <TimelineWarnings warningData={timelineWarningData} />
                </>
              )}

              {activeTab === 'warnings' && (
                <EarlyWarnings
                  warningData={earlyWarningData}
                  loading={earlyWarningLoading}
                />
              )}

              {activeTab === 'crowd' && (
                <CrowdDetection
                  crowdData={crowdData}
                  loading={crowdLoading}
                />
              )}
            </div>
          </div>

          {/* Map */}
          <div className="map-container">
            <MapView
              gridData={gridData}
              hotspots={hotspots}
              anomalyData={anomalyData}
              activeLayer={activeLayer}
              city={cityObj}
              selectedPoint={selectedPoint}
              clickedSpotData={clickedSpotData}
              onMapClick={handleMapClick}
              showHeatmap={showHeatmap}
              showHotspots={showHotspots}
              showAnomalies={showAnomalies}
              showDotMatrix={showDotMatrix}
              trendData={trendData}
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

            {/* Click Hint */}
            {!selectedPoint && !loading && (
              <div className="map-click-hint">
                <span>📍</span> Click anywhere on the map for point analysis
              </div>
            )}

            {/* Point Loading Indicator */}
            {pointLoading && (
              <div className="map-point-loading">
                <div className="loading-spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
                <span>Analyzing point...</span>
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
        </>
      )}

      {/* ═══ ANALYTICS VIEW ═══ */}
      {activeView === 'analytics' && (
        <div className="analytics-container">
          <AnalyticsView
            city={currentCity}
            week={currentWeek}
          />
        </div>
      )}

      {/* ═══ MUNICIPAL VIEW ═══ */}
      {activeView === 'municipal' && (
        <div className="municipal-container">
          <MunicipalDashboard
            dashboardData={municipalData}
            loading={municipalLoading}
          />
        </div>
      )}

    </div>
  );
}
