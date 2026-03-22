import React from 'react';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler);

export default function Dashboard({ gridData, trendData, mlPrediction, activeLayer }) {
  // Stats
  const stats = gridData?.stats || {};
  const unit = gridData?.unit || '';

  // Trend chart data
  let chartData = null;
  let modelLabel = trendData?.model || '';

  if (activeLayer === 'temperature' && mlPrediction?.predictions) {
    chartData = {
      labels: mlPrediction.predictions.map(p => p.year.toString()),
      datasets: [
        {
          label: 'Forecast',
          data: mlPrediction.predictions.map(p => p.predicted_annual),
          borderColor: '#f59e0b', backgroundColor: 'rgba(245, 158, 11, 0.1)',
          fill: true, tension: 0.4, borderDash: [5, 5], pointRadius: 2, borderWidth: 2,
        }
      ]
    };
    modelLabel = 'MLPRegressor (Temp)';
  } else if (activeLayer === 'soil_moisture' && mlPrediction?.result?.forecast_7d_sm_pct) {
    chartData = {
      labels: ['+1d','+2d','+3d','+4d','+5d','+6d','+7d'],
      datasets: [
        {
          label: 'Forecast',
          data: mlPrediction.result.forecast_7d_sm_pct,
          borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true, tension: 0.4, borderDash: [5, 5], pointRadius: 2, borderWidth: 2,
        }
      ]
    };
    modelLabel = 'ARIMA (Soil)';
  } else if (trendData?.historical) {
    chartData = {
      labels: [
        ...(trendData.timestamps || trendData.historical?.map((_, i) => `W${i+1}`) || []).slice(-20),
        ...Array(trendData.forecast?.length || 0).fill(0).map((_, i) => `F${i+1}`),
      ],
      datasets: [
        {
          label: 'Historical',
          data: (trendData.historical || []).slice(-20),
          borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true, tension: 0.4, pointRadius: 0, borderWidth: 2,
        },
        {
          label: 'Forecast',
          data: [
            ...Array((trendData.historical || []).slice(-20).length - 1).fill(null),
            (trendData.historical || []).slice(-1)[0],
            ...(trendData.forecast || []),
          ],
          borderColor: '#f59e0b', backgroundColor: 'rgba(245, 158, 11, 0.1)',
          fill: true, tension: 0.4, borderDash: [5, 5], pointRadius: 0, borderWidth: 2,
        },
      ],
    };
  }

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

  const trendDirection = trendData?.trend?.direction || 'stable';
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
      {chartData ? (
        <div className="card">
          <div className="card-title">
            📈 Trend Analysis
            {modelLabel && (
              <span style={{ 
                fontSize: 9, 
                background: 'rgba(16,185,129,0.15)', 
                color: '#10b981',
                padding: '2px 8px',
                borderRadius: 10,
                fontWeight: 600,
                marginLeft: 'auto',
              }}>
                {modelLabel}
              </span>
            )}
          </div>
          <div className="chart-container">
            <Line data={chartData} options={chartOptions} />
          </div>
          <div style={{ display: 'flex', gap: 16, marginTop: 8, justifyContent: 'center' }}>
            <span style={{ fontSize: 10, color: '#f59e0b' }}>● Forecast</span>
          </div>
        </div>
      ) : (
        <div className="card" style={{ textAlign: 'center', padding: '32px 16px' }}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>📊</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            No trend data available for this layer. Click on the map to run an ML prediction.
          </div>
        </div>
      )}
    </div>
  );
}
