// API configuration for the study agent application

// Backend API URL - change this if your backend server runs on a different port
// Support both environment variable names for better compatibility
export const BACKEND_API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// API endpoints
export const API_ENDPOINTS = {
  CHAT: '/chat/chat',
  PREVIEW: '/preview',
  UPLOAD: '/upload',
  STRUCTURE_PLAN: '/plan/structure-plan',
  GENERATE_PLAN: '/plan/generate-plan'
};

// Helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  return `${BACKEND_API_URL}${endpoint}`;
};
