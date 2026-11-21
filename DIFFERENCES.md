# Differences: site at 08a507c versus the Tierra design system v1

Checked against tokens.json, README.md (sections 4 to 8, 12), and the Button, Card and TierraBar READMEs. Line numbers refer to assets/site.css at 08a507c unless a file is named.

## Colour
| Where | Site | Design system | Status |
| --- | --- | --- | --- |
| site.css:4-24 | 9 colour values typed by hand (hex) | Generated from tokens.json; no raw hex outside generated file (README 13) | Differs (process); values themselves match tokens.json for the 9 used |
| site.css:4-24 | `accent-soft`, `gold-ink`, status colours, shadows not defined | Full token set | Missing, will be generated |
| site.css:10 dark theme (15-23) | `--gold` not redefined in dark | gold dark = #d29a52 | Differs: dark theme keeps the light gold |
| assets/wordmark.svg:3-6, assets/favicon.svg:2-4, assets/og.svg | Hex values inside logo files | Logo files are used as provided (README 4) | Kept as provided; see HANDOFF |

## Typography
| Where | Site | Design system | Status |
| --- | --- | --- | --- |
| site.css:12, 28 | System font stack for everything | Space Grotesk (headings), Inter (text), JetBrains Mono (code) self-hosted (README 6, exception E-1) | Differs; this release closes E-1 |
| site.css:48-50 | h1 clamp 30-48px, h2 24px, h3 20px, no weights set | display-xl 48/52 bold, heading-2 24/30 600, heading-3 18/26 600 | Differs (h3 size, weights, line heights) |
| site.css:28 | body 17px, line-height 1.7 (28.9px) | body-lg 17/28 | Differs slightly |
| site.css:65 | Button label inherits body (17px) | label 15px, weight 600 (Button README) | Differs |
| assets/wordmark.svg:11 | Text in system font | Wordmark: Tierra bold, LLC regular (README 4) | Resolved (SITE-V2): wordmark drawn inline, text in Space Grotesk 700/400 from tokens |

## Spacing, size
| Where | Site | Design system | Status |
| --- | --- | --- | --- |
| site.css:37 | side padding 16px | space-8 (32px) on desktop | Differs |
| site.css:46 | main top padding 40px | space-12 (48px) | Differs |
| site.css:47 | section gap 48px | space-16 (64px) website section spacing | Differs |
| site.css:70 | card gap 20px | space-4 (16px) | Differs |
| site.css:71 | card padding 20px / 4px bottom | space-5 desktop, space-4 phone | Differs |
| site.css:37, tokens reading-max | 64rem | 1024px (same) | Matches |
| site.css:42, 65 | targets 44px | target-min 44px | Matches |

## Shape and depth
| Where | Site | Design system | Status |
| --- | --- | --- | --- |
| site.css:65 | Button radius 6px | radius-md 8px | Differs |
| site.css:71 | Card radius 6px, no shadow | radius-lg 12px, shadow-1 | Differs |
| site.css:71 | Card background surface-alt, 3px gold top border | surface fill, 1px rule border (Card README) | Differs; gold top border is a graphic, proposed exception |
| site.css:75 | Status badge radius 4px, ink border | radius-sm 6px (badge); StatusBadge README governs status pills | Differs |

## Components
| Where | Site | Design system | Status |
| --- | --- | --- | --- |
| site.css:66 | Secondary button transparent fill | surface fill, accent border and label | Differs |
| site.css:67 | Hover uses brightness filter | No filter rule given | Replaced by token colours |
| site.css:68 | Button focus ring in ink | 3px accent outline, 2px offset | Differs |
| header (all pages) | Header on surface with wordmark, nav | TierraBar: 48px ink strip, mark, switcher, search, help, account (stage A: switcher hidden) | Differs; the website has no search, help or account, so not applied; see HANDOFF |
| site.css:44 | Current nav item: gold underline | gold 3px underline on current area (PLATFORM-SHELL 2) | Matches |

## Contrast (text pairs in use; all tokens already meet 4.5:1, see HANDOFF for ratios)
No text is set on gold anywhere. Gold is used for strokes and borders only (site.css:43-44, 62, 71, hero graphic).

## Security / structure
CSP in every page: `default-src 'none'; style-src 'self'; img-src 'self'` (no font-src; fonts would be blocked). Needs `font-src 'self'`.
