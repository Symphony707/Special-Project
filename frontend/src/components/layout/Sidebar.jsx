import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import useStore from '../../store/useStore'
import { logout } from '../../api/auth'

const NAV = [
  { path:'/',           label:'Dashboard',      icon:'⊞' },
  { path:'/analysis',   label:'Analysis Lab',   icon:'🔬' },
  { path:'/prediction', label:'Prediction Lab', icon:'📈' },
  { path:'/data',       label:'Data Manager',   icon:'🗂️' },
  { path:'/chat',       label:'Chat',           icon:'💬' },
  { path:'/account',    label:'Account',        icon:'👤' },
  { path:'/settings',   label:'Settings',       icon:'⚙️' },
]

export default function Sidebar() {
  const navigate   = useNavigate()
  const location   = useLocation()
  const user       = useStore(s => s.user)
  const clearUser  = useStore(s => s.logout) // Updated from useStore spec
  const activeFile = useStore(s => s.activeFile)
  const [collapsed, setCollapsed] = useState(false)

  const W = collapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)'

  const handleLogout = async () => {
    try {
        await logout()
        clearUser()
        navigate('/auth')
    } catch (err) {
        console.error('Logout failed', err)
    }
  }

  return (
    <aside style={{
      position:'fixed', left:0, top:0,
      width:W, height:'100vh',
      background:'var(--bg-surface)',
      borderRight:'1px solid var(--border-subtle)',
      display:'flex', flexDirection:'column',
      zIndex:1000, overflow:'hidden',
      transition:'width var(--transition-slow)',
    }}>
      {/* Logo */}
      <div style={{
        height:'var(--header-height)',
        display:'flex', alignItems:'center',
        padding: collapsed ? '0 17px' : '0 18px',
        borderBottom:'1px solid var(--border-subtle)',
        gap:10, flexShrink:0,
        justifyContent: collapsed ? 'center' : 'flex-start',
      }}>
        <div style={{
          width:32, height:32, borderRadius:9, flexShrink:0,
          background:'linear-gradient(135deg,var(--cyan),var(--purple))',
          display:'flex', alignItems:'center', justifyContent:'center',
          fontFamily:'Syne,sans-serif', fontWeight:800,
          fontSize:16, color:'#08111f',
        }}>D</div>
        {!collapsed && (
          <span style={{
            fontFamily:'Syne,sans-serif', fontWeight:700,
            fontSize:15, color:'var(--text-primary)',
            letterSpacing:'-0.02em', whiteSpace:'nowrap'
          }}>DataMind</span>
        )}
        {!collapsed && (
          <button
            onClick={() => setCollapsed(true)}
            style={{
              marginLeft:'auto', color:'var(--text-muted)',
              fontSize:16, padding:4, borderRadius:6,
              transition:'var(--transition-fast)',
              background:'transparent', border:'none',
              cursor:'pointer',
            }}
          >‹</button>
        )}
      </div>

      {/* Nav items */}
      <nav style={{ flex:1, padding:'10px 8px', overflowY:'auto' }}>
        {collapsed && (
          <button
            onClick={() => setCollapsed(false)}
            style={{
              width:'100%', height:36, borderRadius:8,
              background:'var(--bg-elevated)', border:'none',
              color:'var(--text-muted)', fontSize:14,
              cursor:'pointer', marginBottom:6,
              display:'flex', alignItems:'center',
              justifyContent:'center',
            }}
          >›</button>
        )}
        {NAV.map(({ path, label, icon }) => {
          const active = location.pathname === path
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              title={collapsed ? label : undefined}
              style={{
                display:'flex', alignItems:'center',
                gap:10, width:'100%', padding:'10px 12px',
                borderRadius:10, marginBottom:2,
                background: active
                  ? 'linear-gradient(135deg,rgba(6,210,255,0.15),rgba(6,210,255,0.05))'
                  : 'transparent',
                border: active
                  ? '1px solid rgba(6,210,255,0.2)'
                  : '1px solid transparent',
                color: active ? 'var(--cyan)' : 'var(--text-secondary)',
                fontFamily:'DM Sans,sans-serif', fontSize:13,
                fontWeight: active ? 600 : 500,
                cursor:'pointer',
                transition:'var(--transition-fast)',
                justifyContent: collapsed ? 'center' : 'flex-start',
                whiteSpace:'nowrap', overflow:'hidden',
              }}
            >
              <span style={{ fontSize:15, flexShrink:0 }}>{icon}</span>
              {!collapsed && <span className="truncate">{label}</span>}
              {!collapsed && active && (
                <div style={{
                  marginLeft:'auto', width:5, height:5,
                  borderRadius:'50%', background:'var(--cyan)',
                  flexShrink:0,
                  boxShadow:'0 0 6px var(--cyan)',
                }} />
              )}
            </button>
          )
        })}
      </nav>

      {/* Active file chip */}
      {activeFile && !collapsed && (
        <div style={{
          margin:'0 8px 8px 8px',
          background:'rgba(6,210,255,0.06)',
          border:'1px solid rgba(6,210,255,0.15)',
          borderRadius:10, padding:'9px 12px',
        }}>
          <div style={{
            fontSize:9, fontWeight:700, letterSpacing:'0.1em',
            color:'var(--text-muted)', textTransform:'uppercase',
            marginBottom:3
          }}>Active Dataset</div>
          <div style={{
            fontSize:12, fontWeight:600, color:'var(--cyan)',
            whiteSpace:'nowrap', overflow:'hidden',
            textOverflow:'ellipsis'
          }}>{activeFile.name}</div>
          <div style={{
            fontSize:10, color:'var(--text-muted)', marginTop:1
          }}>{activeFile.rowCount?.toLocaleString()} rows</div>
        </div>
      )}

      {/* User row + logout */}
      <div style={{
        padding:'10px 8px 12px 8px',
        borderTop:'1px solid var(--border-subtle)', flexShrink:0
      }}>
        {!collapsed && (
          <div style={{
            display:'flex', alignItems:'center', gap:10,
            padding:'9px 12px', borderRadius:10,
            background:'var(--bg-elevated)',
            marginBottom:6,
          }}>
            <div style={{
              width:28, height:28, borderRadius:'50%', flexShrink:0,
              background:'linear-gradient(135deg,var(--cyan),var(--purple))',
              display:'flex', alignItems:'center', justifyContent:'center',
              fontFamily:'Syne,sans-serif', fontWeight:700,
              fontSize:12, color:'#08111f',
            }}>{user?.username?.[0]?.toUpperCase() || 'G'}</div>
            <div style={{ flex:1, overflow:'hidden' }}>
              <div style={{
                fontSize:13, fontWeight:600, color:'var(--text-primary)',
                whiteSpace:'nowrap', overflow:'hidden',
                textOverflow:'ellipsis'
              }}>{user?.username || 'Guest'}</div>
              <div style={{
                fontSize:10, color:'var(--text-muted)',
                textTransform:'uppercase', letterSpacing:'0.06em'
              }}>{user?.is_admin ? 'Admin' : 'Analyst'}</div>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          style={{
            display:'flex', alignItems:'center',
            gap:8, width:'100%',
            padding: collapsed ? '10px' : '9px 12px',
            borderRadius:10, border:'none',
            background:'transparent', color:'var(--text-muted)',
            fontSize:12, fontWeight:500, cursor:'pointer',
            fontFamily:'DM Sans,sans-serif',
            transition:'var(--transition-fast)',
            justifyContent: collapsed ? 'center' : 'flex-start',
          }}
        >
          <span>→</span>
          {!collapsed && 'Logout Session'}
        </button>
      </div>
    </aside>
  )
}
