---
description: Ship a fully-executed beads epic — open one PR for the shared epic branch, close all child tasks + the epic, and mark the epic shipped once a re-run confirms the PR merged. The batch analog of /workflow-commands:beads-ship-task and the terminal step of the epic-batch pipeline. NEVER auto-runs; requires explicit invocation + a confirmation gate.
---

# Workflow: Ship an Epic (Python)

Take a **fully-executed** beads epic and ship it: **open one PR for the shared
epic branch** (commit + push + PR), **close the epic's child tasks + the epic**,
and report what is now unblocked. The epic counts as **shipped** only once that
PR has merged: the owner merges it, then re-runs this command, which confirms
the merge and marks the epic `sh:shipped`. This is the **batch analog of
`/workflow-commands:beads-ship-task`** (which ships a single task) and the **terminal step of the
epic-batch pipeline** —
`/workflow-commands:workflow-planning-sequence` → `/workflow-commands:workflow-writing-plans` →
`/workflow-commands:workflow-execution-sequence` → `/workflow-commands:workflow-execute-plans` → **this command**.

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
  **`/workflow-commands:workflow-execute-plans` in particular** may auto-invoke it. `execute-plans`
  ends at `ex:done`; shipping is a **separate, deliberate** user action.
- **It runs only when BOTH hold:** (1) the user **explicitly invokes**
  `/workflow-commands:workflow-ship-epic`, **and** (2) the user **confirms at the Step 4 ship gate**.
- **It never merges to the trunk.** Integration is always the PR: this command
  commits and pushes the epic branch, opens the PR, and stops. The owner reviews
  and merges it — merge-to-trunk is a protected action under
  `.claude/rules/critical ai agent rule.md` — and a re-run afterwards only
  confirms the merge.

If you arrived here from another command's "next step" suggestion, **stop** and
confirm the user actually wants to ship before doing anything.

---

## Core Principle — One Epic, One Integration

The pipeline builds on **one shared epic branch** (`/workflow-commands:workflow-writing-plans` writes
one plan-file per task on that branch; `/workflow-commands:workflow-execute-plans` merges each per-task
worktree back into it on green QA + passed gates). Shipping therefore integrates that
**one epic branch** as a single unit — not one PR/merge per task. That is the whole
point of the batch pipeline: many tasks, one reviewable/integratable branch. (Contrast
`/workflow-commands:beads-ship-task`, which integrates a single task's branch.)

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
| This command's own work | **Cheap** — read beads state, assemble an integration summary, drive `commit-commands:commit-push-pr`. No agent fan-out. |
| Optional | One short summarizer agent **may** draft the change summary / PR body from the per-task plans + QA ledger; not required. |
| Git | Integrates **ONE** epic branch through **one PR** (commit + push + PR). **Never merges to the trunk** — the owner merges the PR. Safe staging only (no `git add -A`). |

---

## Step Map — Segmentation at a Glance

Every step is **[main ctx]** — this command is an interactive ship, never a detached
fan-out. Labels advance at the **END** of each step.

| # | Step | End label |
|---|------|-----------|
| 0 | Resume check; on a re-run, confirm the PR merged | `sh:shipped` (re-run only, once merged) |
| 1 | Precondition: execution complete (HARD GATE) | — |
| 2 | Cross-epic closure check | — |
| 3 | Assemble integration summary | — |
| 4 | 🛑 Ship gate (explicit confirm) | — |
| 5 | Commit + push + open the PR | `sh:pushed` |
| 6 | Close tasks + epic (idempotent) | — |
| 6.5 | Publish beads (Dolt sync) | — |
| 7 | Report: PR opened, or epic shipped | — |

---

## Step 0: Resume Check + Merge Check (idempotency) [main ctx]

Read the epic's `sh:*` labels (`beads:show`). They are history — append-only, the
furthest one wins — so resume from the furthest:

- **`sh:shipped`** → the PR merged and a re-run confirmed it. Report the epic as
  shipped and stop.
- **`sh:pushed`** without `sh:shipped` → an earlier run opened the PR and closed
  the tasks, but nobody has confirmed the merge yet. This is the re-run the owner
  makes after merging:
  1. **Finish the closure first.** Run Step 6 and Step 6.5 again. Both are
     idempotent, and a run that stopped after opening the PR may not have
     finished them.
  2. **Ask GitHub whether the PR merged.** Take the PR URL and the epic head from
     the `PR:` line Step 5 appended to the epic's notes. If that line is missing,
     find the PR with
     `gh pr list --head <epic-branch> --state all --json url,state,mergedAt --limit 1`.
     Then run `gh pr view <pr-url> --json state,mergedAt`; `"state": "MERGED"`
     means merged. Ask GitHub before git: a squash or rebase merge rewrites the
     commits, so the epic head never becomes an ancestor of the trunk, and an
     ancestry check alone would wrongly say "not merged".
  3. **Only if `gh` cannot answer** (not installed, not signed in, or no PR
     found), fall back to git, with `EPIC_HEAD` set to the head commit from the
     `PR:` line:
     ```bash
     # snippet: merge-check
     EPIC_HEAD="${EPIC_HEAD:?set EPIC_HEAD to the head commit on the PR line of the epic notes}"
     trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
     if [ -z "$trunk" ] || ! git rev-parse -q --verify "$trunk^{commit}" >/dev/null 2>&1; then
       git remote set-head origin --auto >/dev/null 2>&1   # unset, or dangling after the remote renamed its default branch
       trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
       git rev-parse -q --verify "$trunk^{commit}" >/dev/null 2>&1 || trunk=""
     fi
     if [ -z "$trunk" ]; then
       echo "merge-check: unknown (no origin trunk found)"
     else
       git fetch --quiet origin || echo "merge-check: fetch failed; using the last fetched $trunk"
       git merge-base --is-ancestor "$EPIC_HEAD" "$trunk"; rc=$?
       case $rc in
         0) echo "merge-check: merged into $trunk" ;;
         1) echo "merge-check: not merged into $trunk" ;;
         *) echo "merge-check: unknown ($EPIC_HEAD is not a commit in this clone)" ;;
       esac
     fi
     ```
     A "not merged" from this fallback can also mean a squash merge, so say so
     when you report it.
  4. **Merged** → add `sh:shipped` to the epic (`beads:label`), read it back with
     `beads:show`, and go to Step 7 to report the shipped epic. **Still open, or
     unknown** → report "PR open, awaiting merge: <pr-url>" and stop. Nothing
     else happens until the owner merges the PR and runs this command again.
     **Closed without merging** (GitHub says `CLOSED`) → say exactly that: the
     epic is closed in beads, but its code never reached the trunk. Ask the owner
     whether to reopen that PR or open a new one; never report it as awaiting
     merge, and never add `sh:shipped`.
- **No `sh:*` label** → start at Step 1.

There is intentionally **no separate status command** — the `sh:*` epic labels are
the resume mechanism, mirroring `wp:*` / `ex:*`.

## Step 1: Precondition — Execution Complete (HARD GATE) [main ctx]

This command ships only a **fully-executed** epic. Verify **every open child task**
of the epic carries **`ex:done`** (closed spikes and closed bugs are finished work)
(via `beads:show` / `beads:list`). If a cross-epic closure was executed (detected
from the pre-existing `exec:<slug>` label set by
`/workflow-commands:workflow-execution-sequence`; see Step 2), verify every open
**closure** task is `ex:done`, not just the named epic's children.

If **any** open task is `ex:blocked`, `ex:smoke-pending`, or lacks `ex:done`:

> ⚠️ Epic **<epic-id>** is not fully executed — cannot ship. Outstanding:
> - <task-id> "<Title>" — <ex:blocked | ex:smoke-pending | not started>
>
> Finish execution with `/workflow-commands:workflow-execute-plans` (resolve blocked bugs / run the
> batched smoke session) first.

**Refuse to ship a partially-executed epic.** Also confirm you are on the epic's
shared branch with all per-task worktrees merged (no `ex:smoke-pending` worktree left
un-merged).

## Step 2: Cross-Epic Closure Check [main ctx]

Ties to the execution-closure model (`/workflow-commands:workflow-execution-sequence`). If execution
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

Build a change summary (used for the commit body and the PR body) in the **project's `/workflow-commands:beads-ship-task` format**:

- **Summary** — thorough technical summary, grouped by logical layer/component when
  the epic spans areas. The *what* and *why*, not file names. (May be drafted by the
  optional summarizer agent from the per-task plans under `docs/plans/<epic-slug>/`.)
- **Test Results** — pull the **QA ledger** produced by `/workflow-commands:workflow-execute-plans`
  (per-task `diff · level · skill · result`, plus the cumulative full-sweep line),
  test counts (passed/failed, pre-existing failures called out separately), new tests
  added, and the **batched smoke session** outcomes.
- **Beads** — the **epic ID** and **all child task IDs** (and closure task IDs if
  Step 2 chose a combined integration). Use `beads:show` on the epic.

Also confirm behavior-affecting changes have their **doc updates** (README,
guides, `.env.example`, API docs) staged with the code.

## Step 4: 🛑 Ship Gate — Explicit Confirm [main ctx]

This is the **permission gate** mandated by the EXECUTION LOCK. Show exactly what will
happen and require an explicit confirmation before anything outward-facing:

```
🚢 Ship epic **<epic-id> "<Title>"**

Branch:   <epic-branch>   (current)
Tasks:    N child tasks (all ex:done) → CLOSED when the PR opens
Epic:     CLOSED when the PR opens, labelled sh:pushed; marked shipped
          (sh:shipped) after the PR merges — re-run this command then
Summary:  <change-summary preview>

Will: commit + push the epic branch, then open a PR
      (`commit-commands:commit-push-pr`, body from the summary above).

Proceed? (yes / edit summary / cancel)
```

Do nothing outward-facing until the user confirms. **Never merge to the trunk
directly** — the PR is the integration path, and the owner merges it.

## Step 5: Commit + Push + Open the PR [main ctx]

On confirm, invoke `commit-commands:commit-push-pr` with the Step 3 summary as the PR
body — do not hand-roll the commit, push or PR logic.

Honor:
- **Safe staging** (`protect_plans_and_commit_all.md`): stage explicitly by path; never
  `git add -A`; flag unexpected deletions; **never delete plans** under `docs/plans/`.
- **No direct trunk commits or pushes** (`no-direct-push-to-master.md`): integration
  always goes through the feature branch and the PR.

Then record the PR, so a later re-run can confirm the merge, and label the epic:

1. Append one line to the epic's notes with
   `beads:update <epic-id> --append-notes "PR: <pr-url> · head: <epic-head-sha> · opened: <YYYY-MM-DD>"`,
   where `<epic-head-sha>` is `git rev-parse HEAD` right after the push.
2. Add **`sh:pushed`** to the epic (`beads:label`).
3. Read both back with `beads:show`. If either is missing, retry once, serially,
   then surface it.

Echo the branch and the PR URL. `sh:pushed` means **PR opened**, not shipped.

## Step 6: Close Tasks + Epic (idempotent) [main ctx]

1. **Close each `ex:done` child task** still `open` via `beads:close` with a meaningful
   reason. (Idempotent — skip any already closed.)
2. **Close the epic** via `beads:close` (`--reason="All child tasks completed"`).
   Skip it if it is already closed. It will not have been closed by
   `/workflow-commands:workflow-execute-plans`, which never touches bead status,
   so this step is the only status transition in the whole batch lane. (That is
   for the epic and its implementation tasks:
   `/workflow-commands:workflow-execute-plans` still closes the `Smoke gate:`
   beads it creates, and `/workflow-commands:workflow-execute-spikes` closes a
   finished spike as the unblock signal.) Child tasks reaching here read `open`
   with `ex:done` — the expected steady state before ship, not a missed update.
3. **Do NOT auto-promote the next epic.** Identify the next open epic by priority
   (P0 → P1 → P2 → P3 → P4) and name it in the Step 7 report, but never run
   `beads:update <next-epic-id> --status=in_progress` here — marking the next epic
   active is the user's call, not a side effect of shipping this one.

The epic keeps the `sh:pushed` label from Step 5 and does **not** get `sh:shipped`
here. Closing happens when the PR opens, but shipped means merged: only a re-run of
this command after the merge (Step 0) adds `sh:shipped`. Until then
`.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md` keeps flagging the
epic as "PR opened, not merged".

## Step 6.5: Publish Beads (team sync) [main ctx]

Code and beads travel on two channels. Step 5's `git push` shipped the code; the
closures from Step 6 still have to be published. Pull first, push last:

```bash
if bd dolt remote list 2>/dev/null | grep -q 'No remotes configured'; then
  echo "Beads: no Dolt remote configured — skipping bd dolt pull and push."
else
  bd dolt pull && bd dolt push
fi
```

With no Dolt remote yet, this prints that one line and carries on: the beads stay
in the local store, versioned by Dolt. (`bd dolt push` alone would skip quietly
without a remote, but `bd dolt pull` fails outright, hence the check.)
On a brand-new, empty remote the pull itself fails with "no branches found in remote":
seed it once with `bd dolt push` (which also publishes this ship's beads), and
the pull-then-push works from then on. Add a remote
later with `bd dolt remote add origin git+https://github.com/<owner>/<repo>.git`.
If the push is rejected as diverged, `bd dolt pull` and retry; never `--force`
except a deliberate, agreed re-baseline.

Then refresh the readable export with `bd export -o .beads/issues.jsonl`. It is a
snapshot for people and tools to read, not a sync channel, and it is never
committed (`.claude/rules/0_Beads x Superpowers/beads.md`).

> If you mirror Beads to an external tracker, reconcile it here — an epic close fires a
> per-`bd close` hook once per child task plus once for the epic, and hooks fail
> silently. The mirror is downstream; Beads remains the source of truth.

## Step 7: Report — Epic Status & Next-Steps Summary [main ctx]

This command runs at least twice for every epic, and the report says which run
this was:

- **First run — PR opened.** The tasks and the epic are closed and the epic is
  `sh:pushed`, but it is **not shipped yet**: give the PR URL and say that the
  owner merges it and then re-runs this command.
- **A re-run before the merge.** Report "PR open, awaiting merge: <pr-url>" and
  nothing else.
- **The confirming re-run — merged.** Step 0 found the PR merged and added
  `sh:shipped`; report the epic as shipped.

Report in the same plain-language style as the rest of the pipeline, not a bare
label dump, using `/workflow-commands:beads-ship-task`'s response formats
(epic-not-complete / epic-complete / project-complete) adapted to the epic level.
Say what beads work the closure unblocked (any task whose `blocks` edge pointed
here). Close with the next steps as a numbered list in which `/clear` is its own
step before the next phase's command:

- **After the first run, or a re-run before the merge:**
  1. Merge the PR.
  2. `/workflow-commands:workflow-ship-epic <epic-id>` again — confirms the merge
     and marks the epic shipped.
- **After the confirming re-run:** name the next open epic by priority (Step 6)
  as information and ask whether the user wants it marked `in_progress` — never
  do so automatically. Then:
  1. `/clear`
  2. The next epic's first batch command:
     `/workflow-commands:workflow-planning-sequence --epic <next-epic-id>` when its
     tasks have not been sequenced yet; otherwise the batch command for the
     earliest pipeline stage holding two or more of its tasks (the router's
     *Recommending What's Next — Batch Beats Single-Task* section). Nothing
     further if no open epics remain.

---

## Beads Label Lifecycle (ship-epic)

Epic-level labels (not per-task). `sh:pushed` is written at the end of Step 5 on
the first run; `sh:shipped` only by Step 0 on a re-run, once the PR has merged:

```
sh:pushed       (first run: PR opened; child tasks + epic closed — Steps 5–6)
   → sh:shipped (re-run: PR merged and confirmed — Step 0)
```

An epic at `sh:pushed` without `sh:shipped` is closed but **not shipped**. Use
`beads:label` / `beads:close` / `beads:show` / `beads:update` skills — never raw
`bd` in Bash. These labels make the ship resumable (Step 0).

---

## Out of Scope

- **Auto-invocation** — see the EXECUTION LOCK. This is always a deliberate user action.
- **Merging to the trunk directly** — integration is always via the PR.
- **Running tests / QA / smoke** — that is `/workflow-commands:workflow-execute-plans`'s job; this command
  only *reports* the QA ledger + smoke outcomes it produced.
- **Per-task integration** — the batch unit is the epic branch. Use `/workflow-commands:beads-ship-task`
  for single-task shipping.
- **Multi-repo hub sync** — not part of this template (no `bd repo sync`).
- **Creating or closing work in an external tracker** — any mirror is downstream,
  never the tracker.

---

## CRITICAL — Honor Project Rules

- **EXECUTION LOCK:** never auto-run; explicit invocation + Step 4 confirm required;
  never merge to the trunk — integration is via the PR.
- **Shipped means merged:** the first run ends at `sh:pushed` (PR opened, tasks and
  epic closed); only a re-run that confirms the merge (Step 0) adds `sh:shipped`.
  Never add `sh:shipped` on the strength of a pushed branch or an open PR.
- **Precondition (Step 1):** never ship a partially-executed epic — every open
  task (closure-wide) must be `ex:done`.
- **Cross-epic closure (Step 2):** never guess the integration strategy when the
  closure spans epics — ask.
- **Git workflow (`no-direct-push-to-master.md`):** never commit or push to the trunk
  directly; ship through a PR; use the `commit-commands:*` skills.
- **Safe staging + plan protection (`protect_plans_and_commit_all.md`):** explicit
  staging, no `git add -A`, never delete `docs/plans/` files, flag unexpected deletions.
- **Protected paths (`critical ai agent rule.md`):** if the epic's merged diff touched
  `migrations/`, managed-cloud resources, secrets/`.env`, or production deploy config,
  those tasks must already have been force-attended + approved in
  `/workflow-commands:workflow-execute-plans` Step 5 — re-confirm before integrating.
- **Docs-before-push:** behavior-affecting changes ship with their doc updates.
- **Any external tracker is downstream:** reconcile a mirror after closure if you have
  one; never treat it as the tracker.
- **Beads via skills:** `beads:*` skills only, never raw `bd` in Bash.

---

> The ship logic here is portable across projects: one epic branch, one integration,
> a hard precondition on execution completeness, and a single confirmation gate. Only
> the QA-ledger source, the smoke wording, and your integration policy are
> project-specific — adapt those and leave the rest.
