import apiClient from './client';

export const reportApi = {
  // Generate or retrieve full case report
  generateReport: async (analysisId) => {
    const response = await apiClient.post('/report/generate', { analysis_id: analysisId });
    return response.data;
  },

  // Check the status of a report generation
  getReportStatus: async (analysisId) => {
    const response = await apiClient.get(`/report/status/${analysisId}`);
    return response.data;
  },

  // Download URL helper
  getDownloadUrl: (reportId, format) => {
    return `${apiClient.defaults.baseURL}/report/download/${reportId}?format=${format}`;
  }
};
