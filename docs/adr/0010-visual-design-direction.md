# ADR-0010: Visual design direction — no black/gray, treasure palette, alerts/favicons/imagery

- Status: Accepted
- Date: 2026-04-25
- Locked by owner: 2026-04-25

## Context
TrésorAI is positioned as a B2B fintech product, not a research demo. The visual language must read as **professional** to a CFO and as **exciting** to a portfolio visitor. The default "dashboard look" of black + gray on white is out — it makes the product feel like every other admin tool and loses the "treasure" connotation in the brand name.

## Decision

### Rules (committed)
1. **No pure black (`#000`) anywhere.** Darkest text uses a deep, warm tone (proposed: `#064E3B` deep forest).
2. **No pure gray anywhere.** Borders, secondary text, and dividers use warm neutrals (sand, bronze, mauve) — never `#666`, `#999`, etc.
3. **Pure white (`#FFFFFF`) is reserved for elevated surfaces** (modals, popovers). Default page background is a warm pearl (`#FAFAF6`).
4. **Customer portal must feel exciting + premium.** The agent reasoning trace, fraud catch, and forecast views are first-impression moments.
5. **Admin portal stays utilitarian but follows the same rules.** Density is higher; chrome is calmer; palette is shared with customer.
6. **Alerts, status pills, and toast notifications are first-class primitives** — not bolted on.
7. **Hero imagery uses customizable vector illustrations** (undraw.co or commissioned), recolored to match the palette. No stock-photo cliché ("smiling team around laptop").
8. **Favicon is a real brand mark** — full pack (16, 32, apple-touch-180, PWA-192/512, ico, webmanifest), not a default Angular logo.

### Strawman palette (proposed)

| Token | Hex | Use |
|---|---|---|
| `brand-emerald-700` | `#047857` | Primary brand, primary CTAs |
| `brand-emerald-500` | `#10B981` | Hover, success accents |
| `brand-gold-500` | `#D4A574` | Premium accent — treasure highlight |
| `brand-gold-700` | `#B08A50` | Pressed / active gold |
| `surface-pearl` | `#FAFAF6` | Page background |
| `surface-cream` | `#F7F1E8` | Card / panel surface |
| `surface-elevated` | `#FFFFFF` | Modals, popovers |
| `border-sand` | `#E8DCC4` | Borders, dividers |
| `text-forest` | `#064E3B` | Primary text |
| `text-bronze` | `#78350F` | Secondary text |
| `text-mauve` | `#5B21B6` | Tertiary / interactive |
| `alert-coral` | `#FB7185` | Errors, fraud catches |
| `alert-coral-bg` | `#FEF2F2` | Alert background |
| `status-mint` | `#34D399` | Success / released |
| `status-amber` | `#F59E0B` | Pending / hold |
| `status-sky` | `#38BDF8` | Info / neutral |
| `chart-primary` | `#047857` | Forecast line |
| `chart-band-upper` | `#D4A574` | Confidence band upper |
| `chart-band-lower` | `#5B21B6` | Confidence band lower |

### Tooling
- **Tailwind CSS** with a shared `tailwind.config.cjs` exporting the palette as `theme.colors.*`. One config file, consumed by both portals.
- **Angular CDK** for accessibility primitives (overlay, focus trap, a11y); no Material default theme — we own the visuals.
- **Headless component primitives** built on CDK: `<tai-alert>`, `<tai-toast>`, `<tai-status-pill>`, `<tai-accordion>`.

### Imagery
- Source: [undraw.co](https://undraw.co) — free, recolorable. Pick a single illustration style, recolor every instance to the palette so the look stays cohesive.
- Use cases: empty states, onboarding screens, hero panels on dashboard cards, 404/500 pages.
- Customer portal hero (Stream view): "money flowing" / "data stream" abstract — stylized, not photographic.
- Admin portal hero (Initial Downloads landing): "warehouse / manifest" abstract — implies install rigor.

### Favicon
- Mark: stylized "T" with a subtle treasure-key cross-stroke, emerald primary, gold accent.
- Source from a single SVG, generate the full pack via realfavicongenerator.net.
- Output: `favicon.ico` + `apple-touch-icon.png` (180) + `icon-192.png`, `icon-512.png` (PWA) + `site.webmanifest`. Checked into each portal's `public/`.

## Consequences
- (+) The product looks distinctive immediately — visitors don't bucket it as "another fintech dashboard."
- (+) A single shared design-tokens config means the two portals can never drift visually.
- (+) Headless primitives + Tailwind keep bundle size tight and theming consistent.
- (−) More upfront design work than using Angular Material defaults. Mitigated by limiting the primitive set (alert, toast, status-pill, accordion + button + input + table) and letting Tailwind utilities handle the rest.
- (−) Palette is taste-driven; locked here. Future shifts require a superseding ADR.
- (−) Sourcing imagery is its own M3 task. M0/M1 ship with palette + primitives + favicon only; rich imagery comes during polish.
