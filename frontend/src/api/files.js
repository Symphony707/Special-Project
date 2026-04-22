import api from './client'

export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const listFiles = () => api.get('/files/list')

export const loadFile = (fileId) => api.post(`/files/load/${fileId}`)

export const deleteFile = (fileId) => api.delete(`/files/${fileId}`)
