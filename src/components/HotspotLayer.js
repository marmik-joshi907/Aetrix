import React from 'react';
import { CircleMarker, Popup } from 'react-leaflet';

export default function HotspotLayer({ hotspots, unit }) {
  if (!hotspots || !hotspots.clusters || hotspots.clusters.length === 0) {
    return null;
  }

  return (
    <>
      {hotspots.clusters.map((cluster, i) => {
        const color = cluster.level === 'critical' ? '#ef4444' :
                      cluster.level === 'high' ? '#f97316' :
                      cluster.level === 'moderate' ? '#eab308' : '#22c55e';

        const sizeBase = 12;
        const sizeScale = Math.min(cluster.size / 10, 3);
        const radius = sizeBase + sizeScale * 6;

        return (
          <CircleMarker
            key={`hotspot-${i}`}
            center={[cluster.centroid_lat, cluster.centroid_lon]}
            radius={radius}
            pathOptions={{
              fillColor: color,
              fillOpacity: 0.4,
              color: color,
              weight: 2,
              opacity: 0.8,
            }}
            className="hotspot-marker"
          >
            <Popup>
              <div style={{ minWidth: 160 }}>
                <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 6, color }}>
                  {hotspots.hotspot_type || 'Hotspot'}
                </div>
                <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 2 }}>
                  Severity: <span style={{ color, fontWeight: 600 }}>{cluster.level.toUpperCase()}</span>
                </div>
                <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 2 }}>
                  Size: {cluster.size} cells
                </div>
                <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 2 }}>
                  Mean: {cluster.mean_value.toFixed(2)} {unit || ''}
                </div>
                <div style={{ fontSize: 10, color: '#64748b', marginTop: 4 }}>
                  {cluster.centroid_lat.toFixed(4)}, {cluster.centroid_lon.toFixed(4)}
                </div>
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
    </>
  );
}
