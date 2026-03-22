import React, { useState } from 'react';

export default function MunicipalDashboard({ dashboardData, loading }) {
  const [taskStatuses, setTaskStatuses] = useState({});
  const [taskAssignees, setTaskAssignees] = useState({});
  const [taskUrgencies, setTaskUrgencies] = useState({});

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

  const toggleStatus = (idx) => {
    setTaskStatuses(prev => {
      const current = prev[idx] || 'pending';
      const next = current === 'pending' ? 'in_progress' : current === 'in_progress' ? 'completed' : 'pending';
      return { ...prev, [idx]: next };
    });
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
            <div className="municipal-subtitle">{dashboardData.city} · {dashboardData.analysis_date}</div>
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
        const statusColor = getStatusColor(status);
        const priorityColors = ['#ef4444', '#f97316', '#eab308'];
        const priorityColor = priorityColors[idx] || '#94a3b8';

        return (
          <div
            key={idx}
            className="municipal-problem-card"
            style={{ animationDelay: `${idx * 0.15}s` }}
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
                  <span className="municipal-value-label">Max</span>
                  <span className="municipal-value-num" style={{ color: '#ef4444' }}>{problem.current_values?.max} {problem.current_values?.unit}</span>
                </div>
                {problem.hotspot_clusters > 0 && (
                  <div className="municipal-value-item">
                    <span className="municipal-value-label">Hotspots</span>
                    <span className="municipal-value-num">{problem.hotspot_clusters} clusters</span>
                  </div>
                )}
              </div>
            )}

            {/* Solutions */}
            <div className="municipal-solutions">
              <div className="municipal-solutions-title">💡 Recommended Solutions</div>
              {problem.solutions?.map((sol, sIdx) => (
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
            <div className="municipal-impact">
              <div className="municipal-impact-title">📈 Projected Impact</div>
              <div className="municipal-impact-row">
                <div className="municipal-impact-item">
                  <span className="municipal-impact-label">After 7 days</span>
                  <span className="municipal-impact-text">{problem.impact_projection?.after_7_days}</span>
                </div>
                <div className="municipal-impact-item">
                  <span className="municipal-impact-label">After 10 days</span>
                  <span className="municipal-impact-text">{problem.impact_projection?.after_10_days}</span>
                </div>
              </div>
            </div>

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
                  onChange={(e) => setTaskAssignees(prev => ({ ...prev, [idx]: e.target.value }))}
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
                      onClick={() => setTaskUrgencies(prev => ({ ...prev, [idx]: u }))}
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
                      onClick={() => setTaskStatuses(prev => ({ ...prev, [idx]: s }))}
                    >
                      {s === 'pending' ? 'Pending' : s === 'in_progress' ? 'In Progress' : 'Completed'}
                    </button>
                  ))}
                </div>
              </div>

            </div>
          </div>
        );
      })}

      {/* Footer */}
      <div className="municipal-footer">
        Generated at {new Date(dashboardData.generated_at).toLocaleString()} | SatIntel Environmental Intelligence
      </div>
    </div>
  );
}
