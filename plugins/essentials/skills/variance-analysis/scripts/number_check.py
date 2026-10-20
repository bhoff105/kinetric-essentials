#!/usr/bin/env python3
"""number_check.py: every number in a draft must trace to a source. Part of Kinetric's Essentials pack (MIT).

    python3 number_check.py DRAFT.md --source results.csv [--source notes.md ...] [--ignore 2026 ...]

Reads the draft, pulls out every number it states ($1.2M, 12.5%, 4,310, 0.8 points), and looks for each one in the
source files, allowing for the draft's rounding and for K/M/B and percent forms (12.5% matches 0.125 or 12.5).
Prints one line per number: TRACED with where it was found, or NOT FOUND. Years, dates and list numbers are skipped.

Exit 0: every number traced. Exit 1: at least one NOT FOUND (listed). Exit 2: a file could not be read.
It reports. It never edits the draft. Standard library only.
"""
import argparse
import csv
import io
import os
import re
import sys
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

NUM = re.compile(
    r"(?<![\w.])(?P<neg>[-−])?(?P<cur>[$£€])?(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"(?P<suf>\s?(?:[kKmMbB](?![a-zA-Z])|bn(?![a-zA-Z])|million|billion|thousand))?(?P<pct>\s?%| percent| points?| pts?)?")
DATE = re.compile(r"\b\d{4}-\d{2}(?:-\d{2})?\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b")
SCALE = {"k": 1e3, "thousand": 1e3, "m": 1e6, "million": 1e6, "b": 1e9, "bn": 1e9, "billion": 1e9}


def parse(text):
    """Return a list of dicts: value, decimals, scale, pct, raw, line."""
    out = []
    for ln, line in enumerate(text.splitlines(), 1):
        clean = DATE.sub(" ", line)
        clean = re.sub(r"^\s*(?:\d+[.)]|[-*])\s+", " ", clean)  # list markers
        for m in NUM.finditer(clean):
            digits = m.group("num").replace(",", "")
            dec = len(digits.split(".")[1]) if "." in digits else 0
            v = float(digits)
            suf = (m.group("suf") or "").strip().lower()
            pct = bool(m.group("pct")) and "%" in m.group("pct") or (m.group("pct") or "").strip() == "percent"
            pts = bool(m.group("pct")) and not pct
            scale = SCALE.get(suf, 1.0)
            if m.group("neg"):
                v = -v
            # Skip years and very small bare integers (counts in prose like "three", list ordinals) unless marked.
            if not (m.group("cur") or suf or m.group("pct")) and dec == 0 and (1900 <= abs(v) <= 2100):
                continue
            out.append({"value": v, "decimals": dec, "scale": scale, "pct": pct, "pts": pts,
                        "raw": m.group(0).strip(), "line": ln})
    return out


def source_numbers(path):
    """Every number in a source file, with a location label."""
    try:
        with open(path, encoding="utf-8-sig", errors="strict") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        raise SystemExit(f"number_check: cannot read source {path}: {e}")
    found = []
    name = os.path.basename(path)
    if path.lower().endswith(".csv"):
        rows = list(csv.reader(io.StringIO(text)))
        head = rows[0] if rows else []
        for r, row in enumerate(rows[1:], 2):
            for c, cell in enumerate(row):
                for n in parse(cell):
                    col = head[c] if c < len(head) else f"col{c + 1}"
                    found.append((n["value"] * n["scale"], f"{name} row {r} {col}"))
    else:
        for n in parse(text):
            found.append((n["value"] * n["scale"], f"{name} line {n['line']}"))
    return found


def matches(n, src):
    """Does source value src, shown at the draft's precision and scale, equal the draft's number?"""
    shown = n["value"]
    cands = [src, abs(src)]
    if n["pct"] or n["pts"]:
        cands += [src * 100, abs(src) * 100]
    q = Decimal(1).scaleb(-n["decimals"])
    want = {Decimal(repr(shown)).quantize(q, ROUND_HALF_UP), Decimal(repr(abs(shown))).quantize(q, ROUND_HALF_UP)}
    for s in cands:
        scaled = Decimal(repr(s)) / Decimal(repr(n["scale"]))
        # People round half up (41.25 shows as 41.3); some tools round half to even. Accept either.
        if scaled.quantize(q, ROUND_HALF_UP) in want or scaled.quantize(q, ROUND_HALF_EVEN) in want:
            return True
    return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("draft")
    ap.add_argument("--source", action="append", required=True, help="a file the numbers should come from; repeat")
    ap.add_argument("--ignore", action="append", default=[], help="a number to skip, as written in the draft")
    a = ap.parse_args(argv)
    try:
        draft = open(a.draft, encoding="utf-8-sig").read()
    except OSError as e:
        print(f"number_check: cannot read draft {a.draft}: {e}", file=sys.stderr)
        return 2
    try:
        pool = [x for p in a.source for x in source_numbers(p)]
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2
    nums = [n for n in parse(draft) if n["raw"] not in a.ignore]
    missing = 0
    for n in nums:
        hit = next((loc for v, loc in pool if matches(n, v)), None)
        if hit:
            print(f"TRACED     line {n['line']:>3}  {n['raw']:<14} {hit}")
        else:
            missing += 1
            print(f"NOT FOUND  line {n['line']:>3}  {n['raw']:<14} in no source")
    print(f"number_check: {len(nums)} numbers in the draft, {len(nums) - missing} traced, {missing} not found; "
          f"{len(pool)} numbers read from {len(a.source)} source file(s)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
