/**
 * TrésorAI shared design tokens — single source of truth for both portals.
 * Per ADR-0010: no pure black, no pure gray. Warm palette only.
 *
 * Each portal extends this config from its own tailwind.config.cjs:
 *   const root = require('../../tailwind.config.cjs');
 *   module.exports = { ...root, content: ['./src/**\/*.{html,ts}'] };
 */
module.exports = {
  content: [
    './frontend/portal-customer/src/**/*.{html,ts}',
    './frontend/portal-admin/src/**/*.{html,ts}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          'emerald-700': '#047857',
          'emerald-500': '#10B981',
          'gold-500':    '#D4A574',
          'gold-700':    '#B08A50',
        },
        surface: {
          pearl:    '#FAFAF6',
          cream:    '#F7F1E8',
          elevated: '#FFFFFF',
        },
        sand:   '#E8DCC4',
        forest: '#064E3B',
        bronze: '#78350F',
        mauve:  '#5B21B6',
        coral:  '#FB7185',
        'coral-bg': '#FEF2F2',
        mint:   '#34D399',
        amber:  '#F59E0B',
        sky:    '#38BDF8',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      borderRadius: {
        'tai-sm': '6px',
        'tai':    '10px',
        'tai-lg': '16px',
      },
      boxShadow: {
        'tai-card':     '0 1px 2px rgba(6, 78, 59, 0.04), 0 4px 12px rgba(6, 78, 59, 0.06)',
        'tai-elevated': '0 8px 24px rgba(6, 78, 59, 0.10)',
      },
    },
  },
  plugins: [],
};
