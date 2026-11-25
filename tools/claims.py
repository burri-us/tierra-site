"""Claims gate for tierra-llc.com (SB2, DEC-662, DEC-671; standard library only).

GitHub Pages serves this repository's pages as they are (no build step), so wording that waits for a claims row must not sit in a
served page, not even in a comment. Pages with gated wording therefore have a template under src/ (not served: _config.yml excludes
it), and the served page is written from the template and the claims-state snapshot src/claims-state.json:

    <!--claim CL-70 when="Current|Decided"-->new wording<!--else-->today's wording<!--/claim-->
    <!--page-claim CL-73-->   (first line: the whole page exists only when the row allows it)

`when` lists the states that allow the new wording (default Current; owner decision 1, DEC-671). Without <!--else--> the block is
simply absent until its row allows it.

Usage:
    python tools/claims.py render              write the served pages from src/ (then run python tools/gen_notices.py)
    python tools/claims.py preview <dir>       write a review copy of the whole site to <dir>, every held block shown with a
                                               "[Held: CL-xx, state]" marker (never served; tools/check.py refuses the marker)
    python tools/claims.py sync <arch> <commit>  refresh src/claims-state.json from the claims register at <commit> (git show)
    python tools/claims.py check               exit 1 if a served page differs from its rendered template (tools/check.py runs it)
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
STATE_FILE = SRC / "claims-state.json"
MAPPING_FILE = SRC / "claims-mapping.json"
REGISTER = "research/design-partners/materials/CLAIMS-REGISTER.md"
STATES = ["Current", "Decided", "Approved wording", "Being validated", "Planned", "Draft", "Withdrawn"]

BLOCK = re.compile(r'<!--claim (CL-[A-Z0-9]+(?:-[A-Z0-9]+)*)(?: when="([^"]+)")?-->(.*?)(?:<!--else-->(.*?))?<!--/claim-->', re.S)
PAGE = re.compile(r'\A<!--page-claim (CL-[A-Z0-9]+(?:-[A-Z0-9]+)*)(?: when="([^"]+)")?-->\n?')
ROW_USE = re.compile(r"<!--(?:page-)?claim (CL-[A-Z0-9]+(?:-[A-Z0-9]+)*)")


def map_state(cell):
    """The register's free-text State cell as one state, or None when it cannot decide (never guesses)."""
    c = re.sub(r"\s+", " ", cell).strip()
    if re.search(r"\*\*Draft\b", c) or re.match(r"Draft\b", c):
        return "Draft"
    if re.match(r"Withdrawn\b", c):
        return "Withdrawn"
    if re.search(r"\s/\s", c):
        return None
    for s in ("Current", "Being validated", "Planned", "Decided", "Approved wording"):
        if re.match(re.escape(s) + r"\b", c):
            return s
    return None


def parse_register(md):
    rows = {}
    for line in md.splitlines():
        m = re.match(r"^\|\s*(CL-[A-Z0-9]+(?:-[A-Z0-9]+)*)\s*\|(.*)\|\s*$", line)
        if m:
            cells = m.group(2).split(" | ")
            if len(cells) >= 3:
                rows[m.group(1)] = cells[1].strip()
    return rows


def load_rows():
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))["rows"]


def templates():
    return sorted(p for p in SRC.rglob("*") if p.suffix in (".html", ".xml"))


def render_text(text, rows, preview, problems):
    """Returns the page text, or None when a page-claim holds the whole page."""
    def allowed(row, when):
        state = rows.get(row)
        if state is None:
            problems.append(f"{row} is not in src/claims-state.json (run python tools/claims.py sync)")
            return False, "not in snapshot"
        return state in (when or "Current").split("|"), state

    m = PAGE.match(text)
    if m:
        ok, state = allowed(m.group(1), m.group(2))
        text = text[m.end():]
        if not ok and not preview:
            return None
        if not ok:
            text = text.replace('<main id="main">', f'<main id="main">\n    <p class="held">[Held: {m.group(1)}, {state}]</p>', 1)

    def block(b):
        ok, state = allowed(b.group(1), b.group(2))
        if ok:
            return b.group(3)
        if preview:
            # The marker goes inside the block's first element when it starts with one (a bare text node inside <ul> or <dl> is
            # invalid markup), otherwise before the text.
            mark = f"[Held: {b.group(1)}, {state}] "
            first = re.match(r"(\s*<(?!/)[^>]+>)", b.group(3))
            return first.group(1) + mark + b.group(3)[first.end():] if first else mark + b.group(3)
        return b.group(4) or ""

    out = BLOCK.sub(block, text)
    if "<!--claim" in out or "<!--/claim" in out or "<!--else" in out:
        problems.append("unbalanced claim block")
    return out


def rendered(preview=False):
    """{served path: text or None} for every template."""
    rows, problems, out = load_rows(), [], {}
    for t in templates():
        rel = t.relative_to(SRC).as_posix()
        out[rel] = render_text(t.read_text(encoding="utf-8"), rows, preview, problems)
    return out, problems


def check(problems):
    pages, render_problems = rendered()
    problems.extend(f"claims: {p}" for p in render_problems)
    for rel, text in pages.items():
        served = ROOT / rel
        if text is None:
            if served.exists():
                problems.append(f"{rel}: held by its page claim but present (run python tools/claims.py render)")
        elif not served.exists() or served.read_text(encoding="utf-8") != text:
            problems.append(f"{rel}: differs from src/{rel} rendered with src/claims-state.json (run python tools/claims.py render)")
    for p in sorted(ROOT.rglob("*.html")):
        if ".git" in p.parts or SRC in p.parents:
            continue
        t = p.read_text(encoding="utf-8")
        if "[Held:" in t or "<!--claim" in t or "<!--page-claim" in t:
            problems.append(f"{p.relative_to(ROOT).as_posix()}: claim marker or block in a served page")
    # Self-tests: a held block falls back, an allowed block shows, a held page disappears, a preview marks.
    probe = {"CL-T1": "Draft", "CL-T2": "Current"}
    sample = '<p><!--claim CL-T1-->new<!--else-->old<!--/claim--> <!--claim CL-T2-->yes<!--/claim--></p>'
    sp = []
    if render_text(sample, probe, False, sp) != "<p>old yes</p>":
        problems.append("claims self-test: publish rendering")
    if render_text(sample, probe, True, sp) != "<p>[Held: CL-T1, Draft] new yes</p>":
        problems.append("claims self-test: preview rendering")
    if render_text('<!--page-claim CL-T1-->\n<main id="main"></main>', probe, False, sp) is not None:
        problems.append("claims self-test: page claim")
    if render_text("<ul><!--claim CL-T1-->  <li>x</li><!--/claim--></ul>", probe, True, sp) != "<ul>  <li>[Held: CL-T1, Draft] x</li></ul>":
        problems.append("claims self-test: preview marker inside the first element")
    for cell, want in (("Current (x)", "Current"), ("Approved wording; **Draft (y)**", "Draft"), ("Current (a) / planned (b)", None)):
        if map_state(cell) != want:
            problems.append(f"claims self-test: mapping {cell!r}")


def cmd_render():
    pages, problems = rendered()
    if problems:
        sys.exit("FAIL " + "\nFAIL ".join(problems))
    for rel, text in pages.items():
        target = ROOT / rel
        if text is None:
            if target.exists():
                target.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
    print(f"rendered {sum(t is not None for t in pages.values())} page(s), held {sum(t is None for t in pages.values())}")


def cmd_preview(dest):
    dest = Path(dest)
    if dest.exists():
        shutil.rmtree(dest)
    files = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True).stdout.split()
    for f in files:
        if f.startswith(("src/", "tools/", "design/")) or f.endswith((".md", ".py", ".yml")):
            continue
        (dest / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / f, dest / f)
    pages, problems = rendered(preview=True)
    for rel, text in pages.items():
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        (dest / rel).write_text(text, encoding="utf-8", newline="\n")
    print(f"preview written: {len(pages)} rendered page(s)" + (f"; {len(problems)} problem(s)" if problems else ""))


def cmd_sync(repo, commit):
    full = subprocess.run(["git", "-C", repo, "rev-parse", "--verify", commit + "^{commit}"], capture_output=True, text=True, check=True).stdout.strip()
    md = subprocess.run(["git", "-C", repo, "show", f"{full}:{REGISTER}"], capture_output=True, text=True, encoding="utf-8", check=True).stdout
    register = parse_register(md)
    used = sorted({m for t in templates() for m in ROW_USE.findall(t.read_text(encoding="utf-8"))})
    mapping = json.loads(MAPPING_FILE.read_text(encoding="utf-8")) if MAPPING_FILE.exists() else {}
    problems, rows = [], {}
    for row in used:
        if row not in register:
            problems.append(f"{row}: used by src/ but not in the register at {full[:8]}")
            continue
        state = mapping.get(row) or map_state(register[row])
        if state not in STATES:
            problems.append(f"{row}: state cell needs a mapping in src/claims-mapping.json: {register[row][:90]!r}")
        else:
            rows[row] = state
    if problems:
        sys.exit("FAIL " + "\nFAIL ".join(problems))
    before = json.loads(STATE_FILE.read_text(encoding="utf-8"))["rows"] if STATE_FILE.exists() else {}
    STATE_FILE.write_text(json.dumps({"register": full, "rows": rows}, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"claims state: {len(rows)} row(s) from register {full[:8]}")
    for row in sorted(set(before) | set(rows)):
        if before.get(row) != rows.get(row):
            print(f"  {row}: {before.get(row, '(new)')} -> {rows.get(row, '(no longer used)')}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["render"]:
        cmd_render()
    elif a[:1] == ["preview"] and len(a) == 2:
        cmd_preview(a[1])
    elif a[:1] == ["sync"] and len(a) == 3:
        cmd_sync(a[1], a[2])
    elif a[:1] == ["check"]:
        p = []
        check(p)
        for x in p:
            print("FAIL", x)
        sys.exit(1 if p else 0)
    else:
        sys.exit(__doc__)
