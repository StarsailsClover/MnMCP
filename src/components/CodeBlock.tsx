import { useState } from 'react'
import { Check, Copy } from 'lucide-react'

interface CodeBlockProps {
  code: string
  lang?: string
  filename?: string
  showLineNumbers?: boolean
}

export default function CodeBlock({
  code,
  lang = 'bash',
  filename,
  showLineNumbers = false,
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false)
  const lines = code.replace(/\n$/, '').split('\n')

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    } catch {
      // noop
    }
  }

  return (
    <div className="group relative overflow-hidden rounded-10 border border-line bg-[#0a0d12]">
      <div className="flex items-center justify-between border-b border-line/70 bg-surface/40 px-4 py-2.5">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]/70" />
          {filename && (
            <span className="ml-3 font-mono text-xs text-muted-2">{filename}</span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted-2">
            {lang}
          </span>
          <button
            type="button"
            onClick={copy}
            className="inline-flex items-center gap-1.5 rounded-md border border-line/70 bg-surface/60 px-2 py-1 text-xs text-muted transition-colors hover:text-ink"
            aria-label="Copy code"
          >
            {copied ? (
              <>
                <Check size={12} className="text-mc" />
                <span className="text-mc">Copied</span>
              </>
            ) : (
              <>
                <Copy size={12} />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>
      <pre className="overflow-x-auto px-4 py-4 text-[13px] leading-relaxed">
        <code className="font-mono text-ink/90">
          {showLineNumbers ? (
            lines.map((line, i) => (
              <div key={i} className="flex">
                <span className="mr-4 inline-block w-6 select-none text-right text-muted-2">
                  {i + 1}
                </span>
                <span className="whitespace-pre">{line || ' '}</span>
              </div>
            ))
          ) : (
            code.replace(/\n$/, '')
          )}
        </code>
      </pre>
    </div>
  )
}
