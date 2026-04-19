import type { Config } from 'tailwindcss';

export default {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    theme: {
        extend: {
            colors: {
                base: '#0a0e1a',
                surface: '#111827',
                elevated: '#1a2235',
                border: '#1e2d45',
                'border-active': '#2a4070',
                'text-primary': '#e8edf5',
                'text-secondary': '#7c8fa8',
                'text-muted': '#4a5568',
                'accent-amber': '#f59e0b',
                'accent-amber-dim': '#92400e',
                'accent-blue': '#3b82f6',
                'accent-green': '#10b981',
                'accent-red': '#ef4444',
                'accent-purple': '#8b5cf6',
            },
            fontFamily: {
                sans: ['DM Sans', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'fade-in': 'fadeIn 0.3s ease-in-out',
                'slide-up': 'slideUp 0.3s ease-out',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
            },
        },
    },
    plugins: [],
} satisfies Config;
