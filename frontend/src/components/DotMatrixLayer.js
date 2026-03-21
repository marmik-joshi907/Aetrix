import React, { useMemo } from 'react';
import { CircleMarker, Popup } from 'react-leaflet';
import { getValueColor, LAYERS } from '../utils/constants';

/**
 * DotMatrixLayer – renders a city-specific grid of colored dots on the map.
 * Each dot's colour maps to the parameter value at that grid cell.
 *
 * Props:
 *   points     – Array of [lat, lon, value] from gridData.points
 *   parameter  – active layer key (temperature | ndvi | pollution | soil_moisture)
 *   stats      – { min, max, mean } from gridData.stats
 *   unit       – unit string from gridData.unit
 *   onDotClick – optional callback(lat, lon) — wired to handleMapClick in App
 */
export default function DotMatrixLayer({ points, parameter, stats, unit, onDotClick }) {
  // Pre-compute coloured dots from grid data
  const dots = useMemo(() => {
    if (!points || points.length === 0) return [];

    return points.map(([lat, lon, value]) => ({
      lat,
      lon,
      value,
      color: getValueColor(value, parameter),
    }));
  }, [points, parameter]);

  if (dots.length === 0) return null;

  const layerInfo = LAYERS[parameter] || {};

  return (
    <>
      {dots.map((dot, i) => (
        <CircleMarker
          key={`dm-${i}`}
          center={[dot.lat, dot.lon]}
          radius={5}
          pathOptions={{
            fillColor: dot.color,
            fillOpacity: 0.85,
            color: dot.color,
            weight: 0.5,
            opacity: 0.6,
          }}
          eventHandlers={{
            click: (e) => {
              // Prevent the map click from also firing
              e.originalEvent?.stopPropagation?.();
              if (onDotClick) {
                onDotClick(dot.lat, dot.lon);
              }
            },
          }}
        >
          <Popup>
            <div style={{ minWidth: 170, fontFamily: "'Inter', sans-serif" }}>
              <div style={{
                fontSize: 13,
                fontWeight: 700,
                color: '#f59e0b',
                marginBottom: 6,
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}>
                📍 Grid Point
              </div>

              <div style={{
                fontSize: 10,
                color: '#64748b',
                marginBottom: 10,
              }}>
                {dot.lat.toFixed(4)}, {dot.lon.toFixed(4)}
              </div>

              <div style={{
                background: 'rgba(0,0,0,0.25)',
                padding: 10,
                borderRadius: 8,
              }}>
                {/* Parameter + Value */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 6,
                }}>
                  <span style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
                    Parameter
                  </span>
                  <span style={{ fontSize: 11, fontWeight: 700, color: '#f1f5f9' }}>
                    {layerInfo.icon} {layerInfo.name || parameter}
                  </span>
                </div>

                {/* Value */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 6,
                }}>
                  <span style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
                    Value
                  </span>
                  <span style={{
                    fontSize: 13,
                    fontWeight: 800,
                    color: dot.color,
                  }}>
                    {dot.value.toFixed(2)} <span style={{ fontSize: 10, fontWeight: 400, opacity: 0.7 }}>{unit || ''}</span>
                  </span>
                </div>

                {/* Range context */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontSize: 10,
                  color: '#64748b',
                }}>
                  <span>Range: {stats?.min?.toFixed(1)} – {stats?.max?.toFixed(1)}</span>
                </div>
              </div>
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </>
  );
}
