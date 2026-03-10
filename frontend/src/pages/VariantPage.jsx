import { useState, useRef } from 'react'
import { Dna, Search, ChevronDown, ChevronUp, ExternalLink, Copy, CheckCheck, Loader2, Info } from 'lucide-react'
import { api } from '../utils/api.js'
import { getSignificanceBadge, getSignificanceLabel, getSignificanceColor, formatDate, GENE_EXAMPLES, parseMarkdown } from '../utils/helpers.js'

function VariantCard({ variant, onExplain, isExplaining, expanded, onToggle }) {
  const [copied, setCopied] = useState(false)

  const copyName = () => {
    navigator.clipboard.writeText(variant.name)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const sigColor = getSignificanceColor(variant.significance)

  return (
    <div className="card" style={{ marginBottom: 12, padding: 0, overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ padding: '16px 20px', display: 'flex', alignItems: 'flex-start', gap: 14, cursor: 'pointer' }} onClick={onToggle}>
        <div style={{
          width: 4, alignSelf: 'stretch', borderRadius: 99,
          background: sigColor, flexShrink: 0, minHeight: 40
        }} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 6 }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--accent-glow)', fontWeight: 500 }}>
              {variant.gene}
            </span>
            <span className={`badge ${getSignificanceBadge(variant.significance)}`}>
              {getSignificanceLabel(variant.significance)}
            </span>
            {variant.submitters > 0 && (
              <span className="badge badge-info">{variant.submitters} submitters</span>
            )}
          </div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            {variant.name?.slice(0, 90)}{variant.name?.length > 90 ? '...' : ''}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
            {variant.phenotype?.split('|')[0]?.trim()?.slice(0, 60)}
          </div>
        </div>
        <div style={{ color: 'var(--text-muted)', flexShrink: 0 }}>
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div style={{ borderTop: '1px solid var(--border)', padding: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 16 }}>
            {[
              { label: 'Position', val: variant.position },
              { label: 'Type', val: variant.type },
              { label: 'Ref/Alt', val: `${variant.ref} → ${variant.alt}` },
              { label: 'dbSNP', val: variant.dbsnp || 'N/A' },
              { label: 'Last Evaluated', val: formatDate(variant.last_evaluated) },
              { label: 'Review Status', val: variant.review_status?.replace('criteria provided, ', '') },
            ].map(({ label, val }) => (
              <div key={label}>
                <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 2 }}>{label}</div>
                <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>{val || 'N/A'}</div>
              </div>
            ))}
          </div>

          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 6 }}>FULL NAME</div>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
              <code style={{ fontSize: 11, color: 'var(--text-secondary)', flex: 1, background: 'var(--bg-raised)', padding: '8px 10px', borderRadius: 6, wordBreak: 'break-all', lineHeight: 1.5 }}>
                {variant.name}
              </code>
              <button className="btn btn-ghost btn-sm btn-icon" onClick={copyName} title="Copy">
                {copied ? <CheckCheck size={13} color="var(--success)" /> : <Copy size={13} />}
              </button>
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 6 }}>ASSOCIATED CONDITIONS</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {(variant.phenotype || '').split('|').slice(0, 5).map((p, i) => (
                <span key={i} className="chip" style={{ fontSize: 11 }}>{p.trim()}</span>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button
              className="btn btn-primary btn-sm"
              onClick={() => onExplain(variant)}
              disabled={isExplaining}
            >
              {isExplaining ? <><div className="spinner" />Analyzing...</> : <><Dna size={13} />AI Explanation</>}
            </button>
            <a
              href={`https://www.ncbi.nlm.nih.gov/clinvar/variation/${variant.variation_id}/`}
              target="_blank" rel="noopener noreferrer"
              className="btn btn-ghost btn-sm"
            >
              <ExternalLink size={13} /> ClinVar
            </a>
          </div>
        </div>
      )}
    </div>
  )
}

function ExplanationPanel({ explanation, gene, variant, onClose }) {
  return (
    <div className="card" style={{
      marginTop: 24,
      border: '1px solid rgba(59,130,246,0.3)',
      background: 'linear-gradient(135deg, rgba(59,130,246,0.05), rgba(45,212,191,0.03))'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-teal))',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <Dna size={16} color="white" />
          </div>
          <div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--text-bright)', fontSize: 15 }}>
              MedGemma Clinical Explanation
            </div>
            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)' }}>
              {gene} • {explanation.latency?.toFixed(1)}s response
              {explanation.demo && ' • Demo Mode'}
            </div>
          </div>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={onClose}>Dismiss</button>
      </div>
      <div
        className="prose"
        style={{ fontSize: 14, lineHeight: 1.8 }}
        dangerouslySetInnerHTML={{ __html: parseMarkdown(explanation.explanation) }}
      />
      <div style={{
        marginTop: 16, padding: '10px 14px', borderRadius: 8,
        background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)',
        fontSize: 12, color: 'var(--accent-amber)',
        display: 'flex', alignItems: 'flex-start', gap: 8
      }}>
        <Info size={13} style={{ flexShrink: 0, marginTop: 1 }} />
        This AI explanation is for educational purposes. Consult a genetic counselor or medical geneticist for clinical decisions.
      </div>
    </div>
  )
}

export default function VariantPage() {
  const [geneInput, setGeneInput] = useState('')
  const [variantInput, setVariantInput] = useState('')
  const [freeInput, setFreeInput] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [expandedId, setExpandedId] = useState(null)
  const [explanation, setExplanation] = useState(null)
  const [explainTarget, setExplainTarget] = useState(null)
  const [explainLoading, setExplainLoading] = useState(false)
  const [geneSummary, setGeneSummary] = useState(null)
  const [mode, setMode] = useState('structured') // structured | free

  const search = async () => {
    setError(null)
    setResults([])
    setExplanation(null)
    setGeneSummary(null)

    if (mode === 'free') {
      // Parse free text first
      if (!freeInput.trim()) return
      setLoading(true)
      try {
        const parsed = await api.variants.parse(freeInput)
        if (parsed.parsed) {
          const res = await api.variants.search({ gene: parsed.gene, variant: parsed.variant })
          setResults(res.results || [])
          if (parsed.gene) {
            const gs = await api.variants.geneSummary(parsed.gene).catch(() => null)
            setGeneSummary(gs)
          }
        } else {
          setError('Could not parse variant. Try: "CFTR F508del" or "HFE C282Y"')
        }
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
      return
    }

    if (!geneInput.trim()) return
    setLoading(true)
    try {
      const params = { gene: geneInput.trim() }
      if (variantInput.trim()) params.variant = variantInput.trim()
      const res = await api.variants.search(params)
      setResults(res.results || [])

      const gs = await api.variants.geneSummary(geneInput.trim()).catch(() => null)
      setGeneSummary(gs)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const explainVariant = async (variant) => {
    setExplainLoading(true)
    setExplainTarget(variant.variation_id)
    setExplanation(null)
    try {
      const res = await api.variants.explain({
        gene: variant.gene,
        variant: variant.name,
        significance: variant.significance,
        disease: variant.phenotype
      })
      setExplanation({ ...res, gene: variant.gene })
    } catch (e) {
      setError(e.message)
    } finally {
      setExplainLoading(false)
      setExplainTarget(null)
    }
  }

  return (
    <div className="container" style={{ padding: '40px 24px', maxWidth: 900 }}>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-rose)', letterSpacing: '0.1em', marginBottom: 8 }}>
          GENETIC VARIANT ANALYSIS
        </div>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: 'var(--text-bright)', marginBottom: 8 }}>
          Variant Explorer
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          Query ClinVar database and get MedGemma-powered clinical explanations
        </p>
      </div>

      {/* Mode toggle */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {['structured', 'free'].map(m => (
          <button key={m} className={`btn ${mode === m ? 'btn-primary' : 'btn-ghost'} btn-sm`} onClick={() => setMode(m)}>
            {m === 'structured' ? 'Gene + Variant' : 'Free Text Input'}
          </button>
        ))}
      </div>

      {/* Search form */}
      <div className="card" style={{ marginBottom: 24 }}>
        {mode === 'free' ? (
          <div>
            <label style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', display: 'block', marginBottom: 8, letterSpacing: '0.06em' }}>
              VARIANT (FREE TEXT)
            </label>
            <input
              className="input input-mono"
              value={freeInput}
              onChange={e => setFreeInput(e.target.value)}
              placeholder="e.g., CFTR F508del  |  HFE C282Y  |  BRCA1 c.5266dupC"
              onKeyDown={e => e.key === 'Enter' && search()}
              style={{ fontSize: 14 }}
            />
            <div style={{ marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {['CFTR F508del', 'HFE C282Y', 'BRCA1 c.5266dupC', 'HFE H63D', 'PTEN R130X'].map(ex => (
                <button key={ex} className="chip chip-clickable" onClick={() => setFreeInput(ex)}>{ex}</button>
              ))}
            </div>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 16 }}>
            <div>
              <label style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', display: 'block', marginBottom: 8, letterSpacing: '0.06em' }}>GENE SYMBOL</label>
              <input
                className="input input-mono"
                value={geneInput}
                onChange={e => setGeneInput(e.target.value.toUpperCase())}
                placeholder="e.g., CFTR"
                onKeyDown={e => e.key === 'Enter' && search()}
              />
              <div style={{ marginTop: 6, display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {GENE_EXAMPLES.slice(0, 6).map(g => (
                  <button key={g} className="chip chip-clickable" style={{ fontSize: 10 }} onClick={() => setGeneInput(g)}>{g}</button>
                ))}
              </div>
            </div>
            <div>
              <label style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', display: 'block', marginBottom: 8, letterSpacing: '0.06em' }}>VARIANT (OPTIONAL)</label>
              <input
                className="input input-mono"
                value={variantInput}
                onChange={e => setVariantInput(e.target.value)}
                placeholder="e.g., F508del  |  C282Y  |  c.845G>A"
                onKeyDown={e => e.key === 'Enter' && search()}
              />
            </div>
          </div>
        )}

        <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
          <button className="btn btn-primary" onClick={search} disabled={loading}>
            {loading ? <><div className="spinner" />Searching ClinVar...</> : <><Search size={15} />Search ClinVar</>}
          </button>
          {(results.length > 0 || error) && (
            <button className="btn btn-ghost btn-sm" onClick={() => { setResults([]); setError(null); setGeneSummary(null); setExplanation(null) }}>
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={{ padding: '14px 16px', borderRadius: 8, background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', color: 'var(--accent-rose)', fontSize: 13, marginBottom: 16 }}>
          {error}
        </div>
      )}

      {/* Gene Summary */}
      {geneSummary?.found && (
        <div className="card" style={{ marginBottom: 24, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 16 }}>
          <div>
            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 4 }}>GENE</div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 22, color: 'var(--accent-glow)' }}>{geneSummary.gene}</div>
          </div>
          <div>
            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 4 }}>TOTAL VARIANTS</div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 20, color: 'var(--text-bright)' }}>{geneSummary.total_variants?.toLocaleString()}</div>
          </div>
          <div>
            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 4 }}>PATHOGENIC</div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 20, color: 'var(--accent-rose)' }}>{geneSummary.pathogenic_count?.toLocaleString()}</div>
          </div>
          <div>
            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 4 }}>ASSOCIATED DISEASES</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {geneSummary.associated_diseases?.slice(0, 3).map((d, i) => (
                <span key={i} className="chip" style={{ fontSize: 10 }}>{d?.slice(0, 30)}</span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div>
          <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: 16, letterSpacing: '0.04em' }}>
            {results.length} variant{results.length > 1 ? 's' : ''} found
          </div>
          {results.map((v, i) => (
            <VariantCard
              key={v.variation_id || i}
              variant={v}
              onExplain={explainVariant}
              isExplaining={explainLoading && explainTarget === v.variation_id}
              expanded={expandedId === (v.variation_id || i)}
              onToggle={() => setExpandedId(expandedId === (v.variation_id || i) ? null : (v.variation_id || i))}
            />
          ))}
        </div>
      )}

      {/* AI Explanation */}
      {explanation && (
        <ExplanationPanel
          explanation={explanation}
          gene={explanation.gene}
          onClose={() => setExplanation(null)}
        />
      )}
    </div>
  )
}
