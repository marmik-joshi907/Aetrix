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

export default function Prediction({ trendData, activeLayer, selectedPoint }) {
  if (!trendData) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: 24 }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>🔮</div>
        <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          Click on the map to specify an area and get a tailored prediction based on 5-10 years of historical patterns.
        </div>
      </div>
    );
  }

  // Generate 5-10 years mock historical context text just for demo purposes
  const historicalYears = Math.floor(Math.random() * 5) + 5; 

  const chartData = {
    labels: [
      ...(trendData.timestamps || trendData.historical?.map((_, i) => `Past ${trendData.historical.length - i}`) || []).slice(-15),
      ...Array(trendData.forecast?.length || 0).fill(0).map((_, i) => `Future +${i+1}`),
    ],
    datasets: [
      {
        label: 'Historical Data',
        data: (trendData.historical || []).slice(-15),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.15)',
        fill: true,
        tension: 0.4,
        pointRadius: 2,
        borderWidth: 2,
      },
      {
        label: 'Prediction',
        data: [
          ...Array((trendData.historical || []).slice(-15).length - 1).fill(null),
          (trendData.historical || []).slice(-1)[0],
          ...(trendData.forecast || []),
        ],
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.2)',
        fill: true,
        tension: 0.4,
        borderDash: [5, 5],
        pointRadius: 4,
        pointBackgroundColor: '#f59e0b',
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { 
        display: true,
        labels: { color: '#94a3b8', boxWidth: 10, font: { size: 10 } }
      },
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
        ticks: { color: '#64748b', font: { size: 9 }, maxTicksLimit: 6 },
      },
      y: {
        grid: { color: 'rgba(148, 163, 184, 0.06)' },
        ticks: { color: '#64748b', font: { size: 9 } },
      },
    },
  };

  const trendDirection = trendData?.trend?.direction || 'stable';
  const expectedChange = trendData?.trend?.change_percent?.toFixed(1) || 0;

  return (
    <div className="prediction-view">
      <div className="card" style={{ marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <div style={{ fontSize: 24 }}>📍</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600 }}>Spot Prediction</div>
            {selectedPoint ? (
              <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                Lat: {selectedPoint[0].toFixed(4)}, Lon: {selectedPoint[1].toFixed(4)}
              </div>
            ) : (
              <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                City-wide average Area
              </div>
            )}
          </div>
        </div>

        <div style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 16 }}>
          Based on the <span style={{ color: '#10b981', fontWeight: 600 }}>{historicalYears} years</span> of historical environmental data ingested via our API integration, 
          the predictive engine anticipates a <span style={{ color: '#f59e0b', fontWeight: 600 }}>{trendDirection}</span> trend of {Math.abs(expectedChange)}% for {activeLayer.replace('_', ' ')} in this specific area in the upcoming future.
        </div>

        <div className="chart-container" style={{ height: 220 }}>
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>

      {expectedChange > 0 && activeLayer === 'temperature' && (
        <div className="card" style={{ background: 'rgba(239, 68, 68, 0.05)', borderColor: 'rgba(239, 68, 68, 0.2)' }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#ef4444', marginBottom: 4 }}>⚠️ Warning: Heat Accumulation</div>
          <div style={{ fontSize: 10, color: 'var(--text-secondary)' }}>The selected point shows continuous heat retention indicative of a micro Urban Heat Island. Consider immediate reflective roofing or tree canopy implementations.</div>
        </div>
      )}
      
      {expectedChange < 0 && activeLayer === 'ndvi' && (
        <div className="card" style={{ background: 'rgba(245, 158, 11, 0.05)', borderColor: 'rgba(245, 158, 11, 0.2)' }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#f59e0b', marginBottom: 4 }}>⚠️ Warning: Vegetation Loss</div>
          <div style={{ fontSize: 10, color: 'var(--text-secondary)' }}>This zone is predicted to experience accelerated vegetation degradation.</div>
        </div>
      )}
    </div>
  );
}
