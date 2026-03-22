import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

const GRADIENTS = {
  temperature: { 0.2: '#313695', 0.5: '#74add1', 0.8: '#fdae61', 1.0: '#d73027' },
  ndvi:        { 0.0: '#d73027', 0.4: '#fee08b', 0.7: '#a6d96a', 1.0: '#1a9641' },
  pollution:   { 0.2: '#ffffcc', 0.5: '#fd8d3c', 0.8: '#e31a1c', 1.0: '#800026' },
  soil_moisture: { 0.2: '#f7fbff', 0.5: '#6baed6', 0.8: '#2171b5', 1.0: '#08306b' },
};

export default function HeatmapLayer({ points, stats, parameter, radius = 20, blur = 15, maxZoom = 17 }) {
  const map = useMap();
  const heatRef = useRef(null);

  useEffect(() => {
    if (!points || points.length === 0) return;

    // Remove previous heat layer
    if (heatRef.current) {
      map.removeLayer(heatRef.current);
    }

    const range = (stats?.max ?? 1) - (stats?.min ?? 0) + 0.001;
    const normalized = points.map(([lat, lng, val]) => [
      lat, lng,
      (val - (stats?.min ?? 0)) / range
    ]);

    const gradient = GRADIENTS[parameter] || GRADIENTS.temperature;

    heatRef.current = L.heatLayer(normalized, {
      radius,
      blur,
      maxZoom,
      gradient,
    }).addTo(map);

    return () => {
      if (heatRef.current) {
        map.removeLayer(heatRef.current);
        heatRef.current = null;
      }
    };
  }, [map, points, stats, parameter, radius, blur, maxZoom]);

  return null;
}
