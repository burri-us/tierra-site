"""Font-face coverage check for the Tierra LLC site (standard library only).

Every (font family, font weight) that the CSS actually applies to text must have a shipped font file, that is an
@font-face for that family and weight in assets/tokens.css. A weight without a file is silently replaced by the
nearest shipped one (bolder from 400 asks for 700, a 500 asks for 400), so the page does not look as the CSS says.

The check resolves the cascade per element: browser defaults < presentation attributes < site CSS (specificity, then
source order, !important last). Covered: comma lists of descendant and child chains of compounds made of tag, .class,
#id, [attr] and [attr="v"]; var() with fallback; normal, bold, bolder, lighter, inherit and numbers; font-weight and
font-family inheritance. Rules with state pseudo-classes or pseudo-elements are dropped (they do not change weight
or family here); any other selector form is counted as unsupported and skipped.
"""
import re
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
SKIP_TEXT = {"style", "script", "title", "desc", "head", "noscript"}
STATE = re.compile(r":(hover|focus|focus-visible|focus-within|active|visited|link|target|checked|disabled|enabled)\b"
                   r"|::?(before|after|first-line|first-letter|selection|placeholder|marker|backdrop)\b")
# Browser defaults (user-agent stylesheet) that matter for weight and family.
UA_WEIGHT = {**{f"h{i}": "bold" for i in range(1, 7)}, "th": "bold", "b": "bolder", "strong": "bolder"}
UA_FAMILY = {t: "monospace" for t in ("pre", "code", "kbd", "samp", "tt")}
COMPOUND = re.compile(r"(?:[A-Za-z][\w-]*|\*)?(?:\.[\w-]+|#[\w-]+|\[[\w-]+(?:=\"[^\"]*\")?\])*")


def blocks(css, out):
    """Collect (head, body) of every rule; rules inside @media and @supports are kept (conservatively all of them)."""
    i = 0
    while i < len(css):
        j = css.find("{", i)
        if j < 0:
            break
        head = css[i:j].strip()
        depth, k = 1, j + 1
        while k < len(css) and depth:
            depth += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        body = css[j + 1:k - 1]
        if head.startswith(("@media", "@supports")):
            blocks(body, out)
        else:
            out.append((head, body))
        i = k


def decls(body):
    out = {}
    for part in body.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def parse_selector(sel):
    """-> (chain, specificity) with chain = [(combinator, compound)], or None when unsupported."""
    chain, comb = [], " "
    ids = cls = tags = 0
    for t in re.findall(r"\s*>\s*|\s+|[^\s>]+", sel.strip()):
        if t.strip() == ">":
            comb = ">"
            continue
        if not t.strip():
            continue
        if not COMPOUND.fullmatch(t):
            return None
        tag = re.match(r"[A-Za-z][\w-]*", t)
        classes = re.findall(r"\.([\w-]+)", t)
        idm = re.findall(r"#([\w-]+)", t)
        attrs = [(m[0], m[1] if m[1] else None) for m in re.findall(r"\[([\w-]+)(?:=\"([^\"]*)\")?\]", t)]
        chain.append((comb, (tag.group(0).lower() if tag else None, classes, idm, attrs)))
        comb = " "
        ids += len(idm)
        cls += len(classes) + len(attrs)
        tags += 1 if tag else 0
    return (chain, (ids, cls, tags)) if chain else None


class Stylesheet:
    def __init__(self, root):
        self.faces = {}           # family -> set of weights
        self.props = {}           # :root custom properties
        self.rules = []           # (specificity, order, chain, {prop: value})
        self.unsupported = []
        self.dropped = 0
        order = 0
        for name in ("tokens.css", "site.css"):
            css = re.sub(r"/\*.*?\*/", "", (root / "assets" / name).read_text(encoding="utf-8"), flags=re.S)
            rules = []
            blocks(css, rules)
            for sel, body in rules:
                d = decls(body)
                if sel == "@font-face":
                    fam = d.get("font-family", "").strip("\"' ")
                    for w in re.findall(r"\d+", d.get("font-weight", "")):
                        self.faces.setdefault(fam, set()).add(int(w))
                    continue
                if sel.startswith("@"):
                    continue
                if sel == ":root":
                    self.props.update({k: v for k, v in d.items() if k.startswith("--")})
                font = {k: v for k, v in d.items() if k in ("font-weight", "font-family")}
                if not font:
                    continue
                for one in (s.strip() for s in sel.split(",")):
                    order += 1
                    if STATE.search(one):
                        self.dropped += 1
                        continue
                    parsed = parse_selector(one)
                    if parsed is None:
                        self.unsupported.append(one)
                        continue
                    self.rules.append((parsed[1], order, parsed[0], font))


class El:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.classes = (self.attrs.get("class") or "").split()
        self.text = False
        self.weight = self.family = None


def match_compound(el, c):
    tag, classes, ids, attrs = c
    if tag and tag != el.tag:
        return False
    if any(x not in el.classes for x in classes) or any(el.attrs.get("id") != i for i in ids):
        return False
    return all(n in el.attrs and (v is None or el.attrs[n] == v) for n, v in attrs)


def match(el, chain):
    comb, comp = chain[-1]
    if not match_compound(el, comp):
        return False
    if len(chain) == 1:
        return True
    if comb == ">":
        return el.parent is not None and match(el.parent, chain[:-1])
    p = el.parent
    while p is not None:
        if match(p, chain[:-1]):
            return True
        p = p.parent
    return False


def resolve_var(value, props, depth=0):
    def sub(m):
        name, fb = m.group(1), m.group(2)
        if name in props and depth < 10:
            return resolve_var(props[name], props, depth + 1)
        return resolve_var(fb, props, depth + 1) if fb is not None else m.group(0)
    return re.sub(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)", sub, value)


def weight_value(v, parent_w):
    v = v.strip().lower()
    if v in ("normal", "initial"):
        return 400
    if v == "bold":
        return 700
    if v == "bolder":
        return 400 if parent_w < 350 else 700 if parent_w < 550 else 900
    if v == "lighter":
        return 100 if parent_w < 550 else 400 if parent_w < 750 else 700
    if v in ("inherit", "unset"):
        return parent_w
    return int(v) if re.fullmatch(r"\d+", v) else None


class Page(HTMLParser):
    def __init__(self, sheet):
        super().__init__(convert_charrefs=True)
        self.sheet, self.stack, self.elements, self.unresolved = sheet, [], [], []

    def handle_starttag(self, tag, attrs):
        el = El(tag, attrs, self.stack[-1] if self.stack else None)
        self.compute(el)
        self.elements.append(el)
        if tag not in VOID:
            self.stack.append(el)

    def handle_startendtag(self, tag, attrs):
        el = El(tag, attrs, self.stack[-1] if self.stack else None)
        self.compute(el)
        self.elements.append(el)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if data.strip() and self.stack:
            el, a = self.stack[-1], self.stack[-1]
            while a is not None and a.tag not in SKIP_TEXT:
                a = a.parent
            if a is None:
                el.text = True

    def compute(self, el):
        props = self.sheet.props
        pw = el.parent.weight if el.parent else 400
        pf = el.parent.family if el.parent else None
        cands = {"font-weight": [], "font-family": []}
        if el.tag in UA_WEIGHT:
            cands["font-weight"].append(((0,), UA_WEIGHT[el.tag]))
        if el.tag in UA_FAMILY:
            cands["font-family"].append(((0,), UA_FAMILY[el.tag]))
        for k in cands:
            if k in el.attrs:
                cands[k].append(((1,), el.attrs[k]))      # presentation attribute: below all author CSS
        for spec, order, chain, font in self.sheet.rules:
            if match(el, chain):
                for k, v in font.items():
                    imp = 1 if "!important" in v else 0
                    cands[k].append(((2 + imp, spec, order), v.replace("!important", "").strip()))
        el.weight, el.family = pw, pf
        if cands["font-weight"]:
            raw = max(cands["font-weight"], key=lambda c: c[0])[1]
            w = weight_value(resolve_var(raw, props), pw)
            if w is None:
                self.unresolved.append(f"<{el.tag}> font-weight {raw} could not be resolved")
            else:
                el.weight = w
        if cands["font-family"]:
            raw = resolve_var(max(cands["font-family"], key=lambda c: c[0])[1], props)
            el.family = pf if raw.strip().lower() in ("inherit", "unset") else raw.split(",")[0].strip().strip("\"'").strip()


def check_font_faces(root, problems):
    """Append one problem per (page, element, family, weight) without a shipped font file; print coverage."""
    sheet = Stylesheet(root)
    pages = sorted(p for p in root.rglob("*.html") if ".git" not in p.parts)
    seen, checked = {}, 0
    for page in pages:
        rel = page.relative_to(root).as_posix()
        parser = Page(sheet)
        parser.feed(page.read_text(encoding="utf-8"))
        for u in sorted(set(parser.unresolved)):
            problems.append(f"{rel}: {u}")
        for el in parser.elements:
            if not el.text:
                continue
            checked += 1
            fam, w = el.family or "(browser default)", el.weight
            have = sheet.faces.get(fam)
            if have is None:
                msg = f"{fam} has no shipped font file at all"
            elif w not in have:
                msg = f"{fam} {w} has no shipped font file (shipped: {', '.join(map(str, sorted(have)))})"
            else:
                continue
            name = el.tag + "".join("." + c for c in el.classes)
            seen[(rel, name, msg)] = seen.get((rel, name, msg), 0) + 1
    for (rel, name, msg), n in sorted(seen.items()):
        problems.append(f"{rel}: <{name}>: {msg}" + (f" [{n} elements]" if n > 1 else ""))
    print(f"font-face check: {checked} text elements in {len(pages)} pages, {len(sheet.rules)} font rules used, "
          f"{len(sheet.unsupported)} unsupported selector(s) skipped, {sheet.dropped} state/pseudo-element selector(s) dropped")
