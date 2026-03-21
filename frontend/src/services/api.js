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

// Action endpoints
export const getActionPlan = (city = null, week = -1) =>
  api.get('/api/action-plan', { params: { city, week } });

// City loading
export const loadCity = (city) => api.get('/api/load-city', { params: { city } });

export default api;
