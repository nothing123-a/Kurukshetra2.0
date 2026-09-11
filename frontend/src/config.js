// API Configuration
const isDevelopment = import.meta.env.DEV || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
const LOCALHOST_API = `${window.location.protocol}//${window.location.hostname || 'localhost'}:8000`
const PRODUCTION_API = 'https://refinify-backend.onrender.com'

// Ensure API_BASE_URL always has full URL
let apiUrl = import.meta.env.VITE_API_BASE_URL || (isDevelopment ? LOCALHOST_API : PRODUCTION_API)

// Fix any malformed URLs
if (apiUrl && !apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
  apiUrl = `http://${apiUrl}`
}

export const API_BASE_URL = apiUrl

console.log('🔗 API Base URL:', API_BASE_URL)

// Environment-based configuration
export const config = {
  apiBaseUrl: API_BASE_URL,
  isDevelopment,
  // Add other configuration options here
};
