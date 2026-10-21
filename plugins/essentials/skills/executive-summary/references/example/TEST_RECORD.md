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
| "Orders were 1,950 in fiscal 2026." against a source without 1950 | 1,950 checked and NOT FOUND; 2026 skipped as a year and counted; exit 1 | Pass |
| The same draft against a source holding a bare 1950 | 1,950 traced, exit 0 | Pass |
| A draft saved in Latin-1, not UTF-8 | Exit 2 (cannot read), never a false NOT FOUND | Pass |

**Run:** `python3 scripts/test_exec_summary.py`, 2026-10-20. Fifteen tests, all pass.

**Known limit:** a number the summary computes (a growth rate, a share) is not in any source, so it is reported NOT
FOUND until it is written into a source table. That is deliberate: the skill's step 4 makes it compute those first, in `OUT/derived.csv`.
