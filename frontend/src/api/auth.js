import api from './client'

export const register = (data) =>
  api.post('/auth/register', data)

export const login = (data) =>
  api.post('/auth/login', data)

export const logout = () =>
  api.post('/auth/logout')

export const getMe = () =>
  api.get('/auth/me')

export const resetRequest = (email) =>
  api.post('/auth/reset-request', { email })

export const resetPassword = (token, newPassword) =>
  api.post('/auth/reset-password', { token, new_password: newPassword })

export const guestSession = () =>
  api.post('/auth/guest')
