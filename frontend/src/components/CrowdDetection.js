import React from 'react';

export default function CrowdDetection({ crowdData, loading }) {
  if (loading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: 24 }}>
        <div className="loading-spinner" style={{ width: 28, height: 28, borderWidth: 2, margin: '0 auto 12px' }} />
        <div style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 600 }}>
          Scanning satellite imagery for crowd patterns...
        </div>
      </div>
    );
  }

  if (!crowdData) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: 24 }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>👥</div>
        <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          Loading crowd detection data...
        </div>
      </div>
    );
  }

  const riskColors = {
    high: '#ef4444',
    moderate: '#f59e0b',
    low: '#22c55e',
  };

  return (
    <div className="crowd-detection">
      {/* Summary Header */}
      <div className="card crowd-summary-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <div style={{ fontSize: 24 }}>🛰️</div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700 }}>Crowd Detection</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
              Satellite-based gathering analysis
            </div>
          </div>
        </div>

        {/* Stats Row */}
        <div className="crowd-stats-row">
          <div className="crowd-stat">
            <div className="crowd-stat-value">{crowdData.total_detections}</div>
            <div className="crowd-stat-label">Gatherings</div>
          </div>
          <div className="crowd-stat">
            <div className="crowd-stat-value" style={{ color: '#f59e0b' }}>
              {crowdData.total_estimated_crowd?.toLocaleString()}
            </div>
            <div className="crowd-stat-label">Est. People</div>
          </div>
          <div className="crowd-stat">
            <div className="crowd-stat-value" style={{ color: '#ef4444' }}>
              {crowdData.high_risk_zones}
            </div>
            <div className="crowd-stat-label">High Risk</div>
          </div>
        </div>
      </div>

      {/* Detection Cards */}
      {crowdData.detections?.map((detection, idx) => (
        <div
          key={idx}
          className="card crowd-detection-card"
          style={{
            borderLeft: `3px solid ${riskColors[detection.stampede_risk] || '#94a3b8'}`,
            animationDelay: `${idx * 0.1}s`,
          }}
        >
          {/* Location Header */}
          <div className="crowd-card-header">
            <div>
              <div className="crowd-location-name">{detection.location}</div>
              <div className="crowd-location-type">{detection.type?.replace('_', ' ')}</div>
            </div>
            <div
              className="crowd-risk-badge"
              style={{
                background: `${riskColors[detection.stampede_risk]}20`,
                color: riskColors[detection.stampede_risk],
              }}
            >
              {detection.stampede_risk?.toUpperCase()} RISK
            </div>
          </div>

          {/* Crowd Metrics */}
          <div className="crowd-metrics">
            <div className="crowd-metric">
              <span className="crowd-metric-icon">👥</span>
              <div>
                <div className="crowd-metric-value">{detection.estimated_crowd?.toLocaleString()}</div>
                <div className="crowd-metric-label">Estimated</div>
              </div>
            </div>
            <div className="crowd-metric">
              <span className="crowd-metric-icon">📊</span>
              <div>
                <div className="crowd-metric-value">{detection.density_percent}%</div>
                <div className="crowd-metric-label">Density</div>
              </div>
            </div>
            <div className="crowd-metric">
              <span className="crowd-metric-icon">🏟️</span>
              <div>
                <div className="crowd-metric-value">{detection.capacity?.toLocaleString()}</div>
                <div className="crowd-metric-label">Capacity</div>
              </div>
            </div>
          </div>

          {/* Density Bar */}
          <div className="crowd-density-bar-container">
            <div className="crowd-density-bar-bg">
              <div
                className="crowd-density-bar-fill"
                style={{
                  width: `${Math.min(detection.density_percent, 100)}%`,
                  background: riskColors[detection.stampede_risk],
                }}
              />
            </div>
          </div>

          {/* Recommendations */}
          {detection.recommendations && detection.recommendations.length > 0 && (
            <div className="crowd-recommendations">
              <div className="crowd-rec-title">🛡️ Stampede Prevention</div>
              <ul className="crowd-rec-list">
                {detection.recommendations.slice(0, 3).map((rec, rIdx) => (
                  <li key={rIdx}>{rec}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Coordinates */}
          <div className="crowd-coords">
            📍 {detection.lat?.toFixed(4)}, {detection.lon?.toFixed(4)}
          </div>
        </div>
      ))}

      {/* Disclaimer */}
      <div className="crowd-disclaimer">
        <div style={{ fontSize: 9, color: 'var(--text-muted)', fontStyle: 'italic', lineHeight: 1.5 }}>
          ⚠️ {crowdData.disclaimer}
        </div>
      </div>
    </div>
  );
}
