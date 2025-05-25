// API configuration for the study agent application

// Backend API URL - change this if your backend server runs on a different port
export const BACKEND_API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// API endpoints
export const API_ENDPOINTS = {
  CHAT: '/chat',
  STUDY_PLAN: '/study-plan',
  UPLOAD: '/upload'
};

// Helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  return `${BACKEND_API_URL}${endpoint}`;
};
