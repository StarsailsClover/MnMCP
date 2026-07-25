import { motion } from 'framer-motion'
import { Boxes, KeyRound, Repeat2, Network } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

interface Feature {
  icon: LucideIcon
  index: string
  title: string
  description: string
  accent: 'mc' | 'mnw' | 'bridge'
  meta: string
}

const FEATURES: Feature[] = [
  {
    icon: Repeat2,
    index: '01',
    title: 'Protocol translation',
    description:
      'Bidirectional codec translating Minecraft Java packets into MiniWorld sessions. 82+ message types with VarInt/String support, wrapped behind a single MCPBridge entrypoint.',
    accent: 'mc',
    meta: '82+ message types',
  },
  {
    icon: Boxes,
    index: '02',
    title: 'Block mapping layer',
    description:
      '844 block mappings between MC and MNW coordinate systems. The mapping module is data-driven, so contributors can extend coverage without touching the codec.',
    accent: 'mnw',
    meta: '844 blocks',
  },
  {
    icon: KeyRound,
    index: '03',
    title: 'Dual crypto stacks',
    description:
      'XXTEA for MiniWorld and AES-CFB8 for Minecraft, isolated behind auth_mcp. Each side speaks its own dialect while the bridge stays transport-agnostic.',
    accent: 'bridge',
    meta: 'XXTEA · AES-CFB8',
  },
  {
    icon: Network,
    index: '04',
    title: 'Adapter architecture',
    description:
      'Seven modules — mapping, crypto, protocol, mc, mini, core, proxy — wired by a 6-state bridge. Swap one transport without rewriting the rest.',
    accent: 'mc',
    meta: '7 modules',
  },
]

export default function Features() {
  return (
    <section id="features" className="section-padding relative">
      <div className="container-page">
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div className="max-w-xl">
            <span className="eyebrow">Core capabilities</span>
            <h2 className="heading-lg mt-4 text-ink">
              Four layers that make cross-world play real.
            </h2>
          </div>
          <p className="max-w-md text-sm leading-relaxed text-muted">
            Each layer below is a real module you can find in the source tree —
            nothing is mocked. Together they cover codec, mapping, crypto, and
            the bidirectional bridge core.
          </p>
        </div>

        <div className="mt-16 grid gap-px overflow-hidden rounded-12 border border-line bg-line/60 md:grid-cols-2">
          {FEATURES.map((f, i) => (
            <FeatureCell key={f.index} feature={f} index={i} />
          ))}
        </div>
      </div>
    </section>
  )
}

function FeatureCell({ feature, index }: { feature: Feature; index: number }) {
  const accentColor = {
    mc: 'text-mc',
    mnw: 'text-mnw',
    bridge: 'text-bridge',
  }[feature.accent]
  const Icon = feature.icon
  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.5, delay: (index % 2) * 0.08 }}
      className="group relative bg-bg p-8 md:p-10"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <span className="inline-flex h-11 w-11 items-center justify-center rounded-10 border border-line bg-surface/60 text-ink transition-all duration-300 group-hover:border-bridge/30 group-hover:shadow-inner-glow">
            <Icon size={18} strokeWidth={1.5} />
          </span>
          <span className={`font-mono text-xs ${accentColor}`}>{feature.index}</span>
        </div>
        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted-2">
          {feature.meta}
        </span>
      </div>
      <h3 className="heading-md mt-6 text-ink">{feature.title}</h3>
      <p className="mt-3 text-sm leading-relaxed text-muted">{feature.description}</p>
      <span
        className={`mt-6 block h-px w-full bg-gradient-to-r from-transparent via-current to-transparent opacity-20 ${accentColor}`}
      />
    </motion.article>
  )
}
