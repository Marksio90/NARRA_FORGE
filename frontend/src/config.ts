/**
 * Application configuration - loaded from environment variables at build time.
 *
 * Set REACT_APP_API_URL in .env or docker-compose to point to the backend.
 * Defaults to http://localhost:8000 for local development.
 */

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
export const API_URL = `${API_BASE_URL}/api`;
