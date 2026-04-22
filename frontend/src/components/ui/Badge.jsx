// Props: children, variant ('cyan'|'purple'|'green'|'red'|'amber'|'muted')
// size ('sm'|'md')

const VARIANTS = {
  cyan:   { bg:'var(--cyan-faint2)',   color:'var(--cyan)',   border:'var(--border-cyan)' },
  purple: { bg:'var(--purple-faint)',  color:'var(--purple)', border:'rgba(124,111,255,0.25)' },
  green:  { bg:'var(--green-faint)',   color:'var(--green)',  border:'rgba(0,224,150,0.25)' },
  red:    { bg:'var(--red-faint)',     color:'var(--red)',    border:'rgba(255,77,109,0.25)' },
  amber:  { bg:'var(--amber-faint)',   color:'var(--amber)',  border:'rgba(255,181,71,0.25)' },
  muted:  { bg:'rgba(255,255,255,0.04)', color:'var(--text-muted)', border:'var(--border-subtle)' },
}

export default function Badge({ children, variant='cyan', size='md' }) {
  const v = VARIANTS[variant] || VARIANTS.cyan
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      padding: size==='sm' ? '2px 8px' : '3px 10px',
      borderRadius: 20,
      background: v.bg, color: v.color,
      border: `1px solid ${v.border}`,
      fontSize: size==='sm' ? 10 : 11,
      fontWeight: 700,
      letterSpacing: '0.04em',
      whiteSpace: 'nowrap',
      fontFamily: 'DM Sans, sans-serif',
    }}>
      {children}
    </span>
  )
}
