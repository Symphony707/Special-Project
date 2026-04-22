import React from 'react'
import useStore from '../store/useStore'
import Card from '../components/ui/Card'
import SectionHeader from '../components/ui/SectionHeader'
import Badge from '../components/ui/Badge'

export default function SettingsPage() {
  const settings = useStore(s => s.settings)
  const setSettings = useStore(s => s.setSettings)

  const toggle = (key) => setSettings({ ...settings, [key]: !settings[key] })

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, marginBottom: 8 }}>Calibration Settings</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Global system parameters for the DataMind analytical core.</p>
      </div>

      <div style={{ display:'flex', flexDirection:'column', gap: 24 }}>
        <Card style={{ padding: 24 }}>
          <SectionHeader label="Forensic Environment" />
          <div style={{ display:'flex', flexDirection:'column', gap: 16 }}>
            {[
                { id: 'darkMode', label: 'Layered Dark Aesthetic', desc: 'Enable the deep-space forensic theme (Recommended)' },
                { id: 'animations', label: 'Micro-Animations', desc: 'Interface kinetics and state transitions' },
                { id: 'notifications', label: 'System Pings', desc: 'Real-time alerts for calibration completion' },
            ].map(s => (
                <div key={s.id} style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                    <div>
                        <div style={{ fontSize:14, fontWeight:600 }}>{s.label}</div>
                        <div style={{ fontSize:12, color:'var(--text-muted)' }}>{s.desc}</div>
                    </div>
                    <button 
                        onClick={() => toggle(s.id)}
                        style={{
                            width: 44, height: 24, borderRadius: 12, background: settings[s.id] ? 'var(--cyan)' : 'var(--bg-elevated)',
                            border: '1px solid var(--border-default)', transition: 'var(--transition-base)',
                            position: 'relative', cursor: 'pointer'
                        }}
                    >
                        <div style={{ 
                            width: 16, height: 16, borderRadius: '50%', background: settings[s.id] ? '#08111f' : 'var(--text-muted)',
                            position: 'absolute', top: 3, left: settings[s.id] ? 24 : 4,
                            transition: 'var(--transition-base)'
                        }} />
                    </button>
                </div>
            ))}
          </div>
        </Card>

        <Card style={{ padding: 24 }}>
          <SectionHeader label="Computation Engine" />
          <div style={{ display:'flex', flexDirection:'column', gap: 20 }}>
            <div>
                <label className="label" style={{ marginBottom: 8, display:'block' }}>Forensic Tier</label>
                <div style={{ display:'flex', gap: 8 }}>
                    {['Fast', 'Balanced', 'Deep'].map(t => (
                        <button 
                            key={t}
                            style={{
                                flex: 1, padding: '10px 0', fontSize: 12, fontWeight: 700,
                                borderRadius: 10, background: t === 'Deep' ? 'var(--bg-overlay)' : 'var(--bg-elevated)',
                                border: t === 'Deep' ? '1px solid var(--border-cyan)' : '1px solid var(--border-subtle)',
                                color: t === 'Deep' ? 'var(--cyan)' : 'var(--text-muted)',
                                cursor: 'pointer'
                            }}
                        >
                            {t}
                        </button>
                    ))}
                </div>
                <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 10 }}>
                    Control the sampling depth and token budget for analytical agents.
                </p>
            </div>
          </div>
        </Card>

        <Card style={{ padding: 24, border: '1px solid var(--red-faint)' }}>
          <SectionHeader label="Core Destruction" />
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
            <div>
                <div style={{ fontSize:14, fontWeight:600, color:'var(--red)' }}>Purge All Analytical Assets</div>
                <div style={{ fontSize:12, color:'var(--text-muted)' }}>Irreversibly wipe every dataset and prediction from the vault</div>
            </div>
            <button style={{ 
                padding: '8px 16px', borderRadius: 8, background: 'var(--red-faint)',
                color:'var(--red)', border: '1px solid rgba(255,77,109,0.2)',
                fontSize: 12, fontWeight: 700, cursor: 'pointer'
            }}>INITIATE WIPE</button>
          </div>
        </Card>
      </div>
    </div>
  )
}
