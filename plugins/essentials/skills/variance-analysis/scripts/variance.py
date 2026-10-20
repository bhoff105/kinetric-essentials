#!/usr/bin/env python3
"""variance.py: budget against actual, the material lines, and a first draft of the commentary.
Part of Kinetric's Essentials pack (MIT). Standard library only.

    python3 variance.py LINES.csv --out DIR [--abs 10000] [--pct 10] [--rule and|or] [--period "September 2026"]

LINES.csv columns (header names are case-insensitive):
    line      the line name as it appears in the pack               (required)
    budget    the budget or forecast figure                         (required)
    actual    the actual figure                                     (required)
    type      revenue, cost, or other: sets favorable/unfavorable (optional; without it, only above/below)
    total     yes on a row that should equal the sum of the others  (optional; tied and reported)
    owner     who to ask about the line                              (optional; named in the draft)

Writes to DIR: variance_table.csv, commentary_draft.md, checks.txt. Never changes an input number.
A line is material when |variance| >= --abs AND |variance %| >= --pct (or OR, with --rule or).

Exit 0: written, totals tie. Exit 1: written, but a total row does not tie or a line has no budget (named in checks.txt
and the draft). Exit 2: the file could not be read or a required column is missing; nothing written.
"""
import argparse
import csv
import os
import sys
from decimal import Decimal, InvalidOperation

TOL = Decimal("0.01")


def num(s, where):
    t = (s or "").strip().replace(",", "").replace("$", "").replace("£", "").replace("€", "")
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()")
    if t == "":
        return None
    try:
        v = Decimal(t)
    except InvalidOperation:
        raise ValueError(f"{where}: '{s}' is not a number")
    return -v if neg else v


def money(v):
    sign = "-" if v < 0 else ""
    return f"{sign}${abs(v):,.0f}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("lines")
    ap.add_argument("--out", required=True)
    ap.add_argument("--abs", type=Decimal, default=Decimal("10000"), help="materiality, absolute (default 10000)")
    ap.add_argument("--pct", type=Decimal, default=Decimal("10"), help="materiality, percent of budget (default 10)")
    ap.add_argument("--rule", choices=["and", "or"], default="and")
    ap.add_argument("--period", default="this period")
    a = ap.parse_args(argv)

    try:
        with open(a.lines, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    except OSError as e:
        print(f"variance: cannot read {a.lines}: {e}", file=sys.stderr)
        return 2
    if not rows:
        print(f"variance: {a.lines} has no rows", file=sys.stderr)
        return 2
    cols = {k.strip().lower(): k for k in rows[0].keys() if k}
    missing = [c for c in ("line", "budget", "actual") if c not in cols]
    if missing:
        print(f"variance: {a.lines} is missing column(s) {', '.join(missing)}; found {', '.join(cols)}", file=sys.stderr)
        return 2
    g = lambda r, c: (r.get(cols[c]) or "").strip() if c in cols else ""

    items, problems = [], []
    for i, r in enumerate(rows, 2):
        name = g(r, "line")
        try:
            b, act = num(g(r, "budget"), f"row {i} budget"), num(g(r, "actual"), f"row {i} actual")
        except ValueError as e:
            print(f"variance: {a.lines} {e}", file=sys.stderr)
            return 2
        typ = g(r, "type").lower() or "other"
        if typ not in ("revenue", "cost", "other"):
            print(f"variance: {a.lines} row {i}: type '{typ}' must be revenue, cost or other", file=sys.stderr)
            return 2
        items.append({"row": i, "line": name, "budget": b, "actual": act, "type": typ,
                      "total": g(r, "total").lower() in ("yes", "y", "true", "1"), "owner": g(r, "owner")})

    for it in items:
        b, act = it["budget"], it["actual"]
        if b is None or act is None:
            it.update(var=None, pct=None, direction="no figure", fav="", material=False)
            problems.append(f"row {it['row']} ({it['line']}): {'budget' if b is None else 'actual'} is blank; no variance computed")
            continue
        var = act - b
        pct = (var / abs(b) * 100) if b != 0 else None
        direction = "above budget" if var > 0 else "below budget" if var < 0 else "on budget"
        if it["type"] == "revenue":
            fav = "favorable" if var > 0 else "unfavorable" if var < 0 else ""
        elif it["type"] == "cost":
            fav = "favorable" if var < 0 else "unfavorable" if var > 0 else ""
        else:
            fav = ""
        big_abs = abs(var) >= a.abs
        big_pct = pct is None or abs(pct) >= a.pct  # no budget: any change is material by % (stated in checks)
        material = (big_abs and big_pct) if a.rule == "and" else (big_abs or big_pct)
        it.update(var=var, pct=pct, direction=direction, fav=fav, material=material and not it["total"])

    # Totals tie: each total row against the sum of the non-total rows above it since the previous total.
    ties = []
    block = []
    for it in items:
        if it["total"]:
            for fld in ("budget", "actual"):
                parts = [x[fld] for x in block if x[fld] is not None]
                s = sum(parts, Decimal(0))
                if it[fld] is None:
                    continue
                diff = it[fld] - s
                ok = abs(diff) <= TOL
                ties.append((it["line"], fld, it[fld], s, diff, ok))
                if not ok:
                    problems.append(f"{it['line']} {fld} is {money(it[fld])} but its lines sum to {money(s)} (a gap of {money(diff)})")
            block = []
        else:
            block.append(it)

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "variance_table.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["line", "type", "budget", "actual", "variance", "variance_pct", "direction", "favorable", "material", "source_row"])
        for it in items:
            w.writerow([it["line"], it["type"], it["budget"] if it["budget"] is not None else "",
                        it["actual"] if it["actual"] is not None else "",
                        it["var"] if it["var"] is not None else "",
                        f"{it['pct']:.1f}" if it["pct"] is not None else "",
                        it["direction"], it["fav"], "yes" if it["material"] else "no", it["row"]])

    mat = [it for it in items if it["material"]]
    mat.sort(key=lambda x: -abs(x["var"]))
    L = [f"# Variance commentary, first draft: {a.period}", ""]
    L.append(f"Materiality: |variance| at least {money(a.abs)} {a.rule} at least {a.pct}% of budget. "
             f"{len(mat)} of {sum(1 for x in items if not x['total'])} lines are material.")
    L.append("")
    for t in [x for x in items if x["total"] and x["var"] is not None]:
        pct = f" ({abs(t['pct']):.1f}%)" if t["pct"] is not None else ""
        L.append(f"- **{t['line']}:** {money(t['actual'])} against a budget of {money(t['budget'])}, "
                 f"{money(abs(t['var']))}{pct} {t['direction']}{', ' + t['fav'] if t['fav'] else ''}.")
    if any(x["total"] for x in items):
        L.append("")
    L.append("## Material lines, largest first")
    L.append("")
    if not mat:
        L.append("None at this threshold.")
    for it in mat:
        pct = f" ({abs(it['pct']):.1f}%)" if it["pct"] is not None else " (no budget to compare)"
        who = it["owner"] or "the line's owner"
        L.append(f"- **{it['line']}:** {money(it['actual'])} against {money(it['budget'])}, "
                 f"{money(abs(it['var']))}{pct} {it['direction']}{', ' + it['fav'] if it['fav'] else ''}. "
                 f"Cause: *not in the data; ask {who}.* (row {it['row']})")
    if problems:
        L += ["", "## Not settled", ""] + [f"- {p}" for p in problems]
    L += ["", "## What this cannot tell you", "",
          "Why a line moved. The figures say how far and which way; the cause is in the business, so each material line "
          "carries a question for its owner. It also doesn't know whether the budget was right, or whether a timing "
          "difference will reverse next month.", ""]
    with open(os.path.join(a.out, "commentary_draft.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))

    C = [f"source: {os.path.basename(a.lines)}", f"rows read: {len(items)}",
         f"lines (not totals): {sum(1 for x in items if not x['total'])}", f"total rows: {sum(1 for x in items if x['total'])}",
         f"material lines: {len(mat)}", f"materiality: abs {a.abs} {a.rule} pct {a.pct}",
         f"typed lines: {sum(1 for x in items if x['type'] != 'other')} (others reported as above/below, not favorable/unfavorable)"]
    for name, fld, v, s, d, ok in ties:
        C.append(f"tie {name} {fld}: page {v} lines {s} gap {d} {'TIES' if ok else 'DOES NOT TIE'}")
    if not ties:
        C.append("tie: no total row given; nothing tied (add a total column marked yes to tie one)")
    C += [f"problem: {p}" for p in problems]
    C.append(f"result: {'PASS' if not problems else 'SEE PROBLEMS'}")
    with open(os.path.join(a.out, "checks.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(C) + "\n")
    print("\n".join(C))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
