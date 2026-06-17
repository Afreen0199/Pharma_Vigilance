import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const kbApi = {
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/knowledgebase/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  listDocuments: async (collectionName = 'knowledge_base') => {
    const response = await api.get(`/knowledgebase/list?collection_name=${collectionName}`);
    return response.data;
  },
  
  deleteDocument: async (documentName, collectionName = 'knowledge_base') => {
    const response = await api.delete(
      `/knowledgebase/document?document_name=${encodeURIComponent(documentName)}&collection_name=${collectionName}`
    );
    return response.data;
  }
};
