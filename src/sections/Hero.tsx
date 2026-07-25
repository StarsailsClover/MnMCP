import { Suspense, lazy } from 'react'
import { ArrowRight, BookOpen, Terminal } from 'lucide-react'
import { Link } from 'react-router-dom'

const HeroScene = lazy(() => import('../three/HeroScene'))

export default function Hero() {
  return (
    <section className="relative min-h-[100svh] w-full overflow-hidden">
      {/* WebGL background */}
      <div className="absolute inset-0">
        <Suspense fallback={<HeroFallback />}>
          <HeroScene className="absolute inset-0 h-full w-full" />
        </Suspense>
      </div>

      {/* Gradient overlays for text legibility */}
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-bg/40 via-transparent to-bg/90" />
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-bg/70 via-transparent to-bg/40" />

      {/* Scan line decoration */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden opacity-40">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-bridge/30 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-bridge/30 to-transparent" />
      </div>

      <div className="container-page relative flex min-h-[100svh] flex-col justify-end pb-20 pt-32 md:pb-24">
        <div className="max-w-3xl">
          <div className="flex flex-wrap items-center gap-2.5">
            <span className="chip border-bridge/30 bg-bridge/5 text-bridge">
              <span className="h-1.5 w-1.5 rounded-full bg-bridge animate-pulse-soft" />
              Victoria v3.1 Phase8 Stable
            </span>
            <span className="chip">Pure Python</span>
            <span className="chip">MIT License</span>
          </div>

          <h1 className="heading-xl mt-6 text-ink">
            A voxel bridge between
            <br />
            <span className="text-mc">Minecraft</span>
            <span className="mx-3 text-muted-2">↔</span>
            <span className="text-mnw">MiniWorld</span>
          </h1>

          <p className="lead mt-6 max-w-xl">
            MnMCP is a protocol bridge that lets Minecraft Java Edition clients
            join MiniWorld servers. Pure-Python translation across TCP and
            UDP/RakNet, with 844 block mappings and 82+ message types.
          </p>

          <div className="mt-9 flex flex-wrap items-center gap-3">
            <Link to="/docs" className="btn btn-primary">
              <BookOpen size={16} />
              Read the docs
              <ArrowRight size={14} />
            </Link>
            <a
              href="https://github.com/NDBlockConnect/MnMCP"
              target="_blank"
              rel="noopener noreferrer"
              className="btn"
            >
              <Terminal size={16} />
              View on GitHub
            </a>
          </div>

          {/* Quick stats */}
          <dl className="mt-14 grid max-w-2xl grid-cols-2 gap-x-6 gap-y-5 border-t border-line/60 pt-8 sm:grid-cols-4">
            <Stat label="Block mappings" value="844" accent="mc" />
            <Stat label="Message types" value="82+" accent="bridge" />
            <Stat label="Unit tests" value="33+" accent="mnw" />
            <Stat label="Languages" value="Py · Go · Rs · TS" accent="ink" />
          </dl>
        </div>
      </div>

      {/* Scroll hint */}
      <div className="pointer-events-none absolute bottom-6 left-1/2 hidden -translate-x-1/2 flex-col items-center gap-2 md:flex">
        <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-muted-2">
          scroll
        </span>
        <span className="h-8 w-px bg-gradient-to-b from-bridge/40 to-transparent" />
      </div>
    </section>
  )
}

function Stat({
  label,
  value,
  accent,
}: {
  label: string
  value: string
  accent: 'mc' | 'mnw' | 'bridge' | 'ink'
}) {
  const color = {
    mc: 'text-mc',
    mnw: 'text-mnw',
    bridge: 'text-bridge',
    ink: 'text-ink',
  }[accent]
  return (
    <div>
      <dd className={`font-display text-2xl font-medium tracking-tight-2 ${color}`}>
        {value}
      </dd>
      <dt className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-muted-2">
        {label}
      </dt>
    </div>
  )
}

function HeroFallback() {
  return (
    <div className="absolute inset-0 bg-gradient-to-b from-[#0a0f17] to-[#07090d]">
      <div className="absolute left-1/2 top-1/2 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full bg-bridge/10 blur-3xl" />
    </div>
  )
}
