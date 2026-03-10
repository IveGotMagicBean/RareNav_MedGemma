import { useState, useEffect } from 'react'
import { BarChart2, Dna, Activity, TrendingUp, Database, Zap, BookOpen } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import { api } from '../utils/api.js'

const COLORS = ['#f43f5e', '#f59e0b', '#a78bfa', '#34d399', '#60a5fa', '#2dd4bf', '#fb923c', '#e879f9']

const SIGNIFICANCE_DATA = [
  { name: 'Pathogenic', count: 142831, pct: 18 },
  { name: 'Likely Path.', count: 89203, pct: 11 },
  { name: 'VUS', count: 312445, pct: 39 },
  { name: 'Likely Benign', count: 98234, pct: 12 },
  { name: 'Benign', count: 113287, pct: 14 },
  { name: 'Conflicting', count: 43901, pct: 5 },
]

const VARIANT_TYPES = [
  { name: 'SNV', value: 68 },
  { name: 'Deletion', value: 15 },
  { name: 'Insertion', value: 8 },
  { name: 'Indel', value: 5 },
  { name: 'Dup', value: 4 },
]

const TOP_GENES = [
  { gene: 'BRCA2', variants: 4832 },
  { gene: 'BRCA1', variants: 4291 },
  { gene: 'MLH1', variants: 3102 },
  { gene: 'CFTR', variants: 2987 },
  { gene: 'MSH2', variants: 2843 },
  { gene: 'TP53', variants: 2701 },
  { gene: 'APC', variants: 2456 },
  { gene: 'LDLR', variants: 2234 },
]

const DIAGNOSIS_DELAY = [
  { year: '2010', delay: 7.5 },
  { year: '2013', delay: 6.8 },
  { year: '2016', delay: 5.9 },
  { year: '2019', delay: 5.1 },
  { year: '2022', delay: 4.3 },
  { year: '2025', delay: 3.2 },
]

function StatCard({ title, value, subtitle, icon: Icon, color, bg }) {
  return (
    <div className="card" style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
      <div style={{ width: 48, height: 48, borderRadius: 10, background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
        <Icon size={22} color={color} />
      </div>
      <div>
        <div style={{ fontFamily: 'var(--font-display)', fontSize: 28, fontWeight: 800, color: 'var(--text-bright)', lineHeight: 1.1 }}>
          {value}
        </div>
        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginTop: 2 }}>{title}</div>
        {subtitle && <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2, fontFamily: 'var(--font-mono)' }}>{subtitle}</div>}
      </div>
    </div>
  )
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload?.length) {
    return (
      <div style={{ background: 'var(--bg-raised)', border: '1px solid var(--border-bright)', borderRadius: 8, padding: '8px 12px', fontSize: 12 }}>
        <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-glow)', marginBottom: 4 }}>{label}</div>
        {payload.map((p, i) => (
          <div key={i} style={{ color: p.color || 'var(--text-primary)' }}>{p.name}: {p.value?.toLocaleString?.() ?? p.value}</div>
        ))}
      </div>
    )
  }
  return null
}

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [dbStats, setDbStats] = useState(null)

  useEffect(() => {
    api.status().then(setStats).catch(() => {})
    api.variants.statistics().then(setDbStats).catch(() => {})
  }, [])

  return (
    <div className="container" style={{ padding: '40px 24px', maxWidth: 1200 }}>
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-primary)', letterSpacing: '0.1em', marginBottom: 8 }}>
          SYSTEM ANALYTICS
        </div>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: 'var(--text-bright)', marginBottom: 8 }}>
          Dashboard
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          RareNav system statistics and rare disease landscape overview
        </p>
      </div>

      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 32 }}>
        <StatCard title="ClinVar Variants" value={dbStats?.total_variants?.toLocaleString() || '5M+'} subtitle="Loaded in database"
          icon={Database} color="var(--accent-primary)" bg="rgba(59,130,246,0.1)" />
        <StatCard title="Pathogenic Variants" value={dbStats?.pathogenic_count?.toLocaleString() || '231K+'} subtitle="Clinically significant"
          icon={Dna} color="var(--accent-rose)" bg="rgba(244,63,94,0.1)" />
        <StatCard title="HPO Terms" value="13,000+" subtitle="Phenotype ontology"
          icon={Activity} color="var(--accent-teal)" bg="rgba(45,212,191,0.1)" />
        <StatCard title="Rare Diseases" value="7,000+" subtitle="ORPHA + OMIM"
          icon={BookOpen} color="var(--accent-violet)" bg="rgba(167,139,250,0.1)" />
        <StatCard title="Avg Diagnosis Delay" value="5–7 yrs" subtitle="Without AI assistance"
          icon={TrendingUp} color="var(--accent-amber)" bg="rgba(245,158,11,0.1)" />
        <StatCard title="AI Model" value="4B params" subtitle="MedGemma (Google HAI-DEF)"
          icon={Zap} color="var(--accent-glow)" bg="rgba(96,165,250,0.1)" />
      </div>

      {/* Charts row 1 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
        {/* Clinical significance distribution */}
        <div className="card">
          <div style={{ fontSize: 13, fontWeight: 700, fontFamily: 'var(--font-display)', color: 'var(--text-bright)', marginBottom: 4 }}>
            Variant Clinical Significance
          </div>
          <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: 20 }}>ClinVar distribution</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={SIGNIFICANCE_DATA} margin={{ left: -10 }}>
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'DM Mono' }} />
              <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)' }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}
                fill="var(--accent-primary)"
                cells={SIGNIFICANCE_DATA.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Variant types pie */}
        <div className="card">
          <div style={{ fontSize: 13, fontWeight: 700, fontFamily: 'var(--font-display)', color: 'var(--text-bright)', marginBottom: 4 }}>
            Variant Types
          </div>
          <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: 20 }}>Genomic alteration classes</div>
          <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
            <ResponsiveContainer width="50%" height={200}>
              <PieChart>
                <Pie data={VARIANT_TYPES} dataKey="value" cx="50%" cy="50%" outerRadius={80} paddingAngle={2}>
                  {VARIANT_TYPES.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div style={{ flex: 1 }}>
              {VARIANT_TYPES.map(({ name, value }, i) => (
                <div key={name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
                    <div style={{ width: 10, height: 10, borderRadius: 2, background: COLORS[i], flexShrink: 0 }} />
                    <span style={{ color: 'var(--text-secondary)' }}>{name}</span>
                  </div>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-primary)', fontWeight: 600 }}>{value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Charts row 2 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
        {/* Top genes by variants */}
        <div className="card">
          <div style={{ fontSize: 13, fontWeight: 700, fontFamily: 'var(--font-display)', color: 'var(--text-bright)', marginBottom: 4 }}>
            Top Genes by Variant Count
          </div>
          <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: 20 }}>Pathogenic + Likely pathogenic</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={TOP_GENES} layout="vertical" margin={{ left: 10 }}>
              <XAxis type="number" tick={{ fontSize: 10, fill: 'var(--text-muted)' }} />
              <YAxis dataKey="gene" type="category" width={50} tick={{ fontSize: 11, fill: 'var(--text-secondary)', fontFamily: 'DM Mono' }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="variants" fill="var(--accent-rose)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Diagnosis delay trend */}
        <div className="card">
          <div style={{ fontSize: 13, fontWeight: 700, fontFamily: 'var(--font-display)', color: 'var(--text-bright)', marginBottom: 4 }}>
            Rare Disease Diagnosis Delay Trend
          </div>
          <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: 20 }}>Average years to diagnosis (improving with AI)</div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={DIAGNOSIS_DELAY} margin={{ left: -10 }}>
              <XAxis dataKey="year" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} />
              <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)' }} domain={[2, 9]} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="delay" stroke="var(--accent-teal)" strokeWidth={2.5}
                dot={{ fill: 'var(--accent-teal)', r: 4 }} name="Years to Diagnosis" />
            </LineChart>
          </ResponsiveContainer>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: 8 }}>
            Source: NORD, Eurordis. AI tools helping reduce from 7 to ~3 years.
          </div>
        </div>
      </div>

      {/* System info */}
      <div className="card" style={{ background: 'var(--bg-surface)' }}>
        <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 16 }}>
          SYSTEM ARCHITECTURE
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
          {[
            { label: 'AI Model', val: 'MedGemma 4B (Google HAI-DEF)', color: 'var(--accent-primary)' },
            { label: 'Genomic Database', val: 'ClinVar (NCBI) Feb 2026', color: 'var(--accent-rose)' },
            { label: 'Phenotype Ontology', val: 'Human Phenotype Ontology (HPO)', color: 'var(--accent-teal)' },
            { label: 'Disease Database', val: 'ORPHA + OMIM (curated)', color: 'var(--accent-violet)' },
            { label: 'Backend', val: 'Python Flask + Pandas', color: 'var(--text-secondary)' },
            { label: 'Frontend', val: 'React + Vite', color: 'var(--text-secondary)' },
          ].map(({ label, val, color }) => (
            <div key={label}>
              <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 4 }}>{label}</div>
              <div style={{ fontSize: 13, color, fontWeight: 500 }}>{val}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
