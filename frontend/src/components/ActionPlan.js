import React from 'react';

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
          <ul className="rec-actions">
            {rec.actions.slice(0, 4).map((action, i) => (
              <li key={i}>{action}</li>
            ))}
          </ul>
          <div className="rec-affected">
            {rec.affected_area_percent}% of area affected
            {rec.hotspot_count > 0 && ` · ${rec.hotspot_count} ${rec.hotspot_type} clusters`}
          </div>
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
