import React from 'react';
import { CircleMarker, Popup } from 'react-leaflet';

export default function AnomalyLayer({ anomalyData, parameter }) {
  if (!anomalyData?.spatial?.anomaly_points || anomalyData.spatial.anomaly_points.length === 0) {
    return null;
  }

  return (
    <>
      {anomalyData.spatial.anomaly_points.map(([lat, lon, score], i) => (
        <CircleMarker
          key={`anomaly-${i}`}
          center={[lat, lon]}
          radius={6}
          pathOptions={{
            color: '#ff9900',
            fillColor: '#ffcc00',
            fillOpacity: 0.8,
            weight: 2,
            opacity: 0.9,
          }}
        >
          <Popup>
            <div style={{ minWidth: 120, textAlign: 'center' }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: '#ff9900', marginBottom: 4 }}>
                ⚠️ Spatial Anomaly
              </div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 2 }}>
                Score: <span style={{ fontWeight: 600, color: '#ffcc00' }}>{score.toFixed(3)}</span>
              </div>
              <div style={{ fontSize: 10, color: '#64748b' }}>
                {lat.toFixed(4)}, {lon.toFixed(4)}
              </div>
              <div style={{ fontSize: 10, color: '#64748b', marginTop: 2, textTransform: 'capitalize' }}>
                {parameter}
              </div>
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </>
  );
}
