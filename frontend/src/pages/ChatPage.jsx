import React, { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import toast from 'react-hot-toast'
import useStore from '../store/useStore'
import { streamChat } from '../api/chat'
import Card from '../components/ui/Card'
import SectionHeader from '../components/ui/SectionHeader'
import EmptyState from '../components/ui/EmptyState'

export default function ChatPage() {
  const activeFile = useStore(s => s.activeFile)
  const chatHistory = useStore(s => s.chatHistory)
  const addChatMessage = useStore(s => s.addChatMessage)
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamContent, setStreamContent] = useState('')
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatHistory, streamContent])

  const handleSend = async (e) => {
    e?.preventDefault()
    if (!input.trim() || isStreaming) return

    if (!activeFile) {
        toast.error('No active asset. Load a file from the vault first.')
        return
    }

    const query = input
    setInput('')
    addChatMessage({ role: 'user', content: query, timestamp: new Date().toLocaleTimeString() })
    setIsStreaming(true)
    setStreamContent('')

    try {
      streamChat(
        { 
            query, 
            file_id: activeFile?.id, 
            conversation_history: chatHistory 
        },
        (chunk) => setStreamContent(prev => prev + chunk),
        (doneData) => {
          setIsStreaming(false)
          addChatMessage({ 
            role: 'assistant', 
            content: doneData.full_content || streamContent, 
            timestamp: new Date().toLocaleTimeString()
          })
          setStreamContent('')
        },
        (err) => {
          setIsStreaming(false)
          toast.error('Uplink lost')
        }
      )
    } catch (err) {
      setIsStreaming(false)
      toast.error('Transmission failed')
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', height: '100%', display:'flex', flexDirection:'column' }}>
       <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: 28, fontWeight: 800 }}>Neural Chat</h1>
          <p style={{ color:'var(--text-secondary)', fontSize: 13 }}>Direct interrogation of analytical models and datasets.</p>
       </div>

       <Card style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ flex: 1, overflowY: 'auto', padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
            {(!activeFile && chatHistory.length === 0) ? (
                <EmptyState 
                    icon="📂" title="No Active Asset" 
                    subtitle="Direct interrogation requires a target dataset. Load an asset from the Forensics Vault to begin." 
                />
            ) : (chatHistory.length === 0 && !streamContent) && (
                <EmptyState 
                    icon="💬" title="Open Channel" 
                    subtitle="Ask anything about your data, system status, or predictive findings." 
                />
            )}
            {chatHistory.map((msg, i) => (
                <div key={i} style={{ 
                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '85%'
                }}>
                    <div style={{
                        background: msg.role === 'user' ? 'var(--cyan-faint2)' : 'var(--bg-elevated)',
                        border: msg.role === 'user' ? '1px solid var(--border-cyan)' : '1px solid var(--border-subtle)',
                        borderRadius: 14, padding: '14px 18px', fontSize: 14, lineHeight: 1.6
                    }}>
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 6, textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                        {msg.role === 'user' ? 'Verified Sender' : 'DataMind Agent'} • {msg.timestamp}
                    </div>
                </div>
            ))}
            {streamContent && (
                <div style={{ alignSelf: 'flex-start', maxWidth: '85%' }}>
                    <div style={{
                        background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)',
                        borderRadius: 14, padding: '14px 18px', fontSize: 14
                    }}>
                        <ReactMarkdown>{streamContent}</ReactMarkdown>
                    </div>
                </div>
            )}
            <div ref={scrollRef} />
          </div>

          <form onSubmit={handleSend} style={{ 
              padding: 24, paddingTop: 12, borderTop: '1px solid var(--border-default)', 
              display:'flex', gap: 12, alignItems: 'flex-end' 
          }}>
             <div style={{ flex: 1, position: 'relative' }}>
                <label className="label" style={{ marginBottom: 8, display:'block' }}>Interrogate Model</label>
                <textarea 
                    value={input} onChange={e => setInput(e.target.value)}
                    placeholder="Describe the analysis task..."
                    style={{
                        width: '100%', minHeight: 80, maxHeight: 200, padding: '12px 14px',
                        background: 'var(--bg-base)', border: '1px solid var(--border-default)',
                        borderRadius: 12, color: 'var(--text-primary)', fontSize: 14,
                        outline: 'none', resize: 'none', fontFamily: 'inherit'
                    }}
                    onKeyDown={e => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault()
                            handleSend()
                        }
                    }}
                />
             </div>
             <button 
                type="submit" disabled={!input.trim() || isStreaming}
                style={{
                  padding: '12px 24px', borderRadius: 10, background: 'var(--cyan)',
                  color: '#08111f', fontWeight: 700, fontSize: 14,
                  cursor: 'pointer', transition: 'var(--transition-base)', marginBottom: 2,
                  opacity: (!input.trim() || isStreaming) ? 0.5 : 1
                }}
             >
                {isStreaming ? 'Thinking...' : 'Send Uplink'}
             </button>
          </form>
       </Card>
    </div>
  )
}
