#!/usr/bin/env python3
"""Regression net for the chronicle skill itself.

Validates the skill's structural integrity and runs the conformance goldens.
This is dev-tooling for the chronicle REPO (run in CI / by contributors); it is
NOT the KB checker that runs in user projects — the runtime assets stay
solo-markdown. Stdlib only, no dependencies.

Usage:  python3 tests/check_skill.py [--root <repo_root>]
Exit 0 if every check passes, 1 otherwise.
"""
import sys
import os
import re
import json
import glob
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "--root" in sys.argv:
    ROOT = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])


def p(*parts):
    return os.path.join(ROOT, *parts)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# --- Golden #1: KB conformance (citation coverage + cross-ref) ---------------
def golden_kb():
    kb = p("assets", "conformance", "sample-kb")
    CITE = re.compile(r"\[(code|doc|user|inferred) · ([^\]]+)\]")
    CLAIM = re.compile(r"^\s*-\s+\*\*([A-Z]{2,}-[A-Z]+-\d+)\*\*")
    claims = cited = 0
    uncited, defined = [], set()
    for f in sorted(glob.glob(kb + "/0[45678]_*.md")):
        for line in read(f).splitlines():
            m = CLAIM.match(line)
            if m:
                claims += 1
                defined.add(m.group(1))
                if CITE.search(line):
                    cited += 1
                else:
                    uncited.append(m.group(1))
    broken = []
    RN = re.compile(r"(RN-[A-Z]+-\d+)")
    for f in sorted(glob.glob(kb + "/0[67]_*.md")):
        us = None
        for line in read(f).splitlines():
            h = re.match(r"^###\s+(US-\d+)", line)
            if h:
                us = h.group(1)
            for c in RN.findall(line):
                if c not in defined:
                    broken.append("%s → %s" % (us, c))
    got = {
        "citation_coverage": {"claims": claims, "cited": cited,
                              "uncited": len(uncited),
                              "value": round(cited / claims, 2),
                              "uncited_items": uncited},
        "cross_ref": {"broken": len(broken), "items": broken},
    }
    exp = json.loads(read(p("assets", "conformance", "expected.json")))
    return got == exp, "got=%s" % json.dumps(got, ensure_ascii=False)


# --- Golden #2: fingerprint normalization + hash ----------------------------
def golden_fingerprint():
    d = p("assets", "conformance", "fingerprint")
    src = read(os.path.join(d, "sample.js"))
    nocom = "\n".join(re.sub(r"//.*$", "", l) for l in src.splitlines())
    norm = re.sub(r"\s+", " ", nocom).strip()
    exp = json.loads(read(os.path.join(d, "expected.json")))
    ok = (norm == exp["normalized"]
          and hashlib.sha256(norm.encode()).hexdigest() == exp["fingerprint"])
    return ok, "normalized/hash %s" % ("match" if ok else "MISMATCH")


# --- Golden #3: citation -> trace-map resolution -----------------------------
def golden_trace_map():
    d = p("assets", "conformance", "trace-map")
    idx = {(r["file"], r["symbol"])
           for r in json.loads(read(os.path.join(d, "trace-map.json")))["rows"]}
    CODE = re.compile(r"\[code · ([^\]]+)\]")
    cc = res = 0
    orph = []
    for line in read(os.path.join(d, "05_reglas.md")).splitlines():
        for anchor in CODE.findall(line):
            cc += 1
            f, _, s = anchor.split(" ~L")[0].partition("#")
            if (f, s) in idx:
                res += 1
            else:
                orph.append("%s#%s" % (f, s))
    got = {"code_citations": cc, "resolved": res,
           "orphans": len(orph), "orphan_items": orph}
    exp = json.loads(read(os.path.join(d, "expected.json")))
    return got == exp, "got=%s" % json.dumps(got, ensure_ascii=False)


# --- Structural: every assets/* path referenced anywhere must exist ----------
def asset_links():
    PATH = re.compile(r"assets/[\w./-]+\.(?:md|json|js)")
    files = [p("SKILL.md"), p("README.md")] + glob.glob(p("assets", "**", "*.md"),
                                                         recursive=True)
    missing = set()
    for f in files:
        for ref in PATH.findall(read(f)):
            if not os.path.exists(p(ref)):
                missing.add(ref)
    return not missing, ("all asset refs resolve" if not missing
                         else "missing: %s" % sorted(missing))


# --- Structural: frontmatter has the required fields -------------------------
def frontmatter():
    text = read(p("SKILL.md"))
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return False, "no frontmatter block"
    fm = m.group(1)
    missing = [k for k in ("name:", "description:", "version:") if k not in fm]
    return not missing, ("name/description/version present" if not missing
                         else "missing: %s" % missing)


# --- Structural: SKILL.md version == README badge version --------------------
def version_consistency():
    sk = re.search(r'version:\s*"([^"]+)"', read(p("SKILL.md")))
    rd = re.search(r"version-([0-9.]+)-green", read(p("README.md")))
    if not sk or not rd:
        return False, "version not found (skill=%s readme=%s)" % (sk, rd)
    return sk.group(1) == rd.group(1), "skill=%s readme=%s" % (sk.group(1), rd.group(1))


# --- Anti-drift: forbidden stale phrases must not reappear -------------------
def no_stale_phrases():
    forbidden = ["10 canonical nodes", "10 nodos canónicos",
                 "10 nodos obligatorios", "10 obligatorios"]
    hits = []
    for f in [p("SKILL.md"), p("README.md")] + glob.glob(p("assets", "**", "*.md"),
                                                          recursive=True):
        text = read(f)
        for phrase in forbidden:
            if phrase in text:
                hits.append("%s: '%s'" % (os.path.relpath(f, ROOT), phrase))
    return not hits, ("no stale phrases" if not hits else "; ".join(hits))


CHECKS = [
    ("golden: KB conformance", golden_kb),
    ("golden: fingerprint", golden_fingerprint),
    ("golden: trace-map resolution", golden_trace_map),
    ("links: asset references resolve", asset_links),
    ("structure: frontmatter fields", frontmatter),
    ("structure: version consistency", version_consistency),
    ("anti-drift: no stale phrases", no_stale_phrases),
]


def main():
    failed = 0
    print("chronicle skill regression net  (root: %s)\n" % ROOT)
    for name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:  # a check that throws is a failure, not a crash
            ok, detail = False, "EXCEPTION: %s" % e
        print("  %s  %-34s  %s" % ("PASS" if ok else "FAIL", name, detail))
        if not ok:
            failed += 1
    print("\n%d/%d checks passed." % (len(CHECKS) - failed, len(CHECKS)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
