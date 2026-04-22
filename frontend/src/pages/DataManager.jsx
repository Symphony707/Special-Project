import React, { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import useStore from '../store/useStore'
import { uploadFile, listFiles, deleteFile, loadFile } from '../api/files'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import SectionHeader from '../components/ui/SectionHeader'
import EmptyState from '../components/ui/EmptyState'

export default function DataManager() {
  const userFiles = useStore(s => s.userFiles)
  const setUserFiles = useStore(s => s.setUserFiles)
  const activeFile = useStore(s => s.activeFile)
  const setActiveFile = useStore(s => s.setActiveFile)
  const [isUploading, setIsUploading] = useState(false)

  const refreshFiles = async () => {
    try {
        const res = await listFiles()
        setUserFiles(res.data.files)
    } catch (err) {
        toast.error('Sync failed')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('IRREVERSIBLE: Purge this artifact from the vault?')) return
    try {
        await deleteFile(id)
        toast.success('Artifact purged')
        refreshFiles()
        if (activeFile?.id === id) setActiveFile(null, null)
    } catch (err) {
        toast.error('Decommission failed')
    }
  }

  const handleLoad = async (id, name) => {
    try {
        await loadFile(id)
        setActiveFile(id, name)
        toast.success(`Activated: ${name}`)
    } catch (err) {
        toast.error('Activation failed')
    }
  }

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return
    setIsUploading(true)
    const tid = toast.loading(`Ingesting ${file.name}...`)
    try {
        const res = await uploadFile(file)
        toast.success('Asset secured', { id: tid })
        refreshFiles()
    } catch (err) {
        toast.error('Ingestion failed', { id: tid })
    } finally {
        setIsUploading(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, multiple: false })

  return (
    <div style={{ display:'flex', flexDirection:'column', gap: 32 }}>
      <div>
        <h1 style={{ fontSize: 32, fontWeight: 800, marginBottom: 8 }}>Forensic Data Portfolio</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Unified analytical asset inventory with instant activation and audit controls.</p>
      </div>

      {/* Stats Bar */}
      <Card style={{ padding: '24px 40px' }}>
        <div style={{ display:'flex', justifyContent: 'space-around', alignItems: 'center' }}>
          {[
            { label: 'TOTAL ASSETS', value: userFiles.length },
            { label: 'TOTAL ROWS', value: userFiles.reduce((acc, f) => acc + f.row_count, 0).toLocaleString() },
            { label: 'MEMORY USED', value: '42.8 MB' },
            { label: 'SYSTEM LOAD', value: '12%' }
          ].map((s, i) => (
            <React.Fragment key={s.label}>
              <div style={{ textAlign:'center' }}>
                <div style={{ fontFamily:'Syne', fontSize:26, fontWeight:800, color:'var(--text-primary)', marginBottom:4 }}>{s.value}</div>
                <div className="label" style={{ fontSize:9 }}>{s.label}</div>
              </div>
              {i < 3 && <div style={{ width:1, height:40, background: 'var(--border-subtle)' }} />}
            </React.Fragment>
          ))}
        </div>
      </Card>

      {/* Assets List */}
      <section>
        <SectionHeader label="Active Assets" />
        <div style={{ display:'flex', flexDirection:'column', gap: 12 }}>
          {userFiles.length > 0 ? (
            userFiles.map(f => (
                <Card 
                  key={f.global_file_id} hover 
                  style={{ 
                    padding: '16px 20px', display: 'flex', alignItems: 'center', gap: 20,
                    borderLeft: f.global_file_id === activeFile?.id ? '4px solid var(--cyan)' : '1px solid var(--border-subtle)',
                    background: f.global_file_id === activeFile?.id ? 'var(--cyan-faint)' : 'var(--bg-card)'
                  }}
                >
                  <div style={{ fontSize: 32 }}>{f.display_name.endsWith('.csv') ? '📊' : '📘'}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 4 }}>{f.display_name}</div>
                    <div style={{ display:'flex', gap: 12, alignItems:'center' }}>
                        <span style={{ fontSize:11, color:'var(--text-muted)' }}>{f.row_count.toLocaleString()} rows</span>
                        <div style={{ width:4, height:4, borderRadius:'50%', background:'var(--text-muted)' }} />
                        <Badge variant="cyan" size="sm">{f.detected_domain || 'Generic'}</Badge>
                    </div>
                  </div>
                  <div style={{ textAlign:'right', paddingRight: 20 }}>
                    <div style={{ fontSize:10, color:'var(--text-muted)', textTransform:'uppercase', marginBottom:2 }}>LAST ACCESSED</div>
                    <div style={{ fontSize:12, fontWeight:500 }}>{f.last_accessed || 'Just now'}</div>
                  </div>
                  <div style={{ display:'flex', gap: 8 }}>
                    <Button 
                        variant={f.global_file_id === activeFile?.id ? 'secondary' : 'ghost'} 
                        size="sm"
                        onClick={() => handleLoad(f.global_file_id, f.display_name)}
                    >
                        {f.global_file_id === activeFile?.id ? 'Reload' : 'Activate'}
                    </Button>
                    <Button variant="danger" size="sm" onClick={() => handleDelete(f.global_file_id)}>Purge</Button>
                  </div>
                </Card>
            ))
          ) : (
            <EmptyState icon="📂" title="Vault Empty" subtitle="System awaiting artifact ingestion." />
          )}
        </div>
      </section>

      {/* Ingestion Zone */}
      <section>
        <SectionHeader label="Asset Ingestion" />
        <div {...getRootProps()} style={{
          background: 'var(--bg-surface)', border: '2px dashed var(--border-default)',
          borderRadius: 20, padding: 60, textAlign: 'center', cursor: 'pointer',
          transition: 'var(--transition-base)',
          borderColor: isDragActive ? 'var(--cyan)' : 'var(--border-default)'
        }}>
          <input {...getInputProps()} />
          <div style={{ fontSize: 56, marginBottom: 20, opacity: 0.3 }}>☁</div>
          <h3 style={{ fontSize: 18, marginBottom: 12 }}>Ingest Forensic Artifact</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 24 }}>CSV, Excel, JSON, or Parquet files up to 50MB supported.</p>
          <div style={{ display:'flex', justifyContent:'center', gap: 10 }}>
            {['.CSV', '.XLSX', '.JSON', '.PARQUET'].map(ext => (
                <div key={ext} style={{ 
                    padding:'4px 12px', background:'var(--bg-elevated)', border:'1px solid var(--border-subtle)',
                    borderRadius: 20, fontSize: 11, fontWeight: 700, color:'var(--text-muted)'
                }}>{ext}</div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
