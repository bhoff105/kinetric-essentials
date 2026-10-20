#!/usr/bin/env python3
"""Known-answer tests for root-cause-analysis. python3 test_drivers.py (exit 0 = pass)."""
import contextlib
import csv
import io
import os
import sys
import tempfile
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drivers  # noqa: E402
import number_check  # noqa: E402

DATA = os.path.join(HERE, "..", "references", "example", "traffic.csv")
fails = 0


def ok(cond, msg):
    global fails
    print(("ok   " if cond else "FAIL ") + msg)
    fails += 0 if cond else 1


def run(mod, *args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return mod.main(list(args))


def table(d):
    with open(os.path.join(d, "drivers.csv"), encoding="utf-8") as f:
        return {(r["dimension"], r["segment"]): r for r in csv.DictReader(f)}


BASE = ["--period-col", "month", "--from", "2026-08", "--to", "2026-09"]
with tempfile.TemporaryDirectory() as d:
    code = run(drivers, DATA, *BASE, "--value", "revenue", "--dims", "channel,device", "--out", d)
    t = table(d)
    ok(code == 0, "additive run is clean")
    want = {"Paid search": 56800, "Affiliate": 16000, "Email": -2200, "Organic": 0}
    ok(all(Decimal(t[("channel", k)]["contribution"]) == v for k, v in want.items()), "channel contributions match the hand-worked answers")
    ok(t[("channel", "Affiliate")]["status"] == "new", "a channel with no August rows is marked new")
    ok(Decimal(t[("device", "Mobile")]["contribution"]) == 67400 and Decimal(t[("device", "Desktop")]["contribution"]) == 3200, "device contributions 67,400 and 3,200")
    checks = open(os.path.join(d, "checks.txt"), encoding="utf-8").read()
    ok("change: 70600" in checks and "rows in other periods (ignored): 1" in checks, "total change 70,600; the July row is counted and ignored")
    ok(run(number_check, os.path.join(d, "drivers.md"), "--source", os.path.join(d, "drivers.csv"), "--source", DATA) == 0,
       "every number in drivers.md traces to drivers.csv or the data")
    first = open(os.path.join(d, "drivers.md"), "rb").read() + open(os.path.join(d, "drivers.csv"), "rb").read()
    run(drivers, DATA, *BASE, "--value", "revenue", "--dims", "channel,device", "--out", d)
    ok(first == open(os.path.join(d, "drivers.md"), "rb").read() + open(os.path.join(d, "drivers.csv"), "rb").read(), "same input, byte-identical output")

with tempfile.TemporaryDirectory() as d:
    code = run(drivers, DATA, *BASE, "--numerator", "orders", "--denominator", "sessions", "--dims", "channel", "--out", d)
    t = table(d)
    total = sum(Decimal(r["contribution"]) for k, r in t.items() if k[0] != "(total)")
    true = Decimal(7370) / Decimal(250000) - Decimal(6500) / Decimal(210000)
    ok(code == 0 and abs(total - true) < Decimal("1e-12"), "rate effects add back to the true change in conversion")
    ok(Decimal(t[("channel", "Organic")]["mix_effect"]) > 0, "a below-average channel losing share lifts the rate through mix")
    ok(Decimal(t[("channel", "Organic")]["rate_effect"]) == 0, "Organic converted the same both months, so its rate effect is zero")
    pm = Decimal(t[("channel", "Paid search")]["rate_effect"])
    ok(abs(pm - Decimal("0.52") * (Decimal(3800) / 130000 - Decimal("0.031"))) < Decimal("1e-12"), "Paid search rate effect = new share x rate change")

with tempfile.TemporaryDirectory() as d:
    ok(run(drivers, DATA, "--period-col", "month", "--from", "2026-08", "--to", "2026-10", "--value", "revenue", "--dims", "channel", "--out", os.path.join(d, "o")) == 2
       and not os.path.exists(os.path.join(d, "o")), "a period with no rows exits 2 and writes nothing")
    ok(run(drivers, DATA, *BASE, "--value", "profit", "--dims", "channel", "--out", d) == 2, "a missing column exits 2")
    ok(run(drivers, DATA, *BASE, "--numerator", "orders", "--dims", "channel", "--out", d) == 2, "a rate without a denominator exits 2")

print(f"\n{'all passed' if not fails else str(fails) + ' failed'}")
sys.exit(1 if fails else 0)
