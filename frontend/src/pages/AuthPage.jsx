import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import useStore from '../store/useStore'
import { login, register, guestSession } from '../api/auth'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'

export default function AuthPage() {
  const [tab, setTab] = useState('signin') // 'signin' | 'signup' | 'guest'
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({ 
    username: '', email: '', password: '', confirm: '' 
  })
  const setUser = useStore(s => s.setUser)
  const navigate = useNavigate()

  const onChange = e => setFormData({ ...formData, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (tab === 'signin') {
        const res = await login({ email: formData.email, password: formData.password })
        setUser(res.data.user)
        toast.success(`Welcome back, ${res.data.user.username}`)
        navigate('/')
      } else if (tab === 'signup') {
        if (formData.password !== formData.confirm) throw new Error('Passwords do not match')
        const res = await register({ 
          username: formData.username, 
          email: formData.email, 
          password: formData.password 
        })
        setUser(res.data.user)
        toast.success('Account created successfully')
        navigate('/')
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleGuest = async () => {
    try {
      const res = await guestSession()
      setUser(res.data.user)
      toast.success('Continuing as Guest (Analytical Trial)')
      navigate('/')
    } catch (err) {
      toast.error('Neural link failed. Try again or register.')
    }
  }

  return (
    <div style={{ display:'flex', height:'100vh', width:'100vw', overflow:'hidden' }}>
      {/* Left Panel: Branding & Visuals */}
      <div style={{ 
        flex: 1.5, background: 'var(--bg-base)', position:'relative',
        display:'flex', flexDirection:'column', justifyContent:'center',
        padding: '0 80px', overflow:'hidden', borderRight: '1px solid var(--border-subtle)'
      }}>
        {/* Animated Background Dots */}
        <div className="auth-background-dots" />
        
        <div style={{ position:'relative', zIndex: 2 }}>
          <div style={{
            width: 56, height: 56, borderRadius: 16,
            background: 'linear-gradient(135deg, var(--cyan), var(--purple))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 28, fontWeight: 800, color: '#08111f', marginBottom: 24,
            fontFamily: 'Syne, sans-serif'
          }}>D</div>
          <h1 style={{ fontSize: 52, fontWeight: 800, marginBottom: 16, maxWidth: 400 }}>
            Master your <span style={{ color: 'var(--cyan)' }}>Data Forensics</span>
          </h1>
          <p style={{ fontSize: 18, color: 'var(--text-secondary)', maxWidth: 440, lineHeight: 1.6 }}>
            The unified platform for neural-link asset analysis, predictive calibration, and automated insights.
          </p>

          {/* Floating Mockup Cards */}
          <div className="floating-cards">
            <div className="mock-card card-1" />
            <div className="mock-card card-2" />
            <div className="mock-card card-3" />
          </div>
        </div>
      </div>

      {/* Right Panel: Auth Form */}
      <div style={{ 
        flex: 1, background: 'var(--bg-surface)', 
        display:'flex', alignItems:'center', justifyContent:'center',
        padding: 40
      }}>
        <Card style={{ width:'100%', maxWidth: 420, padding: 40, borderRadius: 20 }}>
          <div style={{ textAlign:'center', marginBottom: 32 }}>
            <h2 style={{ fontSize: 24, marginBottom: 8 }}>Initialize System</h2>
            <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Enter credentials to access the forensic vault</p>
          </div>

          <div style={{ 
            display:'flex', background: 'var(--bg-base)', padding: 4, borderRadius: 12,
            marginBottom: 28, border: '1px solid var(--border-default)'
          }}>
            {['signin', 'signup', 'guest'].map(t => (
              <button
                key={t}
                onClick={() => setTab(t)}
                style={{
                  flex: 1, padding: '8px 0', fontSize: 12, fontWeight: 600,
                  borderRadius: 10, transition: 'var(--transition-base)',
                  color: tab === t ? 'var(--text-primary)' : 'var(--text-muted)',
                  background: tab === t ? 'var(--bg-elevated)' : 'transparent',
                }}
              >
                {t === 'signin' ? 'Sign In' : t === 'signup' ? 'Register' : 'Guest'}
              </button>
            ))}
          </div>

          {tab === 'guest' ? (
            <div style={{ textAlign:'center' }}>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 24, lineHeight: 1.6 }}>
                Guest users have access to all public analytical tools but cannot persist datasets across sessions.
              </p>
              <Button fullWidth onClick={handleGuest}>Continue as Guest Session</Button>
              <p style={{ fontSize: 11, color: 'var(--text-red)', marginTop: 16 }}>
                ⚠️ Progress will not be saved.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} style={{ display:'flex', flexDirection:'column', gap: 20 }}>
              {tab === 'signup' && (
                <div className="form-group">
                  <label className="label">Access Identity</label>
                  <input 
                    name="username" value={formData.username} onChange={onChange}
                    placeholder="e.g. neuro_analyst" className="auth-input"
                    required
                  />
                </div>
              )}
              <div className="form-group">
                <label className="label">Neural Uplink Address</label>
                <input 
                  name="email" value={formData.email} onChange={onChange}
                  type="email" placeholder="email@datamind.ai" className="auth-input"
                  required
                />
              </div>
              <div className="form-group">
                <div style={{ display:'flex', justifyContent:'space-between' }}>
                  <label className="label">Validation Key</label>
                  {tab === 'signin' && <span style={{ fontSize:10, color:'var(--cyan)', cursor:'pointer' }}>Forgot?</span>}
                </div>
                <input 
                  name="password" value={formData.password} onChange={onChange}
                  type="password" placeholder="••••••••" className="auth-input"
                  required
                />
              </div>
              {tab === 'signup' && (
                <div className="form-group">
                  <label className="label">Confirm Validation Key</label>
                  <input 
                    name="confirm" value={formData.confirm} onChange={onChange}
                    type="password" placeholder="••••••••" className="auth-input"
                    required
                  />
                  {formData.password && (
                    <div style={{ display:'flex', gap:4, marginTop:8 }}>
                      {[1,2,3,4].map(i => (
                        <div key={i} style={{ 
                          flex:1, height:4, borderRadius:2, 
                          background: formData.password.length > i*2 ? 'var(--cyan)' : 'var(--bg-elevated)'
                        }} />
                      ))}
                    </div>
                  )}
                </div>
              )}

              <Button type="submit" fullWidth loading={loading}>
                {tab === 'signin' ? 'Establish Link' : 'Create Credentials'}
              </Button>
            </form>
          )}
        </Card>
      </div>

      <style jsx>{`
        .auth-input {
          width: 100%;
          background: var(--bg-base);
          border: 1px solid var(--border-default);
          border-radius: 10px;
          padding: 12px 14px;
          color: var(--text-primary);
          font-size: 14px;
          transition: var(--transition-base);
          margin-top: 6px;
        }
        .auth-input:focus {
          outline: none;
          border-color: var(--border-cyan);
          box-shadow: 0 0 0 3px var(--cyan-faint);
        }
        .form-group { width: 100%; }
        
        .auth-background-dots {
          position: absolute; top:0; left:0; width:100%; height:100%;
          background-image: radial-gradient(var(--border-default) 1px, transparent 1px);
          background-size: 32px 32px;
          opacity: 0.4;
          mask-image: radial-gradient(circle at center, black 0%, transparent 80%);
        }

        .floating-cards {
          position: absolute; right: -40px; top: 50%;
          transform: translateY(-50%);
          display: flex; flex-direction: column; gap: 24px;
          pointer-events: none;
        }
        .mock-card {
          width: 240px; height: 160px;
          background: var(--bg-card);
          border: 1px solid var(--border-strong);
          border-radius: 18px;
          box-shadow: var(--shadow-lg);
          backdrop-filter: blur(8px);
          opacity: 0.6;
          animation: float 6s infinite ease-in-out;
        }
        .card-1 { transform: translateX(20px); animation-delay: 0s; }
        .card-2 { transform: translateX(-40px); animation-delay: 2s; }
        .card-3 { transform: translateX(60px); animation-delay: 4s; }

        @keyframes float {
          0%, 100% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-20px) scale(1.02); }
        }
      `}</style>
    </div>
  )
}
