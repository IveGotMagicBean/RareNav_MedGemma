import { useNavigate } from 'react-router-dom'
import { Dna, Activity, Search, MessageSquare, BookOpen, ArrowRight, AlertTriangle, Zap, Shield } from 'lucide-react'

const FEATURES = [
  {
    icon: Dna, color: 'var(--accent-rose)', bg: 'rgba(244,63,94,0.1)',
    title: 'Variant Analysis',
    desc: 'Query ClinVar with 5M+ variants. Get AI-powered clinical significance explanations powered by MedGemma.',
    path: '/variant', tag: 'ClinVar + MedGemma'
  },
  {
    icon: Activity, color: 'var(--accent-teal)', bg: 'rgba(45,212,191,0.1)',
    title: 'Symptom Navigator',
    desc: 'Map free-text symptoms to HPO ontology terms. Multi-symptom phenotype analysis with rare disease differential.',
    path: '/symptoms', tag: 'HPO Ontology'
  },
  {
    icon: Search, color: 'var(--accent-amber)', bg: 'rgba(245,158,11,0.1)',
    title: 'Integrated Diagnosis',
    desc: 'Dual-channel AI reasoning: combine genetic + clinical evidence for ranked differential diagnosis.',
    path: '/diagnosis', tag: 'AI Reasoning'
  },
  {
    icon: BookOpen, color: 'var(--accent-violet)', bg: 'rgba(167,139,250,0.1)',
    title: 'Disease Library',
    desc: 'Curated rare disease knowledge base with genes, symptoms, inheritance, treatments, and specialist guidance.',
    path: '/diseases', tag: 'ORPHA + OMIM'
  },
  {
    icon: MessageSquare, color: 'var(--accent-primary)', bg: 'rgba(59,130,246,0.1)',
    title: 'AI Medical Consultant',
    desc: 'Conversational interface powered by MedGemma. Ask follow-up questions, get variant explanations, understand results.',
    path: '/chat', tag: 'MedGemma 4B'
  },
]

const STATS = [
  { val: '5M+', label: 'ClinVar Variants', color: 'var(--accent-rose)' },
  { val: '18K+', label: 'HPO Terms', color: 'var(--accent-teal)' },
  { val: '7,000+', label: 'Rare Diseases', color: 'var(--accent-amber)' },
  { val: '5-7yr', label: 'Avg Diagnosis Delay', color: 'var(--accent-violet)' },
]

export default function HomePage() {
  const navigate = useNavigate()

  return (
    <div style={{ position: 'relative', overflow: 'hidden' }}>
      {/* Hero */}
      <section style={{ 
        padding: '80px 0 60px',
        borderBottom: '1px solid var(--border)',
        position: 'relative'
      }}>
        {/* Background grid pattern */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: `radial-gradient(circle at 1px 1px, rgba(59,130,246,0.06) 1px, transparent 0)`,
          backgroundSize: '32px 32px',
          pointerEvents: 'none'
        }} />

        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ maxWidth: 820 }}>
            {/* Alert banner */}
            <div className="animate-in" style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              padding: '6px 14px', borderRadius: 99,
              background: 'rgba(244,63,94,0.08)',
              border: '1px solid rgba(244,63,94,0.2)',
              marginBottom: 32
            }}>
              <AlertTriangle size={12} color="var(--accent-rose)" />
              <span style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--accent-rose)', letterSpacing: '0.04em' }}>
                RARE DISEASE DIAGNOSTIC TOOL — FOR RESEARCH & EDUCATIONAL USE
              </span>
            </div>

            <h1 className="animate-in animate-delay-1" style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(42px, 6vw, 80px)',
              fontWeight: 800,
              lineHeight: 1.05,
              letterSpacing: '-0.03em',
              marginBottom: 24,
              color: 'var(--text-bright)',
            }}>
              Navigate the<br />
              <span style={{ 
                background: 'linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-teal) 100%)',
                WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'
              }}>Rare Disease</span><br />
              Landscape
            </h1>

            <p className="animate-in animate-delay-2" style={{
              fontSize: 18, color: 'var(--text-secondary)',
              maxWidth: 560, lineHeight: 1.7, marginBottom: 40
            }}>
              An AI-powered system integrating ClinVar genomic data with MedGemma clinical intelligence. 
              Built for clinicians, genetic counselors, and patients navigating rare genetic conditions.
            </p>

            <div className="animate-in animate-delay-3" style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <button className="btn btn-primary btn-lg" onClick={() => navigate('/variant')}>
                <Dna size={18} /> Analyze a Variant
              </button>
              <button className="btn btn-ghost btn-lg" onClick={() => navigate('/symptoms')}>
                <Activity size={18} /> Enter Symptoms
              </button>
              <button className="btn btn-teal btn-lg" onClick={() => navigate('/chat')}>
                <MessageSquare size={18} /> Ask AI
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section style={{ padding: '32px 0', borderBottom: '1px solid var(--border)', background: 'var(--bg-surface)' }}>
        <div className="container" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24 }}>
          {STATS.map(({ val, label, color }) => (
            <div key={label} style={{ textAlign: 'center' }}>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(28px, 4vw, 44px)', fontWeight: 800, color, lineHeight: 1.1 }}>
                {val}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4, fontFamily: 'var(--font-mono)' }}>
                {label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section style={{ padding: '64px 0' }}>
        <div className="container">
          <div style={{ marginBottom: 48, display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)', letterSpacing: '0.1em', marginBottom: 8 }}>
                CLINICAL MODULES
              </div>
              <h2 style={{ fontSize: 32, fontWeight: 800, color: 'var(--text-bright)' }}>
                Full diagnostic pipeline
              </h2>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 16 }}>
            {FEATURES.map(({ icon: Icon, color, bg, title, desc, path, tag }) => (
              <div
                key={title}
                className="card animate-in"
                onClick={() => navigate(path)}
                style={{ cursor: 'pointer', position: 'relative', overflow: 'hidden' }}
              >
                {/* Background accent */}
                <div style={{
                  position: 'absolute', top: 0, right: 0,
                  width: 120, height: 120,
                  background: bg,
                  borderRadius: '0 0 0 100%',
                  opacity: 0.5
                }} />

                <div style={{ position: 'relative', zIndex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16 }}>
                    <div style={{ width: 44, height: 44, borderRadius: 10, background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Icon size={22} color={color} />
                    </div>
                    <span style={{
                      fontSize: 10, fontFamily: 'var(--font-mono)', color, background: bg,
                      padding: '3px 8px', borderRadius: 99, letterSpacing: '0.06em'
                    }}>
                      {tag}
                    </span>
                  </div>
                  <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8, color: 'var(--text-bright)' }}>{title}</h3>
                  <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 16 }}>{desc}</p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4, color, fontSize: 12, fontWeight: 600, fontFamily: 'var(--font-display)' }}>
                    Open module <ArrowRight size={12} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section style={{ padding: '64px 0', background: 'var(--bg-surface)', borderTop: '1px solid var(--border)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-primary)', letterSpacing: '0.1em', marginBottom: 8 }}>
              WORKFLOW
            </div>
            <h2 style={{ fontSize: 32, fontWeight: 800, color: 'var(--text-bright)' }}>How RareNav works</h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 24 }}>
            {[
              { step: '01', title: 'Input Clinical Data', desc: 'Enter genetic variants (VCF/HGVS format), patient symptoms, or family history', icon: Dna },
              { step: '02', title: 'Database Query', desc: 'RareNav queries ClinVar (5M+ variants) and HPO ontology in real-time', icon: Search },
              { step: '03', title: 'AI Reasoning', desc: 'MedGemma 4B generates clinical interpretations, differential diagnoses, and management guidance', icon: Zap },
              { step: '04', title: 'Actionable Output', desc: 'Receive structured reports with ranked diagnoses, specialist referrals, and next steps', icon: Shield },
            ].map(({ step, title, desc, icon: Icon }) => (
              <div key={step} style={{ textAlign: 'center', padding: '24px 16px' }}>
                <div style={{
                  width: 52, height: 52, borderRadius: '50%',
                  background: 'linear-gradient(135deg, rgba(59,130,246,0.15), rgba(45,212,191,0.1))',
                  border: '1px solid var(--border-bright)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 16px'
                }}>
                  <Icon size={22} color="var(--accent-glow)" />
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--accent-primary)', marginBottom: 8, letterSpacing: '0.06em' }}>
                  STEP {step}
                </div>
                <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 8, color: 'var(--text-bright)' }}>{title}</h3>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <footer style={{ padding: '24px 0', borderTop: '1px solid var(--border)', background: 'var(--bg-deep)' }}>
        <div className="container">
          <p style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', textAlign: 'center', lineHeight: 1.8 }}>
            ⚠️ RareNav is a research and educational tool powered by MedGemma (Google Health AI). 
            It does not constitute medical advice. All clinical decisions must be made by qualified healthcare professionals. 
            Genetic counseling is recommended for pathogenic variant findings.
          </p>
        </div>
      </footer>
    </div>
  )
}
