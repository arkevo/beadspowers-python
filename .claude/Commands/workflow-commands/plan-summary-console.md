---
description: Print a numbered + bulleted console summary of the refined plan so the user can review it without opening the .md file. Auto-invoked after plan-refinement-qa completes.
---

# Plan Summary (Console)

## Purpose

After plan refinement, print a scannable summary of the refined plan **directly in the Claude Code console** so the user does not have to open the plan file to review what will be executed.

## Triggers

- **Auto-trigger** — invoked by `beads-workflow-router` immediately after `workflow-commands:plan-refinement-qa` completes and the plan file is updated, BEFORE the execution gate is presented
- **Manual:** "summarize the plan", "plan summary", "show me the plan", "recap the plan"

## Workflow Step

```bash
echo "Plan Summary" > .beads/.workflow-step
```

## Inputs

- `plan_file` path from session state (the `docs/plans/<YYYY-MM-DD>-<topic>.md` file produced by writing-plans and updated by plan-refinement-qa)
- If `plan_file` is not in session state, ask the user which plan to summarize

## Output Format (required)

Print the following, exactly in this order, as plain console markdown:

```
Plan: docs/plans/<filename>.md
Refinement: <one-line delta — what changed during Q&A>

1. <Phase / top-level step name>
   - <sub-task or decision 1>
   - <sub-task or decision 2>
   - <files touched, if concise>

2. <Phase / top-level step name>
   - <sub-task or decision 1>
   - <sub-task or decision 2>

3. <Phase / top-level step name>
   - ...

Refinement Decisions applied: <N> (<X> critical, <Y> recommended, <Z> nice-to-have)
```

### Formatting rules

- **Numbered top-level items** — one per phase / major step, in execution order
- **Bulleted sub-items** under each number — concrete sub-tasks, files, or decisions
- **Keep it tight** — target ≤ ~40 lines total. If the plan is larger, collapse fine-grained file lists into a single bullet ("touches ~8 files under `src/foo/`")
- **Preserve order** — phases appear in the same order as the plan file
- **No narrative prose** — only the header lines, numbered list, and footer. The user wants to scan, not read
- **Do NOT paste the full plan** — this is a summary, not a dump

### What to include per phase

- The phase's goal in ≤ 10 words as the numbered line
- Key sub-tasks, decisions, or file groups as bullets
- Any refinement-driven changes to that phase (mark with `← refined` at the end of the affected bullet)

### What to exclude

- Full code samples from the plan
- Full acceptance criteria (summarize as one bullet if relevant)
- Boilerplate sections ("What's NOT in this plan", test scaffolding notes, etc.) unless they contain a refinement decision

## Reading the Plan

1. Read `plan_file` fully
2. Identify top-level phase / step sections (typically `## Phase N:` or `## Step N:` headings)
3. Extract the phase goal from the heading
4. From each phase body, pull the 2–5 most load-bearing sub-items as bullets
5. Read the `## Refinement Decisions` table (appended by plan-refinement-qa) to build the "Refinement" delta line and tag refined bullets

## Handoff to Execution Gate

After printing the summary, on a new line print:

```
Ready to execute.
```

Then immediately present the execution gate prompt (same wording as plan-refinement-qa handoff):

```
How would you like to execute this plan?

1. **Subagent-Driven (this session)** — Fresh subagent per task, review between tasks, fast iteration. Uses `/superpowers:subagent-driven-development`.
2. **Sequential Execution (this session)** — Execute tasks in batches of 3, pause for review between batches. Uses `/superpowers:executing-plans`.
```

## Bypass

The user can skip the summary by saying "skip summary" or "just execute" — in that case, go straight to the execution gate without printing the summary. Claude must never auto-skip.

## Natural Language Commands

| User Says | Action |
|-----------|--------|
| "1" / "2" | Select corresponding execution option |
| "skip summary" / "just execute" | Skip summary → execution gate |
| "expand N" / "more on step N" | Re-print phase N with deeper sub-items |
| "open the plan" | Print the absolute path so the user can open it |
