import React from 'react';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler);

export default function Prediction({ trendData, mlPrediction, activeLayer, selectedPoint, pointLoading, clickedSpotData }) {

  // Loading state while fetching point data
  if (pointLoading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: 24 }}>
        <div className="loading-spinner" style={{ width: 28, height: 28, borderWidth: 2, margin: '0 auto 12px' }} />
        <div style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 600 }}>
          Analyzing point...
        </div>
        {selectedPoint && (
          <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
            {selectedPoint[0].toFixed(4)}, {selectedPoint[1].toFixed(4)}
          </div>
        )}
      </div>
    );
  }

  // Show clicked point data summary if we have it
  const renderPointSummary = () => {
    if (!clickedSpotData || !selectedPoint) return null;
    return (
      <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-title">📍 Point Analysis</div>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 12 }}>
          {selectedPoint[0].toFixed(4)}, {selectedPoint[1].toFixed(4)}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          <div className="point-stat-card" style={{ borderLeft: '3px solid #ef4444' }}>
            <div style={{ fontSize: 9, color: '#ef4444', fontWeight: 600 }}>🌡️ TEMP</div>
            <div style={{ fontSize: 16, fontWeight: 800, color: '#ef4444', marginTop: 2 }}>
              {clickedSpotData.temperature}
            </div>
          </div>
          <div className="point-stat-card" style={{ borderLeft: '3px solid #f59e0b' }}>
            <div style={{ fontSize: 9, color: '#f59e0b', fontWeight: 600 }}>🏭 POLLUTION</div>
            <div style={{ fontSize: 16, fontWeight: 800, color: '#f59e0b', marginTop: 2 }}>
              {clickedSpotData.pollution_aqi}
            </div>
          </div>
          <div className="point-stat-card" style={{ borderLeft: '3px solid #3b82f6' }}>
            <div style={{ fontSize: 9, color: '#3b82f6', fontWeight: 600 }}>💧 SOIL</div>
            <div style={{ fontSize: 16, fontWeight: 800, color: '#3b82f6', marginTop: 2 }}>
              {clickedSpotData.soil_moisture}
            </div>
          </div>
          <div className="point-stat-card" style={{ borderLeft: '3px solid #10b981' }}>
            <div style={{ fontSize: 9, color: '#10b981', fontWeight: 600 }}>🌿 NDVI</div>
            <div style={{ fontSize: 16, fontWeight: 800, color: '#10b981', marginTop: 2 }}>
              {clickedSpotData.vegetation}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // No data at all yet — initial prompt
  if (!mlPrediction && !clickedSpotData) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: 24 }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>🔮</div>
        <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          Click on the map to see AI-powered predictions for any location.
        </div>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 8, opacity: 0.7 }}>
          Tap any point → see Temperature, Pollution, Soil & Vegetation analysis
        </div>
      </div>
    );
  }

  const renderLocationHeader = (title) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
      <div style={{ fontSize: 24 }}>📍</div>
      <div>
        <div style={{ fontSize: 13, fontWeight: 600 }}>{title}</div>
        {selectedPoint ? (
          <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
            Lat: {selectedPoint[0].toFixed(4)}, Lon: {selectedPoint[1].toFixed(4)}
          </div>
        ) : (
          <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>City-wide Analysis</div>
        )}
      </div>
    </div>
  );

  const getChartOptions = () => ({
    responsive: true, maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { backgroundColor: 'rgba(17, 24, 39, 0.95)', titleColor: '#f1f5f9', bodyColor: '#94a3b8', padding: 10 },
    },
    scales: {
      x: { grid: { color: 'rgba(148, 163, 184, 0.06)' }, ticks: { color: '#64748b', font: { size: 9 } } },
      y: { grid: { color: 'rgba(148, 163, 184, 0.06)' }, ticks: { color: '#64748b', font: { size: 9 } } },
    },
  });

  // ML Prediction panels per layer
  const renderMLPanel = () => {
    if (!mlPrediction) return null;

    if (activeLayer === 'temperature' && Array.isArray(mlPrediction.predictions)) {
      const list = mlPrediction.predictions;
      const chartData = {
        labels: list.map(p => p.year.toString()),
        datasets: [{
          label: 'Annual Mean Temp (°C)',
          data: list.map(p => p.predicted_annual),
          borderColor: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)',
          fill: true, tension: 0.4, borderWidth: 2, pointRadius: 4, pointBackgroundColor: '#ef4444'
        }]
      };
      return (
        <>
          <div className="card" style={{ marginBottom: 12 }}>
            {renderLocationHeader('Temperature Forecast (5-Year)')}
            <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginBottom: 16 }}>
              Powered by <strong>MLPRegressor Neural Network</strong> trained on historical climate data.
            </div>
            <div className="chart-container" style={{ height: 200 }}>
              <Line data={chartData} options={getChartOptions()} />
            </div>
          </div>
          <div className="card" style={{ background: 'rgba(239, 68, 68, 0.05)', borderColor: 'rgba(239, 68, 68, 0.2)' }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#ef4444', marginBottom: 4 }}>📈 Long-Term Trend</div>
            <div style={{ fontSize: 10, color: 'var(--text-secondary)' }}>
              Projected to reach {list[list.length - 1]?.predicted_annual}°C by {list[list.length - 1]?.year}.
            </div>
          </div>
        </>
      );
    }

    if (activeLayer === 'soil_moisture' && mlPrediction.result) {
      const res = mlPrediction.result;
      const riskColors = { 'Low Risk': '#10b981', 'Medium Risk': '#f59e0b', 'High Risk': '#ef4444' };
      const color = riskColors[res.drought_label] || '#94a3b8';
      const chartData = res.forecast_7d_sm_pct ? {
        labels: ['+1d','+2d','+3d','+4d','+5d','+6d','+7d'],
        datasets: [{
          label: 'Forecast Soil Moisture (%)',
          data: res.forecast_7d_sm_pct,
          borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true, tension: 0.4, borderWidth: 2, pointRadius: 3
        }]
      } : null;

      return (
        <div className="card" style={{ marginBottom: 12 }}>
          {renderLocationHeader('Drought Risk Analysis')}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16, padding: 12, background: 'rgba(148,163,184,0.06)', borderRadius: 8 }}>
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: color }} />
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color }}>{res.drought_label}</div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Random Forest Classification</div>
            </div>
            <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
              <div style={{ fontSize: 12, fontWeight: 600 }}>{(res.probabilities[res.drought_label] * 100).toFixed(1)}%</div>
              <div style={{ fontSize: 9, color: 'var(--text-muted)' }}>Confidence</div>
            </div>
          </div>
          {chartData && (
            <>
              <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 8, color: 'var(--text-secondary)' }}>7-Day Trajectory (ARIMA)</div>
              <div className="chart-container" style={{ height: 160 }}>
                <Line data={chartData} options={getChartOptions()} />
              </div>
            </>
          )}
        </div>
      );
    }

    if (activeLayer === 'pollution' && mlPrediction.result) {
      const res = mlPrediction.result;
      const aqiColors = ['#10b981', '#22c55e', '#eab308', '#f97316', '#ef4444', '#7f1d1d'];
      const color = aqiColors[res.aqi_category] || '#94a3b8';
      const exceeded = Object.entries(res.pollutant_risk_flags || {})
        .filter(([_, flag]) => flag === 'EXCEEDS_WHO')
        .map(([p]) => p);

      return (
        <div className="card" style={{ marginBottom: 12 }}>
          {renderLocationHeader('Air Quality Prediction')}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16, padding: 12, background: 'rgba(148,163,184,0.06)', borderRadius: 8 }}>
            <div style={{ fontSize: 24, fontWeight: 800, color }}>AQI {res.aqi_category}</div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color }}>{res.aqi_label}</div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>XGBoost Classification</div>
            </div>
          </div>
          <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 8, color: 'var(--text-secondary)' }}>WHO Threshold Analysis</div>
          {exceeded.length > 0 ? (
            <div style={{ padding: 12, background: 'rgba(239, 68, 68, 0.05)', borderLeft: '3px solid #ef4444', borderRadius: '0 8px 8px 0' }}>
              <div style={{ fontSize: 11, color: '#ef4444', fontWeight: 600, marginBottom: 4 }}>🚨 Exceeding Safe Limits:</div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{exceeded.join(', ')}</div>
            </div>
          ) : (
            <div style={{ padding: 12, background: 'rgba(16, 185, 129, 0.05)', borderLeft: '3px solid #10b981', borderRadius: '0 8px 8px 0' }}>
              <div style={{ fontSize: 11, color: '#10b981', fontWeight: 600 }}>✅ All pollutants within WHO limits</div>
            </div>
          )}
        </div>
      );
    }

    if (activeLayer === 'ndvi' && mlPrediction.result) {
      const res = mlPrediction.result;
      const riskColors = { 'Low': '#10b981', 'Moderate': '#f59e0b', 'High': '#ef4444', 'Very High': '#7f1d1d' };
      const color = riskColors[res.change_risk_label] || '#94a3b8';
      return (
        <div className="card" style={{ marginBottom: 12 }}>
          {renderLocationHeader('Land Use Change Risk')}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16, padding: 16, background: 'rgba(148,163,184,0.06)', borderRadius: 8 }}>
            <div style={{ width: 16, height: 16, borderRadius: 4, background: color }} />
            <div>
              <div style={{ fontSize: 15, fontWeight: 600, color }}>{res.change_risk_label} Risk Zone</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>K-Means Spatial Clustering</div>
            </div>
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            This model fuses satellite vegetation (NDVI) with pollution proxies (PM2.5, NO2) to identify zones at risk of degradation.
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="prediction-view">
      {/* Point Summary always shown first if we have spot data */}
      {renderPointSummary()}

      {/* ML-specific panel */}
      {renderMLPanel()}

      {/* Trend info if available */}
      {trendData?.trend && (
        <div className="card" style={{ marginTop: 8 }}>
          <div className="card-title">📊 Trend Direction</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{
              fontSize: 20,
              color: trendData.trend.direction === 'increasing' ? '#ef4444' :
                     trendData.trend.direction === 'decreasing' ? '#10b981' : '#eab308'
            }}>
              {trendData.trend.direction === 'increasing' ? '↗' :
               trendData.trend.direction === 'decreasing' ? '↘' : '→'}
            </span>
            <div>
              <div style={{ fontSize: 13, fontWeight: 600, textTransform: 'capitalize' }}>
                {trendData.trend.direction}
              </div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                {trendData.trend.change_percent?.toFixed(1)}% change · {trendData.model || 'ARIMA'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
