import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Set JWT Token headers dynamically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const analysisApi = {
  analyze: async (file, text) => {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    if (text) {
      formData.append('text', text);
    }
    const response = await api.post('/analyze/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  listAnalyses: async () => {
    const response = await api.get('/analyze/');
    return response.data;
  },
  
  generateReport: async (analysisId, force = false) => {
    const response = await api.post('/report/generate', {
      analysis_id: analysisId,
      force
    });
    return response.data;
  },
  
  getReportStatus: async (analysisId) => {
    const response = await api.get(`/report/status/${analysisId}`);
    return response.data;
  },
  
  getVerificationDetails: async (analysisId) => {
    const response = await api.get(`/verify-analysis/${analysisId}`);
    return response.data;
  },
  
  getEvidenceDetails: async (analysisId) => {
    const response = await api.get(`/evidence/${analysisId}`);
    return response.data;
  },
  
  getDownloadUrl: (reportId, format) => {
    return `${API_BASE_URL}/report/download/${reportId}?format=${format}`;
  }
};
