import axios from 'axios';
import { API_BASE } from '../utils/constants';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

// Data endpoints
export const getCities = () => api.get('/api/cities');
export const getAvailableLayers = () => api.get('/api/available-layers');
export const getData = (lat, lon, parameter, week = -1, city = null) =>
  api.get('/api/get-data', { params: { lat, lon, parameter, week, city } });
export const getGridData = (parameter, week = -1, city = null, downsample = 2) =>
  api.get('/api/grid-data', { params: { parameter, week, city, downsample } });
export const getTimeSeries = (lat, lon, parameter, city = null) =>
  api.get('/api/time-series', { params: { lat, lon, parameter, city } });
export const getWeekCount = (city = null) =>
  api.get('/api/week-count', { params: { city } });

// ML endpoints
export const getHotspots = (parameter = null, week = -1, city = null) =>
  api.get('/api/get-hotspots', { params: { parameter, week, city } });
export const getAnomalies = (parameter = null, week = -1, city = null) =>
  api.get('/api/get-anomalies', { params: { parameter, week, city } });
export const predictTrend = (lat, lon, parameter, forecastWeeks = 4, city = null) =>
  api.get('/api/predict-trend', { params: { lat, lon, parameter, forecast_weeks: forecastWeeks, city } });

// New specific ML prediction endpoints
export const predictTemperature = (yearsAhead = 5) =>
  api.post('/api/predict/temperature', { years_ahead: yearsAhead });

export const predictSoil = (district, smLevel, smAggPct, smVolPct, dayOfYear, week, month) =>
  api.post('/api/predict/soil', {
    district,
    sm_level: smLevel,
    sm_agg_pct: smAggPct,
    sm_vol_pct: smVolPct,
    day_of_year: dayOfYear,
    week,
    month
  });

export const predictPollution = (state, lat, lon, pollutants) =>
  api.post('/api/predict/pollution', {
    state,
    latitude: lat,
    longitude: lon,
    ...pollutants
  });

export const predictLanduse = (lat, lon, pm25, no2) =>
  api.post('/api/predict/landuse', {
    latitude: lat,
    longitude: lon,
    pm25,
    no2
  });

// Action endpoints
export const getActionPlan = (city = null, week = -1) =>
  api.get('/api/action-plan', { params: { city, week } });

// New Feature endpoints
export const getExplanation = (lat, lon, week = -1, city = null) =>
  api.get('/api/explain', { params: { lat, lon, week, city } });

export const getCrowdDetection = (city = null, week = -1) =>
  api.get('/api/crowd-detection', { params: { city, week } });

export const getTimelineWarnings = (city = null, week = -1, lookback = 4) =>
  api.get('/api/timeline-warnings', { params: { city, week, lookback } });

export const getEarlyWarnings = (city = null, week = -1, forecastDays = 10) =>
  api.get('/api/early-warnings', { params: { city, week, forecast_days: forecastDays } });

export const getMunicipalDashboard = (city = null, week = -1) =>
  api.get('/api/municipal-dashboard', { params: { city, week } });

// City loading
export const loadCity = (city) => api.get('/api/load-city', { params: { city } });

// RAG Chatbot
export const sendChatMessage = (message, city = null, week = -1) =>
  api.post('/api/chat', { message, city, week });

export default api;
