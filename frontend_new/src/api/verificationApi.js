import apiClient from './client';

export const verificationApi = {
  // Retrieve OpenFDA, FAERS, KB evidence for a drug
  verifyDrug: async (drugName) => {
    const response = await apiClient.get(`/verify-drug/${drugName}`);
    return response.data;
  },

  // Verify claims for a specific analysis
  verifyAnalysis: async (analysisId) => {
    const response = await apiClient.get(`/verify-analysis/${analysisId}`);
    return response.data;
  },

  // Get full supporting evidence details for a case analysis
  getEvidence: async (analysisId) => {
    const response = await apiClient.get(`/evidence/${analysisId}`);
    return response.data;
  }
};
