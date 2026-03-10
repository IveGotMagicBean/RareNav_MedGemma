import { useState, useEffect } from 'react'
import { Search, BookOpen, ChevronRight, Dna, Heart, Brain, Microscope, Users } from 'lucide-react'
import { api } from '../utils/api.js'

const URGENCY_COLOR = { critical: 'var(--accent-rose)', high: '#fb923c', medium: 'var(--accent-amber)', low: 'var(--success)' }
const INHERIT_LABEL = {
  'Autosomal recessive': 'AR', 'Autosomal dominant': 'AD',
  'X-linked': 'XL', 'Mitochondrial': 'MT', 'Multiple patterns': 'Multi'
}

function DiseaseDetailPanel({ disease, onClose }) {
  return (
    <div style={{
      position: 'fixed', right: 0, top: 60, bottom: 0, width: 480,
      background: 'var(--bg-deep)', borderLeft: '1px solid var(--border)',
      overflowY: 'auto', zIndex: 40, padding: 28,
      animation: 'fadeIn 0.2s ease'
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 4 }}>
            {disease.id}
          </div>
          <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-bright)', lineHeight: 1.2 }}>
            {disease.name}
          </h2>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={onClose}>Close ✕</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 24 }}>
        {[
          { label: 'Gene(s)', val: disease.gene },
          { label: 'Inheritance', val: disease.inheritance },
          { label: 'Prevalence', val: disease.prevalence },
          { label: 'OMIM', val: disease.omim || 'N/A' },
        ].map(({ label, val }) => (
          <div key={label} style={{ padding: '12px', borderRadius: 8, background: 'var(--bg-surface)', border: '1px solid var(--border)' }}>
            <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: 13, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', fontWeight: 500 }}>{val}</div>
          </div>
        ))}
      </div>

      {[
        { title: 'KEY CLINICAL FEATURES', items: disease.key_symptoms, color: 'var(--accent-teal)' },
        { title: 'DIAGNOSTIC APPROACH', items: [disease.diagnosis], color: 'var(--accent-amber)' },
        { title: 'TREATMENT OPTIONS', items: disease.treatments, color: 'var(--success)' },
        { title: 'RECOMMENDED SPECIALISTS', items: disease.specialists, color: 'var(--accent-primary)' },
      ].map(({ title, items, color }) => (
        <div key={title} style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 8 }}>{title}</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {(items || []).map((item, i) => (
              <span key={i} className="chip" style={{ fontSize: 12, background: `${color}10`, borderColor: `${color}30`, color }}>{item}</span>
            ))}
          </div>
        </div>
      ))}

      {/* External links */}
      <div style={{ borderTop: '1px solid var(--border)', paddingTop: 16 }}>
        <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 10 }}>EXTERNAL RESOURCES</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {disease.omim && (
            <a href={`https://www.omim.org/entry/${disease.omim}`} target="_blank" rel="noopener noreferrer"
              className="btn btn-ghost btn-sm" style={{ justifyContent: 'flex-start' }}>
              OMIM #{disease.omim} →
            </a>
          )}
          {disease.id?.startsWith('ORPHA') && (
            <a href={`https://www.orpha.net/consor/cgi-bin/OC_Exp.php?Lng=EN&Expert=${disease.id.replace('ORPHA:', '')}`}
              target="_blank" rel="noopener noreferrer"
              className="btn btn-ghost btn-sm" style={{ justifyContent: 'flex-start' }}>
              Orphanet {disease.id} →
            </a>
          )}
          <a href={`https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(disease.name)}`}
            target="_blank" rel="noopener noreferrer"
            className="btn btn-ghost btn-sm" style={{ justifyContent: 'flex-start' }}>
            PubMed Literature →
          </a>
          <a href={`https://clinicaltrials.gov/search?cond=${encodeURIComponent(disease.name)}`}
            target="_blank" rel="noopener noreferrer"
            className="btn btn-teal btn-sm" style={{ justifyContent: 'flex-start' }}>
            Clinical Trials →
          </a>
        </div>
      </div>
    </div>
  )
}

function DiseaseRow({ disease, onClick, selected }) {
  const urgColor = URGENCY_COLOR[disease.urgency] || 'var(--text-muted)'
  return (
    <div
      className="card"
      onClick={() => onClick(disease)}
      style={{
        marginBottom: 8, padding: '14px 18px', cursor: 'pointer',
        border: selected ? '1px solid var(--accent-primary)' : '1px solid var(--border)',
        background: selected ? 'rgba(59,130,246,0.05)' : 'var(--bg-card)'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
            <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 14, color: 'var(--text-bright)' }}>
              {disease.name}
            </span>
            <span className="badge badge-info" style={{ fontSize: 10 }}>
              {INHERIT_LABEL[disease.inheritance] || disease.inheritance}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            <span style={{ color: 'var(--accent-glow)' }}>{disease.gene}</span>
            <span>{disease.prevalence}</span>
            <span style={{ color: urgColor }}>{disease.urgency}</span>
          </div>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, maxWidth: 280 }} className="hide-mobile">
          {disease.key_symptoms?.slice(0, 3).map((s, i) => (
            <span key={i} className="chip" style={{ fontSize: 10 }}>{s}</span>
          ))}
        </div>
        <ChevronRight size={15} color="var(--text-muted)" />
      </div>
    </div>
  )
}

export default function DiseasesPage() {
  const [diseases, setDiseases] = useState([])
  const [filtered, setFiltered] = useState([])
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filterInheritance, setFilterInheritance] = useState('')

  useEffect(() => {
    api.diseases.list().then(res => {
      setDiseases(res.diseases || [])
      setFiltered(res.diseases || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    let results = diseases
    if (query) {
      const q = query.toLowerCase()
      results = results.filter(d =>
        d.name.toLowerCase().includes(q) ||
        d.gene.toLowerCase().includes(q) ||
        d.key_symptoms?.some(s => s.toLowerCase().includes(q)) ||
        d.inheritance.toLowerCase().includes(q)
      )
    }
    if (filterInheritance) {
      results = results.filter(d => d.inheritance.includes(filterInheritance))
    }
    setFiltered(results)
  }, [query, filterInheritance, diseases])

  const inheritanceOptions = [...new Set(diseases.map(d => d.inheritance))]

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 60px)' }}>
      {/* Main content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '40px 24px', maxWidth: selected ? 'calc(100% - 480px)' : 1100, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-violet)', letterSpacing: '0.1em', marginBottom: 8 }}>
            DISEASE KNOWLEDGE BASE
          </div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: 'var(--text-bright)', marginBottom: 8 }}>
            Rare Disease Library
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
            Curated rare disease profiles with genetic, clinical, and management information
          </p>
        </div>

        {/* Search & Filters */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: 200 }}>
            <input
              className="input"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search diseases, genes, symptoms..."
              style={{ paddingLeft: 40 }}
            />
            <Search size={15} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          </div>
          <select
            className="input"
            value={filterInheritance}
            onChange={e => setFilterInheritance(e.target.value)}
            style={{ width: 'auto', cursor: 'pointer' }}
          >
            <option value="">All Inheritance Patterns</option>
            {inheritanceOptions.map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        </div>

        {/* Stats bar */}
        <div style={{ display: 'flex', gap: 16, marginBottom: 20, fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', flexWrap: 'wrap' }}>
          <span>{filtered.length} diseases</span>
          <span>•</span>
          <span>{diseases.filter(d => d.inheritance === 'Autosomal recessive').length} autosomal recessive</span>
          <span>•</span>
          <span>{diseases.filter(d => d.urgency === 'high' || d.urgency === 'critical').length} high urgency</span>
        </div>

        {/* Disease list */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)' }}>
            <div className="spinner" style={{ margin: '0 auto 12px', width: 24, height: 24 }} />
            Loading disease library...
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)', fontSize: 13 }}>
            No diseases match your search.
          </div>
        ) : (
          filtered.map(d => (
            <DiseaseRow key={d.id} disease={d} onClick={setSelected} selected={selected?.id === d.id} />
          ))
        )}
      </div>

      {/* Detail panel */}
      {selected && (
        <DiseaseDetailPanel disease={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  )
}
