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

export const chatbotApi = {
  sendMessage: async (analysisId, question) => {
    const response = await api.post(`/chat/${analysisId}`, { question });
    return response.data;
  },
  resetSession: async (analysisId) => {
    const response = await api.delete(`/chat/${analysisId}`);
    return response.data;
  }
};
