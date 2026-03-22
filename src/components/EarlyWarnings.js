import React from 'react';

export default function EarlyWarnings({ warningData, loading }) {
  if (loading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: 24 }}>
        <div className="loading-spinner" style={{ width: 28, height: 28, borderWidth: 2, margin: '0 auto 12px' }} />
        <div style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 600 }}>
          Analyzing environmental trends...
        </div>
      </div>
    );
  }

  if (!warningData) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: 24 }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>🔔</div>
        <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          Loading early warning data...
        </div>
      </div>
    );
  }

  if (warningData.alert_count === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: 24 }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>✅</div>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#22c55e', marginBottom: 4 }}>
          No Active Warnings
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
          All environmental parameters are within safe thresholds for the next {warningData.forecast_days} days.
        </div>
      </div>
    );
  }

  const urgencyConfig = {
    critical: { color: '#ef4444', bg: 'rgba(239, 68, 68, 0.08)', icon: '🔴', label: 'CRITICAL' },
    warning: { color: '#f97316', bg: 'rgba(249, 115, 22, 0.08)', icon: '🟠', label: 'WARNING' },
    watch: { color: '#eab308', bg: 'rgba(234, 179, 8, 0.08)', icon: '🟡', label: 'WATCH' },
  };

  return (
    <div className="early-warnings">
      {/* Summary Header */}
      <div className="card early-warnings-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
          <div style={{ fontSize: 24 }}>🔔</div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700 }}>Early Warning System</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
              {warningData.forecast_days}-day forecast for {warningData.city}
            </div>
          </div>
        </div>

        {/* Alert Summary */}
        <div className="early-warnings-summary">
          <div className="ew-summary-stat">
            <span className="ew-summary-count" style={{ color: '#ef4444' }}>
              {warningData.critical_count}
            </span>
            <span className="ew-summary-label">Critical</span>
          </div>
          <div className="ew-summary-stat">
            <span className="ew-summary-count" style={{ color: '#f59e0b' }}>
              {warningData.alert_count - warningData.critical_count}
            </span>
            <span className="ew-summary-label">Warnings</span>
          </div>
          <div className="ew-summary-stat">
            <span className="ew-summary-count">{warningData.alert_count}</span>
            <span className="ew-summary-label">Total</span>
          </div>
        </div>
      </div>

      {/* Alert Cards */}
      {warningData.alerts.map((alert, idx) => {
        const config = urgencyConfig[alert.urgency] || urgencyConfig.watch;
        return (
          <div
            key={idx}
            className="card early-warning-card"
            style={{
              borderLeft: `3px solid ${config.color}`,
              background: config.bg,
              animationDelay: `${idx * 0.12}s`,
            }}
          >
            {/* Alert Header */}
            <div className="ew-card-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 20 }}>{alert.icon}</span>
                <div>
                  <div className="ew-card-category">{alert.category}</div>
                  <div className="ew-card-urgency" style={{ color: config.color }}>
                    {config.icon} {config.label} — {alert.urgency_label}
                  </div>
                </div>
              </div>
              <div className="ew-card-countdown">
                <div className="ew-countdown-value">{alert.forecast_days}</div>
                <div className="ew-countdown-label">days</div>
              </div>
            </div>

            {/* Alert Message */}
            <div className="ew-card-message">{alert.message}</div>

            {/* Change Rate */}
            <div className="ew-change-rate">
              <span>Change Rate:</span>
              <span style={{ color: config.color, fontWeight: 700 }}>
                {alert.change_rate}%
              </span>
            </div>

            {/* Affected Areas */}
            {alert.affected_areas && alert.affected_areas.length > 0 && (
              <div className="ew-affected-areas">
                <div className="ew-areas-title">📍 Most Affected Areas</div>
                {alert.affected_areas.map((area, aIdx) => (
                  <div key={aIdx} className="ew-area-item">
                    <span className="ew-area-name">{area.name}</span>
                    <span className="ew-area-value">
                      {area.mean_value?.toFixed(alert.parameter === 'ndvi' || alert.parameter === 'soil_moisture' ? 3 : 1)}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Recommended Actions */}
            <div className="ew-actions">
              <div className="ew-actions-title">✅ Recommended Actions</div>
              <ul className="ew-actions-list">
                {alert.recommended_actions?.slice(0, 3).map((action, aIdx) => (
                  <li key={aIdx}>{action}</li>
                ))}
              </ul>
            </div>
          </div>
        );
      })}
    </div>
  );
}
