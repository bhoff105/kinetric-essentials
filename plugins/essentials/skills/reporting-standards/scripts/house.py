#!/usr/bin/env python3
"""house.py: write and keep a team's HOUSE.md, the file every Essentials skill reads first.
Part of Kinetric's Essentials pack (MIT). Standard library only.

    python3 house.py write answers.json --out HOUSE.md [--date 2026-10-12] [--force]
    python3 house.py add-rule HOUSE.md --rule "Revenue is net of returns." --came-from "edit to variance commentary" --approved-by "Dana" [--date ...]
    python3 house.py log-correction HOUSE.md --skill variance-analysis --count 3 [--notes "..."] [--date ...]
    python3 house.py status HOUSE.md
    python3 house.py log-run logs/runs.csv --skill variance-analysis --inputs inbox/pack.csv --out outputs/2026-10-12-variance-analysis --result "totals tie; 11 of 11 traced"

write   builds HOUSE.md from the interview's answers (format in ../references/answers_format.md). It refuses to replace a
        HOUSE.md that already holds learned rules or corrections unless --force, so nothing learned is lost by accident.
add-rule appends one approved rule (L1, L2...) to the Learned rules log. Only ever run after the person said yes.
log-correction appends one line to the Corrections log: how many edits a skill's output needed this run.
log-run appends one line per skill run to a CSV log (date, skill, inputs, out, result), creating it with a header.
status  prints the counts: rules, learned rules, open questions, and corrections per skill, oldest to newest.

Exit 0: done. Exit 1: written, but the answers left sections open (listed). Exit 2: unreadable input, a missing
section in HOUSE.md, or a refusal; nothing written.
"""
import argparse
import csv
import datetime
import json
import os
import re
import sys

VERSION = "1.0"
TERMS = ["Revenue", "Active customer", "Churn", "Conversion rate", "Margin"]
SECTIONS = 8


def one(v):
    return re.sub(r"\s+", " ", str(v if v is not None else "")).strip()


def cell(v):
    return one(v).replace("|", "/")


def lower_first(s):
    """Lower the first letter unless the first word is an acronym (ROAS, CFO)."""
    first = s.split(" ", 1)[0] if s else ""
    if not s or (len(first) > 1 and first[:2].isupper()):
        return s
    return s[:1].lower() + s[1:]


def build(s, today):
    """Return (text, rules, open_questions, answered). Mirrors the desk form's generator."""
    rules, open_q = [], []

    def rule(group, text):
        rules.append((f"R{len(rules) + 1}", group, text))

    readers = [r for r in s.get("readers", []) if one(r.get("who"))]
    for r in readers:
        t = f"Written for {lower_first(one(r['who']))}"
        if one(r.get("decides")):
            t += f", who decides {lower_first(one(r['decides']))}"
        t += "."
        if one(r.get("time")):
            t += f" They give a page {one(r['time'])}."
        if one(r.get("first")):
            t += f" Lead with {lower_first(one(r['first']))}."
        rule("Who reads the work", t)
    if not readers:
        open_q.append("Who reads the work, what they decide, and what they want first.")

    sources = [x for x in s.get("sources", []) if one(x.get("what")) and one(x.get("system"))]
    for x in sources:
        t = f"{one(x['what'])}: the source of truth is {one(x['system'])}."
        if one(x.get("refresh")):
            t += f" Refreshed {lower_first(one(x['refresh']))}."
        rule("Where the numbers live", t + " Read it there, never from a copy.")
    if not sources:
        open_q.append("Where the numbers live: the source of truth for each subject.")

    terms = s.get("terms") or {}
    done = 0
    for term in list(TERMS) + [k for k in terms if k not in TERMS]:
        v = terms.get(term, {})
        dfn = one(v.get("own")) or one(v.get("pick"))
        if dfn:
            rule("Our words", f'"{term}" means: {dfn}.')
            done += 1
        else:
            open_q.append(f'What "{term}" means here.')
    for x in s.get("extraTerms", []):
        if one(x.get("term")) and one(x.get("def")):
            rule("Our words", f'"{one(x["term"])}" means: {one(x["def"])}.')
            done += 1

    good = [one(g) for g in s.get("good", []) if one(g)]
    for g in good:
        rule("What good work looks like", f"{g}.")
    if not good:
        open_q.append("What the team's best work has in common.")
    for b in s.get("bad", []):
        if one(b):
            rule("What went wrong before", f"Watch for this: {lower_first(one(b))}.")

    never = [one(x) for x in s.get("never", []) if one(x)]
    never += [p for p in re.split(r";\s*", one(s.get("neverOther"))) if p]
    for x in never:
        rule("Never", f"Never: {lower_first(x)}.")
    if not never:
        open_q.append("What must never appear or happen.")

    checks = [one(x) for x in s.get("checks", []) if one(x)]
    checks += [p for p in re.split(r";\s*", one(s.get("checksOther"))) if p]
    for x in checks:
        rule("Before anything goes out", f"{x}. Show the result in the output.")
    if not checks:
        open_q.append("What the team checks by hand before anything goes out.")

    tasks = [t for t in s.get("tasks", []) if one(t.get("name"))]
    if not tasks:
        open_q.append("The recurring tasks and how long each takes today (the baseline).")

    answered = sum([bool(readers), bool(sources), done > 0, bool(good), bool(never), bool(checks), bool(tasks),
                    bool(one(s.get("fn")) or s.get("tools"))])

    L = [f"# House file: {one(s.get('team')) or 'Our team'}", "",
         f"Made with Kinetric's reporting-standards skill (v{VERSION}) on {today}. Every AI skill that works for this team "
         "reads this file first. A rule here beats the skill's own default. Keep it in one place and edit it there.", "",
         "## Instructions for the AI reading this file", "",
         "1. Read the shared rules and the learned rules before you start, then the section for your skill if there is one.",
         "2. When a rule here covers the task, follow it, and cite its number (R1, L1...) where it shaped the output.",
         "3. When nothing here covers something you had to decide, end your output with an **Assumptions** block that "
         "lists each guess in one line. Never guess silently.",
         "4. When the person corrects your output, propose each correction as a candidate rule, marked *always* or *just "
         "this once*. Add it to the Learned rules log only after the person says yes. Never change a rule silently.",
         "5. Count the corrections the person made to this output and add one line to the Corrections log.",
         "6. Never change a number from a source. Report what you found; the person decides.", "",
         "## The team", "", f"- Function: {one(s.get('fn')) or 'not given'}"]
    tools = [one(x) for x in s.get("tools", []) if one(x)] + ([one(s.get("toolsOther"))] if one(s.get("toolsOther")) else [])
    L += [f"- Tools: {', '.join(tools) if tools else 'not given'}", "", "## Shared rules", "",
          f"Source for every rule below: the reporting-standards interview, {today}, approved by the person who answered it."]
    last = None
    for rid, group, text in rules:
        if group != last:
            L += ["", f"### {group}", ""]
            last = group
        L.append(f"- **{rid}.** {text}")
    if not rules:
        L += ["", "*No rules yet.*"]
    L += ["", "## Examples to keep beside this file", ""]
    L.append(f"- {one(s.get('examples'))}" if one(s.get("examples")) else
             "- None named yet. Three pieces of work the team was proud of, and one it wasn't, teach more than any rule.")
    L += ["", "## Skill sections", "",
          "Rules that only make sense for one skill go here, under a heading with the skill's name. Empty to start.", "",
          "## Open questions", ""]
    if open_q:
        L += ["Not answered yet. Until they are, a skill states its assumption about each one.", ""] + [f"- {q}" for q in open_q]
    else:
        L.append("None.")
    L += ["", f"## Baseline, {today}", ""]
    if tasks:
        L += ["Where the team starts. Measured again after five runs and every month, so any change can be shown.", "",
              "| Task | How often | Hours each time | Redone after review | Trust AI with it today (1 to 5) |",
              "|---|---|---|---|---|"]
        for t in tasks:
            L.append(f"| {cell(t['name'])} | {cell(t.get('cadence')) or '?'} | {cell(t.get('hours')) or '?'} | "
                     f"{cell(t.get('redone')) or '?'} | {cell(t.get('trust')) or '?'} |")
    else:
        L.append("*Not filled in.*")
    L += ["", "## Learned rules log", "", "| ID | Date | Rule | Came from | Approved by |", "|---|---|---|---|---|", "",
          "## Corrections log", "", "| Date | Skill or task | Corrections | Notes |", "|---|---|---|---|", ""]
    return "\n".join(L), rules, open_q, answered


def table_rows(text, heading):
    """(start, end, rows) of the pipe table under a ## heading; rows exclude the header and divider."""
    lines = text.split("\n")
    try:
        h = next(i for i, ln in enumerate(lines) if ln.strip() == heading)
    except StopIteration:
        return None
    i = h + 1
    while i < len(lines) and not lines[i].startswith("|"):
        if lines[i].startswith("## "):
            return None
        i += 1
    start = i
    while i < len(lines) and lines[i].startswith("|"):
        i += 1
    return start, i, lines[start + 2:i]


def append_row(path, heading, row):
    text = open(path, encoding="utf-8").read()
    found = table_rows(text, heading)
    if not found:
        raise SystemExit(f"house: {path} has no table under '{heading}'; nothing written")
    _, end, _ = found
    lines = text.split("\n")
    lines.insert(end, row)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write"); w.add_argument("answers"); w.add_argument("--out", required=True)
    w.add_argument("--date"); w.add_argument("--force", action="store_true")
    r = sub.add_parser("add-rule"); r.add_argument("house"); r.add_argument("--rule", required=True)
    r.add_argument("--came-from", required=True); r.add_argument("--approved-by", required=True); r.add_argument("--date")
    c = sub.add_parser("log-correction"); c.add_argument("house"); c.add_argument("--skill", required=True)
    c.add_argument("--count", type=int, required=True); c.add_argument("--notes", default=""); c.add_argument("--date")
    st = sub.add_parser("status"); st.add_argument("house")
    lg = sub.add_parser("log-run"); lg.add_argument("log"); lg.add_argument("--skill", required=True)
    lg.add_argument("--inputs", required=True); lg.add_argument("--out", required=True)
    lg.add_argument("--result", required=True); lg.add_argument("--date")
    a = ap.parse_args(argv)
    today = getattr(a, "date", None) or datetime.date.today().isoformat()

    try:
        if a.cmd == "write":
            try:
                s = json.load(open(a.answers, encoding="utf-8-sig"))
            except (OSError, ValueError) as e:
                print(f"house: cannot read {a.answers}: {e}", file=sys.stderr)
                return 2
            if os.path.exists(a.out) and not a.force:
                old = open(a.out, encoding="utf-8").read()
                lr, cr = table_rows(old, "## Learned rules log"), table_rows(old, "## Corrections log")
                if (lr and lr[2]) or (cr and cr[2]):
                    print(f"house: {a.out} already holds learned rules or corrections; refusing to replace it. "
                          "Add rules with add-rule, or pass --force after the person agrees.", file=sys.stderr)
                    return 2
            text, rules, open_q, answered = build(s, today)
            with open(a.out, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print(f"house: wrote {a.out}: {answered} of {SECTIONS} sections answered, {len(rules)} rules, "
                  f"{len(open_q)} open question(s)")
            for q in open_q:
                print(f"  open: {q}")
            return 1 if open_q else 0

        if a.cmd == "log-run":
            new = not os.path.exists(a.log)
            if os.path.dirname(a.log):
                os.makedirs(os.path.dirname(a.log), exist_ok=True)
            with open(a.log, "a", encoding="utf-8", newline="") as f:
                wr = csv.writer(f, lineterminator="\n")
                if new:
                    wr.writerow(["date", "skill", "inputs", "out", "result"])
                wr.writerow([today, a.skill, a.inputs, a.out, a.result])
            print(f"house: logged a {a.skill} run in {a.log}")
            return 0
        if not os.path.exists(a.house):
            print(f"house: {a.house} not found; run reporting-standards first", file=sys.stderr)
            return 2
        if a.cmd == "add-rule":
            found = table_rows(open(a.house, encoding="utf-8").read(), "## Learned rules log")
            n = len(found[2]) + 1 if found else 1
            append_row(a.house, "## Learned rules log",
                       f"| L{n} | {today} | {cell(a.rule)} | {cell(a.came_from)} | {cell(a.approved_by)} |")
            print(f"house: added L{n} to {a.house}")
            return 0
        if a.cmd == "log-correction":
            if a.count < 0:
                print("house: --count can't be negative", file=sys.stderr)
                return 2
            append_row(a.house, "## Corrections log", f"| {today} | {cell(a.skill)} | {a.count} | {cell(a.notes)} |")
            print(f"house: logged {a.count} correction(s) for {a.skill}")
            return 0
        if a.cmd == "status":
            text = open(a.house, encoding="utf-8").read()
            shared = len(re.findall(r"^- \*\*R\d+\.\*\*", text, flags=re.M))
            lr = table_rows(text, "## Learned rules log")
            cr = table_rows(text, "## Corrections log")
            oq = re.search(r"## Open questions\n\n(.*?)\n## ", text, flags=re.S)
            n_open = len([x for x in (oq.group(1).splitlines() if oq else []) if x.startswith("- ")])
            print(f"shared rules: {shared}")
            print(f"learned rules: {len(lr[2]) if lr else 0}")
            print(f"open questions: {n_open}")
            per = {}
            for row in (cr[2] if cr else []):
                parts = [p.strip() for p in row.strip("|").split("|")]
                if len(parts) >= 3 and parts[2].isdigit():
                    per.setdefault(parts[1], []).append(int(parts[2]))
            for k, v in per.items():
                trend = "falling" if len(v) > 1 and v[-1] < v[0] else "flat or rising" if len(v) > 1 else "one run"
                print(f"corrections, {k}: {' -> '.join(map(str, v))} ({trend})")
            if not per:
                print("corrections: none logged yet")
            return 0
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
