import React from 'react';

const PARAM_LABELS = {
  temperature: 'Temperature', pollution: 'Pollution (AQI)',
  ndvi: 'Vegetation (NDVI)', soil_moisture: 'Soil Moisture',
};

function WowBadge({ delta, direction }) {
  if (delta == null) return null;
  const arrow = direction === 'worsening' ? '▲' : direction === 'improving' ? '▼' : '—';
  const color = direction === 'worsening' ? '#ef4444' : direction === 'improving' ? '#22c55e' : '#94a3b8';
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 3,
      fontSize: 10, fontWeight: 700, color,
      background: `${color}15`, padding: '2px 6px', borderRadius: 6,
    }}>
      {arrow} {Math.abs(delta).toFixed(2)} WoW
    </span>
  );
}

function SeverityBar({ dist }) {
  if (!dist) return null;
  const total = (dist.critical || 0) + (dist.high || 0) + (dist.moderate || 0) + (dist.normal || 0);
  if (total === 0) return null;
  const pct = (v) => ((v / total) * 100).toFixed(1);
  return (
    <div style={{ marginTop: 6 }}>
      <div style={{ fontSize: 9, color: 'var(--text-muted)', marginBottom: 3, textTransform: 'uppercase' }}>
        Severity Distribution
      </div>
      <div style={{ display: 'flex', height: 8, borderRadius: 4, overflow: 'hidden', background: 'rgba(148,163,184,0.1)' }}>
        {dist.critical > 0 && <div style={{ width: `${pct(dist.critical)}%`, background: '#ef4444' }} title={`Critical: ${dist.critical} cells`} />}
        {dist.high > 0 && <div style={{ width: `${pct(dist.high)}%`, background: '#f97316' }} title={`High: ${dist.high} cells`} />}
        {dist.moderate > 0 && <div style={{ width: `${pct(dist.moderate)}%`, background: '#eab308' }} title={`Moderate: ${dist.moderate} cells`} />}
        {dist.normal > 0 && <div style={{ width: `${pct(dist.normal)}%`, background: '#22c55e' }} title={`Normal: ${dist.normal} cells`} />}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 8, color: 'var(--text-muted)', marginTop: 2 }}>
        <span>🔴 {dist.critical}</span>
        <span>🟠 {dist.high}</span>
        <span>🟡 {dist.moderate}</span>
        <span>🟢 {dist.normal}</span>
      </div>
    </div>
  );
}

export default function ActionPlan({ plan }) {
  if (!plan) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: 24 }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>📋</div>
        <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          Loading action plan...
        </div>
      </div>
    );
  }

  return (
    <div className="action-plan">
      {/* Overall Risk */}
      <div style={{ marginBottom: 12 }}>
        <div className={`risk-badge risk-${plan.overall_risk}`}>
          <span style={{ fontSize: 14 }}>⚠️</span>
          Overall Risk: {plan.overall_risk}
        </div>
        <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
          Analysis: {plan.analysis_date} | {plan.total_recommendations} recommendations
          {plan.total_area_km2 && ` | ${plan.total_area_km2} km² coverage`}
        </div>
      </div>

      {/* Summary Stats */}
      {plan.summary_stats && (
        <div className="card" style={{ marginBottom: 10 }}>
          <div className="card-title">📊 Current Status</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
            {Object.entries(plan.summary_stats).map(([param, stats]) => (
              <div key={param} style={{
                padding: '6px 8px',
                background: 'rgba(148,163,184,0.06)',
                borderRadius: 6,
                fontSize: 11,
              }}>
                <div style={{ color: 'var(--text-muted)', fontSize: 9, textTransform: 'uppercase' }}>
                  {param.replace('_', ' ')}
                </div>
                <div style={{ fontWeight: 700, marginTop: 2 }}>
                  {stats.mean} <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>{stats.unit}</span>
                </div>
                {/* Enriched stats */}
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 3 }}>
                  {stats.std_dev != null && (
                    <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>σ {stats.std_dev}</span>
                  )}
                  {stats.p95 != null && (
                    <span style={{ fontSize: 9, color: '#f97316' }}>P95: {stats.p95}</span>
                  )}
                </div>
                {stats.wow_delta != null && (
                  <div style={{ marginTop: 3 }}>
                    <WowBadge delta={stats.wow_delta} direction={stats.wow_direction} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {plan.recommendations.map((rec, idx) => (
        <div key={idx} className="recommendation-card">
          <div className="rec-header">
            <span className="rec-icon">{rec.icon}</span>
            <span className="rec-category">{rec.category}</span>
            <span className={`rec-severity severity-${rec.severity}`}>
              {rec.severity}
            </span>
          </div>

          {/* Enriched stats row */}
          <div style={{
            display: 'flex', flexWrap: 'wrap', gap: 6, margin: '8px 0',
            padding: '6px 8px', background: 'rgba(148,163,184,0.05)', borderRadius: 6,
          }}>
            {rec.peak_value != null && (
              <div style={{ fontSize: 10 }}>
                <span style={{ color: 'var(--text-muted)' }}>Peak: </span>
                <span style={{ fontWeight: 700, color: '#ef4444' }}>{rec.peak_value}</span>
              </div>
            )}
            {rec.std_dev != null && (
              <div style={{ fontSize: 10 }}>
                <span style={{ color: 'var(--text-muted)' }}>σ: </span>
                <span style={{ fontWeight: 600 }}>{rec.std_dev}</span>
              </div>
            )}
            {rec.p95 != null && (
              <div style={{ fontSize: 10 }}>
                <span style={{ color: 'var(--text-muted)' }}>P95: </span>
                <span style={{ fontWeight: 600, color: '#f97316' }}>{rec.p95}</span>
              </div>
            )}
            {rec.wow_delta != null && (
              <WowBadge delta={rec.wow_delta} direction={rec.wow_direction} />
            )}
          </div>

          <ul className="rec-actions">
            {rec.actions.slice(0, 4).map((action, i) => (
              <li key={i}>{action}</li>
            ))}
          </ul>

          <div className="rec-affected">
            {rec.affected_area_percent}% of area affected
            {rec.affected_area_km2 != null && ` (${rec.affected_area_km2} km²)`}
            {rec.hotspot_count > 0 && ` · ${rec.hotspot_count} ${rec.hotspot_type} clusters`}
            {rec.hotspot_avg_severity != null && (
              <span style={{ color: '#f97316', marginLeft: 4 }}>
                (avg severity: {(rec.hotspot_avg_severity * 100).toFixed(0)}%)
              </span>
            )}
          </div>

          <SeverityBar dist={rec.severity_distribution} />
        </div>
      ))}

      {/* Footer */}
      <div style={{ 
        fontSize: 9, 
        color: 'var(--text-muted)', 
        textAlign: 'center',
        marginTop: 12,
        padding: '8px 0',
        borderTop: '1px solid var(--border-color)',
      }}>
        {plan.report_footer}
      </div>
    </div>
  );
}
