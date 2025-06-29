import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 45000, // Increased timeout for LinkedIn scraping
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

// LinkedIn scraper service functions
export const linkedInService = {
  searchJobs: async (params) => {
    try {
      const response = await api.get('/services/api/suggestions/jobs', { params });
      return response.data;
    } catch (error) {
      console.error('Job search failed:', error);
      throw error;
    }
  },

  getCompanyInfo: async (companyName) => {
    try {
      const response = await api.get('/services/api/suggestions/companies', { 
        params: { company_name: companyName } 
      });
      return response.data;
    } catch (error) {
      console.error('Company lookup failed:', error);
      throw error;
    }
  }
};

export default api;