import { Link } from 'react-router-dom'
import { Github } from 'lucide-react'

export default function Footer() {
  const year = new Date().getFullYear()
  return (
    <footer className="relative border-t border-line/70 bg-surface/30">
      <div className="container-page py-14">
        <div className="grid gap-10 md:grid-cols-[1.5fr_1fr_1fr]">
          <div>
            <div className="flex items-center gap-3">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-8 border border-line bg-surface">
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
              </span>
              <div className="font-display text-base font-semibold tracking-tight-2 text-ink">
                MnMCP
              </div>
            </div>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted">
              MiniWorld Connection Protocol. A pure-Python bridge translating
              Minecraft Java Edition packets into MiniWorld sessions.
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              <span className="chip">MIT License</span>
              <span className="chip">Python 3.9+</span>
              <span className="chip">v3.1 Phase8</span>
            </div>
          </div>

          <div>
            <div className="font-mono text-xs uppercase tracking-[0.2em] text-muted-2">
              Navigate
            </div>
            <ul className="mt-4 space-y-2.5 text-sm">
              <li>
                <Link to="/" className="text-muted transition-colors hover:text-ink">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/docs" className="text-muted transition-colors hover:text-ink">
                  Docs
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/NDBlockConnect/MnMCP/blob/main/CHANGELOG.md"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted transition-colors hover:text-ink"
                >
                  Changelog
                </a>
              </li>
            </ul>
          </div>

          <div>
            <div className="font-mono text-xs uppercase tracking-[0.2em] text-muted-2">
              Resources
            </div>
            <ul className="mt-4 space-y-2.5 text-sm">
              <li>
                <a
                  href="https://github.com/NDBlockConnect/MnMCP"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-muted transition-colors hover:text-ink"
                >
                  <Github size={14} /> GitHub
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/NDBlockConnect/MnMCP/blob/main/CONTRIBUTING.md"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted transition-colors hover:text-ink"
                >
                  Contributing
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/NDBlockConnect/MnMCP/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted transition-colors hover:text-ink"
                >
                  Issues
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 divider" />

        <div className="mt-6 flex flex-col items-start justify-between gap-3 text-xs text-muted-2 md:flex-row md:items-center">
          <div className="font-mono">
            © {year} NDBlockConnect · mnmcp.n0th1n3ssd0ma1n.top
          </div>
          <div className="font-mono">
            Built with React · Three.js · Vite
          </div>
        </div>
      </div>
    </footer>
  )
}
