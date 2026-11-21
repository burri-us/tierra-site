#!/usr/bin/env python3
"""Checks for the Tierra LLC site (standard library only).

Usage: python tools/check.py [--publish]

Refuses (exit 1) when any page has a script, an external resource or link other
than assuredforge.com and mailto, a missing footer or legal line, a missing meta
description, an <img> without alt, a missing skip link, a DRAFT marker outside
/privacy/ and /terms/, or an [ADDRESS: placeholder. With --publish it also
refuses while any placeholder or DRAFT marker remains anywhere.
"""
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DRAFT_OK = {"privacy/index.html", "terms/index.html"}
ALLOWED_HOSTS = {"assuredforge.com", "www.assuredforge.com"}
ATTR = re.compile(r'\b(src|href)\s*=\s*"([^"]*)"', re.I)
FOOTER = re.compile(r"<footer>.*©\s*\d{4} Tierra LLC.*</footer>", re.S)   # privacy and terms are added after counsel (DEC-448, option A)
LEGAL = "Tierra LLC, a Michigan limited liability company. 5987 Wabash Ln, Stevensville, MI 49127"
DESC = re.compile(r'<meta\s+name="description"\s+content="[^"]+"', re.I)
IMG = re.compile(r"<img[^>]*>", re.I)
SKIP = re.compile(r'<a\s+class="skip"\s+href="#main"', re.I)

HEX = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b(?=[;\s,)}])")
FONTS = re.compile(r"\b(Inter|Space Grotesk|JetBrains Mono|system-ui|Segoe UI|Roboto|Helvetica|Arial|Consolas|Cascadia|sans-serif|monospace)\b", re.I)
COLOUR_FN = re.compile(r"\b(rgba?|hsla?)\(", re.I)

def check_design(problems):
    """Design-system rules: tokens generated, no raw colours or font names outside assets/tokens.css."""
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "gen_tokens.py"), "--check"], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        problems.append(line.replace("FAIL ", ""))
    for f in [ROOT / "assets" / "site.css"] + sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts):
        rel = f.relative_to(ROOT).as_posix()
        text = f.read_text(encoding="utf-8")
        for m in HEX.finditer(text):
            problems.append(f"{rel}: raw hex colour {m.group(0)} (use a token)")
        for m in COLOUR_FN.finditer(text):
            problems.append(f"{rel}: raw colour function {m.group(0)} (use a token)")
        if f.suffix == ".css":
            body = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        else:
            body = "\n".join(re.findall(r"<style.*?</style>|style=\"[^\"]*\"", text, re.S))
        for m in FONTS.finditer(body):
            problems.append(f"{rel}: raw font name {m.group(0)} (use a font token)")
    for page in sorted(ROOT.rglob("*.html")):
        if ".git" in page.parts:
            continue
        rel = page.relative_to(ROOT).as_posix()
        text = page.read_text(encoding="utf-8")
        csp = re.search(r'Content-Security-Policy" content="([^"]*)"', text)
        if not csp or "font-src 'self'" not in csp.group(1) or re.search(r"https?:|unsafe|\*", csp.group(1)):
            problems.append(f"{rel}: CSP must include font-src 'self' and no external source")
        if "/assets/tokens.css" not in text:
            problems.append(f"{rel}: tokens.css not linked")
    for w in (ROOT / "assets" / "fonts").glob("*"):
        if w.suffix != ".woff2":
            problems.append(f"assets/fonts/{w.name}: only woff2 expected")
    if "SIL OPEN FONT LICENSE" not in (ROOT / "THIRD-PARTY-NOTICES.md").read_text(encoding="utf-8").upper():
        problems.append("THIRD-PARTY-NOTICES.md: licence text missing")

def main(publish):
    problems = []
    check_design(problems)
    pages = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
    if not pages:
        problems.append("no pages found")
    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        text = page.read_text(encoding="utf-8")
        if "[ADDRESS:" in text:
            problems.append(f"{rel}: address placeholder")
        if "DRAFT" in text and rel not in DRAFT_OK:
            problems.append(f"{rel}: DRAFT marker outside privacy and terms")
        if "DRAFT" in text and rel in DRAFT_OK and publish:
            problems.append(f"{rel}: DRAFT marker")
        if re.search(r"<script", text, re.I):
            problems.append(f"{rel}: script tag")
        if not FOOTER.search(text):
            problems.append(f"{rel}: footer missing or incomplete")
        if LEGAL not in text:
            problems.append(f"{rel}: legal line missing")
        if not DESC.search(text):
            problems.append(f"{rel}: meta description missing")
        if not SKIP.search(text) or 'id="main"' not in text:
            problems.append(f"{rel}: skip link missing")
        for img in IMG.findall(text):
            if re.search(r'src\s*=\s*"[^"]*logo', img, re.I):
                problems.append(f"{rel}: logo loaded via <img> (draw it inline with token colours)")
            if not re.search(r'alt\s*=', img, re.I):
                problems.append(f"{rel}: img without alt")
        for attr, val in ATTR.findall(text):
            u = urlparse(val)
            if u.scheme == "mailto" or (not u.scheme and not u.netloc):
                continue
            if u.hostname in ALLOWED_HOSTS and u.scheme == "https":
                continue
            problems.append(f"{rel}: external {attr} {val}")
    fatal = problems
    for p in problems:
        print("FAIL", p)
    print(f"{len(pages)} pages checked, {len(fatal)} problem(s)")
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main("--publish" in sys.argv))
