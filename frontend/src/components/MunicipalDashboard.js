import React, { useState } from 'react';

const PARAM_LABELS = {
  temperature: '🌡️ Temp', pollution: '🏭 AQI',
  ndvi: '🌿 NDVI', soil_moisture: '💧 Soil',
};

function WowBadge({ delta, direction, label }) {
  if (delta == null) return null;
  const arrow = direction === 'worsening' ? '▲' : direction === 'improving' ? '▼' : '—';
  const color = direction === 'worsening' ? '#ef4444' : direction === 'improving' ? '#22c55e' : '#94a3b8';
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 2,
      fontSize: 9, fontWeight: 700, color,
      background: `${color}15`, padding: '2px 6px', borderRadius: 6,
    }}>
      {arrow} {label || ''}{typeof delta === 'number' ? Math.abs(delta).toFixed(2) : ''} WoW
    </span>
  );
}

function CrossParamBadges({ context }) {
  if (!context || Object.keys(context).length === 0) return null;
  return (
    <div style={{
      display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 8,
    }}>
      <span style={{ fontSize: 9, color: 'var(--text-muted)', width: '100%', marginBottom: 2, textTransform: 'uppercase' }}>
        📍 At this location
      </span>
      {Object.entries(context).map(([param, data]) => (
        <span key={param} style={{
          fontSize: 9, fontWeight: 600,
          padding: '2px 8px', borderRadius: 10,
          background: 'rgba(148,163,184,0.1)',
          color: 'var(--text-secondary)',
          border: '1px solid rgba(148,163,184,0.15)',
        }}>
          {PARAM_LABELS[param] || param}: {data.value} {data.unit}
        </span>
      ))}
    </div>
  );
}

export default function MunicipalDashboard({ dashboardData, loading }) {
  const [taskStatuses, setTaskStatuses] = useState({});
  const [taskAssignees, setTaskAssignees] = useState({});
  const [taskUrgencies, setTaskUrgencies] = useState({});
  const [selectedProblem, setSelectedProblem] = useState(null);

  if (loading) {
    return (
      <div className="municipal-loading">
        <div className="loading-spinner" style={{ width: 40, height: 40, borderWidth: 3, margin: '0 auto 16px' }} />
        <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-secondary)' }}>
          Generating Municipal Intelligence Report...
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
          Analyzing environmental data, hotspots, and trends
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="municipal-empty">
        <div style={{ fontSize: 48, marginBottom: 12 }}>🏛️</div>
        <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 6 }}>Municipal Dashboard</div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          Loading city planning data...
        </div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#22c55e';
      case 'in_progress': return '#3b82f6';
      default: return '#f59e0b';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✅';
      case 'in_progress': return '🔄';
      default: return '⏳';
    }
  };

  const healthScore = dashboardData.city_health_score || 0;
  const healthColor = healthScore > 70 ? '#22c55e' : healthScore > 40 ? '#f59e0b' : '#ef4444';

  return (
    <div className="municipal-dashboard">
      {/* Header */}
      <div className="municipal-header">
        <div className="municipal-header-top">
          <div>
            <div className="municipal-title">🏛️ Municipal Dashboard</div>
            <div className="municipal-subtitle">
              {dashboardData.city} · {dashboardData.analysis_date}
              {dashboardData.total_area_km2 && ` · ${dashboardData.total_area_km2} km²`}
            </div>
          </div>
        </div>

        {/* City Health Score */}
        <div className="municipal-health-score">
          <div className="health-score-ring" style={{ '--health-color': healthColor, '--health-pct': `${healthScore}%` }}>
            <div className="health-score-inner">
              <div className="health-score-value" style={{ color: healthColor }}>
                {healthScore.toFixed(0)}
              </div>
              <div className="health-score-label">City Health</div>
            </div>
          </div>
          <div className="health-score-info">
            <div className="health-score-desc">
              {healthScore > 70 ? 'Good' : healthScore > 40 ? 'Needs Attention' : 'Critical'}
            </div>
            <div className="health-issues-count">
              {dashboardData.total_issues_detected} issues detected
            </div>
          </div>
        </div>
      </div>

      {/* Top 3 Urgent Problems */}
      <div className="municipal-section-title">
        🚨 Top {dashboardData.top_3_urgent?.length} Urgent Problems
      </div>

      {dashboardData.top_3_urgent?.map((problem, idx) => {
        const status = taskStatuses[idx] || problem.status || 'pending';
        const priorityColors = ['#ef4444', '#f97316', '#eab308'];
        const priorityColor = priorityColors[idx] || '#94a3b8';

        return (
          <div
            key={idx}
            className="municipal-problem-card clickable"
            style={{ animationDelay: `${idx * 0.15}s` }}
            onClick={() => setSelectedProblem(problem)}
          >
            {/* Priority Badge */}
            <div className="municipal-priority-badge" style={{ background: priorityColor }}>
              #{problem.priority_rank}
            </div>

            {/* Problem Header */}
            <div className="municipal-problem-header">
              <div className="municipal-problem-icon">{problem.icon}</div>
              <div className="municipal-problem-info">
                <div className="municipal-problem-title">{problem.title}</div>
                <div className="municipal-problem-location">
                  📍 {problem.location?.area_description}
                </div>
              </div>
              <div className="municipal-problem-score" style={{ color: priorityColor }}>
                {problem.priority_score}
              </div>
            </div>

            {/* Current Values */}
            {problem.parameter === 'multi_factor' ? (
              <div className="municipal-values" style={{ background: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgba(239, 68, 68, 0.3)' }}>
                <div className="municipal-value-item">
                  <span className="municipal-value-label" style={{ color: '#fca5a5' }}>Peak Temp</span>
                  <span className="municipal-value-num" style={{ color: '#ef4444' }}>{problem.current_values?.temp_val}</span>
                </div>
                <div className="municipal-value-item">
                  <span className="municipal-value-label" style={{ color: '#fca5a5' }}>Peak AQI</span>
                  <span className="municipal-value-num" style={{ color: '#f97316' }}>{problem.current_values?.aqi_val}</span>
                </div>
                <div className="municipal-value-item">
                  <span className="municipal-value-label" style={{ color: '#fca5a5' }}>Zones Affected</span>
                  <span className="municipal-value-num" style={{ color: '#ef4444' }}>{problem.hotspot_clusters}</span>
                </div>
              </div>
            ) : (
              <div className="municipal-values">
                <div className="municipal-value-item">
                  <span className="municipal-value-label">Mean</span>
                  <span className="municipal-value-num">{problem.current_values?.mean} {problem.current_values?.unit}</span>
                </div>
                <div className="municipal-value-item">
                  <span className="municipal-value-label">Peak</span>
                  <span className="municipal-value-num" style={{ color: '#ef4444' }}>{problem.current_values?.max} {problem.current_values?.unit}</span>
                </div>
                {problem.current_values?.p95 != null && (
                  <div className="municipal-value-item">
                    <span className="municipal-value-label" style={{ color: '#f97316' }}>P95</span>
                    <span className="municipal-value-num">{problem.current_values.p95} {problem.current_values?.unit}</span>
                  </div>
                )}
                {problem.hotspot_clusters > 0 && (
                  <div className="municipal-value-item">
                    <span className="municipal-value-label">Hotspots</span>
                    <span className="municipal-value-num">{problem.hotspot_clusters} clusters</span>
                  </div>
                )}
              </div>
            )}

            {/* Enriched Stats Row */}
            <div style={{
              display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8,
              padding: '6px 8px', background: 'rgba(148,163,184,0.04)',
              borderRadius: 6, border: '1px solid rgba(148,163,184,0.08)',
            }}>
              {problem.current_values?.std_dev != null && (
                <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>σ {problem.current_values.std_dev}</span>
              )}
              {problem.spatial_coverage_pct != null && (
                <span style={{ fontSize: 9, padding: '1px 6px', borderRadius: 6, background: 'rgba(239,68,68,0.1)', color: '#ef4444', fontWeight: 600 }}>
                  {problem.spatial_coverage_pct}% exceeded
                </span>
              )}
              {problem.affected_area_km2 != null && (
                <span style={{ fontSize: 9, padding: '1px 6px', borderRadius: 6, background: 'rgba(59,130,246,0.1)', color: '#3b82f6', fontWeight: 600 }}>
                  {problem.affected_area_km2} km²
                </span>
              )}
              {problem.wow_delta != null && typeof problem.wow_delta === 'number' && (
                <WowBadge delta={problem.wow_delta} direction={problem.wow_direction} />
              )}
              {problem.wow_delta != null && typeof problem.wow_delta === 'object' && (
                <>
                  <WowBadge delta={problem.wow_delta.temp_delta} direction={problem.wow_delta.temp_delta > 0 ? 'worsening' : 'improving'} label="T " />
                  <WowBadge delta={problem.wow_delta.aqi_delta} direction={problem.wow_delta.aqi_delta > 0 ? 'worsening' : 'improving'} label="AQI " />
                </>
              )}
              {problem.hotspot_intensity > 0 && (
                <span style={{ fontSize: 9, padding: '1px 6px', borderRadius: 6, background: 'rgba(249,115,22,0.1)', color: '#f97316', fontWeight: 600 }}>
                  Intensity: {(problem.hotspot_intensity * 100).toFixed(0)}%
                </span>
              )}
            </div>

            {/* Cross Parameter Context */}
            <CrossParamBadges context={problem.cross_parameter_context} />

            {/* Municipal Controls */}
            <div className="municipal-controls" style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid rgba(148, 163, 184, 0.1)', display: 'flex', flexDirection: 'column', gap: 12 }}>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>👤 Assign Task To</div>
                <select 
                  style={{
                    background: 'var(--bg-card)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', 
                    padding: '4px 8px', borderRadius: 6, fontSize: 12, outline: 'none', cursor: 'pointer'
                  }}
                  value={taskAssignees[idx] || (problem.assigned_to || 'Unassigned')}
                  onChange={(e) => { e.stopPropagation(); setTaskAssignees(prev => ({ ...prev, [idx]: e.target.value })); }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <option value="Unassigned">Unassigned</option>
                  <option value="Mayor's Crisis Team">Mayor's Crisis Team</option>
                  <option value="Environmental Agency">Environmental Agency</option>
                  <option value="Public Works Dept">Public Works Dept</option>
                  <option value="Health Department">Health Department</option>
                </select>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>⚡ Urgency Override</div>
                <div style={{ display: 'flex', gap: 4, background: 'var(--bg-secondary)', padding: 4, borderRadius: 8, border: '1px solid var(--border-color)' }}>
                  {['Standard', 'Elevated', 'Critical'].map(u => (
                    <button
                      key={u}
                      style={{
                        background: (taskUrgencies[idx] || 'Standard') === u ? 'var(--bg-hover)' : 'transparent',
                        color: (taskUrgencies[idx] || 'Standard') === u ? 'var(--text-primary)' : 'var(--text-muted)',
                        border: 'none', padding: '4px 10px', borderRadius: 4, fontSize: 10, fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s'
                      }}
                      onClick={(e) => { e.stopPropagation(); setTaskUrgencies(prev => ({ ...prev, [idx]: u })); }}
                    >
                      {u}
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>{getStatusIcon(status)} Resolution Status</div>
                <div className="municipal-status-toggles" style={{ display: 'flex', gap: 4 }}>
                  {['pending', 'in_progress', 'completed'].map(s => (
                    <button
                      key={s}
                      className={`municipal-status-btn ${status === s ? 'active' : ''}`}
                      style={{
                        ...(status === s ? { background: getStatusColor(s), color: '#fff', borderColor: getStatusColor(s) } : { background: 'transparent' }),
                        border: '1px solid var(--border-color)', padding: '4px 10px', borderRadius: 12, fontSize: 10, fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s'
                      }}
                      onClick={(e) => { e.stopPropagation(); setTaskStatuses(prev => ({ ...prev, [idx]: s })); }}
                    >
                      {s === 'pending' ? 'Pending' : s === 'in_progress' ? 'In Progress' : 'Completed'}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Click Hint */}
            <div className="municipal-card-click-hint">
              🔍 Click for full details
            </div>
          </div>
        );
      })}

      {/* Footer */}
      <div className="municipal-footer">
        Generated at {new Date(dashboardData.generated_at).toLocaleString()} | SatIntel Environmental Intelligence
      </div>

      {/* ═══ DETAIL MODAL ═══ */}
      {selectedProblem && (
        <div className="municipal-modal-overlay" onClick={() => setSelectedProblem(null)}>
          <div className="municipal-modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="municipal-modal-close" onClick={() => setSelectedProblem(null)}>✕</button>

            {/* Modal Header */}
            <div className="municipal-modal-header">
              <div className="municipal-modal-icon">{selectedProblem.icon}</div>
              <div>
                <div className="municipal-modal-title">{selectedProblem.title}</div>
                <div className="municipal-modal-location">📍 {selectedProblem.location?.area_description}</div>
              </div>
            </div>

            {/* Current Values */}
            <div className="municipal-modal-section">
              <div className="municipal-modal-section-title">📊 Current Values</div>
              {selectedProblem.parameter === 'multi_factor' ? (
                <div className="municipal-values" style={{ background: 'rgba(239, 68, 68, 0.1)' }}>
                  <div className="municipal-value-item">
                    <span className="municipal-value-label" style={{ color: '#fca5a5' }}>Peak Temp</span>
                    <span className="municipal-value-num" style={{ color: '#ef4444' }}>{selectedProblem.current_values?.temp_val}</span>
                  </div>
                  <div className="municipal-value-item">
                    <span className="municipal-value-label" style={{ color: '#fca5a5' }}>Peak AQI</span>
                    <span className="municipal-value-num" style={{ color: '#f97316' }}>{selectedProblem.current_values?.aqi_val}</span>
                  </div>
                  <div className="municipal-value-item">
                    <span className="municipal-value-label" style={{ color: '#fca5a5' }}>P95 Temp</span>
                    <span className="municipal-value-num" style={{ color: '#ef4444' }}>{selectedProblem.current_values?.p95_temp}</span>
                  </div>
                  <div className="municipal-value-item">
                    <span className="municipal-value-label" style={{ color: '#fca5a5' }}>P95 AQI</span>
                    <span className="municipal-value-num" style={{ color: '#f97316' }}>{selectedProblem.current_values?.p95_aqi}</span>
                  </div>
                  <div className="municipal-value-item">
                    <span className="municipal-value-label" style={{ color: '#fca5a5' }}>Zones Affected</span>
                    <span className="municipal-value-num" style={{ color: '#ef4444' }}>{selectedProblem.hotspot_clusters}</span>
                  </div>
                </div>
              ) : (
                <div className="municipal-values">
                  <div className="municipal-value-item">
                    <span className="municipal-value-label">Mean</span>
                    <span className="municipal-value-num">{selectedProblem.current_values?.mean} {selectedProblem.current_values?.unit}</span>
                  </div>
                  <div className="municipal-value-item">
                    <span className="municipal-value-label">Max</span>
                    <span className="municipal-value-num" style={{ color: '#ef4444' }}>{selectedProblem.current_values?.max} {selectedProblem.current_values?.unit}</span>
                  </div>
                  {selectedProblem.current_values?.p95 != null && (
                    <div className="municipal-value-item">
                      <span className="municipal-value-label" style={{ color: '#f97316' }}>P95</span>
                      <span className="municipal-value-num">{selectedProblem.current_values.p95} {selectedProblem.current_values?.unit}</span>
                    </div>
                  )}
                  {selectedProblem.current_values?.std_dev != null && (
                    <div className="municipal-value-item">
                      <span className="municipal-value-label">Std Dev (σ)</span>
                      <span className="municipal-value-num">{selectedProblem.current_values.std_dev}</span>
                    </div>
                  )}
                  {selectedProblem.hotspot_clusters > 0 && (
                    <div className="municipal-value-item">
                      <span className="municipal-value-label">Hotspots</span>
                      <span className="municipal-value-num">{selectedProblem.hotspot_clusters} clusters</span>
                    </div>
                  )}
                </div>
              )}

              {/* Enriched stats in modal */}
              <div style={{
                display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 10,
                padding: '6px 8px', background: 'rgba(148,163,184,0.04)',
                borderRadius: 6, border: '1px solid rgba(148,163,184,0.08)',
              }}>
                {selectedProblem.spatial_coverage_pct != null && (
                  <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 8, background: 'rgba(239,68,68,0.1)', color: '#ef4444', fontWeight: 600 }}>
                    📐 {selectedProblem.spatial_coverage_pct}% grid exceeded
                  </span>
                )}
                {selectedProblem.affected_area_km2 != null && (
                  <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 8, background: 'rgba(59,130,246,0.1)', color: '#3b82f6', fontWeight: 600 }}>
                    📏 {selectedProblem.affected_area_km2} km² affected
                  </span>
                )}
                {selectedProblem.wow_delta != null && typeof selectedProblem.wow_delta === 'number' && (
                  <WowBadge delta={selectedProblem.wow_delta} direction={selectedProblem.wow_direction} />
                )}
                {selectedProblem.wow_delta != null && typeof selectedProblem.wow_delta === 'object' && (
                  <>
                    <WowBadge delta={selectedProblem.wow_delta.temp_delta} direction={selectedProblem.wow_delta.temp_delta > 0 ? 'worsening' : 'improving'} label="Temp " />
                    <WowBadge delta={selectedProblem.wow_delta.aqi_delta} direction={selectedProblem.wow_delta.aqi_delta > 0 ? 'worsening' : 'improving'} label="AQI " />
                  </>
                )}
                {selectedProblem.hotspot_intensity > 0 && (
                  <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 8, background: 'rgba(249,115,22,0.1)', color: '#f97316', fontWeight: 600 }}>
                    🔥 Intensity: {(selectedProblem.hotspot_intensity * 100).toFixed(0)}%
                  </span>
                )}
              </div>

              {/* Cross-parameter context in modal */}
              <CrossParamBadges context={selectedProblem.cross_parameter_context} />
            </div>

            {/* Solutions */}
            <div className="municipal-modal-section">
              <div className="municipal-modal-section-title">💡 Recommended Solutions</div>
              {selectedProblem.solutions?.map((sol, sIdx) => (
                <div key={sIdx} className="municipal-solution-item">
                  <div className="municipal-solution-action">{sol.action}</div>
                  <div className="municipal-solution-meta">
                    <span>⏱️ {sol.timeline}</span>
                    <span>💰 {sol.cost}</span>
                    <span>📊 {sol.effectiveness}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Impact Projection */}
            <div className="municipal-modal-section">
              <div className="municipal-modal-section-title">📈 Projected Impact</div>
              <div className="municipal-impact-row">
                <div className="municipal-impact-item">
                  <span className="municipal-impact-label">After 7 days</span>
                  <span className="municipal-impact-text">{selectedProblem.impact_projection?.after_7_days}</span>
                </div>
                <div className="municipal-impact-item">
                  <span className="municipal-impact-label">After 10 days</span>
                  <span className="municipal-impact-text">{selectedProblem.impact_projection?.after_10_days}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
