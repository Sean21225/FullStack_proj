import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// LinkedIn Services API calls
export const linkedinService = {
  // Search for jobs on LinkedIn
  searchJobs: async (params) => {
    const { keywords, location, experience_level, limit = 10 } = params;
    const queryParams = new URLSearchParams({
      keywords,
      limit: limit.toString(),
      ...(location && { location }),
      ...(experience_level && { experience_level })
    });
    
    const response = await api.get(`/services/api/suggestions/jobs?${queryParams}`);
    return response.data;
  },

  // Get company information
  getCompanyInfo: async (companyName) => {
    const queryParams = new URLSearchParams({
      company_name: companyName
    });
    
    const response = await api.get(`/services/api/suggestions/companies?${queryParams}`);
    return response.data;
  },

  // Get personalized job suggestions based on skills
  getPersonalizedJobs: async (skills, location = null) => {
    const response = await api.post('/services/api/personalized/jobs', {
      skills,
      location
    });
    return response.data;
  }
};

export default api;