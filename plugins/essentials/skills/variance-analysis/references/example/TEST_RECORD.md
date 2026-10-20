# Test record: variance-analysis

**Data:** synthetic. `lines.csv` is a made-up company's September 2026 pack: two revenue lines, four cost lines, two
total rows. No real company's data.

**Reference (known answers, worked by hand before the run):**

| Line | Budget | Actual | Variance | % | Material at $10,000 and 10% |
|---|---|---|---|---|---|
| Product revenue | 1,200,000 | 1,318,400 | +118,400 | 9.9 | No (under 10%) |
| Services revenue | 240,000 | 236,900 | -3,100 | 1.3 | No |
| Cost of goods | 540,000 | 601,250 | +61,250 | 11.3 | **Yes**, unfavorable |
| Payroll | 410,000 | 404,100 | -5,900 | 1.4 | No |
| Marketing | 95,000 | 71,800 | -23,200 | 24.4 | **Yes**, favorable |
| Software | 38,000 | 39,950 | +1,950 | 5.1 | No |

Both total rows equal the sum of their lines. `lines_broken_total.csv` plants a total revenue actual $10,000 above its
lines.

**Run:** `python3 scripts/test_variance.py`, 2026-10-12. Twelve tests, all pass:

- material lines are exactly Cost of goods and Marketing; with `--rule or`, Product revenue joins them;
- all four tie lines read TIES; the planted error reads DOES NOT TIE with a gap of $10,000 and exit 1;
- a cost under budget is called favorable, with the right figures;
- every figure in the draft traces to the variance table;
- a second run gives byte-identical files;
- a missing column or a non-number exits 2 and writes nothing.
