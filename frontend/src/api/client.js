import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // Added /api prefix for backend consistency
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' }
})

import useStore from '../store/useStore'

// Global error handler
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      const isAuthPage = window.location.pathname.includes('/auth')
      if (!isAuthPage) {
        // Use Zustand's non-hook state access to trigger a logout
        useStore.getState().logout()
      }
    }
    return Promise.reject(err)
  }
)

export default api
