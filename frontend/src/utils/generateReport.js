/**
 * generateReport.js
 * Generates a detailed, structured PDF Environmental Intelligence Report
 * using the jsPDF library loaded via CDN (window.jspdf).
 */

const COLORS = {
  primary:   [10, 15, 30],
  green:     [5, 150, 105],
  red:       [220, 38, 38],
  orange:    [234, 88, 12],
  amber:     [161, 98, 7],
  gray:      [100, 116, 139],
  lightGray: [241, 245, 249],
  white:     [255, 255, 255],
  black:     [0, 0, 0],
};

function hexToRgb(hex) {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return [r, g, b];
}

function drawHeader(doc, cityName) {
  const pageW = doc.internal.pageSize.getWidth();

  // Dark header banner
  doc.setFillColor(...COLORS.primary);
  doc.rect(0, 0, pageW, 40, 'F');

  // Satellite icon text
  doc.setFontSize(10);
  doc.setTextColor(...COLORS.green);
  doc.text('🛰️  SATINTEL PLATFORM', 14, 14);

  // Title
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...COLORS.white);
  doc.text('Environmental Intelligence Report', 14, 26);

  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(156, 163, 175);
  doc.text(`${cityName}  ·  Generated ${new Date().toLocaleString()}`, 14, 35);

  return 50; // return the Y cursor after header
}

function drawSectionTitle(doc, text, y) {
  const pageW = doc.internal.pageSize.getWidth();
  doc.setFillColor(...COLORS.lightGray);
  doc.rect(14, y - 5, pageW - 28, 10, 'F');
  doc.setFontSize(11);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...COLORS.primary);
  doc.text(text, 16, y + 2);
  return y + 14;
}

function maybeAddPage(doc, y, needed = 30) {
  if (y + needed > doc.internal.pageSize.getHeight() - 20) {
    doc.addPage();
    return 20;
  }
  return y;
}

export function generatePdfReport({ cityName, activeLayer, gridData, hotspots, municipalData, earlyWarningData, actionPlan }) {
  const { jspdf } = window;
  if (!jspdf) {
    alert('PDF library not loaded yet. Please wait a moment and try again.');
    return;
  }

  const { jsPDF } = jspdf;
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const pageW = doc.internal.pageSize.getWidth();
  let y = drawHeader(doc, cityName || 'Ahmedabad');

  // ── SECTION 1: CITY OVERVIEW ─────────────────────────────────
  y = drawSectionTitle(doc, '1.  City Environmental Overview', y);

  const overviewRows = [
    ['City', cityName || 'Ahmedabad'],
    ['Analysis Date', new Date().toLocaleDateString()],
    ['Active Parameter', (activeLayer || '').toUpperCase()],
    ['City Mean Value', gridData?.stats?.mean != null ? `${gridData.stats.mean.toFixed(2)} ${gridData.unit}` : 'N/A'],
    ['Critical Peak Value', gridData?.stats?.max != null ? `${gridData.stats.max.toFixed(2)} ${gridData.unit}` : 'N/A'],
    ['Identified Hotspot Clusters', String(hotspots?.num_clusters || 0)],
    ['City Health Score', municipalData?.city_health_score != null ? `${municipalData.city_health_score.toFixed(0)} / 100` : 'N/A'],
    ['Total Issues Detected', String(municipalData?.total_issues_detected || 0)],
  ];

  doc.autoTable({
    startY: y,
    head: [['Metric', 'Value']],
    body: overviewRows,
    theme: 'grid',
    headStyles: { fillColor: COLORS.primary, textColor: COLORS.white, fontStyle: 'bold' },
    alternateRowStyles: { fillColor: COLORS.lightGray },
    columnStyles: { 0: { fontStyle: 'bold', cellWidth: 75 }, 1: { cellWidth: 'auto' } },
    margin: { left: 14, right: 14 },
  });
  y = doc.lastAutoTable.finalY + 12;

  // ── SECTION 2: PRIORITIZED INTERVENTIONS ─────────────────────
  if (municipalData?.top_3_urgent?.length) {
    y = maybeAddPage(doc, y, 40);
    y = drawSectionTitle(doc, '2.  Top Prioritized Municipal Interventions', y);

    const priorityColors = ['#DC2626', '#EA580C', '#D97706'];

    municipalData.top_3_urgent.forEach((problem, i) => {
      y = maybeAddPage(doc, y, 45);

      // Card header
      const cardColor = hexToRgb(priorityColors[i] || '#6B7280');
      doc.setFillColor(...cardColor);
      doc.rect(14, y, pageW - 28, 10, 'F');
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(10);
      doc.setTextColor(...COLORS.white);
      doc.text(`PRIORITY #${problem.priority_rank}  —  ${problem.title}  (Score: ${problem.priority_score})`, 17, y + 7);
      y += 13;

      // Problem stats
      const statsRows = [];
      if (problem.current_values?.temp_val) {
        statsRows.push(['Peak Temperature', problem.current_values.temp_val]);
        statsRows.push(['Peak AQI', problem.current_values.aqi_val || 'N/A']);
      } else {
        statsRows.push(['Mean Value', `${problem.current_values?.mean} ${problem.current_values?.unit}`]);
        statsRows.push(['Peak Value', `${problem.current_values?.max} ${problem.current_values?.unit}`]);
      }
      statsRows.push(['Location', problem.location?.area_description || 'N/A']);
      statsRows.push(['Hotspot Clusters', String(problem.hotspot_clusters || 0)]);

      doc.autoTable({
        startY: y,
        body: statsRows,
        theme: 'plain',
        styles: { fontSize: 9, cellPadding: 2 },
        columnStyles: { 0: { fontStyle: 'bold', cellWidth: 55, textColor: COLORS.gray }, 1: { cellWidth: 'auto' } },
        margin: { left: 18, right: 14 },
      });
      y = doc.lastAutoTable.finalY + 4;

      // Action plan
      y = maybeAddPage(doc, y, 20);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(9);
      doc.setTextColor(...COLORS.primary);
      doc.text('Prescribed Action Plan:', 18, y);
      y += 5;

      const actionRows = problem.solutions?.map((s, idx) => [
        `${idx + 1}.`,
        s.action,
        s.timeline,
        s.cost,
        s.effectiveness,
      ]) || [];

      doc.autoTable({
        startY: y,
        head: [['#', 'Action', 'Timeline', 'Budget', 'Expected Impact']],
        body: actionRows,
        theme: 'striped',
        headStyles: { fillColor: [30, 41, 59], textColor: COLORS.white, fontSize: 8 },
        styles: { fontSize: 8, cellPadding: 2 },
        columnStyles: { 0: { cellWidth: 8 }, 1: { cellWidth: 65 }, 2: { cellWidth: 22 }, 3: { cellWidth: 25 } },
        margin: { left: 18, right: 14 },
      });
      y = doc.lastAutoTable.finalY + 4;

      // Impact projection
      doc.setFillColor(224, 242, 254);
      doc.setDrawColor(186, 230, 253);
      const projHeight = 12;
      doc.rect(18, y, pageW - 32, projHeight, 'FD');
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(8.5);
      doc.setTextColor(3, 105, 161);
      doc.text(`▸ 7-Day Projection: ${problem.impact_projection?.after_7_days || 'N/A'}`, 21, y + 4.5);
      doc.text(`▸ 10-Day ROI: ${problem.impact_projection?.after_10_days || 'N/A'}`, 21, y + 9.5);
      y += projHeight + 8;
    });
  }

  // ── SECTION 3: EARLY WARNINGS ────────────────────────────────
  if (earlyWarningData?.warnings?.length) {
    y = maybeAddPage(doc, y, 40);
    y = drawSectionTitle(doc, '3.  Automated 7-Day Risk Forecasts', y);

    const warnRows = earlyWarningData.warnings.map((w, i) => [
      `${i + 1}`,
      (w.parameter || '').toUpperCase(),
      w.risk_level || 'MODERATE',
      w.trend_summary || w.message || 'Trend detected',
    ]);

    doc.autoTable({
      startY: y,
      head: [['#', 'Parameter', 'Risk Level', 'Forecast Summary']],
      body: warnRows,
      theme: 'grid',
      headStyles: { fillColor: COLORS.primary, textColor: COLORS.white, fontStyle: 'bold', fontSize: 9 },
      alternateRowStyles: { fillColor: COLORS.lightGray },
      styles: { fontSize: 9, cellPadding: 3 },
      columnStyles: { 0: { cellWidth: 8 }, 1: { cellWidth: 30 }, 2: { cellWidth: 28 } },
      margin: { left: 14, right: 14 },
    });
    y = doc.lastAutoTable.finalY + 12;
  }

  // ── SECTION 4: ACTION PLAN SUMMARY ───────────────────────────
  if (actionPlan?.recommendations?.length) {
    y = maybeAddPage(doc, y, 40);
    y = drawSectionTitle(doc, '4.  AI-Generated Action Plan Summary', y);

    const recRows = actionPlan.recommendations.map((r, i) => [
      `${i + 1}`,
      r.category || '',
      r.severity || '',
      (r.actions || []).slice(0, 2).join('; '),
    ]);

    doc.autoTable({
      startY: y,
      head: [['#', 'Category', 'Severity', 'Key Actions']],
      body: recRows,
      theme: 'striped',
      headStyles: { fillColor: [30, 41, 59], textColor: COLORS.white, fontSize: 9 },
      styles: { fontSize: 8.5, cellPadding: 3 },
      columnStyles: { 0: { cellWidth: 8 }, 1: { cellWidth: 35 }, 2: { cellWidth: 22 } },
      margin: { left: 14, right: 14 },
    });
    y = doc.lastAutoTable.finalY + 12;
  }

  // ── FOOTER on every page ─────────────────────────────────────
  const totalPages = doc.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(...COLORS.gray);
    doc.text(
      `SatIntel Environmental Intelligence Platform  ·  Confidential  ·  Page ${i} of ${totalPages}`,
      14,
      doc.internal.pageSize.getHeight() - 8
    );
  }

  doc.save(`SatIntel_Report_${cityName}_${new Date().toISOString().slice(0,10)}.pdf`);
}
