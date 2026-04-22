import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary caught]', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          height: '100vh', background: '#080e1f',
          color: '#eef2ff', fontFamily: 'DM Sans, sans-serif',
          gap: 16, padding: 40, textAlign: 'center'
        }}>
          <div style={{ fontSize: 48 }}>⚠️</div>
          <div style={{
            fontFamily: 'Syne, sans-serif',
            fontSize: 22, fontWeight: 700
          }}>
            Page crashed
          </div>
          <div style={{
            fontSize: 13, color: '#8899bb',
            maxWidth: 500, lineHeight: 1.7
          }}>
            {this.state.error?.message || 'Unknown error'}
          </div>
          <pre style={{
            background: '#0d1630', border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: 10, padding: '14px 20px',
            fontSize: 11, color: '#ff4d6d',
            maxWidth: 700, overflow: 'auto',
            textAlign: 'left', lineHeight: 1.6
          }}>
            {this.state.error?.stack?.slice(0, 600)}
          </pre>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '10px 24px', borderRadius: 10,
              background: '#06d2ff', color: '#08111f',
              fontWeight: 700, fontSize: 13,
              border: 'none', cursor: 'pointer'
            }}
          >
            Reload Page
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
