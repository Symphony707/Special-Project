import React, { useEffect, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import useStore from './store/useStore'
import { getMe } from './api/auth'
import ErrorBoundary from './components/ui/ErrorBoundary'

// Lazy pages
import Dashboard from './pages/Dashboard'
import AnalysisLab from './pages/AnalysisLab'
import PredictionLab from './pages/PredictionLab'
import DataManager from './pages/DataManager'
import ChatPage from './pages/ChatPage'
import AccountPage from './pages/AccountPage'
import SettingsPage from './pages/SettingsPage'
import AuthPage from './pages/AuthPage'
import PageWrapper from './components/layout/PageWrapper'

const PrivateRoute = ({ children }) => {
  const user = useStore(s => s.user)
  const loading = useStore(s => s.loading)
  
  if (loading) return (
    <div className="min-h-screen bg-[#0B0F1A] flex items-center justify-center">
      <div className="text-[#6366F1] font-medium flex items-center gap-3">
        <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
        Restoring Session Memory...
      </div>
    </div>
  )
  return user ? children : <Navigate to="/auth" />
}

function App() {
  const setUser = useStore(s => s.setUser)
  const setLoading = useStore(s => s.setLoading)

  useEffect(() => {
    // Avoid checking session if we are already in the auth portal
    if (window.location.pathname.includes('/auth')) {
      setLoading(false)
      return
    }

    setLoading(true)
    getMe()
      .then(res => setUser(res.data.user))
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [setUser, setLoading])

  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Toaster position="top-right" />
        <Suspense fallback={
          <div className="min-h-screen bg-[#0B0F1A] flex items-center justify-center">
            <div className="text-cyan-400 font-medium flex items-center gap-3">
              <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
              Loading Interface...
            </div>
          </div>
        }>
          <Routes>
            <Route path="/auth" element={<AuthPage />} />
            
            {/* Protected Routes */}
            <Route path="/" element={<PrivateRoute><PageWrapper><Dashboard /></PageWrapper></PrivateRoute>} />
            <Route path="/analysis" element={<PrivateRoute><PageWrapper><AnalysisLab /></PageWrapper></PrivateRoute>} />
            <Route path="/prediction" element={<PrivateRoute><PageWrapper><PredictionLab /></PageWrapper></PrivateRoute>} />
            <Route path="/data" element={<PrivateRoute><PageWrapper><DataManager /></PageWrapper></PrivateRoute>} />
            <Route path="/chat" element={<PrivateRoute><PageWrapper><ChatPage /></PageWrapper></PrivateRoute>} />
            <Route path="/account" element={<PrivateRoute><PageWrapper><AccountPage /></PageWrapper></PrivateRoute>} />
            <Route path="/settings" element={<PrivateRoute><PageWrapper><SettingsPage /></PageWrapper></PrivateRoute>} />
            
            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </BrowserRouter>
  )
}

export default App
