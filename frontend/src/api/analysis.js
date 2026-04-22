import api from './client';

export const getAnalysis = async (fileId) => {
  const response = await api.get(`/analysis/history/${fileId}`);
  return response.data;
};

export const runAnalysis = async (data) => {
  const response = await api.post('/analysis/run', data);
  return response.data;
};

export const quickSummary = async (fileId) => {
  const response = await api.post(`/prediction/quick-summary/${fileId}`);
  return response.data;
};
