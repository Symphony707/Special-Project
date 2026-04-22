import api from './client';

export const runPrediction = async (data) => {
  const response = await api.post('/prediction/run', data);
  return response.data;
};

export const autoPredict = (data) => {
  return runPrediction(data);
};

export const getPredictionHistory = async (fileId) => {
  const response = await api.get(`/prediction/history/${fileId}`);
  return response.data;
};

export const suggestTarget = async (fileId) => {
  const response = await api.get(`/prediction/suggest-target/${fileId}`);
  return response.data;
};
