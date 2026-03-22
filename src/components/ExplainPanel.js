import React from 'react';

export default function ExplainPanel({ explanationData }) {
  if (!explanationData || !explanationData.explanations || explanationData.explanations.length === 0) {
    return null;
  }

  const severityColors = {
    critical: '#ef4444',
    high: '#f97316',
    moderate: '#eab308',
    normal: '#22c55e',
  };

  const overallColor = severityColors[explanationData.overall_severity] || '#94a3b8';

  return (
    <div className="explain-panel">
      {/* Header */}
      <div className="card explain-header-card" style={{ borderLeft: `3px solid ${overallColor}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
          <div style={{ fontSize: 20 }}>🔍</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700 }}>Why This Is Happening</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
              Cross-parameter causation analysis
            </div>
          </div>
          <div
            className="explain-severity-badge"
            style={{ background: `${overallColor}20`, color: overallColor }}
          >
            {explanationData.overall_severity?.toUpperCase()}
          </div>
        </div>
      </div>

      {/* Explanation Cards */}
      {explanationData.explanations.map((exp, idx) => (
        <div
          key={idx}
          className={`card explain-card explain-card-${exp.severity}`}
          style={{ animationDelay: `${idx * 0.1}s` }}
        >
          {/* Card Header */}
          <div className="explain-card-header">
            <span className="explain-card-icon">{exp.icon}</span>
            <span className="explain-card-title">{exp.title}</span>
            <span
              className="explain-card-badge"
              style={{
                background: `${severityColors[exp.severity] || '#94a3b8'}20`,
                color: severityColors[exp.severity] || '#94a3b8',
              }}
            >
              {exp.severity}
            </span>
          </div>

          {/* Explanation Text */}
          <div className="explain-card-text">{exp.explanation}</div>

          {/* Factors (only for cross-parameter) */}
          {exp.factors && exp.factors.length > 0 && (
            <div className="explain-factors">
              <div className="explain-factors-title">Contributing Factors</div>
              <div className="explain-factors-grid">
                {exp.factors.map((factor, fIdx) => (
                  <div key={fIdx} className={`explain-factor explain-factor-${factor.impact}`}>
                    <span className="explain-factor-icon">{factor.icon}</span>
                    <div>
                      <div className="explain-factor-name">{factor.name}</div>
                      <div className="explain-factor-value">{factor.value}</div>
                    </div>
                    <span className={`explain-impact-tag impact-${factor.impact}`}>
                      {factor.impact}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Type indicator */}
          {exp.type === 'cross_parameter' && (
            <div className="explain-cross-badge">
              ⚡ Cross-parameter correlation detected
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
