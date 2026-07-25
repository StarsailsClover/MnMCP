import { motion } from 'framer-motion'
import { useState } from 'react'

interface Layer {
  no: string
  name: string
  role: string
  modules: { name: string; path: string }[]
  accent: 'mc' | 'bridge' | 'mnw' | 'ink'
}

const LAYERS: Layer[] = [
  {
    no: 'L1',
    name: 'Client layer',
    role: 'Minecraft Java Edition and MiniWorld clients that the bridge connects.',
    modules: [
      { name: 'Minecraft Java', path: 'TCP · port 25565' },
      { name: 'MiniWorld 1.55+', path: 'UDP · RakNet' },
    ],
    accent: 'mc',
  },
  {
    no: 'L2',
    name: 'Adapter layer',
    role: 'Protocol clients speaking the native dialect of each side.',
    modules: [
      { name: 'mcp_mc', path: 'src/mcp_mc/client.py' },
      { name: 'mcp_mini', path: 'src/mcp_mini/client.py' },
    ],
    accent: 'mnw',
  },
  {
    no: 'L3',
    name: 'Protocol layer',
    role: 'Codec, encryption, and block mapping shared across transports.',
    modules: [
      { name: 'mcp_protocol', path: 'codec · packet · msgcode_registry' },
      { name: 'mcp_crypto', path: 'xxtea_mcp · auth_mcp' },
      { name: 'mcp_mapping', path: 'blocks_integrated.py' },
    ],
    accent: 'bridge',
  },
  {
    no: 'L4',
    name: 'Core layer',
    role: 'Bidirectional bridge with 6-state machine, plus HTTP proxy and RakNet gateway.',
    modules: [
      { name: 'mcp_core', path: 'src/mcp_core/bridge.py' },
      { name: 'mcp_proxy', path: 'gateway · http_proxy' },
    ],
    accent: 'ink',
  },
]

export default function Architecture() {
  const [active, setActive] = useState<number>(2)
  return (
    <section id="architecture" className="section-padding relative">
      <div className="container-page">
        <div className="grid gap-12 md:grid-cols-[1fr_1.4fr] md:gap-20">
          <div>
            <span className="eyebrow">Architecture</span>
            <h2 className="heading-lg mt-4 text-ink">
              Four layers.
              <br />
              One bridge.
            </h2>
            <p className="lead mt-6">
              The architecture is intentionally modular: each layer owns a
              single responsibility, and the core layer orchestrates adapters
              instead of knowing about packets directly.
            </p>
            <div className="mt-8 inline-flex items-center gap-3 rounded-10 border border-line bg-surface/40 px-4 py-3">
              <span className="h-2 w-2 rounded-full bg-bridge animate-pulse-soft" />
              <span className="font-mono text-xs text-muted">
                Hover or tap a strip to inspect
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-3">
            {LAYERS.map((l, i) => (
              <LayerRow
                key={l.no}
                layer={l}
                active={active === i}
                onHover={() => setActive(i)}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

function LayerRow({
  layer,
  active,
  onHover,
}: {
  layer: Layer
  active: boolean
  onHover: () => void
}) {
  const accentColor = {
    mc: '#3ddc97',
    mnw: '#f5b942',
    bridge: '#22d3ee',
    ink: '#e7ecf3',
  }[layer.accent]

  return (
    <motion.div
      onHoverStart={onHover}
      onClick={onHover}
      animate={{
        borderColor: active ? `${accentColor}55` : '#1c2230',
        backgroundColor: active ? '#0e1218' : 'rgba(14,18,24,0.4)',
      }}
      transition={{ duration: 0.25 }}
      className="cursor-pointer overflow-hidden rounded-12 border bg-surface/40"
    >
      <div className="flex items-stretch">
        <div
          className="w-1 shrink-0"
          style={{ backgroundColor: accentColor, opacity: active ? 1 : 0.4 }}
        />
        <div className="flex-1 p-5 md:p-6">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <span className="font-mono text-xs text-muted-2">{layer.no}</span>
              <h3 className="font-display text-lg font-medium tracking-tight-2 text-ink">
                {layer.name}
              </h3>
            </div>
            <span
              className="font-mono text-[10px] uppercase tracking-[0.2em]"
              style={{ color: active ? accentColor : '#5a6377' }}
            >
              {layer.modules.length} modules
            </span>
          </div>
          <p className="mt-2 text-sm text-muted">{layer.role}</p>
          <motion.div
            initial={false}
            animate={{
              height: active ? 'auto' : 0,
              opacity: active ? 1 : 0,
              marginTop: active ? 14 : 0,
            }}
            transition={{ duration: 0.28 }}
            className="overflow-hidden"
          >
            <ul className="flex flex-wrap gap-2">
              {layer.modules.map((m) => (
                <li
                  key={m.name}
                  className="inline-flex items-center gap-2 rounded-md border border-line/70 bg-bg/60 px-2.5 py-1 font-mono text-xs text-muted"
                >
                  <span className="text-ink">{m.name}</span>
                  <span className="text-muted-2">·</span>
                  <span className="text-muted-2">{m.path}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        </div>
      </div>
    </motion.div>
  )
}
