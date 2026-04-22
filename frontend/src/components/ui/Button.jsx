// Props: children, variant ('primary'|'secondary'|'ghost'|'danger')
// size ('sm'|'md'|'lg'), onClick, disabled, loading, fullWidth, icon

export default function Button({
  children, variant='primary', size='md',
  onClick, disabled=false, loading=false,
  fullWidth=false, icon, type='button'
}) {
  const styles = {
    primary: {
      background: 'var(--cyan)',
      color: '#ffffff', fontWeight: 800,
      boxShadow: '0 4px 14px rgba(124,111,255,0.25)',
      height: 'auto',
      textTransform: 'uppercase',
      letterSpacing: '0.1em',
    },
    intelligence: {
      background: '#7c6fff',
      color: '#ffffff', fontWeight: 900,
      boxShadow: '0 8px 30px rgba(124,111,255,0.3)',
      textTransform: 'uppercase',
      letterSpacing: '0.15em',
    },
    secondary: {
      background: 'var(--bg-elevated)',
      color: 'var(--text-primary)',
      border: '1px solid var(--border-default)',
    },
    ghost: {
      background: 'transparent',
      color: 'var(--text-secondary)',
      border: '1px solid var(--border-subtle)',
    },
    danger: {
      background: 'var(--red-faint)',
      color: 'var(--red)',
      border: '1px solid rgba(255,77,109,0.25)',
    },
  }
  const sizes = {
    sm: { padding:'6px 14px', fontSize:11, borderRadius:12, height:32 },
    md: { padding:'10px 20px', fontSize:12, borderRadius:14, height:44 },
    lg: { padding:'14px 28px', fontSize:13, borderRadius:16, height:56 },
  }
  const s = sizes[size] || sizes.md
  const v = styles[variant] || styles.primary
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      style={{
        display: 'inline-flex', alignItems: 'center',
        justifyContent: 'center', gap: 10,
        fontFamily: 'Plus Jakarta Sans, sans-serif',
        fontWeight: 700,
        border: 'none', transition: 'var(--transition-base)',
        opacity: (disabled || loading) ? 0.5 : 1,
        cursor: (disabled || loading) ? 'not-allowed' : 'pointer',
        width: fullWidth ? '100%' : 'auto',
        ...v, ...s,
      }}
    >
      {loading && <SpinnerIcon size={14} />}
      {icon && !loading && icon}
      {children}
    </button>
  )
}

function SpinnerIcon({ size=14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24"
         style={{ animation:'spin 0.8s linear infinite' }}>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      <circle cx="12" cy="12" r="10" stroke="currentColor"
              strokeWidth="3" fill="none" strokeDasharray="31"
              strokeDashoffset="10" strokeLinecap="round"/>
    </svg>
  )
}
