import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Bot, User, Brain, Search, Activity, FileText, CheckCircle,
  AlertCircle, Upload, Plus, X, Loader2, ChevronDown, ChevronUp,
  Dna, Zap, Clock, ArrowRight, BarChart2, Users, ClipboardList,
  Heart, Shield, Microscope, RefreshCw, Send, Paperclip
} from 'lucide-react'

// ── Design tokens ────────────────────────────────────────────────────────
const T = {
  bg: '#050810',
  bgCard: '#0a0f1e',
  bgRaised: '#0f1629',
  bgHover: '#141b30',
  border: 'rgba(99,179,237,0.12)',
  borderBright: 'rgba(99,179,237,0.28)',
  teal: '#2dd4bf',
  tealDim: 'rgba(45,212,191,0.15)',
  tealGlow: 'rgba(45,212,191,0.35)',
  blue: '#60a5fa',
  blueDim: 'rgba(96,165,250,0.12)',
  rose: '#fb7185',
  roseDim: 'rgba(251,113,133,0.12)',
  amber: '#fbbf24',
  amberDim: 'rgba(251,191,36,0.12)',
  green: '#34d399',
  greenDim: 'rgba(52,211,153,0.12)',
  purple: '#a78bfa',
  purpleDim: 'rgba(167,139,250,0.12)',
  textBright: '#f0f6ff',
  textPrimary: '#c8d8f0',
  textSecondary: '#7a94b8',
  textMuted: '#4a6080',
  mono: "'DM Mono', 'Fira Code', monospace",
  sans: "'Sora', 'Plus Jakarta Sans', sans-serif",
}

// ── Step definitions ─────────────────────────────────────────────────────
const STEP_CONFIG = {
  input_parsing:   { icon: FileText,    color: T.teal,   label: 'Input Parsing' },
  report_extraction: { icon: Upload,    color: T.blue,   label: 'Report Extraction' },
  clinvar_query:   { icon: Search,      color: T.blue,   label: 'ClinVar Query' },
  hpo_mapping:     { icon: Activity,    color: T.purple, label: 'HPO Mapping' },
  ai_reasoning:    { icon: Brain,       color: T.amber,  label: 'AI Reasoning' },
  report_generated:{ icon: CheckCircle, color: T.green,  label: 'Report Generated' },
  error:           { icon: AlertCircle, color: T.rose,   label: 'Error' },
}

const URGENCY_CONFIG = {
  critical: { color: T.rose,   bg: T.roseDim,   label: 'CRITICAL' },
  high:     { color: T.amber,  bg: T.amberDim,  label: 'HIGH' },
  medium:   { color: T.blue,   bg: T.blueDim,   label: 'MEDIUM' },
  low:      { color: T.green,  bg: T.greenDim,  label: 'LOW' },
}

const CONFIDENCE_COLOR = { high: T.green, medium: T.amber, low: T.rose }

// ── Atoms ────────────────────────────────────────────────────────────────
function GlowDot({ color = T.teal, pulse = false }) {
  return (
    <span style={{
      display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
      background: color, boxShadow: `0 0 8px ${color}`,
      animation: pulse ? 'pulse 1.5s ease-in-out infinite' : 'none',
      flexShrink: 0,
    }} />
  )
}

function Tag({ children, color = T.teal, style = {} }) {
  return (
    <span style={{
      fontSize: 10, fontFamily: T.mono, fontWeight: 600,
      color, background: color + '22', border: `1px solid ${color}44`,
      borderRadius: 4, padding: '2px 7px', letterSpacing: '0.06em',
      ...style
    }}>{children}</span>
  )
}

function ConfidenceBar({ pct = 0, color = T.teal }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{
        flex: 1, height: 4, background: 'rgba(255,255,255,0.06)',
        borderRadius: 99, overflow: 'hidden',
      }}>
        <div style={{
          height: '100%', width: `${pct}%`, background: color,
          boxShadow: `0 0 8px ${color}`,
          borderRadius: 99,
          transition: 'width 1.2s cubic-bezier(0.16,1,0.3,1)',
        }} />
      </div>
      <span style={{ fontSize: 11, fontFamily: T.mono, color, minWidth: 32 }}>{pct}%</span>
    </div>
  )
}

// ── Trace Step Card ───────────────────────────────────────────────────────
function TraceStepCard({ entry, index, total, isLast }) {
  const [open, setOpen] = useState(false)
  const cfg = STEP_CONFIG[entry.step] || { icon: Zap, color: T.teal, label: entry.step }
  const Icon = cfg.icon
  const isDone = entry.step === 'report_generated'
  const isError = entry.step === 'error'

  return (
    <div style={{ display: 'flex', gap: 10, position: 'relative', animation: 'fadeSlideIn 0.3s ease forwards' }}>
      {/* Connector */}
      {!isLast && (
        <div style={{
          position: 'absolute', left: 15, top: 34, bottom: -4,
          width: 1,
          background: `linear-gradient(to bottom, ${cfg.color}66, transparent)`,
          zIndex: 0,
        }} />
      )}

      {/* Icon bubble */}
      <div style={{
        width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
        background: isDone ? T.greenDim : isError ? T.roseDim : `${cfg.color}18`,
        border: `1.5px solid ${cfg.color}55`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        position: 'relative', zIndex: 1,
        boxShadow: `0 0 12px ${cfg.color}30`,
      }}>
        <Icon size={13} color={cfg.color} />
      </div>

      {/* Content */}
      <div style={{ flex: 1, paddingBottom: 14, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3 }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: T.textPrimary, fontFamily: T.sans }}>
            {cfg.label}
          </span>
          <span style={{ fontSize: 10, fontFamily: T.mono, color: T.textMuted }}>
            +{entry.ts}s
          </span>
        </div>
        <p style={{ fontSize: 12, color: T.textSecondary, margin: 0, lineHeight: 1.5 }}>
          {entry.detail}
        </p>
        {entry.data && (
          <>
            <button onClick={() => setOpen(!open)} style={{
              display: 'flex', alignItems: 'center', gap: 4,
              fontSize: 10, color: T.teal, background: 'none', border: 'none',
              cursor: 'pointer', padding: 0, marginTop: 5, fontFamily: T.mono,
            }}>
              {open ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
              {open ? 'hide details' : 'show details'}
            </button>
            {open && (
              <pre style={{
                fontSize: 10, fontFamily: T.mono,
                background: 'rgba(0,0,0,0.3)', border: `1px solid ${T.border}`,
                borderRadius: 6, padding: '8px 10px', marginTop: 6,
                color: T.textSecondary, overflow: 'auto', maxHeight: 100,
              }}>
                {JSON.stringify(entry.data, null, 2)}
              </pre>
            )}
          </>
        )}
      </div>
    </div>
  )
}

// ── Diagnostic Report Card ────────────────────────────────────────────────
function DiagnosticReport({ report }) {
  const [activeTab, setActiveTab] = useState('diagnosis')
  const urgency = URGENCY_CONFIG[report.urgency] || URGENCY_CONFIG.medium
  const diffs = report.differential_diagnosis || []

  const tabs = [
    { id: 'diagnosis', label: 'Diagnosis', icon: Microscope },
    { id: 'workup', label: 'Workup', icon: ClipboardList },
    { id: 'specialists', label: 'Referrals', icon: Users },
    { id: 'family', label: 'Family', icon: Heart },
  ]

  return (
    <div style={{
      background: T.bgCard,
      border: `1px solid ${T.borderBright}`,
      borderRadius: 16,
      overflow: 'hidden',
      boxShadow: '0 4px 40px rgba(0,0,0,0.4)',
      animation: 'fadeSlideIn 0.5s ease forwards',
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 20px',
        background: `linear-gradient(135deg, rgba(45,212,191,0.08), rgba(96,165,250,0.05))`,
        borderBottom: `1px solid ${T.border}`,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: T.tealDim, border: `1px solid ${T.teal}44`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Dna size={16} color={T.teal} />
          </div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: T.textBright, fontFamily: T.sans }}>
              Diagnostic Report
            </div>
            <div style={{ fontSize: 10, fontFamily: T.mono, color: T.textMuted }}>
              RARENAV AGENT · MedGemma 4B
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', align: 'center', gap: 8 }}>
          <Tag color={urgency.color}>{urgency.label} PRIORITY</Tag>
          <Tag color={CONFIDENCE_COLOR[report.confidence_level] || T.teal}>
            {(report.confidence_level || 'medium').toUpperCase()} CONFIDENCE
          </Tag>
        </div>
      </div>

      {/* Summary */}
      <div style={{ padding: '14px 20px', borderBottom: `1px solid ${T.border}` }}>
        <p style={{ fontSize: 13, color: T.textPrimary, lineHeight: 1.6, margin: 0 }}>
          {report.clinical_summary}
        </p>
      </div>

      {/* Tabs */}
      <div style={{
        display: 'flex', borderBottom: `1px solid ${T.border}`,
        overflowX: 'auto',
      }}>
        {tabs.map(tab => {
          const Icon = tab.icon
          const active = activeTab === tab.id
          return (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '10px 16px', background: 'none',
              border: 'none', borderBottom: active ? `2px solid ${T.teal}` : '2px solid transparent',
              color: active ? T.teal : T.textSecondary,
              fontSize: 12, fontWeight: 600, fontFamily: T.sans,
              cursor: 'pointer', whiteSpace: 'nowrap', transition: 'all 0.15s',
            }}>
              <Icon size={12} />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Tab content */}
      <div style={{ padding: '16px 20px' }}>

        {/* ── Differential Diagnosis ── */}
        {activeTab === 'diagnosis' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {diffs.map((d, i) => {
              const confColor = CONFIDENCE_COLOR[d.confidence] || T.teal
              return (
                <div key={i} style={{
                  background: T.bgRaised, border: `1px solid ${T.border}`,
                  borderRadius: 10, padding: '12px 14px',
                  borderLeft: `3px solid ${confColor}`,
                }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{
                        width: 22, height: 22, borderRadius: '50%',
                        background: `${confColor}22`, border: `1px solid ${confColor}44`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 10, fontWeight: 800, color: confColor, fontFamily: T.mono,
                        flexShrink: 0,
                      }}>{d.rank}</span>
                      <div>
                        <div style={{ fontSize: 13, fontWeight: 700, color: T.textBright, fontFamily: T.sans }}>
                          {d.disease}
                        </div>
                        {d.omim && (
                          <span style={{ fontSize: 10, fontFamily: T.mono, color: T.textMuted }}>
                            OMIM: {d.omim}
                          </span>
                        )}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
                      <Tag color={confColor}>{d.confidence?.toUpperCase()}</Tag>
                      {d.inheritance && <Tag color={T.purple}>{d.inheritance.replace('autosomal ', 'AR ').replace('dominant', 'AD').replace('recessive', 'AR').toUpperCase()}</Tag>}
                    </div>
                  </div>

                  {/* Confidence bar */}
                  <ConfidenceBar pct={d.confidence_pct || (d.confidence === 'high' ? 80 : d.confidence === 'medium' ? 50 : 25)} color={confColor} />

                  {/* Evidence */}
                  {d.supporting_evidence?.length > 0 && (
                    <div style={{ marginTop: 10 }}>
                      <div style={{ fontSize: 10, fontFamily: T.mono, color: T.textMuted, marginBottom: 4 }}>SUPPORTING</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        {d.supporting_evidence.map((e, j) => (
                          <div key={j} style={{ display: 'flex', alignItems: 'flex-start', gap: 6 }}>
                            <span style={{ color: T.green, fontSize: 10, marginTop: 2, flexShrink: 0 }}>✓</span>
                            <span style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.4 }}>{e}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {d.against_evidence?.length > 0 && (
                    <div style={{ marginTop: 8 }}>
                      <div style={{ fontSize: 10, fontFamily: T.mono, color: T.textMuted, marginBottom: 4 }}>AGAINST</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        {d.against_evidence.map((e, j) => (
                          <div key={j} style={{ display: 'flex', alignItems: 'flex-start', gap: 6 }}>
                            <span style={{ color: T.rose, fontSize: 10, marginTop: 2, flexShrink: 0 }}>✗</span>
                            <span style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.4 }}>{e}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* ── Workup ── */}
        {activeTab === 'workup' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {[
              { label: 'IMMEDIATE', key: 'immediate', color: T.rose },
              { label: 'SHORT-TERM (1–3 months)', key: 'short_term', color: T.amber },
              { label: 'GENETIC TESTS', key: 'genetic_tests', color: T.teal },
            ].map(section => {
              const items = report.recommended_workup?.[section.key] || []
              if (!items.length) return null
              return (
                <div key={section.key} style={{
                  background: T.bgRaised, border: `1px solid ${T.border}`,
                  borderRadius: 10, padding: '12px 14px',
                }}>
                  <div style={{ fontSize: 10, fontFamily: T.mono, color: section.color, marginBottom: 8, letterSpacing: '0.08em' }}>
                    {section.label}
                  </div>
                  {items.map((item, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, marginBottom: 6 }}>
                      <ArrowRight size={11} color={section.color} style={{ marginTop: 3, flexShrink: 0 }} />
                      <span style={{ fontSize: 12, color: T.textPrimary, lineHeight: 1.5 }}>{item}</span>
                    </div>
                  ))}
                </div>
              )
            })}
          </div>
        )}

        {/* ── Specialist Referrals ── */}
        {activeTab === 'specialists' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {(report.specialist_referrals || []).map((ref, i) => {
              const urg = URGENCY_CONFIG[ref.urgency] || URGENCY_CONFIG.medium
              return (
                <div key={i} style={{
                  background: T.bgRaised, border: `1px solid ${T.border}`,
                  borderRadius: 10, padding: '12px 14px',
                  display: 'flex', alignItems: 'center', gap: 12,
                }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: 8,
                    background: `${urg.color}18`, border: `1px solid ${urg.color}44`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    flexShrink: 0,
                  }}>
                    <Users size={16} color={urg.color} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: T.textBright, fontFamily: T.sans }}>
                      {ref.specialty}
                    </div>
                    <div style={{ fontSize: 11, color: T.textSecondary, lineHeight: 1.4 }}>{ref.reason}</div>
                  </div>
                  <Tag color={urg.color}>{ref.urgency?.toUpperCase()}</Tag>
                </div>
              )
            })}
          </div>
        )}

        {/* ── Family Implications ── */}
        {activeTab === 'family' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {report.family_implications && (
              <>
                <div style={{
                  background: T.bgRaised, border: `1px solid ${T.border}`,
                  borderRadius: 10, padding: '12px 14px',
                }}>
                  <div style={{ fontSize: 10, fontFamily: T.mono, color: T.teal, marginBottom: 8 }}>INHERITANCE RISK</div>
                  <p style={{ fontSize: 12, color: T.textPrimary, margin: 0, lineHeight: 1.6 }}>
                    {report.family_implications.inheritance_risk}
                  </p>
                </div>
                <div style={{
                  background: T.bgRaised, border: `1px solid ${T.border}`,
                  borderRadius: 10, padding: '12px 14px',
                }}>
                  <div style={{ fontSize: 10, fontFamily: T.mono, color: T.purple, marginBottom: 8 }}>CASCADE TESTING</div>
                  <p style={{ fontSize: 12, color: T.textPrimary, margin: 0, lineHeight: 1.6 }}>
                    {report.family_implications.cascade_testing}
                  </p>
                </div>
                <div style={{
                  background: T.bgRaised, border: `1px solid ${T.border}`,
                  borderRadius: 10, padding: '12px 14px',
                  display: 'flex', alignItems: 'center', gap: 10,
                }}>
                  <Shield size={16} color={T.green} />
                  <div>
                    <div style={{ fontSize: 10, fontFamily: T.mono, color: T.textMuted, marginBottom: 2 }}>GENETIC COUNSELING</div>
                    <span style={{ fontSize: 12, color: T.textPrimary, fontWeight: 600 }}>
                      {report.family_implications.genetic_counseling?.toUpperCase()}
                    </span>
                  </div>
                </div>
              </>
            )}
            {/* Patient summary */}
            {report.patient_summary && (
              <div style={{
                background: `linear-gradient(135deg, ${T.tealDim}, ${T.blueDim})`,
                border: `1px solid ${T.teal}33`, borderRadius: 10, padding: '12px 14px',
              }}>
                <div style={{ fontSize: 10, fontFamily: T.mono, color: T.teal, marginBottom: 6 }}>PATIENT SUMMARY</div>
                <p style={{ fontSize: 12, color: T.textPrimary, margin: 0, lineHeight: 1.6, fontStyle: 'italic' }}>
                  "{report.patient_summary}"
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Message Bubble ────────────────────────────────────────────────────────
function MessageBubble({ msg, onSelectOption }) {
  const isUser = msg.role === 'user'
  const isThinking = msg.type === 'thinking'
  const isQuestion = msg.type === 'question'
  const isSuccess = msg.type === 'success'
  const isError = msg.type === 'error' || msg.type === 'warning'

  const bubbleBg = isUser
    ? `linear-gradient(135deg, rgba(96,165,250,0.18), rgba(45,212,191,0.10))`
    : isThinking ? T.bgRaised
    : isError ? T.roseDim
    : isSuccess ? T.greenDim
    : T.bgCard

  const bubbleBorder = isUser ? `1px solid ${T.blue}44`
    : isThinking ? `1px solid ${T.border}`
    : isError ? `1px solid ${T.rose}44`
    : isSuccess ? `1px solid ${T.green}44`
    : `1px solid ${T.border}`

  // Render markdown-like bold
  const renderContent = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g)
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} style={{ color: T.textBright, fontWeight: 700 }}>{part.slice(2, -2)}</strong>
      }
      return part
    })
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: isUser ? 'row-reverse' : 'row',
      alignItems: 'flex-start',
      gap: 10,
      animation: 'fadeSlideIn 0.25s ease forwards',
    }}>
      {/* Avatar */}
      <div style={{
        width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
        background: isUser ? `linear-gradient(135deg, ${T.blue}, ${T.teal})` : T.bgRaised,
        border: isUser ? 'none' : `1px solid ${T.borderBright}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: isUser ? `0 0 12px ${T.teal}44` : 'none',
      }}>
        {isUser
          ? <User size={14} color="white" />
          : isThinking
            ? <Loader2 size={14} color={T.teal} style={{ animation: 'spin 1s linear infinite' }} />
            : <Bot size={14} color={T.teal} />
        }
      </div>

      {/* Bubble */}
      <div style={{ maxWidth: '72%', display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{
          background: bubbleBg,
          border: bubbleBorder,
          borderRadius: isUser ? '14px 4px 14px 14px' : '4px 14px 14px 14px',
          padding: '10px 14px',
        }}>
          {isThinking ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ display: 'flex', gap: 4 }}>
                {[0, 1, 2].map(i => (
                  <span key={i} style={{
                    width: 5, height: 5, borderRadius: '50%',
                    background: T.teal,
                    animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
                    display: 'inline-block',
                  }} />
                ))}
              </div>
              <span style={{ fontSize: 12, color: T.textSecondary, fontStyle: 'italic' }}>
                {msg.content}
              </span>
            </div>
          ) : (
            <p style={{
              margin: 0, fontSize: 13, lineHeight: 1.65,
              color: isUser ? T.textBright : T.textPrimary,
              fontFamily: T.sans, whiteSpace: 'pre-wrap',
            }}>
              {renderContent(msg.content)}
            </p>
          )}
        </div>

        {/* Quick-select options */}
        {isQuestion && msg.options?.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {msg.options.map((opt, i) => (
              <button key={i} onClick={() => onSelectOption(opt, msg.id)} style={{
                padding: '6px 12px', borderRadius: 20,
                background: T.bgRaised,
                border: `1px solid ${T.teal}55`,
                color: T.teal, fontSize: 11, fontWeight: 600,
                fontFamily: T.sans, cursor: 'pointer',
                transition: 'all 0.15s',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = T.tealDim
                e.currentTarget.style.borderColor = T.teal
                e.currentTarget.style.boxShadow = `0 0 10px ${T.teal}44`
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = T.bgRaised
                e.currentTarget.style.borderColor = `${T.teal}55`
                e.currentTarget.style.boxShadow = 'none'
              }}
              >
                {opt}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Streaming token display ───────────────────────────────────────────────
function StreamingText({ text }) {
  return (
    <div style={{
      background: T.bgCard, border: `1px solid ${T.border}`,
      borderRadius: 10, padding: '12px 14px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <GlowDot color={T.amber} pulse />
        <span style={{ fontSize: 11, fontFamily: T.mono, color: T.amber }}>GENERATING ANALYSIS…</span>
      </div>
      <pre style={{
        fontSize: 10, fontFamily: T.mono, color: T.textSecondary,
        whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: 0,
        maxHeight: 100, overflow: 'hidden',
        maskImage: 'linear-gradient(to bottom, black 60%, transparent)',
      }}>
        {text.slice(-400)}
      </pre>
    </div>
  )
}

// ── Trace Panel ───────────────────────────────────────────────────────────
function TracePanel({ steps, isAnalyzing }) {
  if (steps.length === 0 && !isAnalyzing) return null

  return (
    <div style={{
      background: T.bgCard, border: `1px solid ${T.border}`,
      borderRadius: 12, padding: '14px 16px',
      animation: 'fadeSlideIn 0.3s ease forwards',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
        <GlowDot color={T.teal} pulse={isAnalyzing} />
        <span style={{ fontSize: 11, fontFamily: T.mono, color: T.teal, letterSpacing: '0.08em' }}>
          AGENT TRACE
        </span>
        {isAnalyzing && (
          <span style={{
            fontSize: 10, fontFamily: T.mono, color: T.amber,
            background: T.amberDim, border: `1px solid ${T.amber}44`,
            borderRadius: 99, padding: '2px 8px',
          }}>RUNNING</span>
        )}
      </div>
      <div>
        {steps.map((step, i) => (
          <TraceStepCard
            key={`${step.step}-${i}`}
            entry={step}
            index={i}
            total={steps.length}
            isLast={i === steps.length - 1}
          />
        ))}
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────
export default function AgentChatPage() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [traceSteps, setTraceSteps] = useState([])
  const [report, setReport] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [streamingText, setStreamingText] = useState('')
  const [input, setInput] = useState('')
  const [answeredOptions, setAnsweredOptions] = useState(new Set())
  const [uploadedFile, setUploadedFile] = useState(null)

  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)
  const abortRef = useRef(null)

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, traceSteps, report, streamingText])

  // Init session on mount
  useEffect(() => {
    startNewSession()
    return () => abortRef.current?.abort()
  }, [])

  const startNewSession = async () => {
    setMessages([])
    setTraceSteps([])
    setReport(null)
    setStreamingText('')
    setUploadedFile(null)

    try {
      const res = await fetch('/api/agent/session/new', { method: 'POST' })
      const data = await res.json()
      setSessionId(data.session_id)
      // Trigger greeting
      await sendMessage('', null, data.session_id, null)
    } catch (e) {
      console.error('Failed to create session', e)
    }
  }

  const sendMessage = useCallback(async (
    text = '',
    selectedOption = null,
    sid = sessionId,
    file = uploadedFile
  ) => {
    if (isLoading) return
    if (!text && !selectedOption && !file && sid !== sessionId) return

    setIsLoading(true)
    setStreamingText('')
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    const body = {
      session_id: sid || sessionId,
      message: text,
    }
    if (selectedOption) body.selected_option = selectedOption
    if (file) {
      body.file_data = file.base64
      body.file_type = file.type
    }

    try {
      const res = await fetch('/api/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal,
      })

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const evt = JSON.parse(line.slice(6))
            handleSSEEvent(evt)
          } catch {}
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') console.error('SSE error', e)
    } finally {
      setIsLoading(false)
      setStreamingText('')
      setUploadedFile(null)
    }
  }, [sessionId, isLoading, uploadedFile])

  const handleSSEEvent = (evt) => {
    switch (evt.type) {
      case 'message':
        setMessages(prev => {
          const exists = prev.find(m => m.id === evt.message.id)
          if (exists) return prev
          return [...prev, evt.message]
        })
        if (evt.session_id && !sessionId) setSessionId(evt.session_id)
        break
      case 'trace_step':
        setIsAnalyzing(true)
        setTraceSteps(prev => [...prev, { step: evt.step, detail: evt.detail, ts: evt.ts, data: evt.data }])
        break
      case 'token':
        setStreamingText(prev => prev + (evt.text || ''))
        break
      case 'report':
        setReport(evt.report)
        setIsAnalyzing(false)
        setStreamingText('')
        break
      case 'done':
        setIsAnalyzing(false)
        setStreamingText('')
        break
    }
  }

  const handleSend = () => {
    if (!input.trim() && !uploadedFile) return
    sendMessage(input.trim())
    setInput('')
  }

  const handleSelectOption = (option, msgId) => {
    if (answeredOptions.has(msgId)) return
    setAnsweredOptions(prev => new Set([...prev, msgId]))
    sendMessage('', option)
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      const base64 = ev.target.result.split(',')[1]
      setUploadedFile({ name: file.name, base64, type: file.type })
    }
    reader.readAsDataURL(file)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Sora:wght@400;500;600;700;800&display=swap');

        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; box-shadow: 0 0 8px currentColor; }
          50%       { opacity: 0.5; box-shadow: 0 0 3px currentColor; }
        }
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
          40%            { transform: scale(1); opacity: 1; }
        }
        .option-btn:hover {
          background: ${T.tealDim} !important;
          border-color: ${T.teal} !important;
          box-shadow: 0 0 10px ${T.teal}44 !important;
        }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: ${T.border}; border-radius: 99px; }
      `}</style>

      <div style={{
        minHeight: 'calc(100vh - 60px)',
        background: T.bg,
        fontFamily: T.sans,
        display: 'flex',
        flexDirection: 'column',
      }}>
        {/* Page header */}
        <div style={{
          borderBottom: `1px solid ${T.border}`,
          background: `linear-gradient(to bottom, rgba(10,15,30,0.8), transparent)`,
          padding: '16px 24px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: `linear-gradient(135deg, ${T.tealDim}, ${T.blueDim})`,
              border: `1px solid ${T.teal}44`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: `0 0 16px ${T.teal}30`,
            }}>
              <Brain size={18} color={T.teal} />
            </div>
            <div>
              <div style={{ fontSize: 15, fontWeight: 700, color: T.textBright, letterSpacing: '-0.02em' }}>
                RareNav Agent
              </div>
              <div style={{ fontSize: 10, fontFamily: T.mono, color: T.textMuted }}>
                Powered by MedGemma 4B · Multi-turn diagnostic AI
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            {sessionId && (
              <span style={{ fontSize: 10, fontFamily: T.mono, color: T.textMuted }}>
                SESSION <span style={{ color: T.teal }}>{sessionId}</span>
              </span>
            )}
            <button onClick={startNewSession} style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '6px 12px', borderRadius: 8,
              background: T.bgRaised, border: `1px solid ${T.border}`,
              color: T.textSecondary, fontSize: 11, fontWeight: 600,
              cursor: 'pointer', transition: 'all 0.15s',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = T.teal
              e.currentTarget.style.color = T.teal
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = T.border
              e.currentTarget.style.color = T.textSecondary
            }}
            >
              <RefreshCw size={11} />
              New Session
            </button>
          </div>
        </div>

        {/* Main layout */}
        <div style={{
          flex: 1, display: 'flex', gap: 0,
          maxWidth: 1200, width: '100%', margin: '0 auto',
          padding: '0',
          alignItems: 'stretch',
        }}>

          {/* Left: Chat */}
          <div style={{
            flex: 1, display: 'flex', flexDirection: 'column',
            minWidth: 0,
            borderRight: traceSteps.length > 0 || report ? `1px solid ${T.border}` : 'none',
          }}>
            {/* Messages */}
            <div style={{
              flex: 1, overflowY: 'auto',
              padding: '20px 24px',
              display: 'flex', flexDirection: 'column', gap: 16,
            }}>
              {messages.map((msg) => (
                <MessageBubble
                  key={msg.id}
                  msg={msg}
                  onSelectOption={(opt) => handleSelectOption(opt, msg.id)}
                />
              ))}

              {/* Streaming text preview */}
              {streamingText && <StreamingText text={streamingText} />}

              <div ref={messagesEndRef} />
            </div>

            {/* Input bar */}
            <div style={{
              borderTop: `1px solid ${T.border}`,
              padding: '14px 20px',
              background: T.bgCard,
            }}>
              {uploadedFile && (
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  marginBottom: 10, padding: '6px 12px',
                  background: T.tealDim, border: `1px solid ${T.teal}44`,
                  borderRadius: 8,
                }}>
                  <FileText size={12} color={T.teal} />
                  <span style={{ fontSize: 11, color: T.teal, fontFamily: T.mono, flex: 1 }}>
                    {uploadedFile.name}
                  </span>
                  <button onClick={() => setUploadedFile(null)} style={{
                    background: 'none', border: 'none', cursor: 'pointer', color: T.textMuted,
                    padding: 0, display: 'flex',
                  }}>
                    <X size={12} />
                  </button>
                </div>
              )}

              <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
                <button onClick={() => fileInputRef.current?.click()} style={{
                  width: 36, height: 36, borderRadius: 8, flexShrink: 0,
                  background: T.bgRaised, border: `1px solid ${T.border}`,
                  color: T.textSecondary, display: 'flex', alignItems: 'center', justifyContent: 'center',
                  cursor: 'pointer', transition: 'all 0.15s',
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = T.teal; e.currentTarget.style.color = T.teal }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = T.border; e.currentTarget.style.color = T.textSecondary }}
                title="Upload genetic report">
                  <Paperclip size={14} />
                </button>
                <input ref={fileInputRef} type="file" accept=".pdf,.jpg,.jpeg,.png"
                  style={{ display: 'none' }} onChange={handleFileUpload} />

                <textarea
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Describe symptoms, ask a question, or upload a report…"
                  rows={1}
                  style={{
                    flex: 1, background: T.bgRaised,
                    border: `1px solid ${T.border}`,
                    borderRadius: 10, padding: '9px 14px',
                    color: T.textPrimary, fontSize: 13,
                    fontFamily: T.sans, resize: 'none', outline: 'none',
                    lineHeight: 1.5, minHeight: 36,
                    transition: 'border-color 0.15s',
                  }}
                  onFocus={e => e.target.style.borderColor = T.teal}
                  onBlur={e => e.target.style.borderColor = T.border}
                />

                <button
                  onClick={handleSend}
                  disabled={isLoading || (!input.trim() && !uploadedFile)}
                  style={{
                    width: 36, height: 36, borderRadius: 8, flexShrink: 0,
                    background: (isLoading || (!input.trim() && !uploadedFile))
                      ? T.bgRaised
                      : `linear-gradient(135deg, ${T.teal}, ${T.blue})`,
                    border: `1px solid ${(isLoading || (!input.trim() && !uploadedFile)) ? T.border : 'transparent'}`,
                    color: (isLoading || (!input.trim() && !uploadedFile)) ? T.textMuted : 'white',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    cursor: (isLoading || (!input.trim() && !uploadedFile)) ? 'not-allowed' : 'pointer',
                    transition: 'all 0.15s',
                    boxShadow: (isLoading || (!input.trim() && !uploadedFile)) ? 'none' : `0 0 14px ${T.teal}44`,
                  }}
                >
                  {isLoading
                    ? <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
                    : <Send size={14} />
                  }
                </button>
              </div>
              <div style={{ marginTop: 6, fontSize: 10, fontFamily: T.mono, color: T.textMuted }}>
                Enter to send · Shift+Enter for new line · Supports PDF & image reports
              </div>
            </div>
          </div>

          {/* Right: Trace + Report */}
          {(traceSteps.length > 0 || report) && (
            <div style={{
              width: 420, flexShrink: 0,
              overflowY: 'auto',
              padding: '20px 20px',
              display: 'flex', flexDirection: 'column', gap: 16,
            }}>
              <TracePanel steps={traceSteps} isAnalyzing={isAnalyzing} />
              {report && <DiagnosticReport report={report} />}
            </div>
          )}
        </div>
      </div>
    </>
  )
}
