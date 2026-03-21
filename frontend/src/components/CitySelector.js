import React from 'react';
import { CITIES } from '../utils/constants';

export default function CitySelector({ currentCity, onCityChange, loading }) {
  return (
    <div className="city-selector">
      <select
        className="city-select"
        value={currentCity}
        onChange={(e) => onCityChange(e.target.value)}
        disabled={loading}
      >
        {CITIES.map((city) => (
          <option key={city.name} value={city.name}>
            📍 {city.name}
          </option>
        ))}
      </select>
    </div>
  );
}
