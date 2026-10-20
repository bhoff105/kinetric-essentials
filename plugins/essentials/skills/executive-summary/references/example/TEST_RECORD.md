# Test record: executive-summary

**Data:** synthetic. `results.csv` is a made-up store's August and September by channel. No real company's data.

**Reference (known answers):** `summary_good.md` states six numbers, all in `results.csv`. `summary_bad.md` is the same
summary with one planted error: "up 12% on August", which appears in no source (the true change is 9.5%, and it isn't
in the source either, so a correct version must come from a `derived.csv`).

**Run:** `python3 scripts/test_exec_summary.py`, 2026-10-12.

| Test | Expected | Result |
|---|---|---|
| Good summary | 6 numbers, 6 traced, exit 0 | Pass |
| Planted error | Exactly one NOT FOUND, and it is "12%", exit 1 | Pass |
| Scaled and rounded forms ($1.23M, $1,234,568, 1,235K, 3.5%, 3.47%, 41.3%) | Traced to 1234567.89, 0.0347, 41.25 | Pass |
| A wrong scaled figure ($1.24M) | Not found, exit 1 | Pass |
| Dates and years in the draft | Skipped | Pass |
| Missing draft or source | Exit 2, nothing claimed | Pass |

Twelve tests, all pass.

**Known limit:** a number the summary computes (a growth rate, a share) is not in any source, so it is reported NOT
FOUND until it is written into a source table. That is deliberate: the skill's step 2 makes it compute those first.
