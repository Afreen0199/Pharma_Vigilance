import apiClient from './client';

export const chatApi = {
  // Chat with the copilot in the context of a specific case analysis
  askQuestion: async (analysisId, question) => {
    const response = await apiClient.post(`/chat/${analysisId}`, { question });
    return response.data;
  },

  // Reset chat memory for an analysis session
  resetChat: async (analysisId) => {
    const response = await apiClient.delete(`/chat/${analysisId}`);
    return response.data;
  }
};
