# tierra-site

The public website of Tierra LLC, served by GitHub Pages from the `main` branch (root folder), with no build step.

## Status

Holding page only. The site's content is published after the custom domain `tierra-llc.com` serves HTTPS with
"Enforce HTTPS" switched on.

## Rules

- Static HTML and one stylesheet; no scripts, forms, analytics, cookies or third-party resources.
- Every page carries a Content Security Policy in a `meta` tag (GitHub Pages can't send custom headers).
- No link to any sign-in page.
- Commits use the account's GitHub no-reply address.

## Publishing

Commit to `main`; GitHub Pages publishes within a few minutes.
