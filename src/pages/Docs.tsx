import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft, ExternalLink } from 'lucide-react'
import { Link } from 'react-router-dom'
import CodeBlock from '../components/CodeBlock'

interface DocSection {
  id: string
  label: string
}

const SECTIONS: DocSection[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'architecture', label: 'Layered architecture' },
  { id: 'components', label: 'Core components' },
  { id: 'dataflow', label: 'Data flow' },
  { id: 'extensibility', label: 'Extensibility' },
  { id: 'security', label: 'Security design' },
]

export default function Docs() {
  const [active, setActive] = useState('overview')

  return (
    <div className="pt-20">
      <div className="container-page grid gap-12 py-16 md:grid-cols-[220px_1fr] md:py-20">
        <aside className="md:sticky md:top-24 md:self-start">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-sm text-muted transition-colors hover:text-ink"
          >
            <ArrowLeft size={14} />
            Back to home
          </Link>
          <div className="mt-6 font-mono text-[10px] uppercase tracking-[0.25em] text-muted-2">
            On this page
          </div>
          <nav className="mt-3 flex flex-col gap-0.5">
            {SECTIONS.map((s) => (
              <a
                key={s.id}
                href={`#${s.id}`}
                onClick={() => setActive(s.id)}
                className={[
                  'border-l-2 px-3 py-2 text-sm transition-colors',
                  active === s.id
                    ? 'border-bridge text-ink'
                    : 'border-transparent text-muted hover:text-ink',
                ].join(' ')}
              >
                {s.label}
              </a>
            ))}
          </nav>
          <a
            href="https://github.com/NDBlockConnect/MnMCP/blob/main/README.md"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-6 inline-flex items-center gap-1.5 text-xs text-muted transition-colors hover:text-bridge"
          >
            README on GitHub
            <ExternalLink size={11} />
          </a>
        </aside>

        <article className="max-w-3xl">
          <header>
            <span className="eyebrow">Documentation</span>
            <h1 className="heading-lg mt-4 text-ink">
              MnMCP, end to end.
            </h1>
            <p className="lead mt-5">
              A condensed technical reference for the protocol bridge: what each
              module does, how packets move, and where to extend it. For full
              inline docs, see the source tree.
            </p>
          </header>

          <Section id="overview" title="Overview">
            <p>
              MnMCP — the <strong>MiniWorld Connection Protocol</strong> — is a
              protocol bridge that lets Minecraft Java Edition clients connect to
              MiniWorld servers. It is implemented in pure Python with full type
              annotations, async/await, and a small, readable core.
            </p>
            <p>
              The current stable release is{' '}
              <code className="text-mc">Victoria v3.1 Phase8 Stable</code>,
              covering a 6-state bridge core, 844 block mappings, 82+ message
              types, dual encryption stacks, and a 33+ test suite.
            </p>
          </Section>

          <Section id="architecture" title="Layered architecture">
            <p>
              Four layers, each with a single responsibility. Packets flow
              top-down on send and bottom-up on receive, with the core layer
              orchestrating adapter calls.
            </p>
            <CodeBlock
              lang="text"
              filename="layers.txt"
              showLineNumbers
              code={`L1  Client layer
      Minecraft Java  ·  TCP, port 25565
      MiniWorld       ·  UDP / RakNet
L2  Adapter layer
      mcp_mc    ·  MC protocol client
      mcp_mini  ·  MNW protocol client
L3  Protocol layer
      mcp_protocol  ·  codec + packets + registry
      mcp_crypto    ·  XXTEA (MNW) + AES-CFB8 (MC)
      mcp_mapping   ·  844 block mappings
L4  Core layer
      mcp_core   ·  bridge with 6-state machine
      mcp_proxy  ·  HTTP proxy + RakNet gateway`}
            />
          </Section>

          <Section id="components" title="Core components">
            <ComponentRow
              name="mcp_mapping"
              path="src/mcp_mapping/blocks_integrated.py"
              description="844 block mappings between MC and MNW coordinate systems. Data-driven so contributors can extend coverage without touching the codec."
            />
            <ComponentRow
              name="mcp_crypto"
              path="src/mcp_crypto/ · xxtea_mcp.py · auth_mcp.py"
              description="Dual encryption stacks. XXTEA for MiniWorld and AES-CFB8 for Minecraft, isolated behind auth_mcp so each side speaks only its own dialect."
            />
            <ComponentRow
              name="mcp_protocol"
              path="src/mcp_protocol/ · codec.py · packet.py · msgcode_registry.py"
              description="Protocol codec with VarInt/String support and 82+ registered message types. Packets are decoded once and re-encoded per destination."
            />
            <ComponentRow
              name="mcp_mc"
              path="src/mcp_mc/ · client.py · packet_handler.py · protocol/"
              description="Minecraft Java protocol client. TCP transport with handshake, encryption, and packet handling."
            />
            <ComponentRow
              name="mcp_mini"
              path="src/mcp_mini/ · client.py"
              description="MiniWorld protocol client. UDP/RakNet transport with frame assembly and the MNW message codec."
            />
            <ComponentRow
              name="mcp_core"
              path="src/mcp_core/ · bridge.py"
              description="Bidirectional bridge with a 6-state state machine. Owns the lifecycle of both adapters and the routing table between them."
            />
            <ComponentRow
              name="mcp_proxy"
              path="src/mcp_proxy/ · gateway.py · http_proxy.py"
              description="HTTP proxy and RakNet gateway used for local testing and routing traffic toward the fake API / real MiniWorld endpoints."
            />
          </Section>

          <Section id="dataflow" title="Data flow">
            <p>
              Packets enter through one adapter, get decoded by the protocol
              layer, are mapped across the block ID table, get re-encoded for
              the destination dialect, and exit through the opposite adapter.
              The bridge core tracks state on both sides.
            </p>
            <CodeBlock
              lang="text"
              filename="dataflow.txt"
              showLineNumbers
              code={`Minecraft Client
     |  TCP (MC protocol)
     v
MCPMinecraftClient  ──►  MCPBridge
                              |  decode + map + re-encode
                              v
                         MCPMiniClient
                              |  UDP / RakNet (MNW protocol)
                              v
                         MiniWorld Server`}
            />
          </Section>

          <Section id="extensibility" title="Extensibility">
            <p>
              Adding a new game is a bounded, mechanical task:
            </p>
            <ol className="ml-4 list-decimal space-y-2 text-muted">
              <li>Implement <code>mcp_&lt;game&gt;/client.py</code> with the native transport and codec.</li>
              <li>Register message types in <code>mcp_protocol/msgcode_registry.py</code>.</li>
              <li>Add block mappings to <code>mcp_mapping/</code> if applicable.</li>
              <li>Wire the new adapter into <code>MCPBridge</code> alongside the existing ones.</li>
            </ol>
            <p className="mt-3">
              Reference implementations exist in Go, Rust, and TypeScript under{' '}
              <code>src/go/</code>, <code>src/rust/</code>, and{' '}
              <code>src/typescript/</code> respectively, useful as ports or
              scaffolds for non-Python environments.
            </p>
          </Section>

          <Section id="security" title="Security design">
            <p>
              The bridge isolates each side's crypto behind{' '}
              <code>auth_mcp</code>. Credentials and sensitive material are kept
              in environment variables or local config files ignored by git —
              the public repo contains no keys, tokens, or production endpoints.
            </p>
            <div className="mt-4 rounded-10 border border-mnw/30 bg-mnw/5 p-4">
              <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-mnw">
                Known limitations
              </div>
              <p className="mt-2 text-sm text-muted">
                Per the project release notes, block parsing is not fully
                implemented and item / entity sync is still pending. The bridge
                currently covers protocol translation, encryption, and block
                mapping; gameplay-level sync is in progress.
              </p>
            </div>
          </Section>
        </article>
      </div>
    </div>
  )
}

function Section({
  id,
  title,
  children,
}: {
  id: string
  title: string
  children: React.ReactNode
}) {
  return (
    <motion.section
      id={id}
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.4 }}
      className="mt-14 scroll-mt-24 border-t border-line/60 pt-10 first:mt-0 first:border-0 first:pt-0"
    >
      <h2 className="heading-md text-ink">{title}</h2>
      <div className="mt-4 space-y-4 text-[15px] leading-relaxed text-muted">
        {children}
      </div>
    </motion.section>
  )
}

function ComponentRow({
  name,
  path,
  description,
}: {
  name: string
  path: string
  description: string
}) {
  return (
    <div className="rounded-10 border border-line bg-surface/30 p-5">
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <code className="text-bridge">{name}</code>
        <code className="text-xs text-muted-2">{path}</code>
      </div>
      <p className="mt-2 text-sm leading-relaxed text-muted">{description}</p>
    </div>
  )
}
