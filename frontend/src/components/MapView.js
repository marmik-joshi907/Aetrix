import React, { useEffect, useRef, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { getValueColor, getHeatIntensity } from '../utils/constants';

// Fix default markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

export default function MapView({ gridData, hotspots, activeLayer, city, selectedPoint, clickedSpotData, onMapClick }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const heatLayerRef = useRef(null);
  const hotspotsLayerRef = useRef(null);
  const gridLayerRef = useRef(null);
  const selectedMarkerRef = useRef(null);

  // Initialize map
  useEffect(() => {
    if (mapInstance.current) return;
    
    mapInstance.current = L.map(mapRef.current, {
      center: [city?.lat || 23.0225, city?.lon || 72.5714],
      zoom: 12,
      zoomControl: true,
      attributionControl: false,
    });

    // Dark tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
    }).addTo(mapInstance.current);

    // Attribution
    L.control.attribution({ position: 'bottomright' })
      .addAttribution('© CartoDB © OpenStreetMap')
      .addTo(mapInstance.current);

    // Click handler
    mapInstance.current.on('click', (e) => {
      if (onMapClick) onMapClick(e.latlng.lat, e.latlng.lng);
    });

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, []);

  // Update center when city changes
  useEffect(() => {
    if (mapInstance.current && city) {
      mapInstance.current.setView([city.lat, city.lon], 12, { animate: true });
    }
  }, [city]);

  // Render selected point marker
  useEffect(() => {
    if (!mapInstance.current) return;

    if (selectedMarkerRef.current) {
      mapInstance.current.removeLayer(selectedMarkerRef.current);
    }

    if (selectedPoint) {
      selectedMarkerRef.current = L.circleMarker(selectedPoint, {
        radius: 8,
        fillColor: '#ffffff',
        fillOpacity: 1,
        color: '#f59e0b',
        weight: 3,
        opacity: 1,
      });

      let popupContent = `
        <div style="text-align:center; min-width: 140px;">
          <div style="font-size:13px;font-weight:700;color:#f59e0b">Selected Spot</div>
          <div style="font-size:10px;color:#94a3b8;margin-bottom:8px">${selectedPoint[0].toFixed(4)}, ${selectedPoint[1].toFixed(4)}</div>
      `;

      if (clickedSpotData) {
        popupContent += `
          <div style="text-align: left; background: rgba(0,0,0,0.2); padding: 6px; border-radius: 6px;">
            <div style="font-size:11px; margin-bottom: 2px;">🌡️ Temp: <span style="font-weight:600; color:#ef4444">${clickedSpotData.temperature}°C</span></div>
            <div style="font-size:11px; margin-bottom: 2px;">💨 AQI: <span style="font-weight:600; color:#eab308">Class ${clickedSpotData.pollution_aqi}</span></div>
            <div style="font-size:11px; margin-bottom: 2px;">💧 Soil: <span style="font-weight:600; color:#3b82f6">${typeof clickedSpotData.soil_moisture === 'number' ? clickedSpotData.soil_moisture.toFixed(1) + '%' : clickedSpotData.soil_moisture}</span></div>
            <div style="font-size:11px;">🌱 Veg: <span style="font-weight:600; color:#10b981">${clickedSpotData.vegetation_risk} Risk</span></div>
          </div>
        `;
      } else {
        popupContent += `<div style="font-size:11px;color:#94a3b8">Fetching parameters...</div>`;
      }

      popupContent += `</div>`;

      selectedMarkerRef.current.bindPopup(popupContent);
      selectedMarkerRef.current.addTo(mapInstance.current);
      selectedMarkerRef.current.openPopup();
    }
  }, [selectedPoint, clickedSpotData]);

  // Render grid data as colored circles
  const renderGrid = useCallback(() => {
    if (!mapInstance.current) return;

    // Clear previous grid
    if (gridLayerRef.current) {
      mapInstance.current.removeLayer(gridLayerRef.current);
    }

    if (!gridData || !gridData.points || gridData.points.length === 0) return;

    const circles = [];
    const parameter = gridData.parameter;

    gridData.points.forEach(([lat, lon, value]) => {
      const color = getValueColor(value, parameter);
      const intensity = getHeatIntensity(value, parameter);
      
      const circle = L.circleMarker([lat, lon], {
        radius: 6,
        fillColor: color,
        fillOpacity: 0.35 + intensity * 0.45,
        color: color,
        weight: 0.5,
        opacity: 0.5,
      });

      circle.bindPopup(`
        <div style="text-align:center">
          <div style="font-size:10px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.05em">${parameter}</div>
          <div style="font-size:20px;font-weight:800;color:${color};margin:4px 0">${value.toFixed(2)}</div>
          <div style="font-size:10px;color:#64748b">${gridData.unit || ''}</div>
          <div style="font-size:10px;color:#64748b;margin-top:4px">${lat.toFixed(4)}, ${lon.toFixed(4)}</div>
        </div>
      `);

      circles.push(circle);
    });

    gridLayerRef.current = L.layerGroup(circles);
    gridLayerRef.current.addTo(mapInstance.current);
  }, [gridData]);

  useEffect(() => {
    renderGrid();
  }, [renderGrid]);

  // Render hotspot clusters
  useEffect(() => {
    if (!mapInstance.current) return;

    if (hotspotsLayerRef.current) {
      mapInstance.current.removeLayer(hotspotsLayerRef.current);
    }

    if (!hotspots || !hotspots.clusters || hotspots.clusters.length === 0) return;

    const markers = [];
    hotspots.clusters.forEach((cluster) => {
      const color = cluster.level === 'critical' ? '#ef4444' :
                    cluster.level === 'high' ? '#f97316' :
                    cluster.level === 'moderate' ? '#eab308' : '#22c55e';

      const sizeBase = 12;
      const sizeScale = Math.min(cluster.size / 10, 3);
      const radius = sizeBase + sizeScale * 6;

      const marker = L.circleMarker([cluster.centroid_lat, cluster.centroid_lon], {
        radius: radius,
        fillColor: color,
        fillOpacity: 0.4,
        color: color,
        weight: 2,
        opacity: 0.8,
        className: 'hotspot-marker',
      });

      marker.bindPopup(`
        <div style="min-width:160px">
          <div style="font-size:12px;font-weight:700;margin-bottom:6px;color:${color}">
            ${hotspots.hotspot_type || 'Hotspot'}
          </div>
          <div style="font-size:11px;color:#94a3b8;margin-bottom:2px">
            Severity: <span style="color:${color};font-weight:600">${cluster.level.toUpperCase()}</span>
          </div>
          <div style="font-size:11px;color:#94a3b8;margin-bottom:2px">
            Size: ${cluster.size} cells
          </div>
          <div style="font-size:11px;color:#94a3b8;margin-bottom:2px">
            Mean: ${cluster.mean_value.toFixed(2)} ${gridData?.unit || ''}
          </div>
          <div style="font-size:10px;color:#64748b;margin-top:4px">
            ${cluster.centroid_lat.toFixed(4)}, ${cluster.centroid_lon.toFixed(4)}
          </div>
        </div>
      `);

      markers.push(marker);
    });

    hotspotsLayerRef.current = L.layerGroup(markers);
    hotspotsLayerRef.current.addTo(mapInstance.current);
  }, [hotspots, gridData]);

  useEffect(() => {
    renderGrid();
  }, [renderGrid]);

  return <div ref={mapRef} style={{ width: '100%', height: '100%' }} />;
}
