# Test record: root-cause-analysis

**Data:** synthetic. `traffic.csv` is a made-up store's sessions, orders and revenue by channel and device for August
and September 2026, with a new channel (Affiliate) in September and one July row the run must ignore.

**Reference (worked by hand before the run):**

- Revenue went from 542,000 to 612,600, a change of 70,600. By channel: Paid search +56,800, Affiliate +16,000 (new),
  Email -2,200, Organic 0. By device: Mobile +67,400, Desktop +3,200.
- Conversion (orders / sessions) went from 6,500 / 210,000 to 7,370 / 250,000, about 3.10% to 2.95%. Organic converted
  at 2.375% both months, below the 3.10% average, and its share of sessions fell, so its mix effect must be positive and
  its rate effect zero. Paid search's rate effect must equal its September share (0.52) times its rate change
  (3,800 / 130,000 minus 0.031).

**Run:** `python3 scripts/test_drivers.py`, 2026-10-12. Fourteen tests, all pass:

- every channel and device contribution matches the hand-worked figures; Affiliate is marked new;
- the July row is counted and ignored;
- the rate breakdown adds back to the true change to within 1e-12; Organic's mix effect is positive and its rate
  effect zero; Paid search's rate effect matches the formula;
- every number in `drivers.md` traces to `drivers.csv` or the data;
- a second run is byte-identical;
- a missing period, a missing column, or a rate without a denominator exits 2 and writes nothing.

**Fixed during the build:** the first version measured mix effects against zero, so a below-average segment losing
share showed as pulling the rate down. Mix is now measured against the old average, the standard form, which still
adds back exactly. A total row and two-decimal shares were added to `drivers.csv` after the number check found the
headline figures had no source and one share had been rounded twice.
