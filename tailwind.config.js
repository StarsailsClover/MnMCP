/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Surface system
        bg: '#07090d',
        surface: '#0e1218',
        'surface-2': '#131823',
        line: '#1c2230',
        'line-soft': '#161b27',
        // Brand accents
        mc: '#3ddc97',        // Minecraft side - emerald
        mnw: '#f5b942',       // MiniWorld side - amber
        bridge: '#22d3ee',    // data stream - cyan
        // Text
        ink: '#e7ecf3',
        muted: '#8b94a7',
        'muted-2': '#5a6377',
      },
      fontFamily: {
        display: ['Unbounded', 'system-ui', 'sans-serif'],
        sans: ['Manrope', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        '8': '8px',
        '10': '10px',
        '12': '12px',
      },
      maxWidth: {
        '8xl': '88rem',
      },
      letterSpacing: {
        'tight-2': '-0.022em',
        'tight-3': '-0.035em',
      },
      boxShadow: {
        'inner-glow': 'inset 0 0 0 1px rgba(255,255,255,0.04), inset 0 0 24px rgba(34,211,238,0.05)',
        'card-hover': '0 1px 0 0 rgba(255,255,255,0.04), 0 0 0 1px rgba(34,211,238,0.12), 0 24px 60px -24px rgba(34,211,238,0.18)',
      },
      keyframes: {
        'pulse-soft': {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '1' },
        },
        'scan': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        'drift': {
          '0%, 100%': { transform: 'translate3d(0,0,0)' },
          '50%': { transform: 'translate3d(0,-6px,0)' },
        },
      },
      animation: {
        'pulse-soft': 'pulse-soft 2.4s ease-in-out infinite',
        'scan': 'scan 6s linear infinite',
        'drift': 'drift 8s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
