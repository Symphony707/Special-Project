import React, { useState } from 'react'
import useStore from '../../store/useStore'

const PAGE_META = {
  'Dashboard':      { icon:'⊞',  crumb:'Projects / Datasets' },
  'Analysis Lab':   { icon:'🔬', crumb:'Projects / Datasets' },
  'Prediction Lab': { icon:'📈', crumb:'Projects / Datasets' },
  'Data Manager':   { icon:'🗂️', crumb:'Projects / Datasets' },
  'Chat':           { icon:'💬', crumb:'Projects / Datasets' },
  'Account':        { icon:'👤', crumb:'Settings' },
  'Settings':       { icon:'⚙️', crumb:'Settings' },
}

export default function Header({ pageName }) {
  const user        = useStore(s => s.user)
  const activeFile  = useStore(s => s.activeFile)
  const ollamaOk    = useStore(s => s.ollamaOnline) || false
  const [search, setSearch] = useState('')
  const meta = PAGE_META[pageName] || PAGE_META['Dashboard']

  return (
    <header style={{
      position:'fixed',
      left:'var(--sidebar-width)', top:0, right:0,
      height:'var(--header-height)',
      background:'rgba(8,14,31,0.88)',
      backdropFilter:'blur(16px)',
      borderBottom:'1px solid var(--border-subtle)',
      zIndex:999,
      display:'flex', alignItems:'center',
      padding:'0 24px', gap:14,
    }}>
      {/* Left: breadcrumb + page title */}
      <div style={{ flex:1 }}>
        <div style={{
          fontSize:10, color:'var(--text-muted)',
          fontFamily:'DM Sans,sans-serif',
          letterSpacing:'0.04em', marginBottom:1
        }}>{meta.crumb} /</div>
        <div style={{
          fontFamily:'Syne,sans-serif', fontSize:16,
          fontWeight:700, color:'var(--text-primary)',
          display:'flex', alignItems:'center', gap:8
        }}>
          {pageName}
        </div>
      </div>

      {/* Center: Search bar */}
      <div style={{
        position:'relative', width:280,
        flexShrink:0,
      }}>
        <span style={{
          position:'absolute', left:12, top:'50%',
          transform:'translateY(-50%)',
          fontSize:14, color:'var(--text-muted)',
          pointerEvents:'none'
        }}>🔎</span>
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search columns, ask anything..."
          style={{
            width:'100%', padding:'8px 14px 8px 36px',
            background:'var(--bg-elevated)',
            border:'1px solid var(--border-default)',
            borderRadius:24, color:'var(--text-primary)',
            fontSize:12, fontFamily:'DM Sans,sans-serif',
            outline:'none', transition:'var(--transition-fast)',
          }}
          onFocus={e => {
            e.target.style.borderColor = 'var(--border-cyan)'
            e.target.style.boxShadow   = '0 0 0 3px rgba(6,210,255,0.08)'
          }}
          onBlur={e => {
            e.target.style.borderColor = 'var(--border-default)'
            e.target.style.boxShadow   = 'none'
          }}
        />
      </div>

      {/* Right group */}
      <div style={{
        display:'flex', alignItems:'center', gap:14
      }}>
        {/* Active file domain badge */}
        {activeFile?.fingerprint?.detected_domain && (
          <div style={{
            display:'flex', alignItems:'center', gap:6,
            padding:'4px 12px', borderRadius:20,
            background:'var(--cyan-faint2)',
            border:'1px solid var(--border-cyan)',
            fontSize:11, fontWeight:700,
            color:'var(--cyan)',
          }}>
            📊 {activeFile.fingerprint.detected_domain}
          </div>
        )}

        {/* Ollama status */}
        <div style={{
          display:'flex', alignItems:'center', gap:6,
          fontSize:11, color:'var(--text-secondary)',
        }}>
          <div style={{
            width:7, height:7, borderRadius:'50%',
            background: ollamaOk ? 'var(--green)' : 'var(--red)',
            boxShadow: ollamaOk
              ? '0 0 8px var(--green)'
              : '0 0 8px var(--red)',
            animation: ollamaOk ? 'pulse 2s infinite' : 'none',
          }} />
          <span>{ollamaOk ? 'Model Ready' : 'Offline'}</span>
        </div>

        {/* Notification bell */}
        <button style={{
          width:34, height:34, borderRadius:9,
          background:'var(--bg-elevated)',
          border:'1px solid var(--border-default)',
          color:'var(--text-secondary)', fontSize:16,
          display:'flex', alignItems:'center',
          justifyContent:'center', cursor:'pointer',
          transition:'var(--transition-fast)',
        }}>🔔</button>

        {/* Avatar */}
        <div style={{
          width:34, height:34, borderRadius:'50%',
          background:'linear-gradient(135deg,var(--cyan),var(--purple))',
          display:'flex', alignItems:'center',
          justifyContent:'center',
          fontFamily:'Syne,sans-serif', fontWeight:700,
          fontSize:14, color:'#08111f', flexShrink:0,
          cursor:'pointer',
        }}>
          {user?.username?.[0]?.toUpperCase() || 'G'}
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%,100%{opacity:1} 50%{opacity:0.4}
        }
      `}</style>
    </header>
  )
}
