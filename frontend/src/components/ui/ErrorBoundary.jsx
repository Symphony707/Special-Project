import React from 'react';
import { AlertTriangle, RefreshCcw } from 'lucide-react';
import Button from './Button';
import Card from './Card';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          height: '100vh', 
          width: '100vw', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          background: 'var(--bg-base)',
          padding: 24
        }}>
          <Card style={{ maxWidth: 480, padding: 40, textAlign: 'center', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
            <div style={{ 
              width: 64, 
              height: 64, 
              borderRadius: '50%', 
              background: 'rgba(239, 68, 68, 0.1)', 
              color: '#ef4444',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 24px'
            }}>
              <AlertTriangle size={32} />
            </div>
            
            <h1 style={{ fontFamily: 'Syne', fontSize: 24, fontWeight: 800, marginBottom: 16 }}>System Fault Detected</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.6, marginBottom: 32 }}>
              The neural interface encountered an unhandled exception. Forensic logs have been captured.
            </p>
            
            {process.env.NODE_ENV === 'development' && (
              <pre style={{ 
                background: 'rgba(0,0,0,0.3)', 
                padding: 16, 
                borderRadius: 8, 
                fontSize: 11, 
                color: '#ef4444',
                textAlign: 'left',
                overflowX: 'auto',
                marginBottom: 32
              }}>
                {this.state.error?.toString()}
              </pre>
            )}
            
            <Button variant="secondary" onClick={handleReset} fullWidth>
              <RefreshCcw size={16} style={{ marginRight: 8 }} />
              Re-initialize Interface
            </Button>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
