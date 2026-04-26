// Re-export the root TrésorAI design tokens. Single source of truth lives at
// repo root: ../../tailwind.config.cjs (locked by ADR-0010).
const root = require('../../tailwind.config.cjs');
module.exports = {
  ...root,
  content: ['./src/**/*.{html,ts}'],
};
