import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const fdaApi = {
  searchDrug: async (drugName) => {
    const response = await api.post('/fda/drug-search', { drug_name: drugName });
    return response.data;
  },
  
  searchReaction: async (reactionName) => {
    const response = await api.post('/fda/reaction-search', { reaction: reactionName });
    return response.data;
  },
  
  getSignalSummary: async (drugName) => {
    const response = await api.post('/fda/signal-summary', { drug_name: drugName });
    return response.data;
  },
  
  verifyDrug: async (drugName) => {
    const response = await api.get(`/verify-drug/${drugName}`);
    return response.data;
  }
};
