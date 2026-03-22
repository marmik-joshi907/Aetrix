import React from 'react';

export default function TimelineWarnings({ warningData }) {
  if (!warningData || !warningData.warnings || warningData.warnings.length === 0) {
    return null;
  }

  const severityColors = {
    critical: '#ef4444',
    high: '#f97316',
    moderate: '#eab308',
  };

  return (
    <div className="timeline-warnings">
      {/* Header */}
      <div className="card timeline-warnings-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ fontSize: 20 }}>⚠️</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700 }}>Condition Alerts</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
              {warningData.warning_count} worsening trend{warningData.warning_count > 1 ? 's' : ''} detected
              (comparing last {warningData.lookback_weeks} weeks)
            </div>
          </div>
        </div>
      </div>

      {/* Warning Cards */}
      {warningData.warnings.map((warning, idx) => (
        <div
          key={idx}
          className="card timeline-warning-card"
          style={{
            borderLeft: `3px solid ${severityColors[warning.severity] || '#94a3b8'}`,
            animationDelay: `${idx * 0.1}s`,
          }}
        >
          {/* Warning Header */}
          <div className="timeline-warning-header">
            <span className="timeline-warning-icon">{warning.icon}</span>
            <span className="timeline-warning-title">{warning.title}</span>
            <span
              className="timeline-warning-badge"
              style={{
                background: `${severityColors[warning.severity]}20`,
                color: severityColors[warning.severity],
              }}
            >
              {warning.severity}
            </span>
          </div>

          {/* Value Comparison */}
          <div className="timeline-value-comparison">
            <div className="timeline-value-box">
              <div className="timeline-value-label">Previous</div>
              <div className="timeline-value">{warning.previous_value}</div>
            </div>
            <div className="timeline-arrow">
              {warning.direction === 'increasing' ? '↗️' : '↘️'}
            </div>
            <div className="timeline-value-box current">
              <div className="timeline-value-label">Current</div>
              <div className="timeline-value" style={{ color: severityColors[warning.severity] }}>
                {warning.current_value}
              </div>
            </div>
            <div className="timeline-change-badge" style={{ color: severityColors[warning.severity] }}>
              {warning.direction === 'increasing' ? '+' : '-'}{warning.change_percent}%
            </div>
          </div>

          {/* Mini Trend Line (text-based) */}
          {warning.trend_line && warning.trend_line.length > 0 && (
            <div className="timeline-trend-mini">
              <div className="timeline-trend-label">📈 Weekly Trend</div>
              <div className="timeline-trend-dots">
                {warning.trend_line.map((point, pIdx) => (
                  <div key={pIdx} className="timeline-trend-dot">
                    <div className="timeline-trend-dot-label">{point.week?.toString().substring(0, 10)}</div>
                    <div
                      className="timeline-trend-dot-bar"
                      style={{
                        height: `${Math.min(40, Math.max(8, Math.abs(point.value || 0) * (warning.parameter === 'ndvi' || warning.parameter === 'soil_moisture' ? 100 : 1)))}px`,
                        background: pIdx === warning.trend_line.length - 1
                          ? severityColors[warning.severity]
                          : 'rgba(148, 163, 184, 0.3)',
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Neglect Projection */}
          <div className="timeline-neglect-box">
            <div className="timeline-neglect-title">🔮 If Neglected</div>
            <div className="timeline-neglect-text">{warning.neglect_projection}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
