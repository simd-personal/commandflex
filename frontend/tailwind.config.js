/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary Colors
        'primary-bg': '#181A1B',
        'secondary-bg': '#23272f',
        'accent': '#A3B18A',
        'text-primary': '#F3F3E7',
        'text-secondary': '#A3B18A',
        
        // Status Colors
        'status-new': '#3B82F6',
        'status-dispatched': '#F59E0B',
        'status-resolved': '#10B981',
        'status-error': '#EF4444',
        
        // Priority Colors
        'priority-1': '#EF4444', // Critical
        'priority-2': '#F59E0B', // High
        'priority-3': '#3B82F6', // Moderate
        'priority-4': '#10B981', // Low
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'monospace'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      }
    },
  },
  plugins: [],
} 