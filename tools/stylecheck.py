"""DEC-674 (owner): public text is US English, plain and human-written (standard library only; called by tools/check.py).

In visible text, the title, the meta description and alt text of every served page: no em dash, no spaced en dash used as
punctuation, no arrows or middle dots as separators, and no British spellings. Text inside <code> and <pre> (a command or file
name quoted exactly, and the font licence texts on the notices page) is exempt.
"""
import html as htmllib
import re

RULES = [
    ("em dash", re.compile("—")),
    ("en dash used as punctuation", re.compile(r"\s–\s")),
    ("arrow", re.compile("[←-↓⇐-⇔➔⟵⟶]")),
    ("middle dot separator", re.compile(r"\s·\s")),
    ("British spelling", re.compile(r"\b(licence\w*|organis\w*|personalis\w*|behaviour\w*|colour\w*|favour\w*|recognis\w*|"
                                    r"analys(?:e|ed|es|ing)|cancell(?:ed|ing)|labell(?:ed|ing)|modell(?:ed|ing)|travell(?:ed|ing)|"
                                    r"centre[sd]?|catalogue[sd]?|programme[sd]?|whilst|amongst|defence|judgement|enrolment|fulfil|fulfilment)\b", re.I)),
]


def public_text(page):
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", page, flags=re.S | re.I)
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    body = re.sub(r"<(code|pre)\b.*?</\1>", " ", body, flags=re.S | re.I)
    attrs = re.findall(r'<meta\s+name="description"\s+content="([^"]*)"|\salt="([^"]*)"|<title>([^<]*)</title>', body, re.I)
    visible = body.split("</head>", 1)[-1]   # the title and meta description are taken once, from attrs
    text = re.sub(r"<[^>]+>", " ", visible) + " " + " ".join(a or b or c for a, b, c in attrs)
    return re.sub(r"\s+", " ", htmllib.unescape(text))


def problems_in(text):
    out = []
    for name, rx in RULES:
        for m in rx.finditer(text):
            out.append(f'{name} "{text[max(0, m.start() - 25):m.end() + 25].strip()}"')
    return out


def check_style(root, pages, problems):
    for page in pages:
        rel = page.relative_to(root).as_posix()
        if rel.startswith("src/"):
            continue   # templates are checked through the pages rendered from them
        for p in problems_in(public_text(page.read_text(encoding="utf-8"))):
            problems.append(f"{rel}: style (DEC-674): {p}")
    # Self-tests: planted problems are caught; plain US text, a range with an en dash and code are not.
    for t in ("Tierra — tools", "a – b", "Next → step", "About · Tierra", "our organisation", "the licence", "colours"):
        if not problems_in(t):
            problems.append(f"style check: planted {t!r} was not caught")
    for t in ("our organization", "the license", "pages 9–12", public_text("<p>see <pre>licence text</pre></p>")):
        if problems_in(t):
            problems.append(f"style check: {t!r} was caught")
