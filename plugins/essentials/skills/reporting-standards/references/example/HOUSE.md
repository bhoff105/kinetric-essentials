# House file: Growth analytics (example team)

Made with Kinetric's reporting-standards skill (v1.0) on 2026-10-12. Every AI skill that works for this team reads this file first. A rule here beats the skill's own default. Keep it in one place and edit it there.

## Instructions for the AI reading this file

1. Read the shared rules and the learned rules before you start, then the section for your skill if there is one.
2. When a rule here covers the task, follow it, and cite its number (R1, L1...) where it shaped the output.
3. When nothing here covers something you had to decide, end your output with an **Assumptions** block that lists each guess in one line. Never guess silently.
4. When the person corrects your output, propose each correction as a candidate rule, marked *always* or *just this once*. Add it to the Learned rules log only after the person says yes. Never change a rule silently.
5. Count the corrections the person made to this output and add one line to the Corrections log.
6. Never change a number from a source. Report what you found; the person decides.

## The team

- Function: Marketing / growth
- Tools: Google Sheets, SQL, Looker

## Shared rules

Source for every rule below: the reporting-standards interview, 2026-10-12, approved by the person who answered it.

### Who reads the work

- **R1.** Written for an executive (CEO, CFO, COO), who decides where next month's marketing budget goes. They give a page 2 minutes. Lead with the answer or recommendation.
- **R2.** Written for the team's own lead, who decides which campaigns to pause. They give a page 10 minutes or more. Lead with the number against target.

### Where the numbers live

- **R3.** Revenue: the source of truth is Shopify orders export. Refreshed daily. Read it there, never from a copy.
- **R4.** Marketing spend: the source of truth is Meta and Google Ads, via the weekly sheet. Refreshed weekly. Read it there, never from a copy.
- **R5.** Customers: the source of truth is Klaviyo profiles. Refreshed daily. Read it there, never from a copy.

### Our words

- **R6.** "Revenue" means: Net of returns and discounts.
- **R7.** "Active customer" means: Bought in the last 12 months.
- **R8.** "Conversion rate" means: Orders divided by sessions.
- **R9.** "Margin" means: Contribution margin after shipping and ad spend, before overhead.
- **R10.** "New customer" means: First order ever on this email address, not first order this year.

### What good work looks like

- **R11.** The answer is in the first line.
- **R12.** Every number sits beside last period.
- **R13.** One chart per point.
- **R14.** It ends with a recommendation.

### What went wrong before

- **R15.** Watch for this: a number didn't match another report.
- **R16.** Watch for this: too much detail for the reader.

### Never

- **R17.** Never: pie charts.
- **R18.** Never: a metric shown without its target or comparison.
- **R19.** Never: ROAS from the ad platforms quoted as if it were store revenue.

### Before anything goes out

- **R20.** Totals tie to the source system. Show the result in the output.
- **R21.** No duplicate rows or ids. Show the result in the output.

## Examples to keep beside this file

- March budget memo (the one the CEO forwarded); weekly channel report, week 14

## Skill sections

Rules that only make sense for one skill go here, under a heading with the skill's name. Empty to start.

## Open questions

Not answered yet. Until they are, a skill states its assumption about each one.

- What "Churn" means here.

## Baseline, 2026-10-12

Where the team starts. Measured again after five runs and every month, so any change can be shown.

| Task | How often | Hours each time | Redone after review | Trust AI with it today (1 to 5) |
|---|---|---|---|---|
| Weekly channel report | Weekly | 4 | Sometimes | 2 |
| Monthly budget memo | Monthly | 10 | Often | 1 |

## Learned rules log

| ID | Date | Rule | Came from | Approved by |
|---|---|---|---|---|

## Corrections log

| Date | Skill or task | Corrections | Notes |
|---|---|---|---|
