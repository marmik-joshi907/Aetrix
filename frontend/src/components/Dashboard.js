import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler);

export default function Dashboard({ gridData, trendData, activeLayer }) {
  // Stats
  const stats = gridData?.stats || {};
  const unit = gridData?.unit || '';

  // Trend chart data
  const chartData = trendData ? {
    labels: [
      ...(trendData.timestamps || trendData.historical?.map((_, i) => `W${i+1}`) || []).slice(-20),
      ...Array(trendData.forecast?.length || 0).fill(0).map((_, i) => `F${i+1}`),
    ],
    datasets: [
      {
        label: 'Historical',
        data: (trendData.historical || []).slice(-20),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        borderWidth: 2,
      },
      {
        label: 'Forecast',
        data: [
          ...Array((trendData.historical || []).slice(-20).length - 1).fill(null),
          (trendData.historical || []).slice(-1)[0],
          ...(trendData.forecast || []),
        ],
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: true,
        tension: 0.4,
        borderDash: [5, 5],
        pointRadius: 0,
        borderWidth: 2,
      },
    ],
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        borderColor: 'rgba(148, 163, 184, 0.12)',
        borderWidth: 1,
        cornerRadius: 8,
        padding: 10,
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(148, 163, 184, 0.06)' },
        ticks: { color: '#64748b', font: { size: 9 }, maxTicksLimit: 8 },
      },
      y: {
        grid: { color: 'rgba(148, 163, 184, 0.06)' },
        ticks: { color: '#64748b', font: { size: 9 } },
      },
    },
  };

  const trendDirection = trendData?.trend?.direction;
  const trendArrow = trendDirection === 'increasing' ? '↗' :
                     trendDirection === 'decreasing' ? '↘' : '→';
  const trendColor = trendDirection === 'increasing' 
    ? (activeLayer === 'ndvi' || activeLayer === 'soil_moisture' ? '#ef4444' : '#ef4444')
    : trendDirection === 'decreasing'
    ? (activeLayer === 'ndvi' || activeLayer === 'soil_moisture' ? '#ef4444' : '#22c55e')
    : '#eab308';

  return (
    <div>
      {/* Stats Grid */}
      <div className="stats-grid">
        <div className={`stat-card ${activeLayer === 'temperature' ? 'temperature' : activeLayer === 'ndvi' ? 'ndvi' : activeLayer === 'pollution' ? 'pollution' : 'moisture'}`}>
          <div className="stat-value">
            {stats.mean?.toFixed(1) ?? '—'}
            <span className="stat-unit"> {unit}</span>
          </div>
          <div className="stat-label">Mean</div>
        </div>
        <div className={`stat-card ${activeLayer === 'temperature' ? 'temperature' : activeLayer === 'ndvi' ? 'ndvi' : activeLayer === 'pollution' ? 'pollution' : 'moisture'}`}>
          <div className="stat-value">
            {stats.max?.toFixed(1) ?? '—'}
            <span className="stat-unit"> {unit}</span>
          </div>
          <div className="stat-label">Max</div>
        </div>
        <div className={`stat-card ${activeLayer === 'temperature' ? 'temperature' : activeLayer === 'ndvi' ? 'ndvi' : activeLayer === 'pollution' ? 'pollution' : 'moisture'}`}>
          <div className="stat-value">
            {stats.min?.toFixed(1) ?? '—'}
            <span className="stat-unit"> {unit}</span>
          </div>
          <div className="stat-label">Min</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: trendColor }}>
            {trendArrow} {trendData?.trend?.change_percent?.toFixed(1) ?? '—'}%
          </div>
          <div className="stat-label">Trend</div>
        </div>
      </div>

      {/* Trend Chart */}
      {chartData && (
        <div className="card">
          <div className="card-title">
            📈 Trend Analysis
            {trendData?.model && (
              <span style={{ 
                fontSize: 9, 
                background: 'rgba(16,185,129,0.15)', 
                color: '#10b981',
                padding: '2px 8px',
                borderRadius: 10,
                fontWeight: 600,
                marginLeft: 'auto',
              }}>
                {trendData.model}
              </span>
            )}
          </div>
          <div className="chart-container">
            <Line data={chartData} options={chartOptions} />
          </div>
          <div style={{ display: 'flex', gap: 16, marginTop: 8, justifyContent: 'center' }}>
            <span style={{ fontSize: 10, color: '#10b981' }}>● Historical</span>
            <span style={{ fontSize: 10, color: '#f59e0b' }}>● Forecast</span>
          </div>
        </div>
      )}
    </div>
  );
}
