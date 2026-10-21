#!/usr/bin/env python3
"""Known-answer tests for executive-summary's number check. Run from anywhere: python3 test_exec_summary.py (exit 0 = pass)."""
import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import number_check as nc  # noqa: E402

EX = os.path.join(HERE, "..", "references", "example")
fails = 0


def ok(cond, msg):
    global fails
    print(("ok   " if cond else "FAIL ") + msg)
    fails += 0 if cond else 1


def run(*args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        code = nc.main(list(args))
    return code, buf.getvalue()


src = os.path.join(EX, "results.csv")
code, out = run(os.path.join(EX, "summary_good.md"), "--source", src)
ok(code == 0 and "6 traced, 0 not found" in out, "the good summary: all 6 numbers traced")
code, out = run(os.path.join(EX, "summary_bad.md"), "--source", src)
ok(code == 1 and out.count("NOT FOUND") == 1 and "12%" in out.split("NOT FOUND")[1].splitlines()[0],
   "the planted error: exactly one number not found, and it is 12%")

with tempfile.TemporaryDirectory() as d:
    s = os.path.join(d, "s.csv")
    open(s, "w").write("metric,value\nrevenue,1234567.89\nrate,0.0347\nmargin_pct,41.25\n")
    cases = [("Revenue was $1.23M.", 0), ("Revenue was $1,234,568.", 0), ("Revenue was 1,235K.", 0),
             ("The rate was 3.5%.", 0), ("The rate was 3.47%.", 0), ("Margin was 41.3%.", 0),
             ("Revenue was $1.24M.", 1), ("Run on 2026-09-30 for fiscal 2026.", 0)]
    for text, want in cases:
        dpath = os.path.join(d, "d.md")
        open(dpath, "w").write(text + "\n")
        code, _ = run(dpath, "--source", s)
        ok(code == want, f"{text!r} exits {want}")
    open(dpath, "w").write("Orders were 1,950 in fiscal 2026.\n")
    code, out = run(dpath, "--source", s)
    ok(code == 1 and "NOT FOUND" in out and "1,950" in out and "SKIPPED" in out and "1 skipped as years" in out,
       "a comma-formatted 1,950 is checked; a bare 2026 is skipped as a year and counted")
    s2 = os.path.join(d, "s2.csv")
    open(s2, "w").write("metric,value\norders,1950\n")
    code, out = run(dpath, "--source", s2)
    ok(code == 0 and "1 traced" in out, "a draft's 1,950 traces to a bare 1950 in a source")
    code, _ = run(os.path.join(d, "nope.md"), "--source", s)
    ok(code == 2, "a missing draft exits 2")
    code, _ = run(os.path.join(EX, "summary_good.md"), "--source", os.path.join(d, "nope.csv"))
    ok(code == 2, "a missing source exits 2")
    latin = os.path.join(d, "latin.md")
    open(latin, "wb").write(b"Revenue was \xa31.23M.\n")  # a pound sign in Latin-1, not UTF-8
    code, _ = run(latin, "--source", s)
    ok(code == 2, "a draft that is not UTF-8 exits 2, not a false NOT FOUND")

print(f"\n{'all passed' if not fails else str(fails) + ' failed'}")
sys.exit(1 if fails else 0)
