import api from './client'

export const getStats = () => api.get('/dashboard/stats')
export const getActivity = (fileId) => api.get(`/dashboard/activity/${fileId}`)
export const initializeAsset = (fileId) => api.post(`/dashboard/initialize/${fileId}`)
export const getOllamaStatus = () => api.get('/dashboard/ollama-status')
