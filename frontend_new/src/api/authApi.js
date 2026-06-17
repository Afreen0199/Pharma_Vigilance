import apiClient from './client';

export const authApi = {
  login: async (email, password) => {
    const response = await apiClient.post('/auth/login', { email, password });
    return response.data;
  },
  
  register: async (email, password) => {
    const response = await apiClient.post('/auth/register', { email, password });
    return response.data;
  }
};
