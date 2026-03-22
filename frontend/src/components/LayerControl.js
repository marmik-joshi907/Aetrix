import React from 'react';
import { LAYERS } from '../utils/constants';

export default function LayerControl({ activeLayer, onLayerChange }) {
  return (
    <div className="card">
      <div className="card-title">📡 Data Layers</div>
      {Object.entries(LAYERS).map(([key, layer]) => (
        <div
          key={key}
          className={`layer-item ${activeLayer === key ? 'active' : ''}`}
          onClick={() => onLayerChange(key)}
        >
          <button
            className={`layer-toggle ${activeLayer === key ? 'on' : 'off'}`}
            aria-label={`Toggle ${layer.name}`}
          />
          <div>
            <div className="layer-name">
              {layer.icon} {layer.name}
            </div>
            <div className="layer-desc">{layer.description}</div>
          </div>
        </div>
      ))}
      
      {/* Color Legend */}
      {activeLayer && LAYERS[activeLayer] && (
        <div style={{ marginTop: 12 }}>
          <div className="color-legend">
            <span className="legend-label">{LAYERS[activeLayer].range[0]}</span>
            <div
              className="legend-gradient"
              style={{ background: LAYERS[activeLayer].gradient }}
            />
            <span className="legend-label" style={{ textAlign: 'right' }}>
              {LAYERS[activeLayer].range[1]}
            </span>
          </div>
          <div style={{ textAlign: 'center', fontSize: 10, color: 'var(--text-muted)' }}>
            {LAYERS[activeLayer].unit}
          </div>
        </div>
      )}
    </div>
  );
}
