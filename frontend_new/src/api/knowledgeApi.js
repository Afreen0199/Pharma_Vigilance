import apiClient from './client';

export const knowledgeApi = {
  // Upload a document to the knowledge base (PDF, CSV, DOCX, TXT)
  upload: async (formData) => {
    const response = await apiClient.post('/knowledgebase/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // List all documents indexed in the knowledge base
  list: async (collectionName = 'knowledge_base') => {
    const response = await apiClient.get(`/knowledgebase/list?collection_name=${collectionName}`);
    return response.data;
  },

  // Delete a document from the knowledge base
  deleteDocument: async (documentName, collectionName = 'knowledge_base') => {
    const response = await apiClient.delete(
      `/knowledgebase/document?document_name=${encodeURIComponent(documentName)}&collection_name=${collectionName}`
    );
    return response.data;
  },
};
