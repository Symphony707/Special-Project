// Base card used by EVERY section across all pages
// Props: children, className, hover, glow, style, onClick

export default function Card({
  children, className='', hover=false,
  glow=false, style={}, onClick
}) {
  return (
    <div
      onClick={onClick}
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-subtle)',
        borderTop: '1px solid var(--border-strong)',
        borderRadius: 'var(--card-radius)',
        boxShadow: glow
          ? 'var(--shadow-card-glow)'
          : 'var(--shadow-md)',
        transition: 'var(--transition-base)',
        cursor: onClick ? 'pointer' : 'default',
        ...style
      }}
      className={`dm-card ${hover?'dm-card--hover':''} ${className}`}
    >
      {children}
    </div>
  )
}
