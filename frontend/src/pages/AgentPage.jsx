import { useState, useRef } from 'react'
import {
  Bot, Upload, Dna, Activity, FileText, ChevronRight, CheckCircle,
  Loader2, AlertCircle, Zap, Brain, Search, ClipboardList,
  Users, ArrowRight, Info, X, Plus
} from 'lucide-react'
import { parseMarkdown } from '../utils/helpers.js'

const BASE_URL = '/api'

async function postJson(path, body) {
  const r = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  if (!r.ok) {
    const e = await r.json().catch(() => ({ error: `HTTP ${r.status}` }))
    throw new Error(e.error || `HTTP ${r.status}`)
  }
  return r.json()
}

// ── Step Icons ──────────────────────────────────────────────────
const STEP_ICONS = {
  input_parsing: FileText,
  report_extraction: Upload,
  clinvar_query: Search,
  hpo_mapping: Activity,
  ai_reasoning: Brain,
  report_generated: CheckCircle,
  error: AlertCircle,
}

const STEP_COLORS = {
  input_parsing: 'var(--accent-teal)',
  report_extraction: 'var(--accent-glow)',
  clinvar_query: 'var(--accent-primary)',
  hpo_mapping: '#a78bfa',
  ai_reasoning: '#f59e0b',
  report_generated: 'var(--success)',
  error: 'var(--accent-rose)',
}

function TraceStep({ entry, index, total }) {
  const [open, setOpen] = useState(false)
  const Icon = STEP_ICONS[entry.step] || Bot
  const color = STEP_COLORS[entry.step] || 'var(--text-muted)'
  const isLast = index === total - 1
  const isError = entry.step === 'error'
  const isDone = entry.step === 'report_generated'

  return (
    <div style={{ display: 'flex', gap: 12, position: 'relative' }}>
      {/* Connector line */}
      {!isLast && (
        <div style={{
          position: 'absolute', left: 15, top: 32, bottom: -4,
          width: 2, background: 'var(--border)', zIndex: 0
        }} />
      )}

      {/* Icon bubble */}
      <div style={{
        width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
        background: isError ? 'rgba(244,63,94,0.15)' : isDone ? 'rgba(34,197,94,0.15)' : 'var(--bg-raised)',
        border: `2px solid ${color}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        position: 'relative', zIndex: 1
      }}>
        <Icon size={14} color={color} />
      </div>

      {/* Content */}
      <div style={{ flex: 1, paddingBottom: 16, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
          <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-bright)' }}>
            {entry.step.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
          </span>
          <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
            +{entry.ts}s
          </span>
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: entry.data ? 4 : 0 }}>
          {entry.detail}
        </div>
        {entry.data && (
          <button
            onClick={() => setOpen(!open)}
            style={{ fontSize: 10, color: 'var(--accent-primary)', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
          >
            {open ? '▲ hide data' : '▼ show data'}
          </button>
        )}
        {open && entry.data && (
          <pre style={{
            fontSize: 10, background: 'var(--bg-raised)', padding: '8px 10px',
            borderRadius: 6, marginTop: 6, overflow: 'auto',
            color: 'var(--text-secondary)', maxHeight: 120
          }}>
            {JSON.stringify(entry.data, null, 2)}
          </pre>
        )}
      </div>
    </div>
  )
}

function UrgencyBadge({ urgency }) {
  const map = {
    critical: { label: 'CRITICAL', color: '#ef4444' },
    high: { label: 'HIGH', color: '#f97316' },
    medium: { label: 'MEDIUM', color: '#eab308' },
    low: { label: 'LOW', color: '#22c55e' },
  }
  const u = map[urgency] || { label: urgency?.toUpperCase() || 'UNKNOWN', color: 'var(--text-muted)' }
  return (
    <span style={{
      fontSize: 10, fontWeight: 700, fontFamily: 'var(--font-mono)',
      color: u.color, background: u.color + '20',
      padding: '2px 8px', borderRadius: 99, border: `1px solid ${u.color}40`,
      letterSpacing: '0.06em'
    }}>
      {u.label}
    </span>
  )
}

function ConfidenceDots({ level }) {
  const levels = { high: 3, medium: 2, low: 1 }
  const n = levels[level] || 1
  return (
    <span style={{ display: 'inline-flex', gap: 3, alignItems: 'center' }}>
      {[1,2,3].map(i => (
        <span key={i} style={{
          width: 6, height: 6, borderRadius: '50%',
          background: i <= n ? 'var(--accent-teal)' : 'var(--border)'
        }} />
      ))}
    </span>
  )
}

function DiagnosticReport({ report }) {
  const [tab, setTab] = useState('summary')
  const tabs = [
    { id: 'summary', label: 'Summary' },
    { id: 'differential', label: `Differential (${report.differential_diagnosis?.length || 0})` },
    { id: 'workup', label: 'Workup' },
    { id: 'management', label: 'Management' },
    { id: 'family', label: 'Family Risk' },
  ]

  if (report.error && !report.clinical_summary) {
    return (
      <div style={{ padding: 16, borderRadius: 8, background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', color: 'var(--accent-rose)', fontSize: 13 }}>
        Agent error: {report.error}
      </div>
    )
  }

  return (
    <div>
      {/* Tab bar */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 16, flexWrap: 'wrap' }}>
        {tabs.map(t => (
          <button key={t.id}
            className={`btn btn-sm ${tab === t.id ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setTab(t.id)}
            style={{ fontSize: 11 }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Summary tab */}
      {tab === 'summary' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {report.urgency && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>URGENCY</span>
              <UrgencyBadge urgency={report.urgency} />
            </div>
          )}

          {report.clinical_summary && (
            <div>
              <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 6 }}>CLINICAL SUMMARY (FOR PHYSICIAN)</div>
              <div style={{
                padding: '12px 14px', borderRadius: 8, background: 'rgba(59,130,246,0.08)',
                border: '1px solid rgba(59,130,246,0.2)', fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.7
              }}>
                {report.clinical_summary}
              </div>
            </div>
          )}

          {report.patient_summary && (
            <div>
              <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 6 }}>PLAIN LANGUAGE SUMMARY (FOR PATIENT)</div>
              <div style={{
                padding: '12px 14px', borderRadius: 8, background: 'rgba(45,212,191,0.07)',
                border: '1px solid rgba(45,212,191,0.2)', fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.7
              }}>
                {report.patient_summary}
              </div>
            </div>
          )}

          {report.genetic_interpretation && (
            <div>
              <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 6 }}>GENETIC INTERPRETATION</div>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 6 }}>
                {report.genetic_interpretation.overall_classification}
              </div>
              {report.genetic_interpretation.key_findings?.map((f, i) => (
                <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 4, alignItems: 'flex-start' }}>
                  <CheckCircle size={12} color="var(--accent-teal)" style={{ marginTop: 2, flexShrink: 0 }} />
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{f}</span>
                </div>
              ))}
            </div>
          )}

          {report.specialist_referrals?.length > 0 && (
            <div>
              <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 6 }}>SPECIALIST REFERRALS</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {report.specialist_referrals.map((s, i) => {
                  const urgColor = s.urgency === 'urgent' ? 'var(--accent-rose)' : s.urgency === 'soon' ? '#f97316' : 'var(--accent-teal)'
                  return (
                    <div key={i} style={{
                      padding: '6px 10px', borderRadius: 8,
                      background: 'var(--bg-raised)', border: '1px solid var(--border)',
                      fontSize: 11
                    }}>
                      <span style={{ color: 'var(--text-bright)', fontWeight: 600 }}>{s.specialty}</span>
                      <span style={{ color: urgColor, marginLeft: 6, fontSize: 10 }}>({s.urgency})</span>
                      {s.reason && <div style={{ color: 'var(--text-muted)', fontSize: 10, marginTop: 2 }}>{s.reason}</div>}
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Differential tab */}
      {tab === 'differential' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {(report.differential_diagnosis || []).map((dx, i) => (
            <div key={i} style={{
              padding: '14px 16px', borderRadius: 10,
              background: 'var(--bg-raised)', border: '1px solid var(--border)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <span style={{
                  width: 22, height: 22, borderRadius: '50%', background: 'var(--bg-card)',
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 11, fontWeight: 700, color: 'var(--accent-glow)', flexShrink: 0
                }}>
                  {dx.rank}
                </span>
                <span style={{ fontWeight: 700, color: 'var(--text-bright)', fontSize: 14 }}>{dx.disease}</span>
                <ConfidenceDots level={dx.confidence} />
                <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{dx.confidence}</span>
                {dx.omim && <span className="badge badge-info" style={{ fontSize: 9 }}>OMIM:{dx.omim}</span>}
              </div>
              {dx.inheritance && (
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6, fontFamily: 'var(--font-mono)' }}>
                  Inheritance: {dx.inheritance}
                </div>
              )}
              {dx.supporting_evidence?.length > 0 && (
                <div style={{ marginBottom: 4 }}>
                  {dx.supporting_evidence.map((e, j) => (
                    <div key={j} style={{ display: 'flex', gap: 6, marginBottom: 2 }}>
                      <span style={{ color: 'var(--success)', fontSize: 11 }}>✓</span>
                      <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{e}</span>
                    </div>
                  ))}
                </div>
              )}
              {dx.against_evidence?.length > 0 && dx.against_evidence[0] && (
                <div>
                  {dx.against_evidence.map((e, j) => (
                    <div key={j} style={{ display: 'flex', gap: 6, marginBottom: 2 }}>
                      <span style={{ color: 'var(--accent-rose)', fontSize: 11 }}>✗</span>
                      <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{e}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {(!report.differential_diagnosis || report.differential_diagnosis.length === 0) && (
            <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>No differential diagnosis generated.</div>
          )}
        </div>
      )}

      {/* Workup tab */}
      {tab === 'workup' && report.recommended_workup && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {[
            { key: 'immediate', label: '🚨 Immediate Actions', color: 'var(--accent-rose)' },
            { key: 'short_term', label: '📅 Short-term (1–3 months)', color: '#f97316' },
            { key: 'genetic_tests', label: '🧬 Genetic Testing', color: 'var(--accent-teal)' },
          ].map(({ key, label, color }) => (
            report.recommended_workup[key]?.length > 0 && (
              <div key={key}>
                <div style={{ fontSize: 12, fontWeight: 600, color, marginBottom: 6 }}>{label}</div>
                {report.recommended_workup[key].map((item, i) => (
                  <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
                    <ArrowRight size={12} color={color} style={{ marginTop: 2, flexShrink: 0 }} />
                    <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{item}</span>
                  </div>
                ))}
              </div>
            )
          ))}
        </div>
      )}

      {/* Management tab */}
      {tab === 'management' && report.management_plan && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {[
            { key: 'treatment_options', label: '💊 Treatment Options' },
            { key: 'monitoring', label: '📊 Monitoring' },
            { key: 'patient_education', label: '📚 Patient Education' },
          ].map(({ key, label }) => (
            report.management_plan[key]?.length > 0 && (
              <div key={key}>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-bright)', marginBottom: 6 }}>{label}</div>
                {report.management_plan[key].map((item, i) => (
                  <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
                    <ChevronRight size={12} color="var(--accent-primary)" style={{ marginTop: 2, flexShrink: 0 }} />
                    <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{item}</span>
                  </div>
                ))}
              </div>
            )
          ))}
        </div>
      )}

      {/* Family tab */}
      {tab === 'family' && report.family_implications && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {[
            { key: 'inheritance_risk', label: 'Inheritance Risk' },
            { key: 'cascade_testing', label: 'Cascade Testing' },
            { key: 'genetic_counseling', label: 'Genetic Counseling' },
          ].map(({ key, label }) => (
            report.family_implications[key] && (
              <div key={key} style={{
                padding: '12px 14px', borderRadius: 8,
                background: 'var(--bg-raised)', border: '1px solid var(--border)'
              }}>
                <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 4 }}>{label.toUpperCase()}</div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{report.family_implications[key]}</div>
              </div>
            )
          ))}
        </div>
      )}
    </div>
  )
}

// ── Main AgentPage ───────────────────────────────────────────────
export default function AgentPage() {
  const [mode, setMode] = useState('report') // 'report' | 'symptoms' | 'combined'
  const [file, setFile] = useState(null)
  const [fileB64, setFileB64] = useState('')
  const [fileType, setFileType] = useState('')
  const [symptoms, setSymptoms] = useState([''])
  const [patientAge, setPatientAge] = useState('')
  const [patientSex, setPatientSex] = useState('')
  const [familyHistory, setFamilyHistory] = useState('')
  const [running, setRunning] = useState(false)
  const [trace, setTrace] = useState([])
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)
  const [latency, setLatency] = useState(null)
  const fileRef = useRef()

  const handleFile = (f) => {
    if (!f) return
    setFile(f)
    setFileType(f.type || 'image/jpeg')
    const reader = new FileReader()
    reader.onload = (e) => {
      const b64 = e.target.result.split(',')[1]
      setFileB64(b64)
    }
    reader.readAsDataURL(f)
  }

  const addSymptom = () => setSymptoms(s => [...s, ''])
  const updateSymptom = (i, v) => setSymptoms(s => { const n = [...s]; n[i] = v; return n })
  const removeSymptom = (i) => setSymptoms(s => s.filter((_, j) => j !== i))

  const runAgent = async () => {
    setError(null)
    setTrace([])
    setReport(null)
    setRunning(true)

    const body = {
      symptoms: symptoms.filter(s => s.trim()),
      patient: {
        age: patientAge || undefined,
        sex: patientSex || undefined,
        family_history: familyHistory || undefined,
      }
    }

    if ((mode === 'report' || mode === 'combined') && fileB64) {
      body.file_data = fileB64
      body.file_type = fileType
    }

    // Simulate streaming trace by polling or just show steps as they arrive
    try {
      const result = await postJson('/agent/run', body)
      setTrace(result.trace || [])
      setReport(result.report || null)
      setLatency(result.total_latency)
    } catch (e) {
      setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  const canRun = (mode === 'symptoms' && symptoms.some(s => s.trim())) ||
                 (mode === 'report' && fileB64) ||
                 (mode === 'combined' && (fileB64 || symptoms.some(s => s.trim())))

  const exampleSymptoms = [
    ['joint hypermobility', 'skin hyperextensibility', 'chronic pain', 'easy bruising'],
    ['recurrent lung infections', 'chronic cough', 'failure to thrive'],
    ['neuropathic pain', 'cardiomyopathy', 'renal failure', 'angiokeratoma'],
  ]

  return (
    <div className="container" style={{ padding: '40px 24px', maxWidth: 960 }}>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-rose)', letterSpacing: '0.1em', marginBottom: 8 }}>
          AUTONOMOUS DIAGNOSTIC AGENT
        </div>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: 'var(--text-bright)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 12 }}>
          <Bot size={30} color="var(--accent-primary)" />
          RareNav Agent
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14, maxWidth: 600, lineHeight: 1.6 }}>
          Upload a genetic report and/or describe symptoms. The Agent autonomously queries ClinVar,
          maps HPO phenotypes, and synthesizes a structured clinical diagnosis — step by step.
        </p>
      </div>

      {/* Pipeline diagram */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 6, marginBottom: 28,
        padding: '12px 16px', borderRadius: 10, background: 'var(--bg-raised)',
        border: '1px solid var(--border)', flexWrap: 'wrap'
      }}>
        {[
          { icon: Upload, label: 'Report / Symptoms', color: 'var(--accent-glow)' },
          { icon: ChevronRight, label: null, color: 'var(--border)' },
          { icon: Search, label: 'ClinVar Lookup', color: 'var(--accent-primary)' },
          { icon: ChevronRight, label: null, color: 'var(--border)' },
          { icon: Activity, label: 'HPO Mapping', color: '#a78bfa' },
          { icon: ChevronRight, label: null, color: 'var(--border)' },
          { icon: Brain, label: 'AI Reasoning', color: '#f59e0b' },
          { icon: ChevronRight, label: null, color: 'var(--border)' },
          { icon: ClipboardList, label: 'Diagnosis Report', color: 'var(--success)' },
        ].map(({ icon: Icon, label, color }, i) => (
          label ? (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Icon size={13} color={color} />
              <span style={{ fontSize: 11, color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>{label}</span>
            </div>
          ) : (
            <Icon key={i} size={14} color={color} />
          )
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Left: Inputs */}
        <div>
          {/* Mode selector */}
          <div style={{ display: 'flex', gap: 6, marginBottom: 16 }}>
            {[
              { id: 'report', label: '📄 Report', desc: 'Upload genetic report' },
              { id: 'symptoms', label: '🩺 Symptoms', desc: 'Describe symptoms' },
              { id: 'combined', label: '⚡ Both', desc: 'Full pipeline' },
            ].map(m => (
              <button key={m.id}
                onClick={() => setMode(m.id)}
                className={`btn btn-sm ${mode === m.id ? 'btn-primary' : 'btn-ghost'}`}
                style={{ fontSize: 11 }}
              >
                {m.label}
              </button>
            ))}
          </div>

          {/* File upload */}
          {(mode === 'report' || mode === 'combined') && (
            <div className="card" style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 10 }}>
                GENETIC REPORT (PDF / IMAGE)
              </div>
              <div
                onClick={() => fileRef.current?.click()}
                onDragOver={e => e.preventDefault()}
                onDrop={e => { e.preventDefault(); handleFile(e.dataTransfer.files[0]) }}
                style={{
                  border: `2px dashed ${file ? 'var(--accent-teal)' : 'var(--border)'}`,
                  borderRadius: 10, padding: '20px 16px', textAlign: 'center',
                  cursor: 'pointer', background: file ? 'rgba(45,212,191,0.05)' : 'var(--bg-raised)',
                  transition: 'all 0.2s'
                }}
              >
                {file ? (
                  <div>
                    <CheckCircle size={20} color="var(--accent-teal)" style={{ margin: '0 auto 8px' }} />
                    <div style={{ fontSize: 13, color: 'var(--text-bright)', fontWeight: 600 }}>{file.name}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                      {(file.size / 1024).toFixed(1)} KB
                    </div>
                    <button
                      onClick={e => { e.stopPropagation(); setFile(null); setFileB64('') }}
                      style={{ marginTop: 8, fontSize: 11, color: 'var(--accent-rose)', background: 'none', border: 'none', cursor: 'pointer' }}
                    >
                      Remove
                    </button>
                  </div>
                ) : (
                  <div>
                    <Upload size={20} color="var(--text-muted)" style={{ margin: '0 auto 8px' }} />
                    <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Drop PDF or image here</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>or click to browse</div>
                  </div>
                )}
              </div>
              <input
                ref={fileRef} type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                style={{ display: 'none' }}
                onChange={e => handleFile(e.target.files[0])}
              />
            </div>
          )}

          {/* Symptoms */}
          {(mode === 'symptoms' || mode === 'combined') && (
            <div className="card" style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 10 }}>
                SYMPTOMS
              </div>
              {symptoms.map((s, i) => (
                <div key={i} style={{ display: 'flex', gap: 6, marginBottom: 6 }}>
                  <input
                    className="input"
                    value={s}
                    onChange={e => updateSymptom(i, e.target.value)}
                    placeholder={`Symptom ${i + 1} (e.g. joint hypermobility)`}
                    style={{ fontSize: 12 }}
                  />
                  {symptoms.length > 1 && (
                    <button className="btn btn-ghost btn-sm btn-icon" onClick={() => removeSymptom(i)}>
                      <X size={12} />
                    </button>
                  )}
                </div>
              ))}
              <button className="btn btn-ghost btn-sm" onClick={addSymptom} style={{ fontSize: 11 }}>
                <Plus size={12} /> Add symptom
              </button>

              {/* Example sets */}
              <div style={{ marginTop: 10 }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 6 }}>QUICK EXAMPLES:</div>
                {exampleSymptoms.map((ex, i) => (
                  <button key={i} onClick={() => setSymptoms(ex)}
                    style={{
                      fontSize: 10, marginRight: 6, marginBottom: 4,
                      padding: '3px 8px', borderRadius: 99,
                      background: 'var(--bg-raised)', border: '1px solid var(--border)',
                      color: 'var(--text-secondary)', cursor: 'pointer'
                    }}>
                    {ex[0]}…
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Patient info */}
          <div className="card" style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 10 }}>
              PATIENT INFO (OPTIONAL)
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              <input className="input" value={patientAge} onChange={e => setPatientAge(e.target.value)}
                placeholder="Age" style={{ fontSize: 12 }} />
              <select className="input" value={patientSex} onChange={e => setPatientSex(e.target.value)}
                style={{ fontSize: 12 }}>
                <option value="">Sex</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <input className="input" value={familyHistory} onChange={e => setFamilyHistory(e.target.value)}
              placeholder="Family history (e.g. father has Marfan syndrome)"
              style={{ fontSize: 12, marginTop: 8 }} />
          </div>

          <button
            className="btn btn-primary"
            onClick={runAgent}
            disabled={!canRun || running}
            style={{ width: '100%', justifyContent: 'center' }}
          >
            {running
              ? <><div className="spinner" />Agent Running…</>
              : <><Zap size={15} />Run Diagnostic Agent</>}
          </button>

          {error && (
            <div style={{
              marginTop: 12, padding: '12px 14px', borderRadius: 8,
              background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)',
              color: 'var(--accent-rose)', fontSize: 12
            }}>
              {error}
            </div>
          )}
        </div>

        {/* Right: Agent trace + report */}
        <div>
          {/* Trace */}
          {(trace.length > 0 || running) && (
            <div className="card" style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
                <div style={{
                  width: 28, height: 28, borderRadius: 8,
                  background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-teal))',
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  <Bot size={14} color="white" />
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-bright)' }}>Agent Reasoning</div>
                  {latency && <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{latency}s total</div>}
                </div>
                {running && <div className="spinner" style={{ marginLeft: 'auto' }} />}
              </div>

              {trace.map((entry, i) => (
                <TraceStep key={i} entry={entry} index={i} total={trace.length} />
              ))}

              {running && trace.length === 0 && (
                <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>Initializing agent…</div>
              )}
            </div>
          )}

          {/* Diagnostic report */}
          {report && (
            <div className="card" style={{
              border: '1px solid rgba(45,212,191,0.3)',
              background: 'linear-gradient(135deg, rgba(45,212,191,0.04), rgba(59,130,246,0.03))'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                <div style={{
                  width: 32, height: 32, borderRadius: 8,
                  background: 'linear-gradient(135deg, var(--accent-teal), var(--accent-primary))',
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  <ClipboardList size={15} color="white" />
                </div>
                <div>
                  <div style={{ fontWeight: 700, color: 'var(--text-bright)', fontSize: 14 }}>Diagnostic Report</div>
                  <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)' }}>
                    Generated by RareNav Agent
                    {report.engine && ` • ${report.engine}`}
                  </div>
                </div>
                {report.urgency && (
                  <div style={{ marginLeft: 'auto' }}>
                    <UrgencyBadge urgency={report.urgency} />
                  </div>
                )}
              </div>
              <DiagnosticReport report={report} />

              <div style={{
                marginTop: 14, padding: '8px 12px', borderRadius: 8,
                background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)',
                fontSize: 11, color: 'var(--accent-amber)', display: 'flex', gap: 6, alignItems: 'flex-start'
              }}>
                <Info size={12} style={{ flexShrink: 0, marginTop: 1 }} />
                AI-generated for educational purposes. All findings require review by a qualified clinician.
              </div>
            </div>
          )}

          {/* Empty state */}
          {!report && !running && trace.length === 0 && (
            <div style={{
              padding: '40px 24px', textAlign: 'center',
              border: '2px dashed var(--border)', borderRadius: 12, color: 'var(--text-muted)'
            }}>
              <Bot size={32} color="var(--border)" style={{ margin: '0 auto 12px' }} />
              <div style={{ fontSize: 13 }}>Agent output will appear here</div>
              <div style={{ fontSize: 11, marginTop: 4 }}>Configure inputs on the left and click Run</div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
