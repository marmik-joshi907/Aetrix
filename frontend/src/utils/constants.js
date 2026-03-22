// API base URL
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Available cities
export const CITIES = [
  { name: 'Ahmedabad', lat: 23.0225, lon: 72.5714 },
  { name: 'Delhi', lat: 28.6139, lon: 77.2090 },
  { name: 'Bengaluru', lat: 12.9716, lon: 77.5946 },
  { name: 'Mumbai', lat: 19.0760, lon: 72.8777 },
  { name: 'Chennai', lat: 13.0827, lon: 80.2707 },
];

// Layer configuration
export const LAYERS = {
  temperature: {
    name: 'Temperature',
    unit: '°C',
    icon: '🌡️',
    gradient: 'linear-gradient(90deg, #3b82f6, #eab308, #ef4444)',
    colors: ['#3b82f6', '#22c55e', '#eab308', '#f97316', '#ef4444'],
    range: [25, 50],
    description: 'Land Surface Temperature',
  },
  ndvi: {
    name: 'NDVI',
    unit: 'index',
    icon: '🌿',
    gradient: 'linear-gradient(90deg, #92400e, #eab308, #22c55e, #065f46)',
    colors: ['#92400e', '#eab308', '#22c55e', '#065f46'],
    range: [0, 1],
    description: 'Vegetation Health Index',
  },
  pollution: {
    name: 'Pollution',
    unit: 'AQI',
    icon: '🏭',
    gradient: 'linear-gradient(90deg, #22c55e, #eab308, #ef4444, #7f1d1d)',
    colors: ['#22c55e', '#eab308', '#f97316', '#ef4444', '#7f1d1d'],
    range: [0, 300],
    description: 'Air Quality Index',
  },
  soil_moisture: {
    name: 'Soil Moisture',
    unit: 'm³/m³',
    icon: '💧',
    gradient: 'linear-gradient(90deg, #92400e, #eab308, #06b6d4, #1e40af)',
    colors: ['#92400e', '#eab308', '#06b6d4', '#1e40af'],
    range: [0.05, 0.55],
    description: 'Volumetric Soil Moisture',
  },
};

// Color utilities
export function getValueColor(value, parameter) {
  const layer = LAYERS[parameter];
  if (!layer) return '#94a3b8';
  
  const [min, max] = layer.range;
  const t = Math.max(0, Math.min(1, (value - min) / (max - min)));
  const colors = layer.colors;
  
  const idx = t * (colors.length - 1);
  const lower = Math.floor(idx);
  const upper = Math.min(lower + 1, colors.length - 1);
  const frac = idx - lower;
  
  return interpolateColor(colors[lower], colors[upper], frac);
}

function interpolateColor(hex1, hex2, t) {
  const r1 = parseInt(hex1.slice(1, 3), 16);
  const g1 = parseInt(hex1.slice(3, 5), 16);
  const b1 = parseInt(hex1.slice(5, 7), 16);
  const r2 = parseInt(hex2.slice(1, 3), 16);
  const g2 = parseInt(hex2.slice(3, 5), 16);
  const b2 = parseInt(hex2.slice(5, 7), 16);
  
  const r = Math.round(r1 + (r2 - r1) * t);
  const g = Math.round(g1 + (g2 - g1) * t);
  const b = Math.round(b1 + (b2 - b1) * t);
  
  return `rgb(${r},${g},${b})`;
}

// Heatmap intensity based on parameter
export function getHeatIntensity(value, parameter) {
  const layer = LAYERS[parameter];
  if (!layer) return 0.5;
  const [min, max] = layer.range;
  // For NDVI and soil_moisture, invert — low values are concerning
  if (parameter === 'ndvi' || parameter === 'soil_moisture') {
    return 1 - Math.max(0, Math.min(1, (value - min) / (max - min)));
  }
  return Math.max(0, Math.min(1, (value - min) / (max - min)));
}

export { API_BASE };
