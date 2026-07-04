# Precedent — brand assets

The mark: a **wax seal** enclosing a **classical Ionic column** (precedent, permanence, an
authorising seal), with the **PRECEDENT** serif wordmark. "Every incident resolved becomes precedent."

## Palette

| Role | Hex |
|---|---|
| Seal indigo | `#3C3B62` |
| Paper / cream (background, column, light wordmark) | `#F1F1E2` |
| Ink (wordmark on light) | `#2A2A48` |

## Files

| File | Use |
|---|---|
| `precedent-logo-colored.svg` / `.pdf` | **Primary** full logo (seal + column + wordmark) on the cream card — light surfaces, print, slides on paper. |
| `precedent-logo-transparent.svg` / `.pdf` | Full logo, transparent background — for placing on **light** backgrounds. |
| `precedent-logo.png` | 640px raster of the colored logo — README / web. |
| `precedent-seal-dark.png` | **Seal mark only, transparent background, cream column** — for **dark** surfaces (the deck `#0B0F14`, avatars on dark). Pair with a light wordmark. |
| `precedent-avatar.png` | 1024² square (seal on cream) — Agentverse / social agent avatar. |

## Usage

- **Dark backgrounds** (deck, dark UI): use `precedent-seal-dark.png` (the cream column reads on dark);
  set the wordmark in cream/off-white beside or below it.
- **Light backgrounds** (README, print): use `precedent-logo-colored` (self-contained cream card) or
  `precedent-logo-transparent` on a light surface.
- Don't stretch, rotate, recolor the seal, or set the navy wordmark on a dark background (it disappears —
  use the dark seal mark + a light wordmark instead).

_Vector SVG/PDF are the masters; the PNGs are derived. Regenerate the dark seal + avatar with the
Pillow snippet in the commit that introduced them (crop the wordmark, flood-fill the cream border to
transparent, keep the enclosed cream column)._
