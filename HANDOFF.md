# HANDOFF: SITE-V2 (tierra-llc.com, design system 1795242441-3bd7)
Branch w12-phase2. Not pushed, not deployed. `python tools/check.py` passes (4 pages, 0 problems).

## Commits (on top of 09be1f4)
- c51e754 Tokens: design system 1795242441-3bd7 (adds bar, bar-ink); ship Space Grotesk 400
- 4acbb39 Draw the v2 wordmark inline in all pages with token colours and brand face; remove logo file; check fails on logo <img>
- (this file) Handoff: SITE-V2

## What changed
- design/tokens.json copied byte for byte (SHA-256 2ed1bb14...3857, recorded in design/tokens.sha256); assets/tokens.css regenerated (adds --bar, --bar-ink, Space Grotesk 400 @font-face). space-grotesk-latin-400-normal.woff2 added from @fontsource 5.1.1 (same as the other faces; THIRD-PARTY-NOTICES.md updated).
- Home, About, Contact, 404: the `<img>` wordmark is replaced by the inline v2 wordmark (viewBox 0 0 150 36, 150x36, paths M5 7h20M15 7v20 and M8 31h14, stroke-width 4, round caps, text x34 y25 size 20 weight 700, "LLC" 400, letter-spacing 0.2). Colours via classes g-ink / g-gold (var(--ink), var(--gold)); text fill var(--ink), face var(--font-display) (Space Grotesk). Accessible name: role="img" + aria-label="Tierra LLC" on the svg (the link is named "Tierra LLC"), same on every page.
- Fit measured in Chrome (getBBox): text spans x 34 to 130.9 of 150, y 5 to 31 of 36. It fits; no exception needed.
- Inline AssuredForge mark in index.html verified identical to v2 (viewBox 0 0 64 64, fill none, stroke-width 6, round caps and joins, paths M14 54L32 10l18 44 and M20 37l8 8 26-21), colours via g-ink / g-gold. No change needed.
- tools/check.py now fails when an `<img>` src contains "logo".
- DIFFERENCES.md wordmark row marked resolved.

## Files removed
assets/logos/tierra-wordmark.svg and the assets/logos directory. No remaining references to logo files.

## Files kept
- assets/favicon.svg, favicon-32.png, og.png, og.svg unchanged (exception E-2: not in the Logos folder, no derivation rule).
- Dashed "More in development" card (exception E-3).
- No DRAFT banners on these four pages (privacy/terms not present).
- PAGE-WEIGHT.md not regenerated (still describes the linked wordmark); numbers are stale by about 1 KB per page.

## Contrast (WCAG, light / dark; text needs 4.5, graphics 3)
| Pair | Light | Dark |
| --- | --- | --- |
| ink on surface (body, headings, nav, wordmark ink stroke and text, AF mark ink) | 15.06 | 14.84 |
| muted on surface | 8.02 | 9.31 |
| muted on surface-alt (footer) | 7.40 | 8.43 |
| accent on surface (links, secondary button, focus ring) | 6.69 | 8.04 |
| accent-ink on accent (primary button) | 6.69 | 6.93 |
| accent on accent-soft (hover) | 5.74 | 6.47 |
| surface on ink (primary hover) | 15.06 | 14.84 |
| gold on surface (wordmark base stroke, AF mark check, hero) graphic only | 3.60 | 7.06 |
All pass. Gold is never text. rule on surface (1.40 / 1.51) is a decorative divider and card border only, not information-bearing.

## Proposed exceptions (not applied)
- None new.
- Previous 2 (system font in wordmark), previous 4 (inline AF mark) and the C2PA open question are resolved: the wordmark is drawn inline in the brand face and the metadata-carrying file is gone.
- Previous 1 (no Tierra bar on tierra-llc.com): left as is, not in scope. Note tokens now include bar / bar-ink.
- Previous 3 (favicon/og) stays as E-2; previous 5 as E-3.

## Verification
- No sideways scroll at a true 390 px phone (isMobile, touch, DPR 2): scrollWidth 390 on all six pages/themes (home, about, contact x light, dark). 1440: 1440.
- Dark theme verified visually: wordmark text and ink stroke become #e8edf2, gold becomes #d29a52.

## Preview
`npx serve C:\dev\AssuredForge\tierra-site-p2 -l 4174` (stopped; port verified free).

## Screenshots
C:\dev\AssuredForge\ds-previews\site-v2\tierra\{home|about|contact}-{light|dark}-{1440|390}.png (12 files; script shoot.cjs one level up).
