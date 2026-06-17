import apiClient from './client';

export const fdaApi = {
  searchDrug: async (drugName) => {
    const response = await apiClient.post('/fda/drug-search', { drug_name: drugName });
    return response.data;
  },
  
  searchReaction: async (reactionName) => {
    const response = await apiClient.post('/fda/reaction-search', { reaction: reactionName });
    return response.data;
  },
  
  getSignalSummary: async (drugName) => {
    const response = await apiClient.post('/fda/signal-summary', { drug_name: drugName });
    return response.data;
  }
};
