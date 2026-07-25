import { Link, useLocation } from 'react-router-dom'
import { Github, Menu, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useUIStore } from '../store/useUIStore'

const NAV_LINKS = [
  { label: 'Home', to: '/' },
  { label: 'Docs', to: '/docs' },
]

export default function Navbar() {
  const { pathname } = useLocation()
  const { mobileMenuOpen, setMobileMenuOpen } = useUIStore()
  const [shadow, setShadow] = useState(false)

  useEffect(() => {
    const onScroll = () => setShadow(window.scrollY > 8)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    setMobileMenuOpen(false)
  }, [pathname, setMobileMenuOpen])

  return (
    <header
      className={[
        'fixed inset-x-0 top-0 z-50 transition-all duration-300',
        shadow || mobileMenuOpen
          ? 'border-b border-line/70 bg-bg/85 backdrop-blur-xl'
          : 'border-b border-transparent bg-transparent',
      ].join(' ')}
    >
      <div className="container-page flex h-16 items-center justify-between">
        <Link to="/" className="group flex items-center gap-3" aria-label="MnMCP home">
          <Logo />
          <div className="flex flex-col leading-none">
            <span className="font-display text-[15px] font-semibold tracking-tight-2 text-ink">
              MnMCP
            </span>
            <span className="mt-0.5 font-mono text-[10px] uppercase tracking-[0.2em] text-muted-2">
              miniworld connection protocol
            </span>
          </div>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((l) => {
            const active = pathname === l.to
            return (
              <Link
                key={l.to}
                to={l.to}
                className={[
                  'relative px-4 py-2 text-sm transition-colors',
                  active ? 'text-ink' : 'text-muted hover:text-ink',
                ].join(' ')}
              >
                {l.label}
                {active && (
                  <span className="absolute inset-x-4 -bottom-px h-px bg-gradient-to-r from-transparent via-bridge to-transparent" />
                )}
              </Link>
            )
          })}
        </nav>

        <div className="flex items-center gap-2">
          <a
            href="https://github.com/NDBlockConnect/MnMCP"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden h-9 items-center gap-2 rounded-8 border border-line/70 bg-surface/50 px-3 text-xs text-muted transition-colors hover:border-bridge/30 hover:text-ink sm:inline-flex"
            aria-label="GitHub repository"
          >
            <Github size={14} />
            <span className="font-mono">NDBlockConnect/MnMCP</span>
          </a>
          <a
            href="https://github.com/NDBlockConnect/MnMCP"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-9 w-9 items-center justify-center rounded-8 border border-line/70 bg-surface/50 text-muted transition-colors hover:text-ink sm:hidden"
            aria-label="GitHub repository"
          >
            <Github size={16} />
          </a>
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="inline-flex h-9 w-9 items-center justify-center rounded-8 border border-line/70 bg-surface/50 text-muted md:hidden"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={16} /> : <Menu size={16} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="border-t border-line/70 bg-bg/95 backdrop-blur-xl md:hidden">
          <div className="container-page flex flex-col py-3">
            {NAV_LINKS.map((l) => {
              const active = pathname === l.to
              return (
                <Link
                  key={l.to}
                  to={l.to}
                  className={[
                    'border-l-2 px-3 py-3 text-sm',
                    active
                      ? 'border-bridge text-ink'
                      : 'border-transparent text-muted',
                  ].join(' ')}
                >
                  {l.label}
                </Link>
              )
            })}
          </div>
        </div>
      )}
    </header>
  )
}

function Logo() {
  return (
    <span className="relative inline-flex h-8 w-8 items-center justify-center rounded-8 border border-line bg-surface">
      <svg viewBox="0 0 32 32" className="h-5 w-5">
        <g transform="translate(4 10) rotate(-8)">
          <rect x="0" y="0" width="7" height="7" rx="1" fill="#3ddc97" />
        </g>
        <g transform="translate(20 14) rotate(8)">
          <rect x="0" y="0" width="7" height="7" rx="1" fill="#f5b942" />
        </g>
        <path
          d="M11 15 Q15 11 20 17"
          stroke="#22d3ee"
          strokeWidth="1.2"
          fill="none"
          strokeLinecap="round"
        />
      </svg>
      <span className="absolute inset-0 rounded-8 ring-1 ring-inset ring-white/5" />
    </span>
  )
}
