import apiClient from './client';

export const analysisApi = {
  // Fetch all recent analyses for the dashboard
  getAllAnalyses: async () => {
    const response = await apiClient.get('/analyze/');
    return response.data;
  },
  
  // Upload a case document (PDF/TXT/IMG)
  uploadCase: async (formData) => {
    const response = await apiClient.post('/analyze/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Process a text narrative instead of a file
  analyzeText: async (text) => {
    const response = await apiClient.post('/analyze/text', { text });
    return response.data;
  }
};
