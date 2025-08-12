// Utility to ensure API URL has protocol
export const getAPIBaseURL = (): string => {
  let apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:3001';
  
  // Add protocol if missing
  if (apiUrl && !apiUrl.startsWith('http')) {
    apiUrl = `https://${apiUrl}`;
  }
  
  // Remove trailing slash if present
  if (apiUrl.endsWith('/')) {
    apiUrl = apiUrl.slice(0, -1);
  }
  
  return apiUrl;
};

export const API_BASE_URL = getAPIBaseURL();