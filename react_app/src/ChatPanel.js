import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

function ChatPanel({ theme = 'dark' }) {
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Ask me anything about German car sales, 1990–2026 — real numbers from the data, or context on why trends happened.', tag: null }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesContainerRef = useRef(null);

  useEffect(() => {
    // Scroll ONLY the messages container itself, not the whole page —
    // directly setting scrollTop avoids scrollIntoView's page-level scroll.
    const container = messagesContainerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages]);

  const sendQuestion = async () => {
    const question = input.trim();
    if (!question || loading) return;

    setMessages(prev => [...prev, { role: 'user', text: question }]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/ask/', { question });
      setMessages(prev => [...prev, {
        role: 'bot',
        text: response.data.answer,
        tag: response.data.tag,
        sources: response.data.sources
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', text: 'Sorry, something went wrong answering that.', tag: null }]);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') sendQuestion();
  };

  const c = theme === 'dark'
    ? { bg: '#161C2C', border: '#232B3D', text: '#F4F5F7', sub: '#8B93A7', botBg: '#1B2233', userBg: '#4C8DFF', inputBg: '#0F1420' }
    : { bg: '#FFFFFF', border: '#E2E4E9', text: '#171A21', sub: '#5C6272', botBg: '#F4F5F7', userBg: '#4C8DFF', inputBg: '#FFFFFF' };

  return (
    <div style={{
      background: c.bg, border: `1px solid ${c.border}`, borderRadius: 14,
      padding: 18, display: 'flex', flexDirection: 'column', height: 720
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
        <div style={{ width: 9, height: 9, borderRadius: '50%', background: '#34D399' }} />
        <h3 style={{ margin: 0, fontSize: 15, fontWeight: 700, color: c.text }}>Ask the data</h3>
        <span style={{ marginLeft: 'auto', fontSize: 11, color: c.sub }}>Gemini</span>
      </div>

      <div
        ref={messagesContainerRef}
        style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12, paddingRight: 4 }}
      >
        {messages.map((msg, i) => (
          <div key={i} style={{
            maxWidth: '92%',
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
            background: msg.role === 'user' ? c.userBg : c.botBg,
            color: msg.role === 'user' ? '#fff' : c.text,
            border: msg.role === 'bot' ? `1px solid ${c.border}` : 'none',
            borderRadius: 14,
            borderBottomRightRadius: msg.role === 'user' ? 3 : 14,
            borderBottomLeftRadius: msg.role === 'bot' ? 3 : 14,
            padding: '12px 15px',
            fontSize: 14.5,
            lineHeight: 1.6,
          }}>
            {msg.tag && (
              <div style={{
                display: 'inline-block', fontSize: 10, fontWeight: 700, marginBottom: 8,
                textTransform: 'uppercase', letterSpacing: '0.04em', padding: '3px 8px', borderRadius: 6,
                color: msg.tag === 'RAG' ? '#A78BFA' : '#4C8DFF',
                background: msg.tag === 'RAG' ? 'rgba(167,139,250,.15)' : 'rgba(76,141,255,.15)'
              }}>
                {msg.tag}
              </div>
            )}
            <div>{msg.text}</div>
            {msg.sources && (
              <details style={{ marginTop: 8, fontSize: 11.5, color: c.sub, cursor: 'pointer' }}>
                <summary>Sources</summary>
                {typeof msg.sources === 'string'
                  ? <pre style={{ whiteSpace: 'pre-wrap', fontSize: 11 }}>{msg.sources}</pre>
                  : msg.sources.map((s, j) => <div key={j} style={{ marginTop: 5 }}>({s.source}) {s.content}</div>)
                }
              </details>
            )}
          </div>
        ))}
        {loading && <div style={{ fontSize: 13, color: c.sub }}>Thinking...</div>}
      </div>

      <div style={{
        display: 'flex', gap: 10, border: `1px solid ${c.border}`, borderRadius: 12,
        padding: '12px 14px', marginTop: 14, background: c.inputBg
      }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the data..."
          style={{ flex: 1, border: 'none', outline: 'none', background: 'transparent', color: c.text, fontSize: 14 }}
        />
        <button
          onClick={sendQuestion}
          disabled={loading}
          style={{ background: '#4C8DFF', border: 'none', borderRadius: 8, width: 32, height: 32, cursor: 'pointer', color: '#fff', fontSize: 16 }}
        >
          →
        </button>
      </div>
    </div>
  );
}

export default ChatPanel;