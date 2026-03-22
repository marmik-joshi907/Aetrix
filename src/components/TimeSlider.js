import React, { useState, useEffect, useRef } from 'react';

export default function TimeSlider({ totalWeeks, currentWeek, timestamps, onChange }) {
  const [playing, setPlaying] = useState(false);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (playing) {
      intervalRef.current = setInterval(() => {
        onChange((prev) => {
          const next = prev + 1;
          if (next >= totalWeeks) {
            setPlaying(false);
            return 0;
          }
          return next;
        });
      }, 1200);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [playing, totalWeeks, onChange]);

  const currentDate = timestamps && timestamps[currentWeek]
    ? timestamps[currentWeek]
    : `Week ${currentWeek + 1}`;

  return (
    <div className="time-slider-container">
      <div className="time-slider-header">
        <span className="time-slider-label">⏱️ Timeline</span>
        <span className="time-slider-date">{currentDate}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <button
          className="play-btn"
          onClick={() => setPlaying(!playing)}
          aria-label={playing ? 'Pause' : 'Play'}
        >
          {playing ? '⏸' : '▶'}
        </button>
        <input
          type="range"
          className="time-slider"
          min={0}
          max={totalWeeks - 1}
          value={currentWeek}
          onChange={(e) => {
            setPlaying(false);
            onChange(parseInt(e.target.value));
          }}
        />
      </div>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        fontSize: 10, 
        color: 'var(--text-muted)',
        marginTop: 4
      }}>
        <span>W1</span>
        <span>W{totalWeeks}</span>
      </div>
    </div>
  );
}
