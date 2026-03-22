/**
 * Redux store for kepler.gl integration.
 *
 * KEPLER.GL GOTCHAS:
 * 1. The reducer MUST be mounted under the key "keplerGl" (exact spelling)
 * 2. Use enhanceReduxMiddleware() from @kepler.gl/reducers
 * 3. Initialize with activeSidePanel: null and currentModal: null to hide default UI
 */
import { createStore, combineReducers, applyMiddleware, compose } from 'redux';
import keplerGlReducer, { enhanceReduxMiddleware } from '@kepler.gl/reducers';

// Initialize kepler reducer with clean UI state (no modals on load)
const customizedKeplerGlReducer = keplerGlReducer.initialState({
  uiState: {
    activeSidePanel: null,   // Hide side panel by default
    currentModal: null,      // Suppress the "Add Data" modal on startup
    mapControls: {
      visibleLayers: { show: true },
      mapLegend: { show: true, active: true },
      toggle3d: { show: true },
      splitMap: { show: false },
    },
  },
});

// Combine reducers — "keplerGl" key is MANDATORY for kepler.gl to work
const rootReducer = combineReducers({
  keplerGl: customizedKeplerGlReducer,
});

// Create store with enhanced middleware for kepler.gl async actions
const middlewares = enhanceReduxMiddleware([]);
const enhancers = [applyMiddleware(...middlewares)];

// Add Redux DevTools if available
const composeEnhancers =
  typeof window !== 'undefined' && window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__
    ? window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__({ serialize: true })
    : compose;

const store = createStore(rootReducer, {}, composeEnhancers(...enhancers));

export default store;
