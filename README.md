# tierra-site

The public website of Tierra LLC, served by GitHub Pages from the `main` branch (root folder), with no build step. `_config.yml` keeps every internal file (this README, handoffs, notes, `tools/`, `design/`) off the website; the pages and assets are copied as they are. `python tools/check.py` fails if any file outside the allow-list would be served, or if a `.nojekyll` file returns.

## Status

Phase 1: Home (with Products), About and Contact, served at `https://tierra-llc.com` with "Enforce HTTPS" on. Privacy and Terms are added after counsel review (DEC-448, option A).

## Rules

- Static HTML and one stylesheet; no scripts, forms, analytics, cookies or third-party resources.
- Every page carries a Content Security Policy in a `meta` tag (GitHub Pages can't send custom headers).
- No link to any sign-in page.
- Commits use the account's GitHub no-reply address.

## Checking

`python tools/check.py` (standard library only) exits non-zero on a script, an external resource or link other than assuredforge.com and mailto, a missing footer, a DRAFT marker outside `/privacy/` and `/terms/`, or an `[ADDRESS:` placeholder. `python tools/check.py --publish` also fails while a DRAFT marker remains on the privacy and terms pages.

## Publishing

Publishing is a push to `main`, done by the owner only; GitHub Pages publishes within a few minutes. Before pushing, replace the address placeholder, remove the DRAFT markers once counsel has reviewed, and run `python tools/check.py --publish`.
