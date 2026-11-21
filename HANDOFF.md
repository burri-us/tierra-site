# HANDOFF: SITE-T (Tierra design system on tierra-llc.com)
Branch w12-phase2, base 08a507c. Not pushed, not deployed. `python tools/check.py` passes (4 pages, 0 problems).

## Done
- DIFFERENCES.md (a46e143): site vs design system, with file:line.
- Tokens: design/tokens.json copied (SHA-256 03fcc159...d8ef, matches SOURCE.md; recorded in design/tokens.sha256). tools/gen_tokens.py generates assets/tokens.css (variables, dark theme, @font-face); `--check` fails if stale. tools/check.py now also fails on raw hex/rgb or font names in site.css/HTML, a CSP without font-src 'self' or with an external source, and a missing tokens.css link.
- Fonts self-hosted woff2 (Inter 400/600, Space Grotesk 600/700; @fontsource 5.1.1 via npm), OFL text in THIRD-PARTY-NOTICES.md. CSP: font-src 'self' added to all 4 pages. JetBrains Mono not shipped (no code on the site). Closes exception E-1.
- Styling per Button/Card READMEs: radius 8/12, shadow-1, surface cards with 1px rule, secondary button on surface, accent focus ring, token spacing (side 32px, sections 64px desktop), display/heading sizes.
- Wordmark replaced by the approved file assets/logos/tierra-wordmark.svg (sha 569d9d8b...37b2, byte for byte). Old assets/wordmark.svg (sha 97333cb4...a6d5) had the same drawing; the approved one adds an embedded C2PA metadata block. No visible change.
- Contrast (WCAG ratios, light / dark): ink on surface 15.06 / 14.84; muted on surface 8.02 / 9.31; muted on surface-alt (footer) 7.40 / 8.43; accent on surface (links, secondary button) 6.69 / 8.04; accent-ink on accent (primary button) 6.69 / 6.93; accent on accent-soft (hover) 5.74 / 6.47; surface on ink (primary hover) 15.06 / 14.84. No text on gold; gold (3.60 / 7.06) only for strokes.

## Proposed exceptions (owner approval)
1. Tierra bar (48px ink strip) not applied: rule TierraBar README/PLATFORM-SHELL 2; reason: site has no search, help, account or switcher, and the approved wordmark has no light-on-ink variant (never recolour); scope: tierra-llc.com header stays on surface with gold current-page underline; review: when a second product is Active (stage C).
2. Wordmark text renders in the system font (an SVG used as an image cannot load page fonts); rule: README 6 brand faces; scope: wordmark only; review: when the design system supplies an outlined wordmark.
3. favicon.svg / favicon-32.png / og.svg kept as before (not in the Logos folder, README gives no rule to derive them; they hold raw hex and a system font); review: when the design system adds favicon/og assets.
4. Inline AssuredForge mark in index.html is the approved geometry drawn with token colours (the file has fixed ink, unreadable on the dark surface); rule: use the file as is; review: when a reversed mark exists (site-w11 has one, not in Logos).
5. Dashed border on the "More in development" card (Card README: solid rule border).

## Light and dark mode (owner addition)
- Both themes are generated from tokens.json (value.light on :root, value.dark under prefers-color-scheme: dark); automatic only, no toggle, script or storage. No colour outside tokens (check enforces).
- Logos: the approved wordmark switches itself (verified in dark screenshots). Per image: hero graphic is inline SVG on tokens, so it follows the theme; favicon.svg and favicon-32.png are opaque navy tiles with a white T, readable on light and dark tabs, unchanged; og.png is an opaque navy card with white text, unchanged (same in both themes).
- Focus ring (accent, 3px) vs surface: 6.69 light / 8.04 dark (needs 3:1). Status badge: ink text and ink border on surface, 15.06 / 14.84. Button label, link and hover ratios as listed above, both themes.

## Open questions
- POLICY: the approved logo SVG contains a C2PA metadata block whose decoded text says the file was provided by Claude. Copied byte for byte as instructed, but it conflicts with the no-AI-marker repository policy. Decide: strip it (changes the hash) or accept.
- 404 page: not published on Pages tests locally only via /404.html.

## Preview
`npx serve C:\dev\AssuredForge\tierra-site-p2 -l 4174` (server stopped now).

## Screenshots
C:/dev/AssuredForge/ds-previews/site-t/ : before-PAGE-wide|narrow.png (light, 08a507c) and after-light|dark-PAGE-wide|narrow.png for home, about, contact, 404; 1440 and 390; puppeteer-core driving headless Chrome with prefers-color-scheme emulated (dark verified visually on home).
