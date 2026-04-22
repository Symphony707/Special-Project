import api from './client'

export const sendMessage = (data) =>
  api.post('/chat/message', data)

export const sendMessageStreaming = (data, onChunk, onDone, onError) => {
  const url = `${api.defaults.baseURL}/chat/message`
  
  // Custom fetch for SSE with credentials
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    // For cookies inclusion:
    credentials: 'include'
  }).then(response => {
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    function read() {
      reader.read().then(({ done, value }) => {
        if (done) return
        
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')
        
        lines.forEach(line => {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.chunk) onChunk(data.chunk)
              if (data.done) onDone(data)
            } catch (e) { console.error('Parse error', e) }
          }
        })
        read()
      })
    }
    read()
  }).catch(onError)
}

export const streamChat = (data, onChunk, onDone, onError) => {
  return sendMessageStreaming(data, onChunk, onDone, onError);
};
