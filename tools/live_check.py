#!/usr/bin/env python3
"""Live checks around a tierra-llc.com release (standard library only). Reads the public site; changes nothing.

Usage: python tools/live_check.py save <dir>        save every file the site serves (from this checkout's file list) as
                                                    served live now, into <dir> (the copy taken before the release)
       python tools/live_check.py compare           every served file of this checkout must be served live byte for byte,
                                                    and a missing page must answer 404
       python tools/live_check.py diff <dirA> <dirB> list the files that differ between two saved copies
Origin: https://tierra-llc.com, or the LIVE_ORIGIN environment variable.
"""
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import ROOT, jekyll_excludes, served  # noqa: E402

ORIGIN = os.environ.get("LIVE_ORIGIN", "https://tierra-llc.com").rstrip("/")

def files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    return sorted(f for f in served(out, jekyll_excludes()) if f != "CNAME")

def url_path(f):
    return "/" + (f[: -len("index.html")] if f.endswith("index.html") else f)

def get(path):
    req = urllib.request.Request(ORIGIN + path, headers={"Cache-Control": "no-cache", "User-Agent": "site-live-check"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    problems = []
    if mode == "save" and len(argv) == 3:
        d = Path(argv[2])
        for f in files():
            status, body = get(url_path(f))
            (d / f).parent.mkdir(parents=True, exist_ok=True)
            (d / f).write_bytes(body)
            if status != 200:
                problems.append(f"{url_path(f)}: live status {status}")
        print(f"saved {len(files())} files from {ORIGIN} into {d}")
    elif mode == "compare":
        for f in files():
            status, body = get(url_path(f))
            if status != 200:
                problems.append(f"{url_path(f)}: live status {status}")
            elif body != (ROOT / f).read_bytes():
                problems.append(f"{url_path(f)}: live content differs from {f}")
        status, _ = get("/no-such-page/")
        if status != 404:
            problems.append(f"/no-such-page/: live status {status}, expected 404")
        print(f"compared {len(files())} files with {ORIGIN}")
    elif mode == "diff" and len(argv) == 4:
        a, b = Path(argv[2]), Path(argv[3])
        names = sorted({str(p.relative_to(a)) for p in a.rglob("*") if p.is_file()} | {str(p.relative_to(b)) for p in b.rglob("*") if p.is_file()})
        for n in names:
            pa, pb = a / n, b / n
            if not pa.exists() or not pb.exists() or pa.read_bytes() != pb.read_bytes():
                print(f"differs: {n}")
        return 0
    else:
        print(__doc__)
        return 2
    for p in problems:
        print("FAIL", p)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
