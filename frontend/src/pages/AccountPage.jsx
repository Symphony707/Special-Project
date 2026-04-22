import React from 'react'
import useStore from '../store/useStore'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import SectionHeader from '../components/ui/SectionHeader'

export default function AccountPage() {
  const user = useStore(s => s.user)

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, marginBottom: 8 }}>Uplink Identity</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Management of neural credentials and access authorization levels.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: 24 }}>
        {/* Left: Profile Card */}
        <Card style={{ padding: 32, textAlign: 'center', height: 'fit-content' }}>
          <div style={{ 
            width: 100, height: 100, borderRadius: '50%', margin: '0 auto 20px',
            background: 'linear-gradient(135deg, var(--cyan), var(--purple))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 40, fontWeight: 800, color: '#08111f'
          }}>
            {user?.username?.[0]?.toUpperCase() || 'G'}
          </div>
          <h2 style={{ fontSize: 20, marginBottom: 4 }}>{user?.username || 'Guest Identity'}</h2>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>{user?.email || 'unlinked_account@datamind.ai'}</p>
          <Badge variant={user?.is_admin ? 'purple' : 'cyan'}>{user?.is_admin ? 'Root Administrator' : 'Forensic Analyst'}</Badge>
          
          <div style={{ marginTop: 32, paddingTop: 32, borderTop: '1px solid var(--border-subtle)' }}>
             <Button variant="secondary" fullWidth style={{ marginBottom: 10 }}>Update Avatar</Button>
             <Button variant="ghost" fullWidth>Reset Security Key</Button>
          </div>
        </Card>

        {/* Right: Security & Details */}
        <div style={{ display:'flex', flexDirection:'column', gap: 24 }}>
            <Card style={{ padding: 24 }}>
                <SectionHeader label="System Authorization" />
                <div style={{ display:'flex', flexDirection:'column', gap: 16 }}>
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                        <div>
                            <div style={{ fontSize:14, fontWeight:600 }}>Forensic Access Level</div>
                            <div style={{ fontSize:12, color:'var(--text-muted)' }}>Level 4 Clearances Active</div>
                        </div>
                        <Badge variant="green" size="sm">ACTIVE</Badge>
                    </div>
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                        <div>
                            <div style={{ fontSize:14, fontWeight:600 }}>Multi-Factor Authentication</div>
                            <div style={{ fontSize:12, color:'var(--text-muted)' }}>Unlinked biometric hardware</div>
                        </div>
                        <Button variant="ghost" size="sm">Enable</Button>
                    </div>
                </div>
            </Card>

            <Card style={{ padding: 24 }}>
                <SectionHeader label="Analytical History" />
                <div style={{ display:'flex', flexDirection:'column', gap: 12 }}>
                    {[
                        { date: '21 APR 2026', action: 'Injected 14.2k row CSV', target: 'marketing_data' },
                        { date: '20 APR 2026', action: 'Calibrated Random Forest', target: 'churn_prediction' },
                        { date: '19 APR 2026', action: 'Established secure link', target: 'System' },
                    ].map((h, i) => (
                        <div key={i} style={{ display:'flex', justifyContent:'space-between', fontSize:12 }}>
                            <span style={{ color:'var(--text-muted)', fontFamily:'JetBrains Mono' }}>{h.date}</span>
                            <span style={{ fontWeight:600 }}>{h.action}</span>
                        </div>
                    ))}
                </div>
            </Card>
        </div>
      </div>
    </div>
  )
}
