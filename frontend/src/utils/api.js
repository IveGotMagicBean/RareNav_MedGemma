// API utility functions
const BASE_URL = '/api'

async function fetchApi(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({ error: 'Request failed' }))
    throw new Error(err.error || `HTTP ${response.status}`)
  }
  return response.json()
}

export const api = {
  health: () => fetchApi('/health'),
  status: () => fetchApi('/status'),

  variants: {
    search: (params) => fetchApi(`/variants/search?${new URLSearchParams(params)}`),
    explain: (data) => fetchApi('/variants/explain', { method: 'POST', body: JSON.stringify(data) }),
    geneSummary: (gene) => fetchApi(`/variants/gene-summary/${gene}`),
    statistics: () => fetchApi('/variants/statistics'),
    parse: (input) => fetchApi('/variants/parse', { method: 'POST', body: JSON.stringify({ input }) }),
  },

  symptoms: {
    search: (q, limit = 10) => fetchApi(`/symptoms/search?q=${encodeURIComponent(q)}&limit=${limit}`),
    allTerms: () => fetchApi('/symptoms/all-terms'),
    analyze: (data) => fetchApi('/symptoms/analyze', { method: 'POST', body: JSON.stringify(data) }),
    mapText: (text) => fetchApi('/symptoms/map-text', { method: 'POST', body: JSON.stringify({ text }) }),
  },

  diagnosis: {
    symptomBased: (data) => fetchApi('/diagnosis/symptom-based', { method: 'POST', body: JSON.stringify(data) }),
    variantBased: (data) => fetchApi('/diagnosis/variant-based', { method: 'POST', body: JSON.stringify(data) }),
    generateReport: (data) => fetchApi('/diagnosis/report', { method: 'POST', body: JSON.stringify(data) }),
    diseaseList: () => fetchApi('/diagnosis/disease-list'),
  },

  chat: {
    message: (data) => fetchApi('/chat/message', { method: 'POST', body: JSON.stringify(data) }),
    clearSession: (id) => fetchApi(`/chat/session/${id}`, { method: 'DELETE' }),
  },

  diseases: {
    list: (q = '') => fetchApi(`/diseases/${q ? `?q=${encodeURIComponent(q)}` : ''}`),
    get: (id) => fetchApi(`/diseases/${id}`),
    byGene: (gene) => fetchApi(`/diseases/by-gene/${gene}`),
  },

  upload: {
    report: (data) => fetchApi('/upload/report', { method: 'POST', body: JSON.stringify(data) }),
  },

  agent: {
    run: (data) => fetchApi('/agent/run', { method: 'POST', body: JSON.stringify(data) }),
    status: () => fetchApi('/agent/status'),
  },
}

export default api

// Note: api object is extended via direct injection below
// (bypassing the existing object literal limitation)
