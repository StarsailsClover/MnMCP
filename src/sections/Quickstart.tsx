import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import CodeBlock from '../components/CodeBlock'

interface Step {
  no: string
  title: string
  description: string
  code?: string
  lang?: string
  filename?: string
}

const STEPS: Step[] = [
  {
    no: '01',
    title: 'Clone & install',
    description: 'Pull the repo and install Python dependencies.',
    code: `git clone https://github.com/NDBlockConnect/MnMCP.git
cd MnMCP/mnmcp-v3-integrated
pip install -r requirements.txt`,
    lang: 'bash',
    filename: 'terminal',
  },
  {
    no: '02',
    title: 'Verify the install',
    description: 'Run the verification script to confirm the bridge is wired correctly.',
    code: `python verify_mn3.py`,
    lang: 'bash',
    filename: 'verify',
  },
  {
    no: '03',
    title: 'Start the bridge',
    description: 'Configure MCPBridge and run an async loop. The example below is the minimal entrypoint.',
    code: `import asyncio
from mcp_core import MCPBridge, MCPBridgeConfig

async def main():
    config = MCPBridgeConfig(
        mc_host="localhost",
        mc_port=25565,
        mc_username="BridgePlayer",
        mnw_uin=123456,
        mnw_passwd="your_password",
    )
    bridge = MCPBridge(config)
    if await bridge.start():
        print("Bridge started")
        while bridge.is_running:
            await asyncio.sleep(1)
    await bridge.stop()

asyncio.run(main())`,
    lang: 'python',
    filename: 'bridge.py',
  },
  {
    no: '04',
    title: 'Run the test suite',
    description: '33+ unit tests cover bridge, crypto, mapping, and both clients.',
    code: `python -m pytest tests/ -v
# Coverage report
python -m pytest --cov=src --cov-report=html`,
    lang: 'bash',
    filename: 'tests',
  },
]

export default function Quickstart() {
  return (
    <section id="quickstart" className="section-padding relative">
      <div className="container-page">
        <div className="grid gap-12 md:grid-cols-[1fr_1.3fr] md:gap-20">
          <div>
            <span className="eyebrow">Quickstart</span>
            <h2 className="heading-lg mt-4 text-ink">
              From clone to bridge in four steps.
            </h2>
            <p className="lead mt-6">
              No external services required. Pure Python, MIT-licensed, runs on
              any machine with Python 3.9 or newer.
            </p>
            <a
              href="https://github.com/NDBlockConnect/MnMCP/blob/main/docs/QUICKSTART.md"
              target="_blank"
              rel="noopener noreferrer"
              className="btn mt-8"
            >
              Full quickstart guide
              <ArrowRight size={14} />
            </a>
          </div>

          <ol className="relative flex flex-col gap-8 border-l border-line/60 pl-8">
            {STEPS.map((s, i) => (
              <StepRow key={s.no} step={s} index={i} />
            ))}
          </ol>
        </div>
      </div>
    </section>
  )
}

function StepRow({ step, index }: { step: Step; index: number }) {
  return (
    <motion.li
      initial={{ opacity: 0, x: 12 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.4, delay: index * 0.08 }}
      className="relative"
    >
      <span className="absolute -left-[42px] top-0 flex h-7 w-7 items-center justify-center rounded-full border border-bridge/40 bg-bg font-mono text-[10px] text-bridge">
        {step.no}
      </span>
      <h3 className="font-display text-xl font-medium tracking-tight-2 text-ink">
        {step.title}
      </h3>
      <p className="mt-2 text-sm leading-relaxed text-muted">{step.description}</p>
      {step.code && (
        <div className="mt-4">
          <CodeBlock
            code={step.code}
            lang={step.lang}
            filename={step.filename}
            showLineNumbers={step.lang === 'python'}
          />
        </div>
      )}
    </motion.li>
  )
}
