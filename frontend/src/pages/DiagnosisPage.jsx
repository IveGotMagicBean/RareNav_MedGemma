import { useState } from 'react'
import { Search, Dna, Activity, FileText, ChevronRight, Zap, AlertCircle, BarChart2 } from 'lucide-react'
import { api } from '../utils/api.js'
import { getSignificanceBadge, getSignificanceLabel, getMatchColor, parseMarkdown, GENE_EXAMPLES } from '../utils/helpers.js'

function MatchScoreBar({ score, label }) {
  const pct = Math.round(score * 100)
  const color = getMatchColor(score)
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
        <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
        <span style={{ fontFamily: 'var(--font-mono)', color, fontWeight: 600 }}>{pct}%</span>
      </div>
      <div className="confidence-bar">
        <div className="confidence-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  )
}

function DiseaseCard({ disease, rank }) {
  const [expanded, setExpanded] = useState(false)
  const urgencyColor = {
    critical: 'var(--accent-rose)',
    high: '#fb923c',
    medium: 'var(--accent-amber)',
    low: 'var(--success)'
  }[disease.urgency] || 'var(--text-muted)'

  return (
    <div className="card" style={{ marginBottom: 12, padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '16px 20px', display: 'flex', gap: 16, alignItems: 'flex-start', cursor: 'pointer' }} onClick={() => setExpanded(!expanded)}>
        {/* Rank */}
        <div style={{
          width: 40, height: 40, borderRadius: 8, flexShrink: 0,
          background: rank === 1 ? 'linear-gradient(135deg, var(--accent-rose), var(--accent-amber))' :
                      rank === 2 ? 'rgba(59,130,246,0.15)' : 'var(--bg-raised)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 16,
          color: rank <= 2 ? 'white' : 'var(--text-muted)'
        }}>{rank}</div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
            <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 15, color: 'var(--text-bright)' }}>
              {disease.name}
            </span>
            <span className="badge badge-info">{disease.inheritance}</span>
            {disease.urgency && (
              <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: urgencyColor, background: `${urgencyColor}18`, border: `1px solid ${urgencyColor}40`, padding: '2px 8px', borderRadius: 99, letterSpacing: '0.04em' }}>
                {disease.urgency.toUpperCase()}
              </span>
            )}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            Gene: {disease.gene} • {disease.id} • Prevalence: {disease.prevalence}
          </div>
          {disease.match_score !== undefined && (
            <div style={{ marginTop: 8 }}>
              <MatchScoreBar score={disease.match_score} label="Symptom Match" />
            </div>
          )}
        </div>
        <ChevronRight size={16} color="var(--text-muted)" style={{ transform: expanded ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s', flexShrink: 0 }} />
      </div>

      {expanded && (
        <div style={{ borderTop: '1px solid var(--border)', padding: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 16 }}>
            <div>
              <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 6 }}>KEY SYMPTOMS</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {disease.key_symptoms?.map((s, i) => <span key={i} className="chip" style={{ fontSize: 11 }}>{s}</span>)}
              </div>
            </div>
            <div>
              <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 6 }}>SPECIALISTS</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {disease.specialists?.map((s, i) => (
                  <span key={i} className="chip" style={{ fontSize: 11, background: 'rgba(59,130,246,0.08)', borderColor: 'rgba(59,130,246,0.2)', color: 'var(--accent-glow)' }}>{s}</span>
                ))}
              </div>
            </div>
          </div>
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 6 }}>DIAGNOSIS</div>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{disease.diagnosis}</p>
          </div>
          <div>
            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 6 }}>TREATMENTS</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {disease.treatments?.map((t, i) => (
                <span key={i} className="chip" style={{ fontSize: 11, background: 'rgba(52,211,153,0.08)', borderColor: 'rgba(52,211,153,0.2)', color: 'var(--success)' }}>{t}</span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function DiagnosisPage() {
  const [mode, setMode] = useState('symptom') // symptom | variant | combined
  const [symptoms, setSymptoms] = useState([])
  const [symptomInput, setSymptomInput] = useState('')
  const [gene, setGene] = useState('')
  const [variant, setVariant] = useState('')
  const [age, setAge] = useState('')
  const [sex, setSex] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const addSymptom = () => {
    const s = symptomInput.trim()
    if (s && !symptoms.includes(s)) setSymptoms(prev => [...prev, s])
    setSymptomInput('')
  }

  const run = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      let res
      if (mode === 'symptom') {
        if (symptoms.length === 0) { setError('Add at least one symptom'); setLoading(false); return }
        res = await api.diagnosis.symptomBased({ symptoms, age, sex })
        setResult({ type: 'symptom', data: res })
      } else {
        if (!gene) { setError('Gene required'); setLoading(false); return }
        res = await api.diagnosis.variantBased({ gene, variant })
        setResult({ type: 'variant', data: res })
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ padding: '40px 24px', maxWidth: 1000 }}>
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-amber)', letterSpacing: '0.1em', marginBottom: 8 }}>
          INTEGRATED DIAGNOSIS ENGINE
        </div>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: 'var(--text-bright)', marginBottom: 8 }}>
          Diagnostic Reasoning
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          Dual-channel AI: combine symptom phenotype and genetic variant evidence for ranked differential diagnosis
        </p>
      </div>

      {/* Mode selection */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {[
          { id: 'symptom', label: 'Symptom-Based', icon: Activity, color: 'var(--accent-teal)' },
          { id: 'variant', label: 'Variant-Based', icon: Dna, color: 'var(--accent-rose)' },
        ].map(({ id, label, icon: Icon, color }) => (
          <button
            key={id}
            className={`btn ${mode === id ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => { setMode(id); setResult(null) }}
            style={mode === id ? {} : {}}
          >
            <Icon size={15} />{label}
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24, alignItems: 'start' }}>
        {/* Input panel */}
        <div className="card">
          {mode === 'symptom' && (
            <div>
              <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 10 }}>
                CLINICAL SYMPTOMS
              </div>
              <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                <input
                  className="input" value={symptomInput}
                  onChange={e => setSymptomInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && addSymptom()}
                  placeholder="Type symptom and press Enter..."
                  style={{ flex: 1 }}
                />
                <button className="btn btn-ghost btn-sm" onClick={addSymptom}>Add</button>
              </div>

              {/* Quick adds */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 14 }}>
                {['splenomegaly', 'joint hypermobility', 'cardiomyopathy', 'seizures', 'ataxia', 'lens dislocation', 'tall stature'].map(s => (
                  <button key={s} className="chip chip-clickable" style={{ fontSize: 11 }}
                    onClick={() => !symptoms.includes(s) && setSymptoms(prev => [...prev, s])}>+ {s}</button>
                ))}
              </div>

              {symptoms.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, padding: 12, borderRadius: 8, background: 'var(--bg-raised)', border: '1px solid var(--border)', marginBottom: 12 }}>
                  {symptoms.map(s => (
                    <span key={s} style={{
                      display: 'inline-flex', alignItems: 'center', gap: 5, padding: '5px 10px',
                      borderRadius: 99, background: 'rgba(45,212,191,0.1)', border: '1px solid rgba(45,212,191,0.25)',
                      fontSize: 12, color: 'var(--accent-teal)'
                    }}>
                      {s}
                      <button onClick={() => setSymptoms(prev => prev.filter(x => x !== s))} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', padding: 0, lineHeight: 1 }}>
                        <Search size={10} style={{ transform: 'rotate(45deg)' }} />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {mode === 'variant' && (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 14, marginBottom: 14 }}>
                <div>
                  <label style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', display: 'block', marginBottom: 8, letterSpacing: '0.06em' }}>GENE</label>
                  <input className="input input-mono" value={gene} onChange={e => setGene(e.target.value.toUpperCase())} placeholder="HFE, CFTR..." />
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 6 }}>
                    {['HFE', 'CFTR', 'FBN1', 'GBA', 'TSC1'].map(g => (
                      <button key={g} className="chip chip-clickable" style={{ fontSize: 10 }} onClick={() => setGene(g)}>{g}</button>
                    ))}
                  </div>
                </div>
                <div>
                  <label style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', display: 'block', marginBottom: 8, letterSpacing: '0.06em' }}>VARIANT (OPTIONAL)</label>
                  <input className="input input-mono" value={variant} onChange={e => setVariant(e.target.value)} placeholder="C282Y, F508del..." />
                </div>
              </div>
            </div>
          )}

          {/* Patient info */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 8, marginBottom: 16, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
            <div>
              <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Age</label>
              <input className="input" value={age} onChange={e => setAge(e.target.value)} placeholder="e.g., 35" style={{ fontSize: 13 }} />
            </div>
            <div>
              <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Sex</label>
              <div style={{ display: 'flex', gap: 6 }}>
                {['M', 'F'].map(s => (
                  <button key={s} className={`btn btn-sm ${sex === s ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setSex(sex === s ? '' : s)} style={{ flex: 1 }}>{s === 'M' ? 'Male' : 'Female'}</button>
                ))}
              </div>
            </div>
          </div>

          <button className="btn btn-primary w-full" onClick={run} disabled={loading}>
            {loading ? <><div className="spinner" />Running Diagnostic Reasoning...</> : <><Zap size={15} />Run AI Diagnosis</>}
          </button>
        </div>

        {/* Info sidebar */}
        <div>
          <div className="card" style={{ background: 'rgba(245,158,11,0.05)', border: '1px solid rgba(245,158,11,0.15)' }}>
            <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
              <AlertCircle size={16} color="var(--accent-amber)" style={{ flexShrink: 0, marginTop: 1 }} />
              <div style={{ fontSize: 12, fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--accent-amber)' }}>Clinical Note</div>
            </div>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              This system provides AI-assisted differential diagnosis for educational and research purposes. 
              Clinical decisions must involve qualified medical professionals.
            </p>
          </div>

          <div className="card" style={{ marginTop: 12 }}>
            <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 10 }}>HOW IT WORKS</div>
            {['Symptoms mapped to HPO phenotype terms', 'Scored against disease symptom profiles', 'MedGemma generates clinical analysis', 'Ranked differential with evidence basis'].map((s, i) => (
              <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 8, fontSize: 12, color: 'var(--text-secondary)' }}>
                <span style={{ color: 'var(--accent-primary)', fontFamily: 'var(--font-mono)', fontSize: 11, fontWeight: 600, flexShrink: 0 }}>0{i + 1}</span>
                {s}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={{ marginTop: 20, padding: '14px 16px', borderRadius: 8, background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', color: 'var(--accent-rose)', fontSize: 13 }}>
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div style={{ marginTop: 32 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'start' }}>
            {/* Ranked diseases */}
            <div>
              <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16, color: 'var(--text-bright)', display: 'flex', alignItems: 'center', gap: 8 }}>
                <BarChart2 size={18} color="var(--accent-amber)" />
                {result.type === 'symptom' ? 'Differential Diagnosis' : 'Associated Diseases'}
              </h2>
              {(result.data.ranked_diseases || result.data.related_diseases || []).map((d, i) => (
                <DiseaseCard key={d.id || i} disease={d} rank={i + 1} />
              ))}
              {(result.data.ranked_diseases || result.data.related_diseases || []).length === 0 && (
                <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                  No matching diseases found in curated database.
                </div>
              )}
            </div>

            {/* AI Analysis */}
            <div>
              <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16, color: 'var(--text-bright)', display: 'flex', alignItems: 'center', gap: 8 }}>
                <Zap size={18} color="var(--accent-primary)" />
                MedGemma Analysis
              </h2>
              <div className="card" style={{ border: '1px solid rgba(59,130,246,0.2)', background: 'rgba(59,130,246,0.03)' }}>
                {result.data.demo_mode && (
                  <div style={{ marginBottom: 12, fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-amber)', background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 6, padding: '6px 10px' }}>
                    DEMO MODE — Connect MedGemma model for full AI analysis
                  </div>
                )}
                <div
                  className="prose"
                  style={{ fontSize: 13, lineHeight: 1.8 }}
                  dangerouslySetInnerHTML={{
                    __html: parseMarkdown(
                      result.data.ai_analysis || result.data.ai_explanation || 'Analysis not available.'
                    )
                  }}
                />
              </div>

              {/* Variant records (variant mode) */}
              {result.type === 'variant' && result.data.variant_records?.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 10 }}>
                    CLINVAR VARIANTS ({result.data.variant_records.length})
                  </div>
                  {result.data.variant_records.slice(0, 3).map((v, i) => (
                    <div key={i} className="card" style={{ marginBottom: 8, padding: '12px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <span className={`badge ${getSignificanceBadge(v.significance)}`}>{getSignificanceLabel(v.significance)}</span>
                        <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{v.submitters} submitters</span>
                      </div>
                      <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                        {v.name?.slice(0, 80)}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
