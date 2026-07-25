import { motion } from 'framer-motion'
import { Boxes, Gamepad2 } from 'lucide-react'

interface Game {
  name: string
  tagline: string
  transport: string
  protocol: string
  accent: 'mc' | 'mnw'
  icon: typeof Boxes
}

const GAMES: Game[] = [
  {
    name: 'Minecraft Java Edition',
    tagline: 'Connecting client. Speaks MC protocol over TCP.',
    transport: 'TCP',
    protocol: 'MC 1.20.6 · protocol 766',
    accent: 'mc',
    icon: Boxes,
  },
  {
    name: 'MiniWorld',
    tagline: 'Host server. Speaks MNW protocol over UDP/RakNet.',
    transport: 'UDP / RakNet',
    protocol: 'MiniWorld 1.55.0',
    accent: 'mnw',
    icon: Gamepad2,
  },
]

export default function Games() {
  return (
    <section id="games" className="section-padding relative">
      <div className="container-page">
        <div className="max-w-2xl">
          <span className="eyebrow">Supported games</span>
          <h2 className="heading-lg mt-4 text-ink">
            Two worlds. Two protocols. One bridge.
          </h2>
          <p className="lead mt-6">
            MnMCP focuses on a single, well-tested pair: Minecraft Java Edition
            and MiniWorld. Other games can be added by writing a new adapter
            module — the codec and bridge stay the same.
          </p>
        </div>

        <div className="mt-14 grid items-stretch gap-4 md:grid-cols-[1fr_auto_1fr]">
          {GAMES.map((g, i) => (
            <GamePanel key={g.name} game={g} index={i} />
          ))}
          <BridgeAnimation />
        </div>

        <div className="mt-8 grid gap-3 sm:grid-cols-3">
          <NoteCard
            label="Self-hosted"
            value="Run locally"
            description="Python 3.9+ on Windows, macOS, or Linux. No external services required for v3.2."
          />
          <NoteCard
            label="Bidirectional"
            value="Forward & reverse"
            description="Packets flow in both directions through MCPBridge with state tracking."
          />
          <NoteCard
            label="Extensible"
            value="Add a game"
            description="Implement mcp_<game>.client and register it with the bridge core."
          />
        </div>
      </div>
    </section>
  )
}

function GamePanel({ game, index }: { game: Game; index: number }) {
  const Icon = game.icon
  const accent = game.accent === 'mc' ? '#3ddc97' : '#f5b942'
  return (
    <motion.article
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5, delay: index * 0.12 }}
      className="relative overflow-hidden rounded-12 border border-line bg-surface/40 p-7"
    >
      <div
        className="absolute -right-10 -top-10 h-40 w-40 rounded-full blur-3xl"
        style={{ backgroundColor: accent, opacity: 0.08 }}
      />
      <div className="flex items-center justify-between">
        <span
          className="inline-flex h-12 w-12 items-center justify-center rounded-10 border"
          style={{ borderColor: `${accent}40`, backgroundColor: `${accent}10` }}
        >
          <Icon size={20} strokeWidth={1.5} color={accent} />
        </span>
        <span
          className="font-mono text-[10px] uppercase tracking-[0.25em]"
          style={{ color: accent }}
        >
          side {index === 0 ? 'A' : 'B'}
        </span>
      </div>
      <h3 className="mt-6 font-display text-xl font-medium tracking-tight-2 text-ink">
        {game.name}
      </h3>
      <p className="mt-2 text-sm leading-relaxed text-muted">{game.tagline}</p>

      <dl className="mt-6 space-y-2.5 border-t border-line/60 pt-5">
        <div className="flex items-center justify-between">
          <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted-2">
            transport
          </dt>
          <dd className="font-mono text-xs text-ink">{game.transport}</dd>
        </div>
        <div className="flex items-center justify-between">
          <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted-2">
            protocol
          </dt>
          <dd className="font-mono text-xs text-muted">{game.protocol}</dd>
        </div>
      </dl>
    </motion.article>
  )
}

function BridgeAnimation() {
  const pathForward = 'M0 110 Q60 50 120 110'
  const pathBackward = 'M0 110 Q60 170 120 110'
  const colors = ['#3ddc97', '#22d3ee', '#22d3ee', '#f5b942', '#22d3ee']
  return (
    <div className="relative hidden items-center justify-center md:flex">
      <svg width="120" height="220" viewBox="0 0 120 220" className="overflow-visible">
        <defs>
          <linearGradient id="bridgeGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#3ddc97" />
            <stop offset="50%" stopColor="#22d3ee" />
            <stop offset="100%" stopColor="#f5b942" />
          </linearGradient>
          <path id="bridgeFwd" d={pathForward} fill="none" />
          <path id="bridgeBwd" d={pathBackward} fill="none" />
        </defs>
        <path d={pathForward} stroke="url(#bridgeGrad)" strokeWidth="1.5" fill="none" opacity="0.6" />
        <path
          d={pathBackward}
          stroke="url(#bridgeGrad)"
          strokeWidth="1.5"
          fill="none"
          opacity="0.3"
          strokeDasharray="4 4"
        />
        {[0, 0.5, 1, 1.5, 2].map((delay, i) => (
          <circle key={`f${i}`} r="3" fill={colors[i]}>
            <animateMotion
              dur="2.6s"
              repeatCount="indefinite"
              begin={`${delay}s`}
              keyPoints="0;1"
              keyTimes="0;1"
            >
              <mpath href="#bridgeFwd" />
            </animateMotion>
          </circle>
        ))}
        {[0.25, 0.75, 1.25].map((delay, i) => (
          <circle key={`b${i}`} r="2.2" fill="#9ad8ff" opacity="0.7">
            <animateMotion
              dur="3.2s"
              repeatCount="indefinite"
              begin={`${delay}s`}
              keyPoints="1;0"
              keyTimes="0;1"
            >
              <mpath href="#bridgeBwd" />
            </animateMotion>
          </circle>
        ))}
        <text
          x="60"
          y="115"
          textAnchor="middle"
          className="font-mono"
          fontSize="9"
          fill="#8b94a7"
          letterSpacing="2"
        >
          BRIDGE
        </text>
      </svg>
    </div>
  )
}

function NoteCard({
  label,
  value,
  description,
}: {
  label: string
  value: string
  description: string
}) {
  return (
    <div className="rounded-10 border border-line bg-surface/30 p-5">
      <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted-2">
        {label}
      </div>
      <div className="mt-1.5 font-display text-base font-medium tracking-tight-2 text-ink">
        {value}
      </div>
      <p className="mt-2 text-xs leading-relaxed text-muted">{description}</p>
    </div>
  )
}
