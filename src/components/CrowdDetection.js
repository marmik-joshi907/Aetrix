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
          {crowdData.political_gatherings > 0 && (
            <div className="crowd-stat">
              <div className="crowd-stat-value" style={{ color: '#a78bfa' }}>
                {crowdData.political_gatherings}
              </div>
              <div className="crowd-stat-label">Political</div>
            </div>
          )}
        </div>
      </div>

      {/* Satellite Capability Note */}
      {crowdData.satellite_capability && (
        <div className="card" style={{
          background: 'rgba(99, 102, 241, 0.06)',
          borderLeft: '3px solid #818cf8',
          padding: '10px 12px',
          marginBottom: 8,
        }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: '#a5b4fc', marginBottom: 4, textTransform: 'uppercase' }}>
            🛰️ Satellite Detection Capability
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            {crowdData.satellite_capability}
          </div>
        </div>
      )}

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

          {/* Event Type Classification */}
          {detection.event_label && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '6px 10px', marginBottom: 8,
              background: detection.event_type === 'political_rally'
                ? 'rgba(167, 139, 250, 0.1)'
                : 'rgba(148, 163, 184, 0.06)',
              borderRadius: 8,
              border: detection.event_type === 'political_rally'
                ? '1px solid rgba(167, 139, 250, 0.25)'
                : '1px solid rgba(148, 163, 184, 0.1)',
            }}>
              <span style={{ fontSize: 16 }}>{detection.event_icon}</span>
              <div>
                <div style={{
                  fontSize: 11, fontWeight: 700,
                  color: detection.event_type === 'political_rally' ? '#a78bfa' : 'var(--text-primary)',
                }}>
                  {detection.event_label}
                </div>
                <div style={{ fontSize: 9, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  {detection.event_description}
                </div>
              </div>
            </div>
          )}

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

          {/* Satellite Indicators */}
          {detection.satellite_indicators && detection.satellite_indicators.length > 0 && (
            <div style={{
              padding: '8px 10px', marginBottom: 8,
              background: 'rgba(56, 189, 248, 0.05)',
              borderRadius: 8,
              border: '1px solid rgba(56, 189, 248, 0.12)',
            }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: '#38bdf8', marginBottom: 4, textTransform: 'uppercase' }}>
                🛰️ Satellite Indicators
              </div>
              <ul style={{ margin: 0, paddingLeft: 14, fontSize: 10, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {detection.satellite_indicators.map((indicator, iIdx) => (
                  <li key={iIdx}>{indicator}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Stampede Prevention Recommendations */}
          {detection.recommendations && detection.recommendations.length > 0 && (
            <div className="crowd-recommendations">
              <div className="crowd-rec-title">
                🛡️ {detection.event_type === 'political_rally' ? 'Rally Stampede Prevention' : 'Stampede Prevention'}
              </div>
              <ul className="crowd-rec-list">
                {detection.recommendations.map((rec, rIdx) => (
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
