// The exact Contoso-style KPI card with sparkline
// Props: icon, label, value, sub, trend (number %), trendUp, sparkData, accentColor

import React, { useEffect, useRef } from 'react'

export default function KPICard({
  icon, label, value, sub,
  trend, trendUp, sparkData=[],
  accentColor='var(--cyan)'
}) {
  const canvasRef = useRef(null)

  // Draw sparkline on canvas (no library needed)
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !sparkData || sparkData.length < 2) return
    const ctx = canvas.getContext('2d')
    const W = canvas.width, H = canvas.height
    ctx.clearRect(0, 0, W, H)

    const min = Math.min(...sparkData)
    const max = Math.max(...sparkData)
    const range = max - min || 1

    const pts = sparkData.map((v, i) => ({
      x: (i / (sparkData.length - 1)) * W,
      y: H - ((v - min) / range) * H * 0.8 - H * 0.1
    }))

    // Use a simpler fill strategy that doesn't rely on unsafe string manipulation
    const grad = ctx.createLinearGradient(0, 0, 0, H)
    const solidColor = accentColor.includes('--green') ? '#00e096' : (accentColor.includes('--purple') ? '#a855f7' : '#06b6d4')
    
    grad.addColorStop(0, solidColor + '44') // 44 is hex alpha
    grad.addColorStop(1, 'transparent')
    
    ctx.beginPath()
    ctx.moveTo(pts[0].x, H)
    pts.forEach(p => ctx.lineTo(p.x, p.y))
    ctx.lineTo(pts[pts.length-1].x, H)
    ctx.closePath()
    ctx.fillStyle = grad
    ctx.fill()

    // Draw line
    ctx.beginPath()
    pts.forEach((p, i) => i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y))
    ctx.strokeStyle = solidColor
    ctx.lineWidth = 1.5
    ctx.stroke()
  }, [sparkData, accentColor, trendUp])

  const trendColor = trendUp ? 'var(--green)' : 'var(--red)'
  const trendBg   = trendUp ? 'var(--green-faint)' : 'var(--red-faint)'
  const trendBorder= trendUp ? 'rgba(0,224,150,0.2)' : 'rgba(255,77,109,0.2)'

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-subtle)',
      borderTop: '1px solid var(--border-strong)',
      borderRadius: 'var(--card-radius)',
      padding: '18px 20px',
      position: 'relative',
      overflow: 'hidden',
      boxShadow: 'var(--shadow-md)',
      transition: 'var(--transition-base)',
      minHeight: 130,
    }}>
      {/* Top row: label + icon */}
      <div style={{
        display:'flex', justifyContent:'space-between',
        alignItems:'flex-start', marginBottom:10
      }}>
        <div style={{
          fontSize:10, fontWeight:700,
          letterSpacing:'0.12em', textTransform:'uppercase',
          color:'var(--text-muted)',
          fontFamily:'DM Sans,sans-serif'
        }}>{label}</div>
        <div style={{
          width:34, height:34, borderRadius:10,
          background:'var(--bg-elevated)',
          border:'1px solid var(--border-default)',
          display:'flex', alignItems:'center',
          justifyContent:'center', fontSize:16,
          flexShrink:0
        }}>{icon}</div>
      </div>

      {/* Value */}
      <div style={{
        fontFamily:'Syne,sans-serif', fontSize:32,
        fontWeight:800, color:'var(--text-primary)',
        lineHeight:1, marginBottom:6
      }}>{value}</div>

      {/* Trend badge */}
      {trend !== undefined && (
        <div style={{
          display:'inline-flex', alignItems:'center', gap:4,
          padding:'2px 8px', borderRadius:20,
          background:trendBg, color:trendColor,
          border:`1px solid ${trendBorder}`,
          fontSize:11, fontWeight:700, marginBottom:4
        }}>
          {trendUp ? '↑' : '↓'} {Math.abs(trend)}%
          <span style={{
            fontSize:10, color:'var(--text-muted)',
            fontWeight:400
          }}> vs last</span>
        </div>
      )}

      {/* Sub text */}
      {sub && <div style={{
        fontSize:11, color:'var(--text-secondary)',
        fontFamily:'DM Sans,sans-serif', marginTop:2
      }}>{sub}</div>}

      {/* Sparkline canvas — bottom right */}
      <canvas
        ref={canvasRef}
        width={100} height={40}
        style={{
          position:'absolute', bottom:0, right:0,
          opacity:0.7
        }}
      />

      {/* Subtle corner glow */}
      <div style={{
        position:'absolute', top:-30, right:-30,
        width:80, height:80,
        background:`radial-gradient(circle, ${
          trendUp
          ? 'rgba(0,224,150,0.07)'
          : 'rgba(6,210,255,0.07)'
        } 0%, transparent 70%)`,
        borderRadius:'50%', pointerEvents:'none'
      }} />
    </div>
  )
}
