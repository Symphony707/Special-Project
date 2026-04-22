// Contoso-style divider with label + optional right element
export default function SectionHeader({ label, right, style={} }) {
  return (
    <div style={{
      display:'flex', alignItems:'center', gap:12,
      marginBottom:14, ...style
    }}>
      <div style={{
        flex:1, height:1,
        background:'var(--border-subtle)'
      }} />
      <span style={{
        fontSize:10, fontWeight:700,
        letterSpacing:'0.12em', textTransform:'uppercase',
        color:'var(--text-muted)', whiteSpace:'nowrap',
        fontFamily:'DM Sans,sans-serif'
      }}>{label}</span>
      <div style={{
        flex:1, height:1,
        background:'var(--border-subtle)'
      }} />
      {right && <div>{right}</div>}
    </div>
  )
}
