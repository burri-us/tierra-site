#!/usr/bin/env python3
"""Generate third-party-notices/index.html from THIRD-PARTY-NOTICES.md (standard library only).

The licence texts are copied from THIRD-PARTY-NOTICES.md, never typed into the page.
Usage: python tools/gen_notices.py [--check]   (--check: exit 1 if the page is missing or stale)
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "THIRD-PARTY-NOTICES.md"
OUT = ROOT / "third-party-notices" / "index.html"
TEMPLATE = ROOT / "contact" / "index.html"   # header, footer and head come from an existing page

DESC = "Licences of the open-source typefaces this website ships from its own server."


def build():
    md = SRC.read_text(encoding="utf-8")
    rows = re.findall(r"^\| (?!Font |---)([^|]+?) \| ([^|]+?) \| ([^|]+?) \|$", md, re.M)
    blocks = re.findall(r"^## (.+?)\n+```\n(.*?)\n```", md, re.M | re.S)
    if not rows or not blocks:
        sys.exit("THIRD-PARTY-NOTICES.md: no font table or licence blocks found")
    body = ['    <h1>Third-party notices</h1>',
            f'    <p>This website ships {len(rows)} open-source typefaces from its own server. Each is used under the SIL Open Font License 1.1; its notice and licence text follow.</p>',
            '    <ul>']
    for font, pkg, files in rows:
        body.append(f'      <li><strong>{html.escape(font)}</strong>: {html.escape(pkg)} ({html.escape(files)})</li>')
    body.append('    </ul>')
    for name, text in blocks:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        body += [f'    <section aria-labelledby="{slug}-h">',
                 f'      <h2 id="{slug}-h">{html.escape(name)}</h2>',
                 f'      <pre class="notice">{html.escape(text)}</pre>',
                 '    </section>']
    page = TEMPLATE.read_text(encoding="utf-8")
    page = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', page)
    page = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESC}">', page)
    page = page.replace("Contact · Tierra LLC", "Third-party notices · Tierra LLC")
    page = page.replace("https://tierra-llc.com/contact/", "https://tierra-llc.com/third-party-notices/")
    page = page.replace(' aria-current="page"', "")
    page = re.sub(r"<main id=\"main\">.*?</main>", lambda m: '<main id="main">\n' + "\n".join(body) + "\n  </main>", page, flags=re.S)
    return page


def licence_files():
    """One plain-text licence file per family, shipped next to the font files (text from THIRD-PARTY-NOTICES.md)."""
    md = SRC.read_text(encoding="utf-8")
    blocks = re.findall(r"^## (.+?)\n+```\n(.*?)\n```", md, re.M | re.S)
    return {ROOT / "assets" / "fonts" / ("OFL-" + name.replace(" ", "-") + ".txt"): text + "\n" for name, text in blocks}


def main():
    page = build()
    lic = licence_files()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != page:
            print("FAIL third-party-notices/index.html: missing or stale (run python tools/gen_notices.py)")
            return 1
        for f, text in lic.items():
            if not f.exists() or f.read_bytes().decode("utf-8").replace("\r\n", "\n") != text:
                print(f"FAIL assets/fonts/{f.name}: missing or stale (run python tools/gen_notices.py)")
                return 1
        return 0
    for f, text in lic.items():
        f.write_bytes(text.encode("utf-8"))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
