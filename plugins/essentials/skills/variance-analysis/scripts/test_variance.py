#!/usr/bin/env python3
"""Known-answer tests for variance-analysis. python3 test_variance.py (exit 0 = pass)."""
import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import number_check  # noqa: E402
import variance  # noqa: E402

EX = os.path.join(HERE, "..", "references", "example")
fails = 0


def ok(cond, msg):
    global fails
    print(("ok   " if cond else "FAIL ") + msg)
    fails += 0 if cond else 1


def run(mod, *args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return mod.main(list(args))


with tempfile.TemporaryDirectory() as d:
    code = run(variance, os.path.join(EX, "lines.csv"), "--out", d, "--period", "September 2026")
    ok(code == 0, "the example runs clean (exit 0)")
    rows = open(os.path.join(d, "variance_table.csv"), encoding="utf-8").read().splitlines()
    mat = sorted(r.split(",")[0] for r in rows[1:] if r.split(",")[8] == "yes")
    ok(mat == ["Cost of goods", "Marketing"], f"material lines are Cost of goods and Marketing (got {mat})")
    ok("Product revenue" not in mat, "Product revenue at 9.9% stays under the 10% bar")
    checks = open(os.path.join(d, "checks.txt"), encoding="utf-8").read()
    ok(checks.count("TIES") == 4 and "DOES NOT TIE" not in checks, "both totals tie on budget and actual")
    draft = open(os.path.join(d, "commentary_draft.md"), encoding="utf-8").read()
    ok("favorable" in draft and "Marketing:** $71,800 against $95,000, $23,200 (24.4%) below budget, favorable" in draft,
       "a cost under budget reads favorable, with the right figures")
    ok("What this cannot tell you" in draft and "ask Ops lead" in draft, "the draft names the owner and keeps the limit")
    code = run(number_check, os.path.join(d, "commentary_draft.md"), "--source", os.path.join(d, "variance_table.csv"),
               "--ignore", "10%", "--ignore", "$10,000", "--ignore", "2", "--ignore", "6", "--ignore", "5", "--ignore", "7")
    ok(code == 0, "every figure in the draft traces to the variance table (thresholds and row numbers ignored)")
    first = open(os.path.join(d, "variance_table.csv"), "rb").read() + open(os.path.join(d, "commentary_draft.md"), "rb").read()
    run(variance, os.path.join(EX, "lines.csv"), "--out", d, "--period", "September 2026")
    second = open(os.path.join(d, "variance_table.csv"), "rb").read() + open(os.path.join(d, "commentary_draft.md"), "rb").read()
    ok(first == second, "same input, byte-identical output")

with tempfile.TemporaryDirectory() as d:
    run(variance, os.path.join(EX, "lines.csv"), "--out", d, "--rule", "or")
    rows = open(os.path.join(d, "variance_table.csv"), encoding="utf-8").read().splitlines()
    mat = sorted(r.split(",")[0] for r in rows[1:] if r.split(",")[8] == "yes")
    ok(mat == ["Cost of goods", "Marketing", "Product revenue"], f"with --rule or, Product revenue joins (got {mat})")

with tempfile.TemporaryDirectory() as d:
    code = run(variance, os.path.join(EX, "lines_broken_total.csv"), "--out", d)
    checks = open(os.path.join(d, "checks.txt"), encoding="utf-8").read()
    ok(code == 1 and "DOES NOT TIE" in checks and "a gap of $10,000" in checks, "a planted $10,000 total gap is caught, exit 1")
    bad = os.path.join(d, "bad.csv")
    open(bad, "w").write("name,budget,actual\nx,1,2\n")
    ok(run(variance, bad, "--out", os.path.join(d, "o")) == 2 and not os.path.exists(os.path.join(d, "o")),
       "a missing line column exits 2 and writes nothing")
    open(bad, "w").write("line,budget,actual\nx,1,abc\n")
    ok(run(variance, bad, "--out", os.path.join(d, "o")) == 2, "a non-number exits 2")

print(f"\n{'all passed' if not fails else str(fails) + ' failed'}")
sys.exit(1 if fails else 0)
