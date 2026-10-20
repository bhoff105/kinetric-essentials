#!/usr/bin/env python3
"""Known-answer tests for reporting-standards's house.py. python3 test_house.py (exit 0 = pass)."""
import contextlib
import csv
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import house  # noqa: E402

EX = os.path.join(HERE, "..", "references", "example")
fails = 0


def ok(cond, msg):
    global fails
    print(("ok   " if cond else "FAIL ") + msg)
    fails += 0 if cond else 1


def run(*args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = house.main(list(args))
    return code, out.getvalue()


ans = json.load(open(os.path.join(EX, "answers.json"), encoding="utf-8"))
text, rules, open_q, answered = house.build(ans, "2026-10-12")
groups = lambda g: sum(1 for r in rules if r[1] == g)
ok(groups("Who reads the work") == 2 and groups("Where the numbers live") == 3, "2 readers and 3 sources give 5 rules")
ok(groups("Our words") == 5, "3 picked terms, 1 own definition and 1 extra term give 5 word rules")
ok(groups("Never") == 3, "2 ticked never items plus 1 typed")
ok(len(rules) == 21 and open_q == ['What "Churn" means here.'] and answered == 8, "21 rules, churn the only open question, 8 of 8 sections")
ok('"Margin" means: Contribution margin after shipping' in text, "an own definition beats the pick")
ok("Never: ROAS from the ad platforms" in text and "(CEO, CFO, COO)" in text, "acronyms keep their capitals")
ok(text == open(os.path.join(EX, "HOUSE.md"), encoding="utf-8").read(), "byte-identical to the reference HOUSE.md")

e_text, e_rules, e_open, e_ans = house.build({}, "2026-10-12")
ok(not e_rules and len(e_open) == 11 and e_ans == 0 and "*No rules yet.*" in e_text, "empty answers: no rules, 11 open questions, nothing invented")

h = house.build({"team": "A\n# fake", "tasks": [{"name": "a | b\n| c", "cadence": "Weekly", "hours": "1"}]}, "2026-10-12")[0]
ok("\n# fake" not in h and "| a / b / c | Weekly | 1 | ? | ? |" in h, "newlines and pipes in answers can't break the file")

with tempfile.TemporaryDirectory() as d:
    hp = os.path.join(d, "HOUSE.md")
    code, _ = run("write", os.path.join(EX, "answers.json"), "--out", hp, "--date", "2026-10-12")
    ok(code == 1, "write exits 1 while a question is open")
    ok(run("add-rule", hp, "--rule", "Revenue excludes gift cards.", "--came-from", "edit to exec summary", "--approved-by", "Dana", "--date", "2026-10-13")[0] == 0, "add-rule works")
    run("add-rule", hp, "--rule", "Round to thousands | always", "--came-from", "edit to variance", "--approved-by", "Dana", "--date", "2026-10-14")
    t = open(hp, encoding="utf-8").read()
    ok("| L1 | 2026-10-13 | Revenue excludes gift cards." in t and "| L2 | 2026-10-14 | Round to thousands / always |" in t, "rules numbered L1, L2 and pipes escaped")
    for n, dt in ((8, "2026-10-13"), (5, "2026-10-20"), (2, "2026-10-27")):
        run("log-correction", hp, "--skill", "variance-analysis", "--count", str(n), "--date", dt)
    code, out = run("status", hp)
    ok("learned rules: 2" in out and "8 -> 5 -> 2 (falling)" in out and "open questions: 1" in out, "status shows 2 learned rules and corrections falling 8 -> 5 -> 2")
    code, _ = run("write", os.path.join(EX, "answers.json"), "--out", hp, "--date", "2026-10-28")
    ok(code == 2 and "| L2 |" in open(hp, encoding="utf-8").read(), "write refuses to replace a file with learned rules (exit 2, nothing lost)")
    code, _ = run("write", os.path.join(EX, "answers.json"), "--out", hp, "--force", "--date", "2026-10-28")
    ok(code == 1 and "| L1 |" not in open(hp, encoding="utf-8").read(), "--force replaces it when the person agrees")
    ok(run("add-rule", os.path.join(d, "none.md"), "--rule", "x", "--came-from", "y", "--approved-by", "z")[0] == 2, "a missing HOUSE.md exits 2")
    ok(run("log-correction", hp, "--skill", "x", "--count", "-1")[0] == 2, "a negative count exits 2")
    lp = os.path.join(d, "logs", "runs.csv")
    run("log-run", lp, "--skill", "variance-analysis", "--inputs", "inbox/a.csv", "--out", "outputs/x", "--result", "ties, 9 of 9 traced", "--date", "2026-10-13")
    run("log-run", lp, "--skill", "executive-summary", "--inputs", "a, b", "--out", "outputs/y", "--result", "6 of 6 traced", "--date", "2026-10-14")
    rows = list(csv.reader(open(lp, encoding="utf-8")))
    ok(rows[0] == ["date", "skill", "inputs", "out", "result"] and len(rows) == 3 and rows[2][2] == "a, b", "log-run creates the log with one header and appends one row per run")

print(f"\n{'all passed' if not fails else str(fails) + ' failed'}")
sys.exit(1 if fails else 0)
