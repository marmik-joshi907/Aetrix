import React, { useEffect, useState, useCallback } from 'react';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, Title, Tooltip, Legend, Filler, ArcElement
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { getGridData } from '../services/api';
import { LAYERS, CITIES } from '../utils/constants';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, Title, Tooltip, Legend, Filler, ArcElement
);

// Fix leaflet icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

function MapResizer() {
  const map = useMap();
  useEffect(() => {
    const timer = setTimeout(() => map.invalidateSize(), 200);
    return () => clearTimeout(timer);
  }, [map]);
  return null;
}

const PARAM_COLORS = {
  temperature: { main: '#ef4444', bg: 'rgba(239,68,68,0.15)', border: 'rgba(239,68,68,0.4)' },
  ndvi: { main: '#10b981', bg: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.4)' },
  pollution: { main: '#f59e0b', bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.4)' },
  soil_moisture: { main: '#3b82f6', bg: 'rgba(59,130,246,0.15)', border: 'rgba(59,130,246,0.4)' },
};

const PARAM_LABELS = {
  temperature: 'Temperature',
  ndvi: 'NDVI',
  pollution: 'Pollution (AQI)',
  soil_moisture: 'Soil Moisture',
};

export default function AnalyticsView({ city = 'Ahmedabad', week = -1 }) {
  const [allData, setAllData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const cityObj = CITIES.find(c => c.name === city) || CITIES[0];

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = ['temperature', 'ndvi', 'pollution', 'soil_moisture'];
      const responses = await Promise.all(
        params.map(p => getGridData(p, week, city, 2).catch(() => null))
      );
      const data = {};
      params.forEach((p, i) => {
        if (responses[i]?.data) {
          data[p] = responses[i].data;
        }
      });
      setAllData(data);
    } catch (err) {
      console.error('Analytics data load error:', err);
      setError('Failed to load data. Make sure the backend is running on port 8000.');
    }
    setLoading(false);
  }, [city, week]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const params = Object.keys(allData);
  const hasData = params.length > 0;

  // Comparison bar chart
  const comparisonChart = hasData ? {
    labels: params.map(p => PARAM_LABELS[p] || p),
    datasets: [
      {
        label: 'Mean Value',
        data: params.map(p => allData[p]?.stats?.mean ?? 0),
        backgroundColor: params.map(p => PARAM_COLORS[p]?.bg || 'rgba(148,163,184,0.2)'),
        borderColor: params.map(p => PARAM_COLORS[p]?.main || '#94a3b8'),
        borderWidth: 2,
        borderRadius: 8,
      },
    ],
  } : null;

  // Distribution doughnut for each parameter
  const getDistChartData = (param) => {
    const d = allData[param];
    if (!d?.stats) return null;
    const { min, max, mean } = d.stats;
    const range = max - min || 1;
    const lowPct = ((mean - min) / range * 100).toFixed(0);
    const highPct = ((max - mean) / range * 100).toFixed(0);
    return {
      labels: ['Below Mean', 'Above Mean'],
      datasets: [{
        data: [lowPct, highPct],
        backgroundColor: [PARAM_COLORS[param]?.bg, PARAM_COLORS[param]?.border],
        borderColor: ['transparent', 'transparent'],
        borderWidth: 0,
      }],
    };
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(10,15,30,0.95)',
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        borderColor: 'rgba(148,163,184,0.12)',
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12,
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(148,163,184,0.06)' },
        ticks: { color: '#64748b', font: { size: 10 } },
      },
      y: {
        grid: { display: false },
        ticks: { color: '#e2e8f0', font: { size: 11, weight: 600 } },
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '70%',
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(10,15,30,0.95)',
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        cornerRadius: 8,
        padding: 10,
      },
    },
  };

  // Overview map points — top 100 from each parameter
  const mapPoints = [];
  params.forEach(p => {
    const pts = allData[p]?.points || [];
    pts.slice(0, 80).forEach(([lat, lon, val]) => {
      mapPoints.push({ lat, lon, val, param: p });
    });
  });

  return (
    <div className="analytics-view">
      {/* Header */}
      <div className="analytics-header">
        <div className="analytics-header-left">
          <span className="analytics-icon">📊</span>
          <div>
            <div className="analytics-title">Environmental Analytics</div>
            <div className="analytics-subtitle">{city} · Week {week === -1 ? 'Latest' : week}</div>
          </div>
        </div>
        <button className="analytics-refresh-btn" onClick={fetchAll} disabled={loading}>
          {loading ? '⏳' : '🔄'} Refresh
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="analytics-loading">
          <div className="loading-spinner" />
          <div style={{ marginTop: 12, fontSize: 13 }}>Loading environmental data...</div>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="analytics-error">
          <div style={{ fontSize: 32, marginBottom: 8 }}>⚠️</div>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Data Load Error</div>
          <div style={{ color: '#94a3b8', fontSize: 12 }}>{error}</div>
          <button className="analytics-refresh-btn" onClick={fetchAll} style={{ marginTop: 12 }}>
            🔄 Retry
          </button>
        </div>
      )}

      {/* Main Content */}
      {!loading && hasData && (
        <>
          {/* Stats Cards Row */}
          <div className="analytics-cards-row">
            {params.map(p => {
              const d = allData[p];
              const stats = d?.stats || {};
              const layer = LAYERS[p] || {};
              const colors = PARAM_COLORS[p] || {};
              return (
                <div
                  key={p}
                  className="analytics-stat-card"
                  style={{ borderColor: colors.border }}
                >
                  <div className="analytics-stat-icon">{layer.icon || '📌'}</div>
                  <div className="analytics-stat-name">{layer.name || p}</div>
                  <div className="analytics-stat-value" style={{ color: colors.main }}>
                    {stats.mean?.toFixed(1) ?? '—'}
                    <span className="analytics-stat-unit"> {d?.unit || ''}</span>
                  </div>
                  <div className="analytics-stat-range">
                    <span>Min: {stats.min?.toFixed(1) ?? '—'}</span>
                    <span>Max: {stats.max?.toFixed(1) ?? '—'}</span>
                  </div>
                  <div className="analytics-stat-bar">
                    <div
                      className="analytics-stat-bar-fill"
                      style={{
                        width: `${Math.min(100, ((stats.mean - stats.min) / ((stats.max - stats.min) || 1)) * 100)}%`,
                        background: `linear-gradient(90deg, ${colors.bg}, ${colors.main})`,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Charts Row */}
          <div className="analytics-charts-row">
            {/* Comparison Bar Chart */}
            <div className="analytics-chart-card analytics-chart-wide">
              <div className="analytics-chart-title">📊 Parameter Comparison — Mean Values</div>
              <div className="analytics-chart-body">
                {comparisonChart && <Bar data={comparisonChart} options={barOptions} />}
              </div>
            </div>

            {/* Distribution Doughnuts */}
            <div className="analytics-chart-card analytics-chart-narrow">
              <div className="analytics-chart-title">🎯 Value Distribution</div>
              <div className="analytics-doughnut-grid">
                {params.map(p => {
                  const dData = getDistChartData(p);
                  if (!dData) return null;
                  return (
                    <div key={p} className="analytics-doughnut-item">
                      <div style={{ width: 80, height: 80 }}>
                        <Doughnut data={dData} options={doughnutOptions} />
                      </div>
                      <div className="analytics-doughnut-label" style={{ color: PARAM_COLORS[p]?.main }}>
                        {PARAM_LABELS[p]}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Overview Map */}
          <div className="analytics-chart-card analytics-map-card">
            <div className="analytics-chart-title">🗺️ Multi-Parameter Overview Map</div>
            <div className="analytics-map-wrapper">
              <MapContainer
                center={[cityObj.lat, cityObj.lon]}
                zoom={11}
                scrollWheelZoom={true}
                style={{ height: '100%', width: '100%', borderRadius: 12 }}
                attributionControl={false}
              >
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                  maxZoom={19}
                />
                <MapResizer />
                {mapPoints.map((pt, i) => (
                  <CircleMarker
                    key={i}
                    center={[pt.lat, pt.lon]}
                    radius={4}
                    pathOptions={{
                      fillColor: PARAM_COLORS[pt.param]?.main || '#94a3b8',
                      fillOpacity: 0.6,
                      color: 'transparent',
                      weight: 0,
                    }}
                  >
                    <Popup>
                      <div style={{ fontSize: 11, textAlign: 'center' }}>
                        <strong style={{ color: PARAM_COLORS[pt.param]?.main }}>
                          {LAYERS[pt.param]?.icon} {PARAM_LABELS[pt.param]}
                        </strong>
                        <br />
                        Value: {pt.val?.toFixed(2)}
                        <br />
                        <span style={{ color: '#64748b' }}>
                          {pt.lat.toFixed(4)}, {pt.lon.toFixed(4)}
                        </span>
                      </div>
                    </Popup>
                  </CircleMarker>
                ))}
              </MapContainer>
              {/* Map Legend */}
              <div className="analytics-map-legend">
                {params.map(p => (
                  <div key={p} className="analytics-map-legend-item">
                    <span
                      className="analytics-map-legend-dot"
                      style={{ background: PARAM_COLORS[p]?.main }}
                    />
                    {LAYERS[p]?.name || p}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {/* No Data */}
      {!loading && !hasData && !error && (
        <div className="analytics-empty">
          <div style={{ fontSize: 48, marginBottom: 12 }}>🛰️</div>
          <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 6 }}>No Data Available</div>
          <div style={{ fontSize: 12, color: '#94a3b8' }}>
            Connect the backend to see environmental analytics.
          </div>
        </div>
      )}
    </div>
  );
}
