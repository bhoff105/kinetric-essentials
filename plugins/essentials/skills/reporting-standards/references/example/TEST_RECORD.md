# Test record: reporting-standards

**Data:** a made-up growth analytics team (`answers.json`), labelled as an example. No real team's answers.

**Reference:** the same example team was used by the browser version of the form (2026-10-12), whose tests fixed the
expected counts: 2 readers, 3 sources, 5 word rules (3 picked, 1 own, 1 extra), 3 never items (2 ticked, 1 typed),
churn the only open question. `HOUSE.md` in this folder is the reviewed reference output; the test requires a
byte-identical match.

**Run:** `python3 scripts/test_house.py`, 2026-10-12. Eighteen tests, all pass:

- the expected counts above, 21 rules in all, 8 of 8 sections answered;
- an own definition beats a picked one; acronyms (CEO, ROAS) keep their capitals;
- byte-identical to the reference file;
- empty answers produce no rules and 11 open questions;
- newlines and pipes in answers can't break the file's headings or tables;
- `add-rule` numbers learned rules L1, L2 and escapes pipes; `log-correction` and `status` show corrections falling
  8 -> 5 -> 2;
- `write` refuses to replace a file that holds learned rules (nothing lost) unless `--force`;
- a missing file or a negative count exits 2;
- `log-run` creates the run log with one header and appends one row per run (added 2026-10-12).

**Fixed during the build:** the browser version lowercased whole phrases, turning "CEO" into "ceo" and "ROAS" into
"rOAS", and wrote "Customers comes from". The script keeps acronyms and words a source as "the source of truth is".
