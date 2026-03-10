// Helper utilities

export function getSignificanceBadge(sig) {
  if (!sig) return 'badge-uncertain'
  const s = sig.toLowerCase()
  if (s.includes('pathogenic') && !s.includes('likely') && !s.includes('conflict')) return 'badge-pathogenic'
  if (s.includes('likely pathogenic')) return 'badge-likely-pathogenic'
  if (s.includes('benign') && !s.includes('likely')) return 'badge-benign'
  if (s.includes('likely benign')) return 'badge-benign'
  if (s.includes('conflict')) return 'badge-conflicting'
  if (s.includes('risk')) return 'badge-amber'
  return 'badge-uncertain'
}

export function getSignificanceLabel(sig) {
  if (!sig) return 'Unknown'
  const s = sig.toLowerCase()
  if (s.includes('pathogenic/likely pathogenic')) return 'Path/LP'
  if (s.includes('pathogenic') && !s.includes('likely') && !s.includes('conflict')) return 'Pathogenic'
  if (s.includes('likely pathogenic')) return 'Likely Pathogenic'
  if (s.includes('likely benign')) return 'Likely Benign'
  if (s.includes('benign')) return 'Benign'
  if (s.includes('conflict')) return 'Conflicting'
  if (s.includes('uncertain')) return 'VUS'
  return sig.slice(0, 20)
}

export function getSignificanceColor(sig) {
  if (!sig) return 'var(--accent-violet)'
  const s = sig.toLowerCase()
  if (s.includes('pathogenic') && !s.includes('conflict')) return 'var(--accent-rose)'
  if (s.includes('likely pathogenic')) return 'var(--accent-amber)'
  if (s.includes('benign')) return 'var(--success)'
  if (s.includes('conflict')) return '#fb923c'
  return 'var(--accent-violet)'
}

export function formatDate(dateStr) {
  if (!dateStr || dateStr === 'nan' || dateStr === 'NaT') return 'Unknown'
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch { return dateStr }
}

export function truncate(str, len = 60) {
  if (!str) return ''
  return str.length > len ? str.slice(0, len) + '...' : str
}

export function getMatchColor(score) {
  if (score >= 0.7) return 'var(--accent-rose)'
  if (score >= 0.4) return 'var(--accent-amber)'
  return 'var(--accent-teal)'
}

export function parseMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/gs, '<ul>$&</ul>')
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    .replace(/\n\n/g, '<br/><br/>')
}

export function debounce(fn, ms) {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), ms)
  }
}

export const GENE_EXAMPLES = ['CFTR', 'BRCA1', 'BRCA2', 'HFE', 'FBN1', 'LDLR', 'PTEN', 'PKD1', 'GBA', 'GLA', 'TSC1', 'PAH']
export const VARIANT_EXAMPLES = ['F508del', 'C282Y', 'H63D', 'c.845G>A', 'p.Cys282Tyr']
export const SYMPTOM_EXAMPLES = [
  'seizures', 'joint hypermobility', 'cardiomyopathy', 'splenomegaly',
  'muscle weakness', 'ataxia', 'proteinuria', 'anemia', 'hepatomegaly',
  'neuropathic pain', 'lens dislocation', 'failure to thrive', 'dementia'
]
