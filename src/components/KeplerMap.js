/**
 * KeplerMap.js — Kepler.gl 3D Map component for the Analytics view.
 *
 * Renders satellite environmental data (temperature, NDVI, pollution, soil moisture)
 * on a 3D interactive map using kepler.gl with deck.gl WebGL layers.
 *
 * Uses AutoSizer for responsive sizing and loads data from the backend API.
 */
import React, { useEffect, useCallback, useState } from 'react';
import { useDispatch } from 'react-redux';
import KeplerGl from '@kepler.gl/components';
import { addDataToMap, updateMap } from '@kepler.gl/actions';
import { processCsvData } from '@kepler.gl/processors';
import AutoSizer from 'react-virtualized/dist/commonjs/AutoSizer';
import { getGridData } from '../services/api';
import { CITIES } from '../utils/constants';

// Free Mapbox token (kepler.gl demo token) — replace with your own for production
const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN || 'pk.eyJ1IjoidWJlcmRhdGEiLCJhIjoiY2pwY3owbGFxMDVwNTNxcXdwMms2OWtzbiJ9.1PPVl0VLUQgqrosrI2nUhg';

// Custom dark theme to match the SatIntel platform aesthetic
const KEPLER_THEME = {
  sidePanelBg: '#0a0f1e',
  sidePanelHeaderBg: '#0d1424',
  titleTextColor: '#f1f5f9',
  subtextColor: '#64748b',
  subtextColorActive: '#10b981',
  activeColor: '#10b981',
  sideBarCloseBtnBgd: '#1e293b',
  panelBackgroundHover: '#111827',
  inputBgd: '#111827',
  inputBgdHover: '#1e293b',
  inputBgdActive: '#1e293b',
  dropdownListBgd: '#111827',
  dropdownListHighlightBg: '#1e293b',
  primaryBtnBgd: '#10b981',
  primaryBtnBgdHover: '#059669',
  secondaryBtnBgd: '#1e293b',
  secondaryBtnBgdHover: '#334155',
  floatingBtnBgd: '#1e293b',
  floatingBtnBgdHover: '#334155',
  textColor: '#e2e8f0',
  textColorHl: '#f1f5f9',
  mapPanelBackgroundColor: '#0a0f1e',
  mapPanelHeaderBackgroundColor: '#0d1424',
};

/**
 * Convert grid point data to CSV string for kepler.gl ingestion.
 */
function gridDataToCsv(gridData, paramName) {
  if (!gridData?.points || gridData.points.length === 0) return null;
  const header = 'latitude,longitude,value,parameter';
  const rows = gridData.points.map(([lat, lon, val]) =>
    `${lat},${lon},${val},${paramName}`
  );
  return [header, ...rows].join('\n');
}

/**
 * Build a kepler.gl config for 3D environmental visualization.
 */
function buildKeplerConfig(cityObj) {
  return {
    version: 'v1',
    config: {
      mapState: {
        latitude: cityObj.lat,
        longitude: cityObj.lon,
        zoom: 11,
        pitch: 45,         // 3D tilt angle
        bearing: 15,       // Slight rotation for 3D effect
        dragRotate: true,
      },
      mapStyle: {
        styleType: 'dark',
      },
      visState: {
        layers: [],
        interactionConfig: {
          tooltip: { enabled: true, fieldsToShow: {} },
          brush: { enabled: false },
          geocoder: { enabled: false },
        },
      },
    },
  };
}

const KEPLER_MAP_ID = 'satintel_analytics';

export default function KeplerMap({ city = 'Ahmedabad', week = -1 }) {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const cityObj = CITIES.find(c => c.name === city) || CITIES[0];

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = ['temperature', 'ndvi', 'pollution', 'soil_moisture'];
      const paramLabels = {
        temperature: 'Temperature (°C)',
        ndvi: 'NDVI Vegetation',
        pollution: 'Pollution AQI',
        soil_moisture: 'Soil Moisture',
      };

      const responses = await Promise.all(
        params.map(p => getGridData(p, week, city, 2).catch(() => null))
      );

      const datasets = [];
      responses.forEach((res, i) => {
        if (!res?.data) return;
        const csv = gridDataToCsv(res.data, params[i]);
        if (!csv) return;

        const processedData = processCsvData(csv);
        if (processedData) {
          datasets.push({
            info: {
              id: params[i],
              label: paramLabels[params[i]] || params[i],
            },
            data: processedData,
          });
        }
      });

      if (datasets.length === 0) {
        setError('No data available. Ensure the backend is running on port 8000.');
        setLoading(false);
        return;
      }

      dispatch(
        addDataToMap({
          datasets,
          options: {
            centerMap: true,
            readOnly: false,
            keepExistingConfig: false,
          },
          config: buildKeplerConfig(cityObj),
        })
      );

      setLoading(false);
    } catch (err) {
      console.error('Kepler data load error:', err);
      setError('Failed to load environmental data for kepler.gl map.');
      setLoading(false);
    }
  }, [city, week, cityObj, dispatch]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    dispatch(
      updateMap({
        latitude: cityObj.lat,
        longitude: cityObj.lon,
        zoom: 11,
        pitch: 45,
        bearing: 15,
      })
    );
  }, [cityObj, dispatch]);

  return (
    <div className="kepler-map-container" style={{
      width: '100%',
      height: '100%',
      position: 'relative',
      background: '#0a0f1e',
    }}>
      {/* Header */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0,
        zIndex: 10,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 20px',
        background: 'linear-gradient(180deg, rgba(10,15,30,0.95) 0%, rgba(10,15,30,0) 100%)',
        pointerEvents: 'none',
      }}>
        <div style={{ pointerEvents: 'auto' }}>
          <div style={{
            fontSize: 16, fontWeight: 800, color: '#f1f5f9',
            letterSpacing: '-0.02em',
            display: 'flex', alignItems: 'center', gap: 8,
          }}>
            <span>🛰️</span> 3D Environmental Analytics
          </div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>
            {city} · Week {week === -1 ? 'Latest' : week} · kepler.gl WebGL
          </div>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          style={{
            pointerEvents: 'auto',
            padding: '6px 16px',
            background: loading ? '#1e293b' : 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: 8,
            color: '#10b981',
            fontSize: 11, fontWeight: 700,
            cursor: loading ? 'wait' : 'pointer',
            fontFamily: 'inherit',
            transition: 'all 0.2s',
          }}
        >
          {loading ? '⏳ Loading...' : '🔄 Refresh Data'}
        </button>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
          zIndex: 20,
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          background: 'rgba(10,15,30,0.85)',
          backdropFilter: 'blur(8px)',
        }}>
          <div className="loading-spinner" style={{ width: 36, height: 36, borderWidth: 3 }} />
          <div style={{ fontSize: 13, color: '#e2e8f0', marginTop: 12, fontWeight: 600 }}>
            Loading 3D environmental layers...
          </div>
          <div style={{ fontSize: 10, color: '#64748b', marginTop: 4 }}>
            Fetching satellite data for {city}
          </div>
        </div>
      )}

      {/* Error Overlay */}
      {error && !loading && (
        <div style={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 20,
          background: 'rgba(10,15,30,0.95)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: 12,
          padding: '24px 32px',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>⚠️</div>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#ef4444', marginBottom: 8 }}>
            Data Load Error
          </div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 16 }}>{error}</div>
          <button onClick={loadData} style={{
            padding: '8px 20px', background: '#10b981',
            border: 'none', borderRadius: 8,
            color: 'white', fontWeight: 600,
            cursor: 'pointer', fontFamily: 'inherit',
          }}>
            🔄 Retry
          </button>
        </div>
      )}

      {/* Kepler.gl Map — AutoSizer ensures responsive fill */}
      <AutoSizer>
        {({ height, width }) => (
          <KeplerGl
            id={KEPLER_MAP_ID}
            mapboxApiAccessToken={MAPBOX_TOKEN}
            width={width}
            height={height}
            theme={KEPLER_THEME}
          />
        )}
      </AutoSizer>
    </div>
  );
}
