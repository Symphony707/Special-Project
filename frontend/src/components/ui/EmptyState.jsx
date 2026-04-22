export default function EmptyState({ icon, title, subtitle, action }) {
  return (
    <div style={{
      display:'flex', flexDirection:'column',
      alignItems:'center', justifyContent:'center',
      padding:'52px 24px', textAlign:'center', gap:12
    }}>
      <div style={{ fontSize:48, opacity:0.3, lineHeight:1 }}>{icon}</div>
      <div style={{
        fontFamily:'Syne,sans-serif', fontSize:17,
        fontWeight:700, color:'var(--text-secondary)'
      }}>{title}</div>
      {subtitle && <div style={{
        fontSize:12, color:'var(--text-muted)',
        maxWidth:260, lineHeight:1.7
      }}>{subtitle}</div>}
      {action && <div style={{marginTop:8}}>{action}</div>}
    </div>
  )
}
