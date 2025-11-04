// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// App Configuration
export const APP_NAME = 'StegoGen';
export const APP_VERSION = '2.0.0';

// File Limits
export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
export const MAX_PAYLOAD_SIZE = 10 * 1024 * 1024; // 10MB

// Supported Formats
export const SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'];
export const SUPPORTED_AUDIO_FORMATS = ['.wav'];
export const SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv'];

// LocalStorage Keys
export const STORAGE_KEYS = {
  THEME: 'theme',
  HISTORY: 'stego_history',
  PRESETS: 'stego_presets',
  SETTINGS: 'user_settings'
};

export default {
  API_BASE_URL,
  APP_NAME,
  APP_VERSION,
  MAX_FILE_SIZE,
  MAX_PAYLOAD_SIZE,
  SUPPORTED_IMAGE_FORMATS,
  SUPPORTED_AUDIO_FORMATS,
  SUPPORTED_VIDEO_FORMATS,
  STORAGE_KEYS
};