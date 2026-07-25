import { motion } from 'framer-motion'
import { ArrowUpRight, GitFork, Heart } from 'lucide-react'

export default function Org() {
  return (
    <section id="org" className="section-padding relative">
      <div className="container-page">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.6 }}
          className="relative overflow-hidden rounded-16 border border-line bg-gradient-to-b from-surface/60 to-bg p-10 md:p-16"
        >
          {/* Decorative grid + glows */}
          <div className="pointer-events-none absolute inset-0 opacity-50">
            <div className="absolute -left-20 -top-20 h-72 w-72 rounded-full bg-mc/10 blur-3xl" />
            <div className="absolute -bottom-20 -right-20 h-80 w-80 rounded-full bg-mnw/10 blur-3xl" />
            <div className="absolute left-1/2 top-1/2 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full bg-bridge/8 blur-3xl" />
          </div>

          <div className="relative grid gap-10 md:grid-cols-[1.4fr_1fr] md:items-center">
            <div>
              <span className="eyebrow">Open source · MIT</span>
              <h2 className="heading-lg mt-4 text-ink">
                Built in the open.
                <br />
                Ready for contributors.
              </h2>
              <p className="lead mt-6 max-w-xl">
                MnMCP lives under the NDBlockConnect organization. The codebase
                is small enough to read in one sitting and structured so new
                adapters, mappings, and crypto paths can land without
                destabilizing the bridge core.
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-3">
                <a
                  href="https://github.com/NDBlockConnect/MnMCP"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary"
                >
                  <ArrowUpRight size={16} />
                  Visit the repository
                </a>
                <a
                  href="https://github.com/NDBlockConnect/MnMCP/blob/main/CONTRIBUTING.md"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn"
                >
                  <Heart size={14} />
                  Contributing guide
                </a>
              </div>
            </div>

            <div className="grid gap-3">
              <StatCard
                icon={<GitFork size={14} />}
                label="Repository"
                value="NDBlockConnect/MnMCP"
                href="https://github.com/NDBlockConnect/MnMCP"
              />
              <StatCard
                icon={<span className="font-mono text-[10px]">v3.1</span>}
                label="Current release"
                value="Victoria Phase8 Stable"
                href="https://github.com/NDBlockConnect/MnMCP/releases"
              />
              <StatCard
                icon={<span className="font-mono text-[10px]">MIT</span>}
                label="License"
                value="Permissive · commercial-friendly"
                href="https://github.com/NDBlockConnect/MnMCP/blob/main/LICENSE"
              />
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

function StatCard({
  icon,
  label,
  value,
  href,
}: {
  icon: React.ReactNode
  label: string
  value: string
  href: string
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex items-center justify-between gap-4 rounded-10 border border-line bg-bg/60 px-4 py-3.5 transition-colors hover:border-bridge/30"
    >
      <div className="flex items-center gap-3">
        <span className="inline-flex h-7 w-7 items-center justify-center rounded-md border border-line bg-surface/60 text-muted">
          {icon}
        </span>
        <div>
          <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted-2">
            {label}
          </div>
          <div className="mt-0.5 text-sm font-medium text-ink">{value}</div>
        </div>
      </div>
      <ArrowUpRight
        size={14}
        className="text-muted-2 transition-all group-hover:-translate-y-0.5 group-hover:text-bridge"
      />
    </a>
  )
}
