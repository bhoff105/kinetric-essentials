#!/usr/bin/env python3
"""drivers.py: where did the number move? Break a change between two periods down by segment, and check it adds up.
Part of Kinetric's Essentials pack (MIT). Standard library only.

Additive metric (revenue, orders, cost):
    python3 drivers.py DATA.csv --period-col month --from 2026-08 --to 2026-09 --value revenue --dims channel,region --out DIR
Rate metric (conversion = orders / sessions), split into mix and rate effects:
    python3 drivers.py DATA.csv --period-col month --from 2026-08 --to 2026-09 --numerator orders --denominator sessions --dims channel --out DIR

DATA.csv is long: one row per period and segment, with the dimension columns and the number column(s). Rows of the same
period and segment are summed.

For each dimension on its own: every segment's contribution to the change, ranked, with its share of the change.
Additive: contribution = segment(to) - segment(from). Rate: change in overall rate = sum of mix effects
(share change x how far the segment's old rate sat from the old average) + sum of rate effects (new share x the
segment's rate change). A segment that grows its share while converting above average lifts the rate through mix. A
segment new in the second period is measured against the old average. Both decompositions add back to the total
exactly, and the script checks that they do.

A comma is read only as a thousands separator; a decimal comma stops the run (exit 2). A blank number cell in either
period is read as 0, counted in checks.txt and reported as a problem.

Writes to DIR: drivers.md, drivers.csv, checks.txt. Exit 0: written, every decomposition adds up. Exit 1: written, but
something is off (named): a breakdown doesn't add up, or a number cell is blank. Exit 2: unreadable input, a missing
column, a figure that is not a number, or a period with no rows; nothing written.
"""
import argparse
import csv
import os
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation

TOL = Decimal("0.000001")


def d(s, where):
    t = (s or "").strip().replace("$", "")
    if t == "":
        return Decimal(0)
    if "," in t:
        if not re.fullmatch(r"[-+]?\d{1,3}(,\d{3})+(\.\d+)?", t):
            raise ValueError(f"{where}: '{s}' has a comma that is not a thousands separator (a decimal comma is not read)")
        t = t.replace(",", "")
    try:
        v = Decimal(t)
    except InvalidOperation:
        raise ValueError(f"{where}: '{s}' is not a number")
    if not v.is_finite():
        raise ValueError(f"{where}: '{s}' is not a number")
    return v


def q(v):
    return v.quantize(Decimal("0.000001")) if v == v else v


def fmt(v, rate=False):
    if rate:
        return f"{v * 100:.2f}%"
    if abs(v) >= 1000 or v == v.to_integral_value():
        return f"{v:,.0f}"
    return f"{v:,.2f}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("data")
    ap.add_argument("--period-col", required=True)
    ap.add_argument("--from", dest="p0", required=True)
    ap.add_argument("--to", dest="p1", required=True)
    ap.add_argument("--value")
    ap.add_argument("--numerator")
    ap.add_argument("--denominator")
    ap.add_argument("--dims", required=True, help="comma-separated dimension columns")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rate = bool(a.numerator or a.denominator)
    if rate and not (a.numerator and a.denominator):
        print("drivers: a rate needs both --numerator and --denominator", file=sys.stderr)
        return 2
    if not rate and not a.value:
        print("drivers: give --value for an additive metric, or --numerator and --denominator for a rate", file=sys.stderr)
        return 2
    dims = [x.strip() for x in a.dims.split(",") if x.strip()]
    try:
        with open(a.data, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        print(f"drivers: cannot read {a.data} (save it as UTF-8 CSV): {e}", file=sys.stderr)
        return 2
    need = [a.period_col] + dims + ([a.numerator, a.denominator] if rate else [a.value])
    have = set(rows[0].keys()) if rows else set()
    miss = [c for c in need if c not in have]
    if miss:
        print(f"drivers: {a.data} is missing column(s) {', '.join(miss)}", file=sys.stderr)
        return 2
    sel = {a.p0: [], a.p1: []}
    for i, r in enumerate(rows, 2):
        p = (r[a.period_col] or "").strip()  # a short row reads its missing cells as None
        if p in sel:
            sel[p].append((i, r))
    for p, rs in sel.items():
        if not rs:
            print(f"drivers: no rows for period '{p}' in column {a.period_col}", file=sys.stderr)
            return 2
    other = len(rows) - len(sel[a.p0]) - len(sel[a.p1])
    num_cols = [a.numerator, a.denominator] if rate else [a.value]
    blanks = {c: [i for p in (a.p0, a.p1) for i, r in sel[p] if (r[c] or "").strip() == ""] for c in num_cols}

    def tot(p, col):
        return sum((d(r[col], f"row {i} {col}") for i, r in sel[p]), Decimal(0))

    try:
        if rate:
            N0, N1, D0, D1 = tot(a.p0, a.numerator), tot(a.p1, a.numerator), tot(a.p0, a.denominator), tot(a.p1, a.denominator)
            if D0 == 0 or D1 == 0:
                print("drivers: the denominator totals zero in one period; the rate is undefined", file=sys.stderr)
                return 2
            T0, T1 = N0 / D0, N1 / D1
        else:
            T0, T1 = tot(a.p0, a.value), tot(a.p1, a.value)
    except ValueError as e:
        print(f"drivers: {e}", file=sys.stderr)
        return 2
    change = T1 - T0
    problems, tables, csv_rows = [], {}, []
    for c, at in blanks.items():
        if at:
            shown = ", ".join(str(i) for i in at[:10]) + (" ..." if len(at) > 10 else "")
            problems.append(f"{len(at)} blank cell(s) in {c} (row {shown}), read as 0; fill them or confirm they are zero")

    for dim in dims:
        seg = defaultdict(lambda: {"n0": Decimal(0), "n1": Decimal(0), "d0": Decimal(0), "d1": Decimal(0)})
        for p, key in ((a.p0, "0"), (a.p1, "1")):
            for i, r in sel[p]:
                s = (r[dim] or "").strip() or "(blank)"
                if rate:
                    seg[s]["n" + key] += d(r[a.numerator], f"row {i}")
                    seg[s]["d" + key] += d(r[a.denominator], f"row {i}")
                else:
                    seg[s]["n" + key] += d(r[a.value], f"row {i}")
        out = []
        for s, v in seg.items():
            if rate:
                w0, w1 = v["d0"] / D0, v["d1"] / D1
                r0 = v["n0"] / v["d0"] if v["d0"] else None
                r1 = v["n1"] / v["d1"] if v["d1"] else None
                base = r0 if r0 is not None else T0  # a new segment is measured against the old average
                mix = (w1 - w0) * (base - T0)  # sums to the same total because both shares sum to 1
                rt = w1 * ((r1 if r1 is not None else base) - base)
                # Lost segment: w1 = 0, so the rate term is 0 and its whole effect is mix.
                out.append({"seg": s, "from": r0, "to": r1, "mix": mix, "rate": rt, "contrib": mix + rt,
                            "status": "new" if r0 is None else "gone" if r1 is None else ""})
            else:
                c = v["n1"] - v["n0"]
                out.append({"seg": s, "from": v["n0"], "to": v["n1"], "contrib": c,
                            "status": "new" if v["n0"] == 0 and v["n1"] != 0 else "gone" if v["n1"] == 0 and v["n0"] != 0 else ""})
        out.sort(key=lambda x: (-abs(x["contrib"]), x["seg"]))
        s_sum = sum((x["contrib"] for x in out), Decimal(0))
        gap = s_sum - change
        if abs(gap) > TOL:
            problems.append(f"{dim}: segment contributions sum to {s_sum} but the total changed by {change}")
        tables[dim] = (out, gap)
        for x in out:
            share = (x["contrib"] / change * 100) if change else None
            csv_rows.append([dim, x["seg"], x["status"],
                             "" if x["from"] is None else x["from"], "" if x["to"] is None else x["to"],
                             x.get("mix", ""), x.get("rate", ""), x["contrib"],
                             "" if share is None else f"{share:.2f}", ""])

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "drivers.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["dimension", "segment", "status", "from", "to", "mix_effect", "rate_effect", "contribution", "share_of_change_pct", "pct_change"])
        w.writerow(["(total)", "all", "", T0, T1, "", "", change, "100", f"{change / T0 * 100:.2f}" if (T0 and not rate) else ""])
        w.writerows(csv_rows)

    name = f"{a.numerator} / {a.denominator}" if rate else a.value
    pct = f" ({change / T0 * 100:+.1f}%)" if (T0 and not rate) else ""
    move = f"{fmt(T0, rate)} to {fmt(T1, rate)}, a change of {('%+.2f points' % (change * 100)) if rate else fmt(change)}{pct}"
    L = [f"# What moved {name}: {a.p0} to {a.p1}", "", f"**{name}** went from {move}.", ""]
    for dim, (out, gap) in tables.items():
        L.append(f"## By {dim}")
        L.append("")
        if rate:
            L.append("| Segment | Rate before | Rate after | Mix effect (points) | Rate effect (points) | Total (points) | Share of change |")
            L.append("|---|---|---|---|---|---|---|")
        else:
            L.append("| Segment | Before | After | Contribution | Share of change |")
            L.append("|---|---|---|---|---|")
        for x in out[: a.top]:
            share = f"{x['contrib'] / change * 100:.0f}%" if change else "n/a"
            tag = f" ({x['status']})" if x["status"] else ""
            if rate:
                L.append(f"| {x['seg']}{tag} | {'-' if x['from'] is None else fmt(x['from'], True)} | "
                         f"{'-' if x['to'] is None else fmt(x['to'], True)} | {x['mix'] * 100:+.2f} | {x['rate'] * 100:+.2f} | "
                         f"{x['contrib'] * 100:+.2f} | {share} |")
            else:
                L.append(f"| {x['seg']}{tag} | {fmt(x['from'])} | {fmt(x['to'])} | {fmt(x['contrib'])} | {share} |")
        if len(out) > a.top:
            rest = sum((x["contrib"] for x in out[a.top:]), Decimal(0))
            L.append(f"| {len(out) - a.top} others | | | {('%+.2f' % (rest * 100)) if rate else fmt(rest)} | |")
        top = out[0] if out else None
        if top and change:
            L.append("")
            L.append(f"Largest: **{top['seg']}**, {top['contrib'] / change * 100:.0f}% of the change.")
        L.append("")
    if problems:
        L += ["## Not settled", ""] + [f"- {p}" for p in problems] + [""]
    L += ["## What this cannot tell you", "",
          "Why each segment moved. The breakdown shows where the change sits and, for a rate, how much came from the mix "
          "shifting and how much from the segments themselves. Each dimension is read on its own, so overlaps between "
          "dimensions (a channel that is mostly one region) aren't split out. Where a change sits is not what caused it.", ""]
    with open(os.path.join(a.out, "drivers.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))

    C = [f"source: {os.path.basename(a.data)}", f"rows read: {len(rows)}",
         f"rows in {a.p0}: {len(sel[a.p0])}", f"rows in {a.p1}: {len(sel[a.p1])}", f"rows in other periods (ignored): {other}",
         *[f"blank cells, {c}: {len(at)}" for c, at in blanks.items()],
         *[f"blank {dim} cells, grouped as '(blank)': {n}" for dim in dims
           if (n := sum(1 for p in (a.p0, a.p1) for _, r in sel[p] if not (r[dim] or "").strip()))],
         f"metric: {'rate ' if rate else 'additive '}{name}", f"total {a.p0}: {q(T0)}", f"total {a.p1}: {q(T1)}", f"change: {q(change)}"]
    for dim, (out, gap) in tables.items():
        C.append(f"adds up, {dim}: {len(out)} segments, gap {q(gap)} {'OK' if abs(gap) <= TOL else 'FAIL'}")
    C += [f"problem: {p}" for p in problems]
    C.append(f"result: {'PASS' if not problems else 'SEE PROBLEMS'}")
    with open(os.path.join(a.out, "checks.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(C) + "\n")
    print("\n".join(C))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
