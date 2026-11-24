# tierra-llc.com content refresh: plan (local only, for the owner's review)

Author: Burri (Site Brand window). 2026-11-24. Plan only; nothing changed on any page, nothing pushed. Branch `content-refresh-plan`
from `dec577-copy-round` 6f8008f (the release head). Root `.md` files are not served (`_config.yml`).

Sources: `design/BRAND-DIRECTION.md` (architecture main, blob 290bbc2); DEC-577 (AI wording rule); DEC-450 (tierra-llc.com is the trust and
company layer that endorses AssuredForge; future products unnamed; post-handover backlog S-110: Tierra Trust Center, mission on About,
product index only with a second product); DEC-451 and DEC-579 (2) (mission, Vision change list CL-11); claims register on architecture
main e61a7f1 (CL-06, CL-23, CL-28, CL-29, CL-53).

**Base state:** the plan starts from what goes live with the release (6920 design system, then the DEC-577 copy round), not from today's
live `main` 744b56f. The refresh is a new branch after both are live.

## 0. Mission wording: owner to confirm

| Version | Text | Record |
|---|---|---|
| As quoted in the request | "... build and run what matters with **AI** they can trust and evidence they can show." | DEC-451 (decided 2026-11-21) |
| Amended, on the release branch | "... build and run what matters with **software** they can trust and evidence they can show." | DEC-579 (2), T-1 (b), 2026-11-23: CL-11 amended "from the next copy round"; DEC-577 keeps "AI" out of taglines |

This plan uses the amended text (it is the later decision and matches DEC-577). If the owner wants "AI" back, that reverses DEC-579 (2)
and needs a new DEC; the About page commit 6f8008f would be reverted.

## 1. Pages: what each says today, what it should say, what is missing

The site has five pages and one menu: Home, Products (an anchor on Home, `/#products`), About, Contact, plus Page not found and
Third-party notices.

### Home (`index.html`, 457 words)

| Part | Today | Should say | Why |
|---|---|---|---|
| Headline | "Practical tools for work you can stand behind." | Keep, or lead with the mission: "Software you can trust. Evidence you can show." | No "AI" either way (DEC-577). The mission-led line ties Home to About; it needs a row (company line, Vision CL-11 as source) |
| Lead | "Tierra LLC builds software that makes decisions visible, work accountable and results provable, without unnecessary complexity." | Keep; add one line naming the first product: "AssuredForge is our first product." (already on About) | Home never says Tierra makes AssuredForge in one sentence; CL-28 is the source |
| Product card | "Governed software delivery with traceability, release approvals signed by named people and a tamper-evident audit chain. For individuals and small teams today; a hosted edition for organizations is planned." | Keep the claim-backed facts (CL-05, CL-06, CL-23). Add the brand positioning only within the register: "named people make every decision, and every decision is recorded and verifiable." **Do not** say "agents prepare the work" while CL-40R is Being validated; if used, it follows the assuredforge.com AI switch wording ("Agent-assisted planning and delivery is being validated ...") | Brand note positioning; DEC-577; WR-01 (AI facts follow the switch). tierra-llc.com has no switch, so it should not state AI availability at all until the switch is on |
| Status badge | "Available to design partners" | Keep (CL-23) | |
| More in development | "We are building further tools on the same principles. They will be announced here when they are ready." | Keep | DEC-450: future products stay unnamed |
| Trust | "No tracking on our sites. Your data stays yours. Security reports for AssuredForge: security@assuredforge.com." | "No cookies or tracking on our sites. In AssuredForge's desktop edition your records stay on your own PC." plus the security line | "Your data stays yours" is wider than any row: CL-53 covers the desktop edition only; the hosted edition is planned |
| Footer | Company, address, Third-party notices | Add a link to "Trust" (section 2) once it exists | |

### About (`about/index.html`, 331 words)

| Part | Today (release head) | Should say | Missing |
|---|---|---|---|
| Mission | Amended wording (section 0) | Same | Owner confirmation (section 0) |
| How we work | Three principles: people decide; privacy first; plain and practical | Keep. Align "People decide: our tools prepare and record; named people approve." with the brand pillar Decide ("Named people sign every decision"). "our products keep your records under your control" narrows to "AssuredForge's desktop edition keeps your records on your own PC" (CL-53) | A fourth principle "Prove: every decision is recorded and verifiable" (brand pillar, CL-06) |
| Founder | One paragraph naming the founder | Keep as is | Team and company page waits for CQ-2 and each person's consent (brand roadmap 8): not in this round |
| Company line | Not present | CL-28's sentence: "AssuredForge is developed and operated by Tierra LLC, a Michigan-based software company focused on software delivery governance, traceability and audit-ready release management." | The endorsing sentence, so both sites describe the company alike |

### Contact (`contact/index.html`, 236 words)

| Part | Today | Should say | Missing |
|---|---|---|---|
| Company and address | Registered address | Keep | |
| General, named contact | Company email; the founder's email | Keep | |
| AssuredForge routes | Not present | "About AssuredForge: info@assuredforge.com. Partner support: support@assuredforge.com. Security reports only: security@assuredforge.com." (CL-29, verbatim) | Partners write to the company address for product questions today. OQ-029 stays respected: no product addresses on tierra-llc.com, only links to assuredforge.com addresses |

### Page not found, Third-party notices

No content change. The notices page is generated (`tools/gen_notices.py`).

## 2. New page: Trust (DEC-450 backlog S-110)

| Section | Content | Depends on |
|---|---|---|
| Our sites | No cookies, no tracking, no analytics (true today; `tools/check.py` refuses scripts) | Nothing |
| Security reports | CL-29 route; link to assuredforge.com responsible disclosure | Nothing |
| AssuredForge's Trust Center | Link to assuredforge.com Trust Center (privacy notice, AI use policy, subprocessors and model providers). A disclosure place: "AI" may be named here (DEC-577) | assuredforge.com release live |
| Company privacy, legal pages, AI principles | Company-level texts | Counsel (P2 tier); not in this round, shown as nothing rather than "coming soon" |

Menu: Home, Products, About, Trust, Contact (no "AI" in navigation, DEC-577).

## 3. Not in this round

- Team and company page (CQ-2 and consent).
- Product index (only once a second product is committed, DEC-450).
- Long-lived product addresses such as sign-in or email sending (OQ-029).

## 4. Claims rows needed first (Kit Notices)

Every new sentence about AssuredForge or Tierra needs a row before release (brand note, "How changes are made" 2):
1. Home headline (if mission-led) and the Trust line on Home (desktop-scoped, CL-53).
2. Home product card line "named people make every decision, and every decision is recorded and verifiable" (rests on CL-05, CL-06).
3. About: the fourth principle (CL-06) and the narrowed privacy principle (CL-53); CL-28 reused verbatim.
4. Contact: CL-29 reused verbatim.
5. Trust page: "no cookies, no tracking, no analytics" for Tierra's sites.

## 5. Effort and checks

| Step | Effort |
|---|---|
| Rows from Kit Notices (section 4) | Kit Notices; about 5 rows |
| Copy on Home, About, Contact; meta and share descriptions follow | 2 to 3 hours |
| Trust page (one new page; sitemap; menu on every page; `tools/check.py` allow-list) | 2 hours |
| Checks: `python tools/check.py` and `--publish`; accessibility scan at 390 and 1440 px, light and dark, plus 320 px overflow (25 runs); preview screenshots for review | 1 hour |
| Release: one pull request to `main` (unprotected, deploys on merge), live compare (`tools/live_check.py`), rollback by revert (RELEASE-PACKAGE §7.3 pattern) | 30 minutes, about 1 Actions minute |

Total about one day of window time, Sonnet (DEC-428, routine copy). Order: after both site releases are live; rows first; then copy,
checks, owner review, release as its own owner gate.

## 6. Decisions for the owner

1. Mission wording: the amended "software they can trust" (recommended, DEC-579 (2)) or "AI they can trust" (needs a new DEC).
2. Home headline: keep "Practical tools for work you can stand behind." (recommended for this round: no new row) or mission-led.
3. Add the Trust page now with the counsel-free sections only (recommended), or wait for counsel.
4. Narrow "Your data stays yours" to the desktop edition (recommended; the current line is wider than the register).
