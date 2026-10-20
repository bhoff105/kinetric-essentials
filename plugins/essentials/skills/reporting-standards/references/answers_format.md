# answers.json: the format house.py reads

Every key is optional. A missing or empty key becomes an open question in HOUSE.md. Text is kept as the person said
it; line breaks and pipes are flattened so they can't break the file. Full example: `example/answers.json`.

```json
{
  "team": "Finance",
  "fn": "Finance / FP&A",
  "tools": ["Excel", "SQL"],
  "toolsOther": "NetSuite",
  "readers": [{"who": "An executive (CEO, CFO, COO)", "decides": "...", "time": "2 minutes", "first": "The answer or recommendation"}],
  "sources": [{"what": "Revenue", "system": "NetSuite GL", "refresh": "At month-end close"}],
  "terms": {"Revenue": {"pick": "Recognised revenue (the accounting figure)", "own": ""}},
  "extraTerms": [{"term": "Run rate", "def": "Last full month times twelve"}],
  "good": ["The answer is in the first line"],
  "bad": ["Too long"],
  "examples": "the September board pack; the Q2 variance memo",
  "never": ["Pie charts"],
  "neverOther": "anything separated by semicolons; becomes one rule each",
  "checks": ["Totals tie to the source system"],
  "checksOther": "",
  "tasks": [{"name": "Month-end variance commentary", "cadence": "Monthly", "hours": "6", "redone": "Often", "trust": "2"}]
}
```

`terms` always covers Revenue, Active customer, Churn, Conversion rate and Margin; any other key in `terms` is kept
too. For a term, `own` (their words) beats `pick` (a listed definition).
