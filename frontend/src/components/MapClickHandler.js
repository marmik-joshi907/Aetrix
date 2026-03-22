import { useMapEvents } from 'react-leaflet';

export default function MapClickHandler({ onMapClick, activeSpatialTool, setDrawnPolygon, setComparePins }) {
  useMapEvents({
    click: (e) => {
      // 1. Draw mode
      if (activeSpatialTool === 'draw') {
        setDrawnPolygon(prev => [...prev, [e.latlng.lat, e.latlng.lng]]);
        return;
      }
      
      // 2. Compare mode
      if (activeSpatialTool === 'compare') {
        setComparePins(prev => {
          if (prev.length >= 2) return [[e.latlng.lat, e.latlng.lng]];
          return [...prev, [e.latlng.lat, e.latlng.lng]];
        });
        return;
      }
      
      // 3. Default click
      if (onMapClick) {
        onMapClick(e.latlng.lat, e.latlng.lng);
      }
    },
    // Right click to undo last draw point
    contextmenu: (e) => {
      if (activeSpatialTool === 'draw' && setDrawnPolygon) {
        setDrawnPolygon(prev => prev.slice(0, -1));
      }
    }
  });
  return null;
}
