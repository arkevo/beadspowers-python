---
description: Ship a fully-executed beads epic — integrate the shared epic branch via a PR, close all child tasks + the epic, and report unblocked work. The batch analog of /beads-ship-task and the terminal step of the epic-batch pipeline. NEVER auto-runs; requires explicit invocation + a confirmation gate.
---

# Workflow: Ship an Epic (Python)

Take a **fully-executed** beads epic and ship it: **integrate the shared epic
branch** (commit + push, then offer how to integrate), **close the epic's child
tasks + the epic**, and report what is now unblocked. This is the **batch analog of
`/beads-ship-task`** (which ships a single task) and the **terminal step of the
epic-batch pipeline** —
`/workflow-planning-sequence` → `/workflow-writing-plans` →
`/workflow-execution-sequence` → `/workflow-execute-plans` → **this command**.

This command obeys the beads workflow router
(`.claude/rules/0_Beads x Superpowers/beads-workflow-router.md`), the hard-lock rules
(`.claude/rules/critical ai agent rule.md`), the git workflow
(`.claude/rules/Git Best Practices/no-direct-push-to-master.md` → never commit to
the trunk; feature branches; ship via PR), and the
safe-staging / plan-protection rules
(`.claude/rules/Git Best Practices/protect_plans_and_commit_all.md`). It uses the
**beads plugin skills** for all issue operations
(`.claude/rules/0_Beads x Superpowers/skill-usage.md`), never ad-hoc `bd` CLI.

> **Repo conventions this command honors** (per the router): **single repo, no
> multi-repo hub** (no `bd repo sync`); **shipping goes through a PR** — never a
> direct commit or push to `master` / `main`; Beads is the source of truth, and
> any external-tracker mirror is downstream.

---

## 🔒 EXECUTION LOCK (read first)

This command performs **outward-facing, hard-to-reverse actions**: it pushes,
opens a PR, and closes the epic. Therefore:

- **It NEVER runs as an automatic handoff.** No skill, no router rule, and
  **`/workflow-execute-plans` in particular** may auto-invoke it. `execute-plans`
  ends at `ex:done`; shipping is a **separate, deliberate** user action.
- **It runs only when BOTH hold:** (1) the user **explicitly invokes**
  `/workflow-ship-epic`, **and** (2) the user **confirms at the Step 4 ship gate**.
- **It never merges to `main` on its own.** Merge-to-`main` is a destructive git
  action that needs **explicit owner confirmation** every time
  (`.claude/rules/critical ai agent rule.md`). The default is commit + push the epic
  branch and stop.

If you arrived here from another command's "next step" suggestion, **stop** and
confirm the user actually wants to ship before doing anything.

---

## Core Principle — One Epic, One Integration

The pipeline builds on **one shared epic branch** (`/workflow-writing-plans` writes
one plan-file per task on that branch; `/workflow-execute-plans` merges each per-task
worktree back into it on green QA + passed gates). Shipping therefore integrates that
**one epic branch** as a single unit — not one PR/merge per task. That is the whole
point of the batch pipeline: many tasks, one reviewable/integratable branch. (Contrast
`/beads-ship-task`, which integrates a single task's branch.)

---

## Input

`$ARGUMENTS` = `<epic-id>`. **No arg** → show in-progress
epics (`beads:list --status=in_progress --type=epic`), else the last 10 created
epics, and ask the user to pick. Never infer-and-run.

Derive `<epic-slug>` (lowercase kebab from the title) for artifact/branch lookups.

---

## Model & Budget

| Setting | Value |
|---------|-------|
| This command's own work | **Cheap** — read beads state, assemble an integration summary, drive the chosen `commit-commands:*` skill. No agent fan-out. |
| Optional | One short summarizer agent **may** draft the change summary / PR body from the per-task plans + QA ledger; not required. |
| Git | Integrates **ONE** epic branch. Default = commit + push. **Never merges to `main`** without explicit confirmation. Safe staging only (no `git add -A`). |

---

## Step Map — Segmentation at a Glance

Every step is **[main ctx]** — this command is an interactive ship, never a detached
fan-out. Labels advance at the **END** of each step.

| # | Step | End label |
|---|------|-----------|
| 0 | Resume check (idempotency) | — |
| 1 | Precondition: execution complete (HARD GATE) | — |
| 2 | Cross-epic closure check | — |
| 3 | Assemble integration summary | — |
| 4 | 🛑 Ship gate (explicit confirm + integration choice) | — |
| 5 | Commit + push (+ chosen integration) | `sh:pushed` |
| 6 | Close tasks + epic (idempotent) | `sh:shipped` |
| 7 | Report unblocked + next epic | — |

---

## Step 0: Resume Check (idempotency) [main ctx]

Read the epic's `sh:*` label (`beads:show`). Resume from the furthest stage:
- `sh:pushed` → the epic branch is already pushed (and possibly PR'd/merged per the
  Step 4 choice); skip Step 5, continue at Step 6.
- `sh:shipped` → already shipped; report status and stop (idempotent).
- No `sh:*` label → start at Step 1.

There is intentionally **no separate status command** — the `sh:*` epic label is the
resume mechanism, mirroring `wp:*` / `ex:*`.

## Step 1: Precondition — Execution Complete (HARD GATE) [main ctx]

This command ships only a **fully-executed** epic. Verify **every child task** of the
epic carries **`ex:done`** (via `beads:show` / `beads:list`). If a cross-epic closure
was executed (detected from the pre-existing `exec:<slug>` label set by
`/workflow-execution-sequence`; see Step 2), verify every **closure** task is `ex:done`, not just the named
epic's children.

If **any** task is `ex:blocked`, `ex:smoke-pending`, or lacks `ex:done`:

> ⚠️ Epic **<epic-id>** is not fully executed — cannot ship. Outstanding:
> - <task-id> "<Title>" — <ex:blocked | ex:smoke-pending | not started>
>
> Finish execution with `/workflow-execute-plans` (resolve blocked bugs / run the
> batched smoke session) first.

**Refuse to ship a partially-executed epic.** Also confirm you are on the epic's
shared branch with all per-task worktrees merged (no `ex:smoke-pending` worktree left
un-merged).

## Step 2: Cross-Epic Closure Check [main ctx]

Ties to the execution-closure model (`/workflow-execution-sequence`). If execution
spanned **more than one epic** (an `exec:<slug>` closure label is present, or tasks
from other epics were built into this branch), **STOP and ask** — never guess the
integration strategy:

```
This epic's execution closure spans multiple epics: <epic-a>, <epic-b>.
How should I ship it?
  1. One combined integration for the whole closure (single branch)
  2. One integration per owning epic
```

For a self-contained epic (closure == epic), skip straight to Step 3.

## Step 3: Assemble Integration Summary [main ctx]

Build a change summary (used for the commit body and, if the user later chooses a PR,
the PR body) in the **project's `/beads-ship-task` format**:

- **Summary** — thorough technical summary, grouped by logical layer/component when
  the epic spans areas. The *what* and *why*, not file names. (May be drafted by the
  optional summarizer agent from the per-task plans under `docs/plans/<epic-slug>/`.)
- **Test Results** — pull the **QA ledger** produced by `/workflow-execute-plans`
  (per-task `diff · level · skill · result`, plus the cumulative full-sweep line),
  test counts (passed/failed, pre-existing failures called out separately), new tests
  added, and the **batched smoke session** outcomes.
- **Beads** — the **epic ID** and **all child task IDs** (and closure task IDs if
  Step 2 chose a combined integration). Use `beads:show` on the epic.

Also confirm behavior-affecting changes have their **doc updates** (README,
guides, `.env.example`, API docs) staged with the code.

## Step 4: 🛑 Ship Gate — Explicit Confirm + Integration Choice [main ctx]

This is the **permission gate** mandated by the EXECUTION LOCK. Show exactly what will
happen and require an explicit confirmation before anything outward-facing:

```
🚢 Ship epic **<epic-id> "<Title>"**

Branch:   <epic-branch>   (current)
Tasks:    N child tasks (all ex:done) → will be CLOSED on ship
Epic:     will be CLOSED after integration
Summary:  <change-summary preview>

Will: commit + push the epic branch, then open a PR
      (`commit-commands:commit-push-pr`, body from the summary above).

Proceed? (yes / edit summary / cancel)
```

Do nothing outward-facing until the user confirms. **Never merge to the trunk
directly** — the PR is the integration path.

## Step 5: Commit + Push (+ chosen integration) [main ctx]

On confirm, invoke the matching skill (do not hand-roll commit/push/PR logic):

- `commit-commands:commit-push-pr` (PR body = the Step 3 summary).

Honor:
- **Safe staging** (`protect_plans_and_commit_all.md`): stage explicitly by path; never
  `git add -A`; flag unexpected deletions; **never delete plans** under `docs/plans/`.
- **No direct trunk commits or pushes** (`no-direct-push-to-master.md`): integration
  always goes through the feature branch and the PR.

Advance the epic label to **`sh:pushed`** and echo the branch / PR URL.

## Step 6: Close Tasks + Epic (idempotent) [main ctx]

1. **Close each `ex:done` child task** still `open` via `beads:close` with a meaningful
   reason. (Idempotent — skip any already closed.)
2. **Close the epic** via `beads:close` (`--reason="All child tasks completed"`).
   Skip if `/workflow-execute-plans` already closed it.
3. **Do NOT auto-promote the next epic.** Identify the next open epic by priority
   (P0 → P1 → P2 → P3 → P4) and name it in the Step 7 report, but never run
   `beads:update <next-epic-id> --status=in_progress` here — marking the next epic
   active is the user's call, not a side effect of shipping this one.

Advance the epic label to **`sh:shipped`**.

> If the user chose "push only" (integrate later), still close the tasks/epic now — the
> work is done and reviewable. If they prefer to hold closure until merge, stop at
> `sh:pushed` and close on a re-run after merge.

## Step 6.5: Publish Beads (team sync) [main ctx]

After the epic + child tasks are closed (all beads mutations done), publish beads so
teammates get the closure.

**Default setup (`issues.jsonl` in git):** the beads changes are files in the repo —
they ship with Step 5's commit. Nothing extra to do here.

**Dolt-remote setup:** beads is a **second channel** that Step 5's `git push` did not
ship:
```bash
bd dolt pull        # fast-forward first
bd dolt push        # publish the beads changes
```
If the push is rejected as diverged, `bd dolt pull` and retry — never `--force` except
a deliberate, agreed re-baseline.

> If you mirror Beads to an external tracker, reconcile it here — an epic close fires a
> per-`bd close` hook once per child task plus once for the epic, and hooks fail
> silently. The mirror is downstream; Beads remains the source of truth.

## Step 7: Report — Epic Status & Next-Steps Summary [main ctx]

Show what is now unblocked, the branch / PR URL, and recommend `/clear` before the next
epic. Name the next open epic by priority (Step 6) as information, and ask whether the
user wants it marked `in_progress` — never do so automatically. Use `/beads-ship-task`'s
response formats (epic-not-complete / epic-complete / project-complete) adapted to the
epic level.

Give this in the same plain-language style as the rest of the pipeline's status
reports, not a bare label dump: name the epic that just shipped, say what beads
work is now unblocked by its closure (any task whose `blocks` edge pointed
here), and state the single next command — normally `/workflow-planning-sequence`
or `/workflow-execution-sequence` for whatever epic is next by priority (Step 6),
or nothing further if no open epics remain.

---

## Beads Label Lifecycle (ship-epic)

Epic-level labels (not per-task), advancing at the **end** of each step:

```
sh:pushed       (epic branch committed + pushed; PR/merge per the Step 4 choice)
   → sh:shipped (child tasks closed + epic closed)
```

Use `beads:label` / `beads:close` / `beads:show` / `beads:update` skills — never raw
`bd` in Bash. These labels make the ship resumable (Step 0).

---

## Out of Scope

- **Auto-invocation** — see the EXECUTION LOCK. This is always a deliberate user action.
- **Merging to the trunk directly** — integration is always via the PR.
- **Running tests / QA / smoke** — that is `/workflow-execute-plans`'s job; this command
  only *reports* the QA ledger + smoke outcomes it produced.
- **Per-task integration** — the batch unit is the epic branch. Use `/beads-ship-task`
  for single-task shipping.
- **Multi-repo hub sync** — not part of this template (no `bd repo sync`).
- **Creating or closing work in an external tracker** — any mirror is downstream,
  never the tracker.

---

## CRITICAL — Honor Project Rules

- **EXECUTION LOCK:** never auto-run; explicit invocation + Step 4 confirm required;
  never merge to the trunk — integration is via the PR.
- **Precondition (Step 1):** never ship a partially-executed epic — every task
  (closure-wide) must be `ex:done`.
- **Cross-epic closure (Step 2):** never guess the integration strategy when the
  closure spans epics — ask.
- **Git workflow (`no-direct-push-to-master.md`):** never commit or push to the trunk
  directly; ship through a PR; use the `commit-commands:*` skills.
- **Safe staging + plan protection (`protect_plans_and_commit_all.md`):** explicit
  staging, no `git add -A`, never delete `docs/plans/` files, flag unexpected deletions.
- **Protected paths (`critical ai agent rule.md`):** if the epic's merged diff touched
  `migrations/`, managed-cloud resources, secrets/`.env`, or production deploy config,
  those tasks must already have been force-attended + approved in
  `/workflow-execute-plans` Step 5 — re-confirm before integrating.
- **Docs-before-push:** behavior-affecting changes ship with their doc updates.
- **Any external tracker is downstream:** reconcile a mirror after closure if you have
  one; never treat it as the tracker.
- **Beads via skills:** `beads:*` skills only, never raw `bd` in Bash.

---

> The ship logic here is portable across projects: one epic branch, one integration,
> a hard precondition on execution completeness, and a single confirmation gate. Only
> the QA-ledger source, the smoke wording, and your integration policy are
> project-specific — adapt those and leave the rest.
