import { useState, useRef, useEffect, useCallback } from 'react'
import { sendMessageStreaming } from '../../api/chat'
import useStore from '../../store/useStore'

export default function ChatPanel({
  title        = 'DataMind AI',
  accentColor  = 'var(--cyan)',
  dotColor     = '#06d2ff',
  fileId,
  placeholder  = 'Ask about your data...',
  suggestions  = [],
}) {
  const activeFile = useStore(s => s.activeFile)
  const [messages,  setMessages]  = useState([])
  const [query,     setQuery]     = useState('')
  const [inFlight,  setInFlight]  = useState(false)
  const [streaming, setStreaming]  = useState('')
  const [isTyping,  setIsTyping]  = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef       = useRef(null)
  const cancelRef      = useRef(null)

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streaming, isTyping])

  const handleSend = useCallback(async () => {
    const q = query.trim()
    if (!q || inFlight || !fileId) return

    // Add user message immediately
    const userMsg = {
      id:      Date.now(),
      role:    'user',
      content: q,
    }
    setMessages(prev => [...prev, userMsg])
    setQuery('')
    setInFlight(true)
    setIsTyping(true)
    setStreaming('')

    const conversationHistory = messages.map(m => ({
      role:    m.role,
      content: m.content,
    }))

    let fullText = ''
    let isFirst  = true

    cancelRef.current = sendMessageStreaming(
      {
        query:               q,
        file_id:             fileId,
        conversation_history: conversationHistory,
      },
      // onChunk
      (chunk) => {
        if (isFirst) {
          setIsTyping(false)
          isFirst = false
        }
        fullText += chunk
        setStreaming(fullText)
      },
      // onDone
      (meta) => {
        setMessages(prev => [...prev, {
          id:         Date.now() + 1,
          role:       'assistant',
          content:    fullText || 'No response received.',
          tier:       meta?.tier || 2,
          latency_ms: meta?.latency_ms || 0,
        }])
        
        // --- SYNC WITH LABS ---
        if (meta?.category === 'simulation' && meta?.structured_response) {
           useStore.getState().addPredictionResult(meta.structured_response)
        } else if (meta?.category === 'analysis' && meta?.lab_narrative) {
           // analysis lab sync (if needed)
        }

        setStreaming('')
        setIsTyping(false)
        setInFlight(false)
        fullText = ''
      },
      // onError
      (err) => {
        setMessages(prev => [...prev, {
          id:      Date.now() + 1,
          role:    'assistant',
          content: 'Connection error. Please try again.',
          tier:    1,
          isError: true,
        }])
        setStreaming('')
        setIsTyping(false)
        setInFlight(false)
      }
    )
  }, [query, inFlight, fileId, messages])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const tierLabels = { 1:'⚡', 2:'💬', 3:'🔬' }

  return (
    <div style={{
      display: 'flex', flexDirection: 'column',
      height: '100%', overflow: 'hidden',
      background: 'var(--bg-card)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 14,
    }}>

      {/* ── HEADER (Tidio style) ── */}
      <div style={{
        padding: '14px 16px',
        background: `linear-gradient(135deg, ${
          dotColor === '#06d2ff'
            ? 'rgba(6,210,255,0.15), rgba(6,210,255,0.05)'
            : 'rgba(124,111,255,0.15), rgba(124,111,255,0.05)'
        })`,
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex', alignItems: 'center', gap: 12,
        flexShrink: 0,
      }}>
        {/* Avatar */}
        <div style={{
          width: 38, height: 38, borderRadius: '50%',
          background: `linear-gradient(135deg, ${dotColor}, ${
            dotColor === '#06d2ff' ? '#0499cc' : '#5b52e0'
          })`,
          display: 'flex', alignItems: 'center',
          justifyContent: 'center', fontSize: 18, flexShrink: 0,
          boxShadow: `0 0 12px ${dotColor}40`,
        }}>🤖</div>

        <div style={{ flex: 1 }}>
          <div style={{
            fontFamily: 'Syne, sans-serif', fontSize: 14,
            fontWeight: 700, color: 'var(--text-primary)',
            lineHeight: 1.2,
          }}>{title}</div>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 5,
            marginTop: 2,
          }}>
            <div style={{
              width: 7, height: 7, borderRadius: '50%',
              background: fileId ? 'var(--green)' : 'var(--text-muted)',
              boxShadow: fileId ? '0 0 5px var(--green)' : 'none',
              animation: fileId ? 'chatPulse 2s infinite' : 'none',
            }} />
            <span style={{
              fontSize: 11, color: 'var(--text-muted)',
            }}>
              {fileId ? 'Active Neural Link' : 'Load a dataset first'}
            </span>
          </div>
        </div>

        {/* Tier legend */}
        <div style={{
          display: 'flex', gap: 4, flexShrink: 0,
        }}>
          {[
            { label:'⚡', title:'Instant',  bg:'rgba(0,224,150,0.15)',  color:'var(--green)' },
            { label:'💬', title:'Quick',    bg:'rgba(6,210,255,0.15)', color:'var(--cyan)' },
            { label:'🔬', title:'Deep',     bg:'rgba(124,111,255,0.15)',color:'var(--purple)' },
          ].map(t => (
            <div key={t.label} title={t.title} style={{
              width: 22, height: 22, borderRadius: 6,
              background: t.bg, color: t.color,
              display: 'flex', alignItems: 'center',
              justifyContent: 'center', fontSize: 11,
              cursor: 'default',
            }}>{t.label}</div>
          ))}
        </div>
      </div>

      {/* ── MESSAGES AREA ── */}
      <div style={{
        flex: 1, overflowY: 'auto',
        padding: '16px 12px',
        display: 'flex', flexDirection: 'column', gap: 4,
      }}>

        {/* No file warning */}
        {!fileId && (
          <div style={{
            background: 'rgba(255,181,71,0.08)',
            border: '1px solid rgba(255,181,71,0.2)',
            borderRadius: 10, padding: '10px 14px',
            fontSize: 12, color: 'var(--amber)',
            textAlign: 'center', lineHeight: 1.6,
          }}>
            ⚠️ Upload a dataset to enable the AI assistant
          </div>
        )}

        {/* Suggestions (shown when no messages) */}
        {fileId && messages.length === 0 && !inFlight && (
          <div style={{ marginBottom: 8 }}>
            <div style={{
              fontSize: 10, color: 'var(--text-muted)',
              fontWeight: 700, letterSpacing: '0.08em',
              textTransform: 'uppercase', marginBottom: 8,
              textAlign: 'center',
            }}>Try asking</div>
            {suggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => {
                  setQuery(s)
                  inputRef.current?.focus()
                }}
                style={{
                  display: 'block', width: '100%',
                  textAlign: 'left',
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 20,
                  padding: '7px 14px', marginBottom: 6,
                  fontSize: 12, color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontFamily: 'DM Sans, sans-serif',
                  transition: 'all 0.15s ease',
                }}
                onMouseEnter={e => {
                  e.target.style.borderColor = dotColor + '60'
                  e.target.style.color = 'var(--text-primary)'
                }}
                onMouseLeave={e => {
                  e.target.style.borderColor = 'var(--border-subtle)'
                  e.target.style.color = 'var(--text-secondary)'
                }}
              >{s}</button>
            ))}
          </div>
        )}

        {/* Messages */}
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            msg={msg}
            accentColor={accentColor}
            dotColor={dotColor}
            tierLabels={tierLabels}
          />
        ))}

        {/* Streaming bubble */}
        {streaming && (
          <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end',
                        marginBottom: 4 }}>
            <div style={{
              width: 28, height: 28, borderRadius: '50%',
              background: `linear-gradient(135deg,${dotColor},${
                dotColor === '#06d2ff' ? '#0499cc' : '#5b52e0'})`,
              display: 'flex', alignItems: 'center',
              justifyContent: 'center', fontSize: 14, flexShrink: 0,
            }}>🤖</div>
            <div style={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '16px 16px 16px 4px',
              padding: '10px 14px',
              maxWidth: '82%', fontSize: 13,
              color: 'var(--text-primary)',
              lineHeight: 1.6,
              boxShadow: 'var(--shadow-sm)',
            }}>
              {streaming}
              <span style={{
                color: dotColor,
                animation: 'blink 0.7s infinite',
              }}>▌</span>
            </div>
          </div>
        )}

        {/* Typing indicator (before first chunk arrives) */}
        {isTyping && !streaming && (
          <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end',
                        marginBottom: 4 }}>
            <div style={{
              width: 28, height: 28, borderRadius: '50%',
              background: `linear-gradient(135deg,${dotColor},${
                dotColor === '#06d2ff' ? '#0499cc' : '#5b52e0'})`,
              display: 'flex', alignItems: 'center',
              justifyContent: 'center', fontSize: 14, flexShrink: 0,
            }}>🤖</div>
            <div style={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '16px 16px 16px 4px',
              padding: '12px 16px',
              display: 'flex', gap: 5, alignItems: 'center',
              boxShadow: 'var(--shadow-sm)',
            }}>
              {[0,1,2].map(i => (
                <div key={i} style={{
                  width: 7, height: 7, borderRadius: '50%',
                  background: dotColor,
                  opacity: 0.4,
                  animation: `typingDot 1.2s ease ${i * 0.2}s infinite`,
                }} />
              ))}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* ── INPUT BAR (Tidio style) ── */}
      <div style={{
        padding: '10px 12px',
        borderTop: '1px solid var(--border-subtle)',
        background: 'var(--bg-elevated)',
        display: 'flex', gap: 8, alignItems: 'flex-end',
        flexShrink: 0,
        borderRadius: '0 0 14px 14px',
      }}>
        <textarea
          ref={inputRef}
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={fileId ? placeholder : 'Load a dataset first...'}
          disabled={!fileId || inFlight}
          rows={1}
          style={{
            flex: 1, resize: 'none',
            background: 'transparent',
            border: 'none', outline: 'none',
            color: 'var(--text-primary)',
            fontSize: 13, lineHeight: 1.5,
            fontFamily: 'DM Sans, sans-serif',
            padding: '4px 0',
            maxHeight: 80, overflowY: 'auto',
            opacity: (!fileId || inFlight) ? 0.5 : 1,
          }}
          onInput={e => {
            e.target.style.height = 'auto'
            e.target.style.height = Math.min(
              e.target.scrollHeight, 80) + 'px'
          }}
        />

        {/* Circular send button — Tidio style */}
        <button
          onClick={handleSend}
          disabled={!query.trim() || !fileId || inFlight}
          style={{
            width: 36, height: 36, borderRadius: '50%',
            background: query.trim() && fileId && !inFlight
              ? `linear-gradient(135deg, ${dotColor}, ${
                  dotColor === '#06d2ff' ? '#0499cc' : '#5b52e0'
                })`
              : 'var(--bg-overlay)',
            border: 'none', cursor:
              query.trim() && fileId && !inFlight
                ? 'pointer' : 'not-allowed',
            display: 'flex', alignItems: 'center',
            justifyContent: 'center', flexShrink: 0,
            transition: 'all 0.2s',
            boxShadow: query.trim() && fileId && !inFlight
              ? `0 2px 12px ${dotColor}40`
              : 'none',
          }}
        >
          {inFlight ? (
            <div style={{
              width: 14, height: 14,
              border: '2px solid rgba(255,255,255,0.3)',
              borderTop: '2px solid white',
              borderRadius: '50%',
              animation: 'spin 0.8s linear infinite',
            }} />
          ) : (
            <svg width="16" height="16" viewBox="0 0 24 24"
                 fill="none">
              <path d="M22 2L11 13" stroke="#08111f"
                    strokeWidth="2.5" strokeLinecap="round"
                    strokeLinejoin="round"/>
              <path d="M22 2L15 22L11 13L2 9L22 2Z"
                    stroke="#08111f" strokeWidth="2.5"
                    strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          )}
        </button>
      </div>

      <style>{`
        @keyframes chatPulse {
          0%,100%{opacity:1} 50%{opacity:0.4}
        }
        @keyframes blink {
          0%,100%{opacity:1} 50%{opacity:0}
        }
        @keyframes typingDot {
          0%,100%{opacity:0.4;transform:translateY(0)}
          50%{opacity:1;transform:translateY(-3px)}
        }
        @keyframes spin {
          to{transform:rotate(360deg)}
        }
      `}</style>
    </div>
  )
}

// ── Individual message bubble ──
function MessageBubble({ msg, accentColor, dotColor, tierLabels }) {
  const isUser = msg.role === 'user'

  if (msg.isSystem) {
    return (
      <div style={{
        background: 'rgba(124,111,255,0.08)',
        border: '1px solid rgba(124,111,255,0.18)',
        borderRadius: 10, padding: '9px 14px',
        fontSize: 12, color: 'var(--text-secondary)',
        fontStyle: 'italic', textAlign: 'center',
        margin: '6px 0',
      }}>{msg.content}</div>
    )
  }

  if (isUser) {
    return (
      <div style={{
        display: 'flex', justifyContent: 'flex-end',
        marginBottom: 4,
      }}>
        <div style={{
          background: `linear-gradient(135deg, ${dotColor}, ${
            dotColor === '#06d2ff' ? '#0499cc' : '#5b52e0'
          })`,
          borderRadius: '16px 16px 4px 16px',
          padding: '10px 14px',
          maxWidth: '80%', fontSize: 13,
          color: '#08111f', fontWeight: 500,
          lineHeight: 1.6, wordBreak: 'break-word',
          boxShadow: `0 2px 12px ${dotColor}30`,
        }}>
          {msg.content}
        </div>
      </div>
    )
  }

  // AI message
  return (
    <div style={{
      display: 'flex', gap: 8,
      alignItems: 'flex-end', marginBottom: 4,
    }}>
      {/* Small bot avatar */}
      <div style={{
        width: 28, height: 28, borderRadius: '50%',
        background: `linear-gradient(135deg,${dotColor},${
          dotColor === '#06d2ff' ? '#0499cc' : '#5b52e0'})`,
        display: 'flex', alignItems: 'center',
        justifyContent: 'center', fontSize: 14,
        flexShrink: 0,
      }}>🤖</div>

      <div style={{ maxWidth: '80%' }}>
        <div style={{
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '16px 16px 16px 4px',
          padding: '10px 14px',
          fontSize: 13, color: 'var(--text-primary)',
          lineHeight: 1.6, wordBreak: 'break-word',
          boxShadow: 'var(--shadow-sm)',
        }}>
          {msg.content}
        </div>
        {/* Meta row */}
        <div style={{
          display: 'flex', gap: 6,
          alignItems: 'center', marginTop: 4,
          paddingLeft: 4,
        }}>
          {msg.tier && (
            <span style={{
              fontSize: 10, fontWeight: 700,
              padding: '1px 6px', borderRadius: 4,
              background: msg.tier === 1
                ? 'rgba(0,224,150,0.15)'
                : msg.tier === 2
                ? 'rgba(6,210,255,0.15)'
                : 'rgba(124,111,255,0.15)',
              color: msg.tier === 1 ? 'var(--green)'
                   : msg.tier === 2 ? 'var(--cyan)'
                   : 'var(--purple)',
            }}>
              {tierLabels[msg.tier]}
            </span>
          )}
          {msg.latency_ms > 0 && (
            <span style={{
              fontSize: 10, color: 'var(--text-muted)',
            }}>
              {msg.latency_ms < 1000
                ? `${msg.latency_ms}ms`
                : `${(msg.latency_ms/1000).toFixed(1)}s`}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
