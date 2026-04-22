import React from 'react'
import { useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

const PAGE_NAMES = {
  '/':          'Dashboard',
  '/analysis':  'Analysis Lab',
  '/prediction':'Prediction Lab',
  '/data':      'Data Manager',
  '/chat':      'Chat',
  '/account':   'Account',
  '/settings':  'Settings',
}

export default function PageWrapper({ children }) {
  const { pathname } = useLocation()
  const pageName = PAGE_NAMES[pathname] || 'DataMind'

  return (
    <div style={{ display:'flex', minHeight:'100vh',
                  background:'var(--bg-base)' }}>
      <Sidebar />
      <div style={{
        marginLeft:'var(--sidebar-width)', flex:1,
        display:'flex', flexDirection:'column',
        minWidth:0,
      }}>
        <Header pageName={pageName} />
        <main style={{
          marginTop:'var(--header-height)',
          padding:'var(--content-padding)',
          flex:1, minHeight:`calc(100vh - var(--header-height))`,
        }}>
          {children}
        </main>
      </div>
    </div>
  )
}
