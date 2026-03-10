import { useState, useEffect, useCallback } from 'react'
import { Plus, X, Search, Activity, ChevronRight, Info } from 'lucide-react'
import { api } from '../utils/api.js'
import { SYMPTOM_EXAMPLES, parseMarkdown, debounce } from '../utils/helpers.js'

function SymptomTag({ symptom, hpoId, onRemove }) {
  return (
    <div style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '6px 12px', borderRadius: 99,
      background: 'rgba(45,212,191,0.1)', border: '1px solid rgba(45,212,191,0.25)',
      fontSize: 13, color: 'var(--accent-teal)', fontWeight: 500,
      animation: 'fadeIn 0.2s ease'
    }}>
      {symptom}
      {hpoId && <span style={{ fontSize: 9, fontFamily: 'var(--font-mono)', opacity: 0.6 }}>{hpoId}</span>}
      <button onClick={onRemove} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', padding: 0, display: 'flex', lineHeight: 1 }}>
        <X size={12} />
      </button>
    </div>
  )
}

function HPOSuggestion({ term, onClick }) {
  return (
    <button
      onClick={() => onClick(term)}
      style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        width: '100%', padding: '10px 14px', background: 'transparent',
        border: 'none', borderBottom: '1px solid var(--border)', cursor: 'pointer',
        textAlign: 'left', transition: 'background 0.1s',
        color: 'var(--text-primary)'
      }}
      onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-raised)'}
      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
    >
      <div>
        <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-bright)' }}>{term.name}</div>
        <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)', marginTop: 2 }}>
          {term.id} • {term.category || 'General'}
        </div>
      </div>
      <ChevronRight size={14} color="var(--text-muted)" />
    </button>
  )
}

function AnalysisResult({ result, symptoms }) {
  const [activeTab, setActiveTab] = useState('ai')
  const hpoMapping = result.hpo_mapping || []

  return (
    <div className="card" style={{ marginTop: 24, border: '1px solid rgba(45,212,191,0.25)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 8,
          background: 'linear-gradient(135deg, rgba(45,212,191,0.2), rgba(59,130,246,0.1))',
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <Activity size={18} color="var(--accent-teal)" />
        </div>
        <div>
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--text-bright)' }}>
            Symptom Analysis
          </div>
          <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)' }}>
            {symptoms.length} symptoms • MedGemma {result.demo_mode ? '(Demo)' : `${result.ai_latency?.toFixed(1)}s`}
          </div>
        </div>
      </div>

      {/* HPO Mapping */}
      {hpoMapping.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 8 }}>
            HPO TERM MAPPING
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {hpoMapping.map((m, i) => (
              <div key={i} style={{
                padding: '4px 10px', borderRadius: 99,
                background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.2)',
                fontSize: 12
              }}>
                <span style={{ color: 'var(--text-secondary)' }}>{m.symptom}</span>
                <span style={{ color: 'var(--text-muted)', margin: '0 4px' }}>→</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-glow)', fontSize: 10 }}>
                  {m.hpo_id}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Analysis */}
      <div
        className="prose"
        style={{ fontSize: 14, lineHeight: 1.8 }}
        dangerouslySetInnerHTML={{ __html: parseMarkdown(result.analysis) }}
      />

      <div style={{
        marginTop: 16, padding: '10px 14px', borderRadius: 8,
        background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)',
        fontSize: 12, color: 'var(--accent-amber)',
        display: 'flex', alignItems: 'flex-start', gap: 8
      }}>
        <Info size={13} style={{ flexShrink: 0, marginTop: 1 }} />
        Symptom analysis is AI-generated for educational purposes. Rare disease diagnosis requires specialist evaluation.
      </div>
    </div>
  )
}

export default function SymptomsPage() {
  const [searchText, setSearchText] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedSymptoms, setSelectedSymptoms] = useState([])
  const [hpoMap, setHpoMap] = useState({}) // symptom -> {id, name}
  const [age, setAge] = useState('')
  const [sex, setSex] = useState('')
  const [familyHistory, setFamilyHistory] = useState('')
  const [analysisResult, setAnalysisResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchSuggestions = useCallback(debounce(async (q) => {
    if (q.length < 2) { setSuggestions([]); return }
    try {
      const res = await api.symptoms.search(q, 8)
      setSuggestions(res.results || [])
      setShowSuggestions(true)
    } catch {}
  }, 300), [])

  useEffect(() => {
    fetchSuggestions(searchText)
  }, [searchText])

  const addSymptom = (term) => {
    if (!selectedSymptoms.includes(term.name)) {
      setSelectedSymptoms(prev => [...prev, term.name])
      setHpoMap(prev => ({ ...prev, [term.name]: term.id }))
    }
    setSearchText('')
    setSuggestions([])
    setShowSuggestions(false)
  }

  const addFreeText = () => {
    const text = searchText.trim()
    if (!text || selectedSymptoms.includes(text)) return
    setSelectedSymptoms(prev => [...prev, text])
    setSearchText('')
    setSuggestions([])
    setShowSuggestions(false)
  }

  const removeSymptom = (sym) => {
    setSelectedSymptoms(prev => prev.filter(s => s !== sym))
  }

  const analyze = async () => {
    if (selectedSymptoms.length === 0) return
    setLoading(true)
    setError(null)
    setAnalysisResult(null)
    try {
      const res = await api.symptoms.analyze({
        symptoms: selectedSymptoms,
        age, sex, family_history: familyHistory
      })
      setAnalysisResult(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ padding: '40px 24px', maxWidth: 900 }}>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)', letterSpacing: '0.1em', marginBottom: 8 }}>
          PHENOTYPE NAVIGATOR
        </div>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: 'var(--text-bright)', marginBottom: 8 }}>
          Symptom Analysis
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          Map clinical symptoms to HPO ontology terms and get AI-powered rare disease differential analysis
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 24, alignItems: 'start' }}>
        {/* Main panel */}
        <div>
          <div className="card" style={{ marginBottom: 20 }}>
            {/* Symptom search */}
            <div style={{ marginBottom: 20 }}>
              <label style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', display: 'block', marginBottom: 8, letterSpacing: '0.06em' }}>
                SEARCH SYMPTOMS (HPO TERMS)
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  className="input"
                  value={searchText}
                  onChange={e => setSearchText(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') suggestions.length > 0 ? addSymptom(suggestions[0]) : addFreeText()
                    if (e.key === 'Escape') setShowSuggestions(false)
                  }}
                  onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                  placeholder="Type a symptom (e.g., ataxia, seizures, cardiomyopathy)..."
                  style={{ paddingLeft: 40 }}
                />
                <Search size={15} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />

                {/* Autocomplete dropdown */}
                {showSuggestions && suggestions.length > 0 && (
                  <div style={{
                    position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 20,
                    background: 'var(--bg-surface)', border: '1px solid var(--border-bright)',
                    borderRadius: var(--radius-sm), borderTop: 'none',
                    boxShadow: 'var(--shadow-card)', overflow: 'hidden'
                  }}>
                    {suggestions.map((term, i) => (
                      <HPOSuggestion key={term.id || i} term={term} onClick={addSymptom} />
                    ))}
                    {searchText && (
                      <button
                        onClick={addFreeText}
                        style={{
                          width: '100%', padding: '10px 14px', background: 'rgba(59,130,246,0.05)',
                          border: 'none', cursor: 'pointer', textAlign: 'left', fontSize: 12,
                          color: 'var(--accent-glow)', fontFamily: 'var(--font-display)', fontWeight: 600
                        }}
                      >
                        + Add "{searchText}" as custom symptom
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Quick examples */}
              <div style={{ marginTop: 10 }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 6, fontFamily: 'var(--font-mono)' }}>QUICK ADD:</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                  {SYMPTOM_EXAMPLES.slice(0, 8).map(s => (
                    <button key={s} className="chip chip-clickable" style={{ fontSize: 11 }}
                      onClick={() => { setSelectedSymptoms(prev => prev.includes(s) ? prev : [...prev, s]) }}>
                      <Plus size={10} />{s}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Selected symptoms */}
            {selectedSymptoms.length > 0 && (
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 8 }}>
                  SELECTED SYMPTOMS ({selectedSymptoms.length})
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, padding: '12px', borderRadius: 8, background: 'var(--bg-raised)', border: '1px solid var(--border)', minHeight: 48 }}>
                  {selectedSymptoms.map(s => (
                    <SymptomTag
                      key={s} symptom={s}
                      hpoId={hpoMap[s]}
                      onRemove={() => removeSymptom(s)}
                    />
                  ))}
                </div>
              </div>
            )}

            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-primary" onClick={analyze} disabled={loading || selectedSymptoms.length === 0}>
                {loading ? <><div className="spinner" />Analyzing with MedGemma...</> : <><Activity size={15} />Analyze Phenotype</>}
              </button>
              {selectedSymptoms.length > 0 && (
                <button className="btn btn-ghost btn-sm" onClick={() => { setSelectedSymptoms([]); setAnalysisResult(null) }}>
                  Clear All
                </button>
              )}
            </div>
          </div>

          {error && (
            <div style={{ padding: '14px 16px', borderRadius: 8, background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', color: 'var(--accent-rose)', fontSize: 13, marginBottom: 16 }}>
              {error}
            </div>
          )}

          {analysisResult && (
            <AnalysisResult result={analysisResult} symptoms={selectedSymptoms} />
          )}
        </div>

        {/* Patient info sidebar */}
        <div>
          <div className="card">
            <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 16 }}>
              PATIENT CONTEXT
            </div>

            <div style={{ marginBottom: 14 }}>
              <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Age / Onset Age</label>
              <input className="input" value={age} onChange={e => setAge(e.target.value)} placeholder="e.g., 8 years, adult" style={{ fontSize: 13 }} />
            </div>

            <div style={{ marginBottom: 14 }}>
              <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Biological Sex</label>
              <div style={{ display: 'flex', gap: 6 }}>
                {['Male', 'Female', 'Other'].map(s => (
                  <button key={s} className={`btn btn-sm ${sex === s ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setSex(sex === s ? '' : s)} style={{ flex: 1, fontSize: 11 }}>
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: 14 }}>
              <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Family History</label>
              <textarea
                className="input"
                value={familyHistory}
                onChange={e => setFamilyHistory(e.target.value)}
                placeholder="e.g., Father with similar symptoms, consanguinity..."
                rows={3}
                style={{ fontSize: 13, resize: 'vertical' }}
              />
            </div>

            <div style={{ padding: '12px', borderRadius: 8, background: 'rgba(59,130,246,0.06)', border: '1px solid rgba(59,130,246,0.15)', fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              <strong style={{ color: 'var(--accent-glow)' }}>Tip:</strong> Add more clinical context to improve differential diagnosis accuracy.
            </div>
          </div>

          <div className="card" style={{ marginTop: 16 }}>
            <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 12 }}>
              ABOUT HPO
            </div>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Human Phenotype Ontology (HPO) provides a standardized vocabulary of phenotypic abnormalities. 
              Each symptom is mapped to an HPO term (HP:XXXXXXX) for precise clinical communication.
            </p>
            <a href="https://hpo.jax.org" target="_blank" rel="noopener noreferrer"
              style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 8, fontSize: 12, color: 'var(--accent-primary)', textDecoration: 'none' }}>
              Visit HPO Browser →
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
