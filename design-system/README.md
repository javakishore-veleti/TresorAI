# design-system

Single source of truth for TrésorAI visual identity. Locked by [ADR-0010](../docs/adr/0010-visual-design-direction.md).

## Layout

```
design-system/
├── README.md                  # this file
├── tokens.css                 # CSS variables — palette, type, radii, shadows
├── brand/
│   ├── brand-mark.svg         # source SVG for portal-customer favicon
│   └── brand-mark-admin.svg   # source SVG for portal-admin favicon (adds mauve "A" badge)
└── favicons/
    ├── customer/              # generated PNGs + ico + webmanifest for portal-customer
    │   ├── favicon-16.png
    │   ├── favicon-32.png
    │   ├── favicon-48.png
    │   ├── apple-touch-icon-180.png
    │   ├── icon-192.png
    │   ├── icon-512.png
    │   ├── favicon.ico
    │   └── site.webmanifest
    └── admin/                 # same set, admin variant
```

## Companion: `tailwind.config.cjs` (repo root)

The Tailwind palette mirrors `tokens.css`. Both portals re-export the root config:

```js
// frontend/portal-customer/tailwind.config.cjs (after T03 scaffolds it)
const root = require('../../tailwind.config.cjs');
module.exports = { ...root, content: ['./src/**/*.{html,ts}'] };
```

## Design rules (locked, ADR-0010)

1. **Never** `#000` or pure `#666` / `#999` gray. Borders use sand `#E8DCC4`, secondary text uses bronze `#78350F`, primary text uses forest `#064E3B`.
2. Page background is pearl `#FAFAF6` — never flat `#FFFFFF`. White is reserved for elevated surfaces (modals, popovers).
3. Customer portal must feel **exciting + premium**; admin stays calmer but uses the same palette.
4. Alerts, toasts, and status pills are first-class primitives (`<tai-alert>`, `<tai-toast>`, `<tai-status-pill>`).
5. Hero imagery is recolored undraw.co illustrations — no stock photos.

## Regenerating favicons

If the brand mark changes:

```bash
# 1. Edit design-system/brand/brand-mark.svg and/or brand-mark-admin.svg
# 2. Regenerate the PNG/ico pack
npm run generate:favicons
# 3. Commit the regenerated files
```

The generated PNGs are checked in so portal builds don't depend on running the generator.

## Palette

| Token | Hex | Use |
|---|---|---|
| `brand-emerald-700` | `#047857` | Primary brand, primary CTAs |
| `brand-emerald-500` | `#10B981` | Hover, success accents |
| `brand-gold-500` | `#D4A574` | Premium accent (treasure) |
| `brand-gold-700` | `#B08A50` | Pressed / active gold |
| `surface-pearl` | `#FAFAF6` | Page background |
| `surface-cream` | `#F7F1E8` | Card / panel surface |
| `surface-elevated` | `#FFFFFF` | Modals, popovers (only) |
| `sand` | `#E8DCC4` | Borders, dividers |
| `forest` | `#064E3B` | Primary text |
| `bronze` | `#78350F` | Secondary text |
| `mauve` | `#5B21B6` | Tertiary / interactive |
| `coral` | `#FB7185` | Errors, fraud catches |
| `coral-bg` | `#FEF2F2` | Alert background |
| `mint` | `#34D399` | Success / released |
| `amber` | `#F59E0B` | Pending / hold |
| `sky` | `#38BDF8` | Info / neutral |
