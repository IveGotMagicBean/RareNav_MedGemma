import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { 
  Dna, Activity, Search, MessageSquare, BookOpen, 
  BarChart2, Menu, X, Zap, AlertCircle, CheckCircle2, Bot
} from 'lucide-react'
import HomePage from './pages/HomePage.jsx'
import VariantPage from './pages/VariantPage.jsx'
import SymptomsPage from './pages/SymptomsPage.jsx'
import DiagnosisPage from './pages/DiagnosisPage.jsx'
import ChatPage from './pages/ChatPage.jsx'
import DiseasesPage from './pages/DiseasesPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import AgentPage from './pages/AgentPage.jsx'
import AgentChatPage from './pages/AgentChatPage.jsx'
import { api } from './utils/api.js'

const NAV_ITEMS = [
  { to: '/', label: 'Home', icon: Zap, exact: true },
  { to: '/agent', label: '⚡ Agent Chat', icon: Bot },
  { to: '/variant', label: 'Variant Analysis', icon: Dna },
  { to: '/symptoms', label: 'Symptom Navigator', icon: Activity },
  { to: '/diagnosis', label: 'Diagnosis', icon: Search },
  { to: '/diseases', label: 'Disease Library', icon: BookOpen },
  { to: '/chat', label: 'AI Consultant', icon: MessageSquare },
  { to: '/dashboard', label: 'Dashboard', icon: BarChart2 },
]

function Navbar({ systemStatus, mobileOpen, setMobileOpen }) {
  const location = useLocation()

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
      background: 'rgba(8,11,16,0.92)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border)',
    }}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', height: 60, gap: 24 }}>
        {/* Logo */}
        <NavLink to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none', flexShrink: 0 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-teal))',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <Dna size={18} color="white" />
          </div>
          <span style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 18, color: 'var(--text-bright)', letterSpacing: '-0.03em' }}>
            RareNav
          </span>
          <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)', background: 'rgba(45,212,191,0.1)', border: '1px solid rgba(45,212,191,0.2)', borderRadius: 99, padding: '2px 6px' }}>
            BETA
          </span>
        </NavLink>

        {/* Desktop nav */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1, overflowX: 'auto' }} className="hide-mobile">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              style={({ isActive }) => ({
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '6px 12px', borderRadius: 6,
                textDecoration: 'none', fontSize: 13,
                fontFamily: 'var(--font-display)', fontWeight: 600,
                color: isActive ? 'var(--accent-glow)' : 'var(--text-secondary)',
                background: isActive ? 'rgba(59,130,246,0.1)' : 'transparent',
                transition: 'all 0.15s', whiteSpace: 'nowrap'
              })}
            >
              <Icon size={14} />
              {label}
            </NavLink>
          ))}
        </div>

        {/* Status indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }} className="hide-mobile">
          {systemStatus === 'ok' ? (
            <><CheckCircle2 size={13} color="var(--success)" /><span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--success)' }}>SYSTEM READY</span></>
          ) : systemStatus === 'error' ? (
            <><AlertCircle size={13} color="var(--danger)" /><span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--danger)' }}>OFFLINE</span></>
          ) : (
            <><div className="spinner" style={{ width: 12, height: 12 }} /><span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>CONNECTING</span></>
          )}
        </div>

        {/* Mobile menu */}
        <button className="btn-icon btn-ghost" style={{ marginLeft: 'auto', display: 'none' }} onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X size={18} /> : <Menu size={18} />}
        </button>
      </div>

      {/* Mobile nav dropdown */}
      {mobileOpen && (
        <div style={{ background: 'var(--bg-deep)', borderTop: '1px solid var(--border)', padding: 16 }}>
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} end={to === '/'} onClick={() => setMobileOpen(false)}
              style={({ isActive }) => ({
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '10px 12px', borderRadius: 8, marginBottom: 4,
                textDecoration: 'none', fontSize: 14,
                fontFamily: 'var(--font-display)', fontWeight: 600,
                color: isActive ? 'var(--accent-glow)' : 'var(--text-secondary)',
                background: isActive ? 'rgba(59,130,246,0.1)' : 'transparent',
              })}
            >
              <Icon size={16} />{label}
            </NavLink>
          ))}
        </div>
      )}
    </nav>
  )
}

function AppContent() {
  const [systemStatus, setSystemStatus] = useState('loading')
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    api.health()
      .then(() => setSystemStatus('ok'))
      .catch(() => setSystemStatus('error'))
  }, [])

  return (
    <div style={{ minHeight: '100vh', paddingTop: 60, position: 'relative', zIndex: 1 }}>
      <Navbar systemStatus={systemStatus} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/variant" element={<VariantPage />} />
        <Route path="/symptoms" element={<SymptomsPage />} />
        <Route path="/diagnosis" element={<DiagnosisPage />} />
        <Route path="/diseases" element={<DiseasesPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/agent" element={<AgentChatPage />} />
      </Routes>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  )
}
