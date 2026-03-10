import { useState, useRef, useEffect } from 'react'
import { Send, MessageSquare, User, Bot, Trash2, Dna, Activity, Plus } from 'lucide-react'
import { api } from '../utils/api.js'
import { parseMarkdown } from '../utils/helpers.js'

const QUICK_QUESTIONS = [
  "What does it mean if a variant is 'Likely Pathogenic'?",
  "Explain autosomal recessive inheritance",
  "What is genetic counseling and when should I seek it?",
  "How reliable is genetic testing for rare diseases?",
  "What is the difference between a carrier and being affected?",
  "How do I find clinical trials for my condition?",
]

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className="animate-in" style={{
      display: 'flex', gap: 12, marginBottom: 20,
      flexDirection: isUser ? 'row-reverse' : 'row',
      alignItems: 'flex-start'
    }}>
      {/* Avatar */}
      <div style={{
        width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: isUser
          ? 'linear-gradient(135deg, var(--accent-primary), var(--accent-teal))'
          : 'linear-gradient(135deg, #1e3a5f, #162a44)',
        border: isUser ? 'none' : '1px solid rgba(59,130,246,0.3)'
      }}>
        {isUser ? <User size={16} color="white" /> : <Bot size={16} color="var(--accent-glow)" />}
      </div>

      {/* Bubble */}
      <div style={{
        maxWidth: '75%',
        padding: '14px 16px',
        borderRadius: isUser ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
        background: isUser ? 'var(--accent-primary)' : 'var(--bg-surface)',
        border: isUser ? 'none' : '1px solid var(--border)',
        fontSize: 14,
        lineHeight: 1.7,
        color: isUser ? 'white' : 'var(--text-primary)',
      }}>
        {isUser ? (
          <span>{msg.content}</span>
        ) : (
          <div
            className="prose"
            dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.content) }}
          />
        )}
        {msg.latency && (
          <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', opacity: 0.5, marginTop: 8 }}>
            {msg.demo ? 'demo' : `${msg.latency.toFixed(1)}s`}
          </div>
        )}
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div style={{ display: 'flex', gap: 12, marginBottom: 20, alignItems: 'flex-start' }}>
      <div style={{
        width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'linear-gradient(135deg, #1e3a5f, #162a44)',
        border: '1px solid rgba(59,130,246,0.3)'
      }}>
        <Bot size={16} color="var(--accent-glow)" />
      </div>
      <div style={{
        padding: '14px 20px', borderRadius: '4px 16px 16px 16px',
        background: 'var(--bg-surface)', border: '1px solid var(--border)',
        display: 'flex', gap: 6, alignItems: 'center'
      }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{
            width: 7, height: 7, borderRadius: '50%',
            background: 'var(--accent-primary)',
            animation: `blink 1.2s ease ${i * 0.2}s infinite`
          }} />
        ))}
      </div>
    </div>
  )
}

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I'm **RareNav AI**, powered by MedGemma. I'm here to help you understand rare genetic diseases, genetic variants, test results, and diagnostic pathways.\n\nI can explain:\n- Genetic variant clinical significance\n- Rare disease symptoms and genetics\n- Inheritance patterns and family risk\n- Diagnostic approaches and next steps\n\nHow can I help you today?"
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(`session_${Date.now()}`)
  const [context, setContext] = useState(null)
  const [contextInput, setContextInput] = useState({ gene: '', variant: '', disease: '' })
  const [showContextPanel, setShowContextPanel] = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const send = async (text) => {
    const msg = (text || input).trim()
    if (!msg || loading) return

    setMessages(prev => [...prev, { role: 'user', content: msg }])
    setInput('')
    setLoading(true)

    try {
      const res = await api.chat.message({
        session_id: sessionId,
        message: msg,
        context: context || undefined
      })
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.reply,
        latency: res.latency,
        demo: res.demo_mode
      }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      }])
    } finally {
      setLoading(false)
    }
  }

  const setContextFromInputs = () => {
    if (contextInput.gene || contextInput.disease) {
      setContext(contextInput)
    }
    setShowContextPanel(false)
  }

  const clearChat = () => {
    setMessages([{
      role: 'assistant',
      content: "Chat cleared. How can I help you with rare genetic diseases?"
    }])
    api.chat.clearSession(sessionId).catch(() => {})
  }

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 60px)' }}>
      {/* Sidebar */}
      <div style={{
        width: 280, flexShrink: 0,
        borderRight: '1px solid var(--border)',
        background: 'var(--bg-surface)',
        display: 'flex', flexDirection: 'column',
        padding: 16, overflowY: 'auto'
      }} className="hide-mobile">
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 12 }}>
            QUICK QUESTIONS
          </div>
          {QUICK_QUESTIONS.map((q, i) => (
            <button key={i}
              onClick={() => send(q)}
              style={{
                display: 'block', width: '100%', textAlign: 'left',
                padding: '8px 10px', borderRadius: 6, marginBottom: 4,
                background: 'transparent', border: '1px solid var(--border)',
                cursor: 'pointer', fontSize: 12, color: 'var(--text-secondary)',
                transition: 'all 0.15s', lineHeight: 1.4
              }}
              onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-raised)'; e.currentTarget.style.color = 'var(--text-primary)'; e.currentTarget.style.borderColor = 'var(--border-bright)' }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-secondary)'; e.currentTarget.style.borderColor = 'var(--border)' }}
            >
              {q}
            </button>
          ))}
        </div>

        <div style={{ borderTop: '1px solid var(--border)', paddingTop: 16 }}>
          <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 12 }}>
            VARIANT CONTEXT
          </div>

          {context ? (
            <div style={{ padding: '10px 12px', borderRadius: 8, background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.2)', marginBottom: 8 }}>
              <div style={{ fontSize: 12, color: 'var(--accent-glow)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                {context.gene} {context.variant}
              </div>
              {context.disease && <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>{context.disease?.slice(0, 40)}</div>}
              <button className="btn btn-ghost btn-sm" style={{ marginTop: 6, fontSize: 10, padding: '3px 8px' }} onClick={() => setContext(null)}>Clear context</button>
            </div>
          ) : (
            <button className="btn btn-ghost btn-sm w-full" onClick={() => setShowContextPanel(!showContextPanel)}>
              <Plus size={12} /> Set gene/variant context
            </button>
          )}

          {showContextPanel && (
            <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 8 }}>
              <input className="input input-mono" value={contextInput.gene} onChange={e => setContextInput(p => ({ ...p, gene: e.target.value.toUpperCase() }))} placeholder="Gene (e.g., CFTR)" style={{ fontSize: 12 }} />
              <input className="input input-mono" value={contextInput.variant} onChange={e => setContextInput(p => ({ ...p, variant: e.target.value }))} placeholder="Variant (optional)" style={{ fontSize: 12 }} />
              <input className="input" value={contextInput.disease} onChange={e => setContextInput(p => ({ ...p, disease: e.target.value }))} placeholder="Disease (optional)" style={{ fontSize: 12 }} />
              <button className="btn btn-primary btn-sm" onClick={setContextFromInputs}>Set Context</button>
            </div>
          )}
        </div>

        <div style={{ marginTop: 'auto', paddingTop: 16, borderTop: '1px solid var(--border)' }}>
          <button className="btn btn-ghost btn-sm w-full" onClick={clearChat} style={{ color: 'var(--accent-rose)', borderColor: 'rgba(244,63,94,0.2)' }}>
            <Trash2 size={13} /> Clear Chat
          </button>
        </div>
      </div>

      {/* Chat area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px', maxWidth: 820, margin: '0 auto', width: '100%' }}>
          {messages.map((msg, i) => <Message key={i} msg={msg} />)}
          {loading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>

        {/* Input area */}
        <div style={{
          borderTop: '1px solid var(--border)',
          padding: '16px 24px',
          background: 'var(--bg-deep)',
          maxWidth: 820, margin: '0 auto', width: '100%'
        }}>
          {context && (
            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)', marginBottom: 8 }}>
              Context: {context.gene} {context.variant}
            </div>
          )}
          <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
            <textarea
              ref={textareaRef}
              className="input"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  send()
                }
              }}
              placeholder="Ask about genetic variants, rare diseases, inheritance... (Enter to send)"
              rows={2}
              style={{ resize: 'none', flex: 1, lineHeight: 1.5 }}
            />
            <button
              className="btn btn-primary"
              onClick={() => send()}
              disabled={loading || !input.trim()}
              style={{ height: 48, padding: '0 18px', flexShrink: 0 }}
            >
              {loading ? <div className="spinner" /> : <Send size={16} />}
            </button>
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6, fontFamily: 'var(--font-mono)' }}>
            Shift+Enter for new line • Powered by MedGemma 4B
          </div>
        </div>
      </div>
    </div>
  )
}
