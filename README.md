# Kinetric Essentials

Four AI skills that explain and report a data team's numbers. Install them once and Claude uses them whenever the work
comes up: drafting the variance commentary, working out why a number moved, turning an analysis into five lines for a
leader. The hours you get back go to implementation, new ideas and better products.

Free, MIT licensed, from [Kinetric](https://kinetric.co). Version 1.2.0.

> **Using Claude Code?** Download the workspace instead (`kinetric-workspace-1.2.0.zip`, free at [kinetric.co/download.html](https://kinetric.co/download.html)): the same four
> skills in a ready folder with `inbox/`, `outputs/`, a house file Claude reads every session, safe permissions, and
> optional read-only connectors for Snowflake, BigQuery, Postgres and AWS. Open the folder and read `START_HERE.md`.
> This pack is for the Claude app (web or desktop) and for adding the skills to a setup you already have.

## Start with the house file

Run **reporting-standards** first. It's a ten-minute interview that writes `HOUSE.md`: who reads your work, where your
numbers live, what your words mean, and what must never appear. The other three skills read it before every draft, so
the first draft already uses your definitions and your thresholds instead of generic ones.

## Every number is tied out

The three analysis skills hand the arithmetic to a small script and check their own draft before you see it.
Variance analysis ties every total to your pack. Root cause analysis proves the segments add up to the change. All three
trace each number in their draft back to your file, and a number they can't trace is named, never used. No skill
changes one of your numbers; a total that doesn't tie is reported, not fixed.

## What these skills cannot tell you

| Skill | What it leaves to you |
|---|---|
| **reporting-standards** | Whether your team's rules are the right ones. It writes down how you work today, accurately |
| **variance-analysis** | Why a line moved, whether the budget was right, or whether a timing difference reverses next month. The draft asks each owner |
| **root-cause-analysis** | Why each segment moved, or whether the move will last. It says where the change sits and proves the arithmetic |
| **executive-summary** | Whether the analysis was right, or whether the action is the right call. It proves the summary matches the analysis |

## What's inside

| Skill | What it does | Ask Claude something like |
|---|---|---|
| **reporting-standards** | Run first. A ten-minute interview that writes `HOUSE.md`: who reads your work, where your numbers live, what your words mean, what must never appear. Every other skill reads it | "Document our reporting standards" |
| **variance-analysis** | Budget against actual in, a first draft of the commentary out, material lines only, totals tied | "Draft the variance commentary for September" |
| **root-cause-analysis** | Breaks a change down by segment (and for a rate, into mix and rate effects) and proves it adds up | "Why did conversion drop last month?" |
| **executive-summary** | Five lines for a leader (answer, number, action, risk, what it rests on), every number traced | "Summarise this for the CEO" |

Every skill reads `HOUSE.md` first, shows its working, lists what it had to assume, and never changes one of your
numbers. When you correct its output, it offers the correction as a rule; it keeps only the ones you say yes to, and
logs how many corrections each run needed, so you can see it learn your way of working.

## What the pack leaves out on purpose

Reconciling reports to their sources, and the deeper analysis behind a decision (scoring, test design, segments,
forecasts), only work once a team's own rules are in: its sources, its tolerances, its history. Kinetric does that work
as a setup, not in the free pack. See [kinetric.co/essentials.html](https://kinetric.co/essentials.html).

## What you need

| | |
|---|---|
| **An AI** | Claude. The skills follow the open [Agent Skills](https://agentskills.io) format, so other AI tools that read it may run them, but we build and test on Claude only. |
| **A plan** | In the Claude app (web or desktop): any plan, including Free, according to Anthropic's help centre. In Claude Code: a Claude subscription or an Anthropic Console account (see [claude.com/pricing](https://claude.com/pricing)). |
| **Code execution** | On. The skills run small Python scripts. In the Claude app: Settings > Capabilities > **Code execution and file creation**. On a Team or Enterprise plan an owner turns on Skills and code execution for the organisation. |
| **Python** | Only for Claude Code, which runs the scripts on your machine: Python 3 as `python3`. Standard library only, nothing to install. The Claude app runs them in its own sandbox. |

## Install in the Claude app (web or desktop)

1. Turn on **Code execution and file creation** (Settings > Capabilities).
2. Go to **Customize > Skills**, click **+**, choose **Create skill**, then **Upload a skill**.
3. Upload each zip in the `for-claude-app/` folder, one at a time (four zips, one per skill).
4. Make sure each skill's toggle is on.
5. Start a new chat and say: **"Document our reporting standards."** Save the `HOUSE.md` it writes into your project's knowledge so
   every chat can see it.

**Team or Enterprise:** an owner can upload the zips once under **Organization settings > Plugins & skills** and
everyone gets them.

## Install in Claude Code (terminal or the VS Code extension)

From inside a Claude Code session, straight from GitHub:

```
/plugin marketplace add bhoff105/kinetric-essentials
/plugin install essentials@kinetric
```

Or with this folder unzipped somewhere on your machine, use its path in place of `bhoff105/kinetric-essentials`.

The skills are then available as `/essentials:variance-analysis`, `/essentials:root-cause-analysis` and so on, and Claude picks
them up on its own when the work matches. To skip the plugin, copy the folders in `plugins/essentials/skills/` into
`~/.claude/skills/` instead.

Run `/essentials:reporting-standards` first and keep `HOUSE.md` in your working folder (mention it in your `CLAUDE.md`).

## Try it before your own files

Every skill carries a small made-up example in `references/example/`. Ask: "Run the variance analysis on your example pack," or
"Show me root-cause-analysis on the example data." Each one should give the answer its `TEST_RECORD.md` describes. Each skill
also has a test script (`scripts/test_*.py`); exit 0 means it works on your setup.

## Where it works

| Where | Status |
|---|---|
| Claude on the web | Supported in Anthropic's docs. PENDING-TEST |
| Claude desktop app, chat | Supported in Anthropic's docs for skills an organisation provides; personal uploads follow your account. PENDING-TEST |
| Claude Code, terminal | Supported in Anthropic's docs. PENDING-TEST |
| Claude Code in VS Code | Uses the same skills as the terminal. PENDING-TEST |
| Claude desktop app, Code tab | Not stated in Anthropic's docs |
| Mobile apps | Not supported |
| Other AI tools | May work (open format); not tested |

## Before you install anything

A skill is code and instructions. Read it before you install it, including this one. These skills read only the files
you give them, send nothing anywhere, and never change an input file.

## What this pack leaves out

Your team's rules, tested. The pack starts from sensible defaults and your house file. It doesn't know which date basis
your board expects or which attribution window your brand reports, and it hasn't been checked against the last six
months of your own work. Setting that up for a team (the rules found and written down, each step tested on your own
history, the steps joined) is what Kinetric does for a fee. Write to brendan@kinetric.co.

## Licence

MIT. See `LICENSE`.
