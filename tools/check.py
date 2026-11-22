#!/usr/bin/env python3
"""Checks for the Tierra LLC site (standard library only).

Usage: python tools/check.py [--publish]

Refuses (exit 1) when any page has a script, an external resource or link other
than assuredforge.com and mailto, a missing footer or legal line, a missing meta
description, an <img> without alt, a missing skip link, a DRAFT marker outside
/privacy/ and /terms/, or an [ADDRESS: placeholder. With --publish it also
refuses while any placeholder or DRAFT marker remains anywhere.
"""
import json
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
# Legal line in the footer: the company, its legal form and a postal address (number and street, city, state, ZIP). The exact
# address is not fixed here, so a move changes only the pages; the [ADDRESS: placeholder check still refuses an unfilled one.
LEGAL = re.compile(r"<footer>.*?Tierra LLC, an? [A-Z][A-Za-z ]+ limited liability company\.\s+"
                   r"\d+[A-Za-z]? [^,<]+, [^,<]+, [A-Z]{2} \d{5}(?:-\d{4})?.*?</footer>", re.S)
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
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "gen_notices.py"), "--check"], capture_output=True, text=True)
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
    tok = json.loads((ROOT / "design" / "tokens.json").read_text(encoding="utf-8"))
    bp = next(x["value"] for x in tok["size"]["tokens"] if x["name"] == "breakpoint-stack")
    css = (ROOT / "assets" / "site.css").read_text(encoding="utf-8")
    m = re.search(r"@media \(min-width: ([\d.]+)rem\)\s*\{\s*/\* breakpoint-stack", css)
    if not m or float(m.group(1)) * 16 != float(bp.replace("px", "")):
        problems.append(f"assets/site.css: stacking media query must be min-width {bp} (token breakpoint-stack), marked /* breakpoint-stack */")
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
        if w.suffix != ".woff2" and not re.fullmatch(r"OFL-[A-Za-z-]+\.txt", w.name):
            problems.append(f"assets/fonts/{w.name}: only woff2 and OFL-<family>.txt expected")
    for w in (ROOT / "assets" / "fonts").glob("*.woff2"):
        fam = w.name.rsplit("-latin-", 1)[0]
        if not any(l.name.lower() == f"ofl-{fam}.txt" for l in (ROOT / "assets" / "fonts").glob("OFL-*.txt")):
            problems.append(f"assets/fonts/{w.name}: licence file OFL-<family>.txt missing next to the font")
    if "SIL OPEN FONT LICENSE" not in (ROOT / "THIRD-PARTY-NOTICES.md").read_text(encoding="utf-8").upper():
        problems.append("THIRD-PARTY-NOTICES.md: licence text missing")

# What GitHub Pages may serve (allow-list). Pages builds this repo with Jekyll: files whose path has a part starting
# with "." or "_" and the _config.yml "exclude" patterns are not served; everything else is. With a .nojekyll file,
# every file is served, so .nojekyll must stay absent.
SERVED_ALLOW = [re.compile(p) for p in (
    r"index\.html", r"404\.html", r"[a-z0-9-]+/index\.html",
    r"assets/[a-z0-9.-]+\.(css|png|svg)", r"assets/fonts/[a-z0-9-]+\.woff2", r"assets/fonts/OFL-[A-Za-z-]+\.txt",
    r"CNAME", r"robots\.txt", r"sitemap\.xml",
)]

def jekyll_excludes():
    cfg = ROOT / "_config.yml"
    if not cfg.exists():
        return None
    return [m.strip().strip('"') for m in re.findall(r"^\s*-\s*(.+)$", cfg.read_text(encoding="utf-8").split("exclude:", 1)[-1], re.M)]

def served(files, excludes):
    """The files Pages would serve, from the repo's file list."""
    if ".nojekyll" in files or excludes is None:
        return list(files)
    import fnmatch
    out = []
    for f in files:
        parts = f.split("/")
        if any(p[:1] in "._" for p in parts):
            continue
        if any(fnmatch.fnmatch(f, x) or fnmatch.fnmatch(parts[0], x) for x in excludes):
            continue
        out.append(f)
    return out

def served_problems(files, excludes):
    return [f"{f}: would be served by GitHub Pages but is not a site file (allow-list in tools/check.py)"
            for f in served(files, excludes) if not any(p.fullmatch(f) for p in SERVED_ALLOW)]

def check_served(problems):
    """Internal files (handoffs, notes, tools, design records) must never be served."""
    git = lambda *a: subprocess.run(["git", "-C", str(ROOT), "ls-files", *a], capture_output=True, text=True).stdout.split("\n")
    files = sorted({f for f in git() + git("--others", "--exclude-standard") if f})
    excludes = jekyll_excludes()
    if ".nojekyll" in files:
        problems.append(".nojekyll: makes GitHub Pages serve every file; remove it")
    if excludes is None:
        problems.append("_config.yml: missing (it keeps internal files off the website)")
    problems.extend(served_problems(files, excludes))
    # Negative test: a planted internal file, or a .nojekyll, must be caught.
    for planted in (["HANDOFF.txt"], ["notes/COUNSEL-LIST.html"], [".nojekyll"]):
        if not served_problems(files + planted, excludes):
            problems.append(f"served-file check: planted {planted[0]} was not caught")

def main(publish):
    problems = []
    check_design(problems)
    check_served(problems)
    pages = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
    if not pages:
        problems.append("no pages found")
    if not (ROOT / "third-party-notices" / "index.html").exists():
        problems.append("third-party-notices/index.html: missing (fonts are shipped under the OFL; run python tools/gen_notices.py)")
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
        if '<a href="/third-party-notices/">Third-party notices</a>' not in text:
            problems.append(f"{rel}: footer link to the third-party notices missing")
        if not LEGAL.search(text):
            problems.append(f"{rel}: legal line (company, legal form and postal address) missing from the footer")
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
