import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { LAYERS } from '../utils/constants';
import HeatmapLayer from './HeatmapLayer';
import HotspotLayer from './HotspotLayer';
import AnomalyLayer from './AnomalyLayer';
import DotMatrixLayer from './DotMatrixLayer';
import MapClickHandler from './MapClickHandler';

// Fix default marker icons (webpack issue)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Component to update map center when city changes
function MapCenterUpdater({ city }) {
  const map = useMap();
  useEffect(() => {
    if (city) {
      map.setView([city.lat, city.lon], 12, { animate: true });
    }
  }, [city, map]);
  return null;
}

// Component to invalidate size when map becomes visible
function MapResizer() {
  const map = useMap();
  useEffect(() => {
    setTimeout(() => map.invalidateSize(), 100);
  }, [map]);
  return null;
}

export default function MapView({
  gridData,
  hotspots,
  anomalyData,
  activeLayer,
  city,
  selectedPoint,
  clickedSpotData,
  onMapClick,
  showHeatmap = true,
  showHotspots = true,
  showAnomalies = false,
  showDotMatrix = true,
  trendData,
}) {
  const center = [city?.lat || 23.0225, city?.lon || 72.5714];

  return (
    <MapContainer
      center={center}
      zoom={12}
      scrollWheelZoom={true}
      style={{ height: '100%', width: '100%' }}
      zoomControl={true}
      attributionControl={false}
    >
      {/* Dark CartoDB Tiles */}
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        maxZoom={19}
        attribution='&copy; <a href="https://carto.com/">CartoDB</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />

      {/* Auto-update center on city change */}
      <MapCenterUpdater city={city} />

      {/* Invalidate size fix */}
      <MapResizer />

      {/* Click Handler */}
      <MapClickHandler onMapClick={onMapClick} />

      {/* Heatmap Overlay */}
      {showHeatmap && gridData?.points && (
        <HeatmapLayer
          points={gridData.points}
          stats={gridData.stats}
          parameter={activeLayer}
        />
      )}

      {/* Dot Matrix Grid */}
      {showDotMatrix && gridData?.points && (
        <DotMatrixLayer
          points={gridData.points}
          parameter={activeLayer}
          stats={gridData.stats}
          unit={gridData.unit}
          onDotClick={onMapClick}
        />
      )}

      {/* Hotspot Markers */}
      {showHotspots && hotspots && (
        <HotspotLayer
          hotspots={hotspots}
          unit={gridData?.unit}
        />
      )}

      {/* Anomaly Markers */}
      {showAnomalies && anomalyData && (
        <AnomalyLayer
          anomalyData={anomalyData}
          parameter={activeLayer}
        />
      )}

      {/* Selected Point Marker */}
      {selectedPoint && (
        <>
          {/* Outer pulsing ring */}
          <CircleMarker
            center={selectedPoint}
            radius={18}
            pathOptions={{
              fillColor: 'transparent',
              fillOpacity: 0,
              color: '#f59e0b',
              weight: 2,
              opacity: 0.5,
              dashArray: '4 4',
            }}
            className="selected-point-pulse"
          />
          {/* Inner solid marker */}
          <CircleMarker
            center={selectedPoint}
            radius={8}
            pathOptions={{
              fillColor: '#fbbf24',
              fillOpacity: 1,
              color: '#f59e0b',
              weight: 3,
              opacity: 1,
            }}
          >
            <Popup>
              <div style={{ minWidth: 200, fontFamily: "'Inter', sans-serif" }}>
                <div style={{ fontSize: 14, fontWeight: 700, color: '#f59e0b', marginBottom: 2 }}>
                  Selected Spot
                </div>
                <div style={{ fontSize: 10, color: '#64748b', marginBottom: 10 }}>
                  {selectedPoint[0].toFixed(4)}, {selectedPoint[1].toFixed(4)}
                </div>

                <div style={{ background: 'rgba(0,0,0,0.25)', padding: 10, borderRadius: 8 }}>
                  {/* Parameter row */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: 11 }}>
                    <span style={{ color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase', fontSize: 10 }}>Parameter</span>
                    <span style={{ fontWeight: 700, color: '#f1f5f9' }}>
                      {LAYERS[activeLayer]?.name?.toUpperCase() || activeLayer.toUpperCase()}
                    </span>
                  </div>

                  {/* Trend row */}
                  {trendData?.trend && (
                    <>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: 11 }}>
                        <span style={{ color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase', fontSize: 10 }}>Trend</span>
                        <span style={{
                          fontWeight: 700,
                          color: trendData.trend.direction === 'increasing' ? '#ef4444' :
                                 trendData.trend.direction === 'decreasing' ? '#10b981' : '#eab308',
                        }}>
                          {trendData.trend.direction?.toUpperCase() || 'STABLE'}
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: 11 }}>
                        <span style={{ color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase', fontSize: 10 }}>Change</span>
                        <span style={{ fontWeight: 700, color: '#f1f5f9' }}>
                          {trendData.trend.change_percent?.toFixed(1) ?? '—'}%
                        </span>
                      </div>
                    </>
                  )}

                  {/* Model row */}
                  {trendData?.model && (
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10 }}>
                      <span style={{ color: '#64748b' }}>Model</span>
                      <span style={{ color: '#64748b', fontWeight: 500 }}>{trendData.model}</span>
                    </div>
                  )}

                  {/* Parameter values */}
                  {clickedSpotData && (
                    <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid rgba(148,163,184,0.15)' }}>
                      <div style={{ fontSize: 11, marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
                        <span>🌡️ Temp</span>
                        <span style={{ fontWeight: 600, color: '#ef4444' }}>{clickedSpotData.temperature}</span>
                      </div>
                      <div style={{ fontSize: 11, marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
                        <span>💨 AQI</span>
                        <span style={{ fontWeight: 600, color: '#eab308' }}>{clickedSpotData.pollution_aqi}</span>
                      </div>
                      <div style={{ fontSize: 11, marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
                        <span>💧 Soil</span>
                        <span style={{ fontWeight: 600, color: '#3b82f6' }}>{clickedSpotData.soil_moisture}</span>
                      </div>
                      <div style={{ fontSize: 11, display: 'flex', justifyContent: 'space-between' }}>
                        <span>🌿 NDVI</span>
                        <span style={{ fontWeight: 600, color: '#10b981' }}>{clickedSpotData.vegetation}</span>
                      </div>
                    </div>
                  )}

                  {!clickedSpotData && (
                    <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 8, textAlign: 'center' }}>Fetching parameters...</div>
                  )}
                </div>
              </div>
            </Popup>
          </CircleMarker>
        </>
      )}
    </MapContainer>
  );
}
