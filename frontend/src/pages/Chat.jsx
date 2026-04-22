import React, { useState, useRef, useEffect } from 'react'
import toast from 'react-hot-toast'
import useStore from '../store/useStore'
import { sendMessage, streamChat } from '../api/chat'
import '../styles/chat.css'

const Chat = () => {
    const activeFile = useStore(s => s.activeFile)
    const chatHistory = useStore(s => s.chatHistory)
    const addChatMessage = useStore(s => s.addChatMessage)
    const [input, setInput] = useState('')
    const [isThinking, setIsThinking] = useState(false)
    const [streamingContent, setStreamingContent] = useState('')
    const chatEndRef = useRef(null)

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [chatHistory, streamingContent])

    const handleSend = async (e) => {
        e.preventDefault()
        if (!input.trim() || isThinking || !activeFile) return

        const query = input
        setInput('')
        
        // Add user message
        addChatMessage({ role: 'user', content: query, timestamp: new Date() })
        setIsThinking(true)
        setStreamingContent('')

        try {
            // Check tier first or just go for it (the backend handles it)
            // For now, let's treat it as a potential stream
            let fullContent = ''
            
            streamChat(
                { query, file_id: activeFile.id, conversation_history: chatHistory },
                (chunk) => {
                    setStreamingContent(prev => prev + chunk)
                    fullContent += chunk
                },
                (doneData) => {
                    setIsThinking(false)
                    addChatMessage({ 
                        role: 'assistant', 
                        content: fullContent, 
                        tier: doneData.tier || 2,
                        latency: doneData.latency_ms,
                        timestamp: new Date() 
                    })
                    setStreamingContent('')
                },
                (err) => {
                    setIsThinking(false)
                    toast.error('Forensic uplink lost')
                }
            )
        } catch (err) {
            setIsThinking(false)
            toast.error('Transmission failed')
        }
    }

    if (!activeFile) {
        return (
            <div className="chat-empty">
                <span className="empty-icon">⚠️</span>
                <h3>Neural Interface Locked</h3>
                <p>Please select an active asset from the Dashboard to begin interrogation.</p>
            </div>
        )
    }

    return (
        <div className="chat-container">
            <div className="chat-messages">
                {chatHistory.map((msg, i) => (
                    <div key={i} className={`message-wrapper ${msg.role}`}>
                        <div className="message-avatar">
                            {msg.role === 'user' ? 'U' : 'DM'}
                        </div>
                        <div className="message-bubble">
                            <div className="message-content">{msg.content}</div>
                            {msg.latency && (
                                <div className="message-meta">
                                    Tier {msg.tier} • {msg.latency}ms
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {streamingContent && (
                    <div className="message-wrapper assistant">
                        <div className="message-avatar">DM</div>
                        <div className="message-bubble">
                            <div className="message-content">{streamingContent}</div>
                        </div>
                    </div>
                )}

                {isThinking && !streamingContent && (
                    <div className="message-wrapper assistant">
                        <div className="message-avatar thinking-avatar">DM</div>
                        <div className="message-bubble thinking-bubble">
                            <div className="typing-indicator">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>

            <form className="chat-input-area" onSubmit={handleSend}>
                <input 
                    type="text" 
                    placeholder="Interrogate active asset..." 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={isThinking}
                />
                <button type="submit" disabled={isThinking || !input.trim()}>
                    Execute
                </button>
            </form>
        </div>
    )
}

export default Chat
