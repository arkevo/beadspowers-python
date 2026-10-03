---
description: Author + refine an implementation plan for the tasks in a planning-sequence file, single-pass — fanning out per wave (parallel / sequential / spike) and deferring exec-gated tasks until their upstream is executed
---

# Workflow: Writing Plans from a Sequence File

Produce and refine an implementation plan for the tasks named in a
**planning-sequence file** (the artifact emitted by
`/workflow-commands:workflow-planning-sequence`). Per-task work fans out across **Claude
Workflows** (the `Workflow` tool), but — unlike a flat fan-out — this command
**obeys the sequence**: it plans wave-by-wave, pipelines `SEQ-PLAN` chains so a
downstream plan reads the real upstream decision, emits lightweight spike plans
for `SPIKE-FIRST` tasks, and **defers `EXEC-GATED` tasks** until their upstream
is actually executed. Interactive review happens in the **main context** between
workflow runs.

This command obeys the beads workflow router
(`.claude/rules/0_Beads x Superpowers/beads-workflow-router.md`) and saves all
artifacts under `docs/plans/<epic-slug>/` per Rule 1 of the plan-protection rule
(`.claude/rules/Git Best Practices/protect_plans_and_commit_all.md`). The per-epic subfolder + `<task-id>-<slug>.md`
naming is an intentional epic-folder organization that still honors the rule's
intent (plans as permanent files under `docs/plans/`).

This is the **planning** half of the pipeline:
`/workflow-commands:workflow-planning-sequence` (decompose → classify → order → emit sequence
file) → **this command** (author plans) → `/workflow-commands:workflow-execute-plans` (build).
Execution, QA, smoke gates, and worktrees are **out of scope** here.

---

## Core Principle — Obey the Sequence, Plan Once

**Planning is interactive + non-conflicting; execution is parallel +
conflicting.** A background Workflow **runs detached and cannot pause for
interactive input.** So this command is a **segmented sequence**:

- **Workflow fan-outs** handle the parallel, automated work (draft, refine,
  apply), driven by the sequence file's waves.
- **Main-context steps** handle anything that needs the user (load, the budget
  gate, the single review gate).

Each step row below is tagged **[workflow]** or **[main ctx]**. Never collect
user input from inside a Workflow — return to main context first.

Because planning writes a **separate file per task**, all per-task work is
**non-conflicting** and runs on a **single shared epic branch** — no worktrees.
The sequence is about *which plans may be written when*, not about file
conflicts.

---

## Input — A Planning-Sequence File

`$ARGUMENTS` = a **sequence-file path** (default: the newest
`docs/plans/**/*-planning-sequence.md`) **or** an **epic-id** (resolves to that
epic's sequence file under `docs/plans/<epic-slug>/`; if none exists, stop and
tell the user to run `/workflow-commands:workflow-planning-sequence <epic-id>` first). Accepting an
epic-id keeps `/workflow-commands:workflow-execution-sequence`'s handoff working. **No interactive
epic selection** — the conscious input is the sequence file (or the epic-id that
names it).

**Parse only the structured block.** The sequence file carries a
machine-readable block (frontmatter YAML or a fenced ```json) produced by
`/workflow-commands:workflow-planning-sequence`, reusing its `TASK_SCHEMA`:

```json
{
  "epic": "<epic-id>",
  "tasks": [
    {
      "id_slug": "db-foundation",
      "bead_id": "<task-id>",
      "title": "DB foundation (models + pgvector)",
      "plan_readiness": "PLAN-READY | SPIKE-FIRST",
      "track": "B",
      "wave": 1,
      "plan_depth": "PLAN-FULL | PLAN-LITE | TDD-DIRECT",
      "depth_reason": "…",
      "deps": [{ "on": "<task-id>", "type": "PARALLEL | SEQ-PLAN | EXEC-GATED", "why": "..." }]
    }
  ]
}
```

Read classification (`plan_readiness`, `plan_depth`, `deps[].type`, `deps[].on`,
`track`, `wave`) **from this block only** — never parse the human-readable
markdown table. The epic id for `wp:*` labels comes from the block's `epic`
field; a single fallback prompt is allowed only if the file carries no epic id.

**Consume plan depth — do not re-derive it.** `plan_depth` was assigned by
`/workflow-commands:workflow-planning-sequence` (its Axis 3, the batch mirror of
the router's *Sizing Gate — Claude picks the lane* section), adversarially
reviewed by its critic, and possibly **adjusted by the owner** at that command's
review gate. Re-deciding it here would silently discard the owner's call. If a
task carries **no** `plan_depth` — an older sequence file that predates the
depth axis — treat it as **`PLAN-FULL`** and name it once in the Step 2
preview. Never infer the cheapest option from a missing field.

If drafting a task reveals that its depth is plainly wrong (a "two-file" task
turns out to touch a migration), **stop that task, label it `wp:deferred`, and
report it** for re-classification. Do not quietly upgrade it mid-flight: the
depth is also what the owner budgeted at the preview gate. When deferring for
this reason, record it on the task with `beads:update` — an appended notes line
`wp:deferred (depth): <what is wrong>` — so later runs and reports can tell it
from an upstream wait.

**Consume precomputed waves — do not recompute.** The `wave:n` ordering is
authoritative (computed once by `/workflow-commands:workflow-planning-sequence`). This command
reads those waves; it does **not** re-run a topological sort. This keeps a
single planning-toposort implementation and prevents the two commands from
disagreeing on order.

**Reconcile on load, report, don't auto-fix.** Diff the sequence file's task set
against the epic's beads tasks. Report orphans **both directions** (in-file-not-
in-epic; in-epic-not-in-file), then proceed with the **intersection**. No silent
skips, no auto-mutation — if drift is real, the user re-runs
`/workflow-commands:workflow-planning-sequence`.

---

## Model & Budget

| Setting | Value |
|---------|-------|
| Draft/Refine agent model (Steps 3-4) | **Opus** (`opts.model: "opus"`) |
| Draft/Refine reasoning effort (Steps 3-4) | **Per task, by difficulty**: `medium`, `high` or `xhigh` — see "Effort by difficulty" below |
| Apply agent model (Step 6) | **Sonnet** (`opts.model: "sonnet"`) |
| Apply reasoning effort (Step 6) | **medium** |
| Git model | One shared epic branch (separate files per task → non-conflicting); Step 6 additionally uses short-lived per-bucket worktrees + a main-context merge when it splits — see Step 6 |
| Budget shown as | **% of the 5-hr usage limit** — Step 6 runs on Sonnet and isn't separately metered against that limit |

**Pass the tier alias, never a pinned version.** `opts.model` takes
`"opus"` / `"sonnet"` / `"haiku"` / `"fable"` — a *tier*, which resolves to
whatever generation of that tier the session is running. Do not write a
versioned id like `"claude-opus-4-8"` or `"opus-4.8"`: those are not enum
members, and even where one is tolerated it pins the fan-out to a
superseded generation while the main loop moves on. This file previously
said "Opus 4.8" throughout and was already stale — the tier alias is what
keeps it from going stale again.

**The model tier is settled, not a question for the user.** These rows are
the command's own configuration; they are not a choice to surface at the
budget gate or anywhere else. Never print the model in a preview and never
ask the user to confirm it. If they ask which model a run used, name the
tier or read the resolved id back from the run — but do not volunteer it.

Steps 3 and 4 do judgment-heavy work: discovering unknowns, drafting original
plan content, and tiering and reasoning about trade-offs. They use Opus
(`opts.model: "opus"`), with **effort chosen per task by difficulty**.

### Effort by difficulty (Steps 3 and 4)

Planning does not default every draft and refine agent to xhigh. **Effort
follows how hard the task is.** Step 6 is unaffected and stays Sonnet at
medium.

Don't invent a new difficulty rating. It is already recorded in the sequence
block's `plan_depth`, `plan_readiness` and `depth_reason`, set by
planning-sequence's depth axis and reviewed by the owner. Read the effort from
them:

| Task | Draft effort (Step 3) | Refine effort (Step 4) |
|---|---|---|
| `TDD-DIRECT` (task card) | `medium` | not refined |
| `PLAN-LITE` | `high` | not refined |
| `SPIKE-FIRST` (spike plan, any depth) | `high` | not refined |
| `PLAN-FULL`, no hard trigger | `high` | `high` |
| `PLAN-FULL` with any hard trigger | `xhigh` | `xhigh` |

**Hard triggers** are the design-risk subset of the Sizing Gate's Lane C
criteria. Check them against the task's description and `depth_reason`:

- **Sensitive areas:** it touches auth, security, payments, permissions, or
  user data.
- **Data or infra changes:** a schema change, a migration, or anything against
  production data or infrastructure.
- **Contracts and dependencies:** a client–server or service contract, a public
  API, or a new dependency.
- **Foundation plans:** it is the head of a `SEQ-PLAN` chain, so other tasks'
  plans are built on its decisions.
- **Open design:** real design alternatives exist, or the acceptance criteria
  are ambiguous.

**Ties go to `xhigh`,** the same tie-break toward more planning the Sizing Gate
uses. A task with no `plan_depth` is already treated as `PLAN-FULL` (see
"Input" above); with no trigger evident either, give it `xhigh`, since its
difficulty was never assessed.

How effort flows through the run:

- **Step 1** assigns each task's effort once, from the table.
- **Step 2's preview** shows the mix, and the owner can raise or lower any task
  there.
- **Steps 3 and 4** pass it as `opts.effort`.
- **Harder than expected:** if drafting shows a task is harder than its effort
  (a "lite" task turns out to need a migration), handle it like the wrong-depth
  case in "Input" above: label it `wp:deferred` and report it. Don't silently
  re-run it at a higher effort. When deferring for this reason,
  record it on the task with `beads:update` — an appended notes line
  `wp:deferred (effort): <what is wrong>` — so later runs and reports can tell
  it from an upstream wait.

### Apply step and concurrency

Step 6 is different in kind: every decision it applies already carries a
fully specified "Recommended / auto-selected" option written out by Step 4 —
Step 6 is copy-editing against a known target, not open design work. Use
Sonnet at medium effort there (`opts.model: "sonnet"`,
`opts.effort: "medium"`). See Step 6 for the batching/splitting technique
that keeps this step's cost from compounding across many small edits — a
naive one-agent-many-small-edits apply pass at Opus/xhigh has been observed
to cost 190k+ tokens and 15+ minutes for a single plan; that is a bug in how
the step was run, not an acceptable baseline.

Within a wave, pass every plannable task to the workflow at once; concurrency
is capped at **min(16, cores − 2)** and the rest queue. Use the workflow
`budget` object to scale toward the user's token target — roughly **one
agent per plannable task** per draft/refine step (Step 6 may use two agents
per task when it splits by section — see Step 6).

---

## Workflow Primitives (reference for the executor)

Inside a workflow script you have: `agent(prompt, opts)` (`opts.schema`,
`opts.model`, `opts.effort`, `opts.phase`), `parallel(thunks)` (barrier),
`pipeline(items, ...stages)` (no barrier — the natural fit for `SEQ-PLAN`
chains), `phase(title)`, `log(msg)`, and `budget`. `SEQ-PLAN` chains map onto
`pipeline()` so stage N+1 receives stage N's plan decisions:

```js
// Illustrative — a SEQ-PLAN chain: plan the parent, then feed its decisions down.
// t.effort is the per-task effort assigned in Step 1 ("Effort by difficulty").
pipeline(
  seqChain,
  (t) => agent(draftPrompt(t), { model: "opus", effort: t.effort, phase: "draft" }),
  (parentPlan, t) => agent(draftPrompt(t, { upstream: parentPlan }),
    { model: "opus", effort: t.effort, phase: "draft" })
);
```

---

## Step Map — Segmentation at a Glance

Stage labels advance at the **END** of each step.

| # | Step | Where | End label |
|---|------|-------|-----------|
| 0 | Unshipped-epic check, then resume check (idempotency) | main ctx | — |
| 1 | Load sequence file (parse block, resolve epic, reconcile) | main ctx | — |
| 2 | Preview & budget gate (by wave + deferred set) | main ctx | — |
| 3 | Sequence-aware draft (conditional, depth-driven) | **workflow** | `wp:drafted` / `wp:skipped` / `wp:carded` / `wp:deferred` |
| 4 | Refine + auto-select — Round 1 (upstream decisions injected) — **`PLAN-FULL` only** | **workflow** | `wp:refined-r1` |
| 5 | Review #1 — **`PLAN-FULL` only** | **main ctx** | — |
| 6 | Apply #1 → approve (lite plans, task cards and spike plans enter here for the stamp only) | **workflow** | `wp:applied-r1` → `wp:approved` + `status: approved` |
| 7 | Epic status & next-steps summary | main ctx | — |

Steps 4–5 process only `PLAN-FULL` implementation plans. `PLAN-LITE` plans,
`TDD-DIRECT` task cards and spike plans (every `SPIKE-FIRST` task, whatever its
depth) skip them and enter Step 6 for the approval stamp only, reaching the same
`wp:approved` + `status: approved` terminal state — so nothing downstream has to
know which depth produced a file.

---

## Step 0: Unshipped-Epic Check, then Resume Check [main ctx]

**0a — Check for a finished epic that never shipped.** Before touching this
epic, run the check in `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md`
(Rules 1 and 2):

- **Finished but never shipped:** an epic whose open children all carry
  `ex:done` while the epic itself has neither `sh:pushed` nor `sh:shipped`. Find
  candidates with `beads:list --type=epic --all`, then read each one's children
  with `beads:list --parent <epic-id> --all`.
- **PR opened, not merged:** a closed epic carrying `sh:pushed` but not
  `sh:shipped` — its integration PR was opened on the epic's close date and the
  merge has not been confirmed yet.
- **Stacking onto an unmerged branch:** run `git fetch origin`, then compare the
  current branch with the trunk (`git rev-list --left-right --count <trunk>...HEAD`,
  where `<trunk>` comes from `git symbolic-ref --short refs/remotes/origin/HEAD`).
  If the branch already carries another epic's unmerged commits, name that epic
  and the commit count, and say that shipping this branch would ship both.

If any of these turns up, surface it in the rule's words and ask before going
on: ship the finished epic first (`/workflow-commands:workflow-ship-epic <epic-id>`),
merge the open PR and re-run `/workflow-commands:workflow-ship-epic <epic-id>` so
it confirms the merge and adds `sh:shipped`, or proceed and stack this work on
top. It is a surface-and-ask, not a hard stop — what must never happen is
stacking silently. When nothing turns up, continue without comment.

**0b — Resume check (idempotency).** Before doing any task work, read each
task's `wp:*` stage label (via `beads:show` / `beads:list`) and **resume each
task from its furthest stage** — skip steps already completed.

- A task at **`wp:approved`** is **skipped** (idempotent) **unless** its source
  description changed since approval **or** the user passed `--force`.
- A task at **`wp:deferred`** is re-evaluated: an exec-gated task rejoins the
  pipeline once its upstream is executed (see Step 3's unblock signal), and a
  task deferred because its depth was plainly wrong rejoins once its depth has
  been re-classified (re-run `/workflow-commands:workflow-planning-sequence --epic <epic-id>`,
  or raise it at this command's Step 2 preview). Otherwise it stays deferred.
- A crashed/interrupted run resumes from the last label written.

```bash
# PLAN-FULL:               wp:drafted|wp:skipped → wp:refined-r1 → wp:applied-r1 → wp:approved
# PLAN-LITE:               wp:drafted|wp:skipped ─────────────────────────────────→ wp:approved
# TDD-DIRECT (task card):  wp:carded ─────────────────────────────────────────────→ wp:approved
# SPIKE-FIRST (any depth): wp:drafted ────────────────────────────────────────────→ wp:approved
# Deferred (any depth):    wp:deferred → (unblocked) → re-enters Step 3 on its route above
```

A resumed task takes its route from its **current** `plan_depth`, not from the
one in force when it was drafted. So if the owner raised a task from
`PLAN-LITE` to `PLAN-FULL` and re-ran, a task sitting at `wp:drafted` now
correctly flows into Step 4 instead of jumping to the approval stamp.

---

## Step 1: Load Sequence File [main ctx]

1. Resolve `$ARGUMENTS` to a sequence-file path (or its epic-id → file).
2. Parse the **structured block** (above). Resolve the epic id.
3. **Reconcile** the file's task set against the epic's beads tasks; report
   orphans both directions; continue with the intersection.
4. Group the plannable tasks by their precomputed `wave:n`, and split out the
   **deferred set** (`EXEC-GATED` tasks whose upstream is not yet executed, and
   any task whose notes carry a `wp:deferred (depth)` or `wp:deferred (effort)`
   line and whose depth or effort has not changed since — unless the owner
   overrides it at Step 2).
5. **Assign each plannable task its effort** (`medium` / `high` / `xhigh`) from
   "Effort by difficulty". For `xhigh`, note which hard trigger applied so the
   Step 2 preview can name it.

Do not author anything in this step — it only loads and validates.

---

## Step 2: Preview & Budget Gate [main ctx]

Before committing any workflow run, show a preview and require confirmation. The
estimate is a **heuristic band, not an exact meter.** Show the **wave shape**,
not just a count:

```
📋 Plan workflow for epic **<epic-id> "<Epic Title>"**
   (sequence: docs/plans/<epic-slug>/<file>-planning-sequence.md)

Wave 1 (parallel, plan now):            N
Wave 2 (seq-plan, after wave 1):        M
Spikes (lightweight plan now):          S
Deferred (exec-gated, blocked):         K   ← planned on a later run, after upstream executes
Deferred for depth/effort — needs your call: <task-id: reason>, … (override depth or effort for this run, or re-classify with /workflow-commands:workflow-planning-sequence)
Resuming: R from prior stages · skipping J already approved

Plan depth: F full (refined) · L lite (no refinement) · T tdd-direct (task card only)
            <named, if any: tasks defaulted to PLAN-FULL for want of a plan_depth field>
Effort:     A medium · B high · C xhigh
            <named: each xhigh task with its hard trigger, e.g. "<task-id>: migration">

Agents: ≈(N+M+S) + F (one per plannable task, plus one refinement agent per
        PLAN-FULL plan; capped at min(16, cores−2))
Estimated cost: ~X–Y% of the 5-hr usage limit

Artifacts: docs/plans/<epic-slug>/

Branches:  Step 6 may split a long plan across two worktree agents. This
           fan-out creates temporary worktree branches, which are merged back
           and removed as each agent finishes; approving this gate is the branch
           approval that `critical ai agent rule.md` requires.

Proceed? (yes / adjust scope / cancel)
```

The depth line is what makes the estimate legible: it is the difference between
"30 plans and 30 refinement rounds" and "6 plans, 9 short plans, 15 task cards".
It counts implementation tasks only; spike plans are counted on the Spikes line
and are never refined. If the owner wants a task planned deeper (or shallower)
than assigned, they say so here and it is honoured for this run — the same
override the planning-sequence review gate offers, available once more before
any spend. The effort line works the same way: the owner can move any task
between `medium`, `high` and `xhigh` here, and that choice wins over the
difficulty table for this run. An override lasts for this run only: the plan is
authored at the overridden depth and its frontmatter `plan_depth` records that
depth, while the sequence block and the `depth:*` label keep the classified
value — so a re-run or a resume after a crash uses the block's depth again
unless the owner restates the override. To make it permanent, re-classify with
`/workflow-commands:workflow-planning-sequence`.

Show the **Branches** line only when the run includes at least one `PLAN-FULL`
plan. Only those reach Step 6's apply agents, so a run of lite plans, task cards
and spike plans creates no branch, and the line is left out.

Do not start the Step 3 workflow until the user confirms.

---

## Step 3: Sequence-Aware Draft (conditional, depth-driven) [workflow]

Drive the fan-out **by class**, using the parsed block. Derive **shared
conventions** (naming, error-handling approach, migration numbering) once from
the wave-1 drafts and carry them as constraints into every later draft +
refinement (this is the slimmed remnant of "epic criteria" — folded into context,
written to no separate file).

| Class | Behavior |
|---|---|
| `PARALLEL` + `PLAN-READY` | Fan out together — this is **wave 1** |
| `SEQ-PLAN` | **Pipeline**: author after the upstream plan lands; inject the upstream plan's concrete design decisions (schema, interface, types) into this task's drafting + refinement context |
| `SPIKE-FIRST` | Author a **lightweight spike/prototype plan** (goal, the unknown to resolve, prototype steps, the contract the spike must produce, **and the probe frontmatter — `spike_probe` / `probe_steps` / `needs_human_verdict` — telling `/workflow-commands:workflow-execute-spikes` how to exercise it**; the available `spike_probe` values are defined by that repo's executor), **not** a full implementation plan |
| `EXEC-GATED` | **Do not author.** Defer; label `wp:deferred`; report "blocked until `<upstream>` is *executed*." |

**Then apply plan depth — it decides how much gets authored.** The class table
above says *when* a task is authored and against what context; `plan_depth`
says *how deep*. Both apply, except that `SPIKE-FIRST` overrides depth
entirely: a spike always gets its lightweight spike plan, and a spike plan is
never refined.

| `plan_depth` | Author | Refinement (Steps 4–5) |
|---|---|---|
| `PLAN-FULL` | A full plan via `superpowers:writing-plans`. | **Yes** — Round 1 as normal. |
| `PLAN-LITE` | A **short** plan via `superpowers:writing-plans`: the goal, the ordered steps, the files touched, the testing strategy and the risks. No alternatives analysis and no decision log — the approach is already settled. | **No.** Straight to the Step 6 approval stamp. |
| `TDD-DIRECT` | **No plan.** A minimal **task card** (below). | **No.** Straight to the Step 6 approval stamp. |

**The `TDD-DIRECT` task card.** It is written to the normal path
`docs/plans/<epic-slug>/<task-id>-<slug>.md` with the normal frontmatter plus
`plan_depth: tdd-direct`, so every downstream gate keeps working:
`/workflow-commands:workflow-execute-plans` requires a file with
`status: approved` and must not need a special case to find it. The card
carries only four things — the behaviour change, the acceptance criteria, the
files expected to change, and the **first failing pytest test** to write:

````markdown
---
smoke_test: required | none
smoke_steps: "..."   # "" when none
bead_id: <task-id>
plan_depth: tdd-direct
status: draft
---

# <task-id> — <Title> (task card)

**Behaviour change:** <one line: what is different once this lands>

**Acceptance criteria:**
- <an observable condition a reviewer can check>
- <another one, if there is one>

**Files expected to change:** `src/<your_package>/<module>.py`,
`tests/<path>/test_<module>.py`

**First failing test:** `tests/<path>/test_<module>.py::test_<behaviour>`

```python
def test_<behaviour>():
    # Arrange the input that shows the change, call the code, and assert the
    # new behaviour. It must fail before the change, for the stated reason.
    ...
```
````

The card is deliberately not a plan. `/workflow-commands:workflow-execute-plans`
executes it test-first with `superpowers:test-driven-development` — write the
named failing test, watch it fail, implement, stop — and never rebuilds a plan
from it.

**Conditional-draft skip (per task, per wave) — `PLAN-FULL` and `PLAN-LITE`
only.** Skip authoring only if the task description clears BOTH gates — (1) a
structural floor (scope, approach/steps, files touched, testing strategy, edge
cases present) and (2) the agent judges it genuinely sufficient for a future
executor. **Borderline → write the plan.** Skipped → the task description
becomes the plan file content. `TDD-DIRECT` never routes through this gate: it
already has its own, smaller artifact.

**EXEC-GATED unblock signal.** An `EXEC-GATED` task unblocks when its upstream
beads task is **closed / execution-labeled** (checked via `beads:show`). On a
re-run, deferred tasks whose upstream is now executed rejoin the pipeline. When
present, the optional `docs/plans/<epic-slug>/<spike-id>-findings.md` supplies
the **content** (measured interface/throughput) the now-unblocked downstream
plan reads. Execution itself happens in
`/workflow-commands:workflow-execute-spikes` (for the spike that produces the
findings) and `/workflow-commands:workflow-execute-plans` (for real
implementation tasks), never here.

Write each authored plan to `docs/plans/<epic-slug>/<task-id>-<slug>.md` with
frontmatter:

```yaml
---
smoke_test: required | none
smoke_steps: "..."   # human steps to smoke the change; "" when none
bead_id: <task-id>
plan_depth: full | lite | tdd-direct   # the depth this run uses: the sequence block's value, or the owner's Step 2 override; spike plans omit it
status: draft
---
```

> **Spike plans** additionally carry the probe frontmatter from the SPIKE-FIRST row —
> `spike_probe` / `probe_steps` / `needs_human_verdict` — and set `smoke_test: none`
> (a spike has no smoke gate; `/workflow-commands:workflow-execute-spikes` exercises + observes it
> instead, and records evidence into the findings file).

**End-of-step labels:** `wp:drafted` (a full, lite or spike plan authored) /
`wp:skipped` (description sufficient) / `wp:carded` (`TDD-DIRECT` task card
written) / `wp:deferred` (exec-gated with its upstream not yet executed, or a
depth found plainly wrong while drafting).

**Routing after this step.** `wp:drafted` / `wp:skipped` tasks whose depth is
`PLAN-FULL` (and that are not spikes) continue into Step 4. `PLAN-LITE` plans,
`TDD-DIRECT` task cards and spike plans **bypass Steps 4–5** and go straight to
Step 6 for the approval stamp — there is no refinement round to review, which is
the entire point of their depth. They still get `wp:approved` +
`status: approved` like everything else, so the execution gate is unchanged.

---

## Step 4: Refine + Auto-Select — Round 1 [workflow]

**Scope: `PLAN-FULL` implementation plans only.** `PLAN-LITE` plans,
`TDD-DIRECT` task cards and spike plans do not enter this step or Step 5 —
skipping the refinement round is what their depth buys, and a spike plan is a
throwaway prototype plan with nothing to refine. If that leaves nothing to
refine, say so plainly and go to Step 6 rather than spinning up an empty
fan-out.

Apply the shared Refinement Methodology (`references/refinement-methodology.md`) in
**`autonomous` mode**: fan out ~**one agent per drafted `PLAN-FULL` plan**
(deferred tasks excluded), passing the engine's content into each agent's context.
Each refine agent runs at **its task's assigned effort** (`high`, or `xhigh` for a
hard-trigger task, per "Effort by difficulty"), not a blanket xhigh. Per §Mode
Contract, autonomous mode uses a **fixed quota — 5 critical + 5 recommended**
decisions per plan and **auto-selects the recommended option** (§Recommendation
Logic), because a detached `Workflow` cannot pause for input. Constrain each
agent by the **shared conventions** (Step 3) and — for `SEQ-PLAN` tasks — by the
**upstream plan's decisions**.

Discover, tier, and analyze each decision **per the engine** (§Decision Discovery,
§Tier Taxonomy, §Per-Decision Anatomy) — do not restate the methodology here.

**Autonomous output** (this adapter's half of §Output Contract): store **every decision
verbatim** in `docs/plans/<epic-slug>/refinements.md` (single round — no Round 2), using
the per-decision anatomy fields. Layout:

```
## <task-id> "<Title>"

### Decision 1 (critical): <question>
- Option A — pros: ... · cons: ...
- Option B — pros: ... · cons: ...
Reasoning: ...
Recommended / auto-selected: Option A
Confidence: HIGH (B clearly weaker) | CLOSE (A barely edged B)
```

**End-of-step label:** `wp:refined-r1`.

🔔 After this workflow completes, fire a push notification via the
`PushNotification` tool (the pipeline now needs the user for Review #1).

---

## Step 5: Review #1 [main ctx]

Return to main context and hand the user `refinements.md`.

```
🔔 Round 1 refinements ready for **<epic-id>**.

Review: docs/plans/<epic-slug>/refinements.md  (opening in VSCode)

Submit changes either way:
  • Tell me in chat ("override decision 3 on <task-id> to option B"), OR
  • Edit refinements.md directly and save.

Say "done" when finished.
```

Open the file in VSCode. On **"done"**, **re-read `refinements.md`** from disk to
pick up direct edits, **and** fold in any changes the user stated in chat. The
two channels are merged before Step 6.

---

## Step 6: Apply #1 → Approve [workflow]

Fan out per plan. Apply the (possibly user-overridden) Round 1 decisions from
`refinements.md` into each `PLAN-FULL` `<task-id>-<slug>.md` plan file, then
stamp each: set frontmatter `status: approved`.

**`PLAN-LITE` plans, `TDD-DIRECT` task cards and spike plans enter here** with
no decisions to apply — they were never refined. For them this step is only the
stamp: set `status: approved` and label `wp:approved`, leaving the short plan,
task card or spike plan exactly as drafted. They reach the identical terminal
state, so `/workflow-commands:workflow-execute-plans`'s gate (`wp:approved` +
`status: approved`) and `/workflow-commands:workflow-execute-spikes`'s selection
need no special case for them.

**Model: Sonnet at medium effort** (`opts.model: "sonnet"`,
`opts.effort: "medium"`) — not Opus/xhigh. Every decision here already
carries a fully specified "Recommended / auto-selected" option from Step 4;
applying it is copy-editing against a known target, not design work.

**Batch edits — never make one Edit call per decision.** A single decision
often touches more than one place in a plan (a new step plus every
downstream cross-reference, once renumbering cascades), so 10 decisions
applied naively can easily become 25+ small Edit calls — and because this
all happens inside one continuous agent turn, every one of those calls
resends the full accumulated conversation so far, so cost grows much faster
than linearly with call count (this is exactly what produced the 190k-token,
15-minute apply run this rule exists to prevent). Instruct the agent to read
the plan once, plan out every change across all of its assigned decisions
*before* editing, then execute as few, as large Edit calls as it reasonably
can — one per contiguous section touched (a whole step block, the whole
"Contract" section, etc.), folding every decision that lands in that section
into that one call, rather than reopening the same region once per decision.

**Split across two agents when the drafted plan is large enough to justify
it** — as a rule of thumb, a plan file over roughly 400 lines. (Step 4's
autonomous mode always produces exactly 10 decisions — 5 critical + 5
recommended — regardless of plan size, so decision *count* is not a useful
split signal; plan *length* is. Below the threshold, one sonnet / medium
agent applying all 10 decisions with batched edits is already fast and
cheap — don't add worktree overhead for a small plan.)

When splitting: bucket the 10 decisions by which section of the plan they
primarily touch (their quoted step references make this cheap to determine),
aiming for two roughly even, **non-overlapping** buckets. Instruct each
bucket's agent to make surgical edits — touch only the lines its own
assigned decisions require, and never rewrite or re-flow a neighboring
bullet/sentence that belongs to a decision it wasn't assigned, even when
that neighbor sits inside the same list or section it's already editing.
A plan's Edge Cases/Interfaces sections are often one shared list every
decision funnels through, so "non-overlapping by topic" does not always
mean "non-overlapping by line" — keeping each edit narrow is what actually
shrinks the conflict surface when a shared section can't be avoided.

Run one agent per bucket, **each in its own `opts.isolation: 'worktree'`**,
applying only that bucket's decisions (batched per the rule above).

**Worktree base-drift guard (mandatory).** `isolation: 'worktree'` does not
start an agent on the epic branch: the worktree may start from the trunk, or be
a *reused* worktree whose branch was never moved to the epic branch's current
tip. In practice, bucket agents have silently landed on a commit several commits
behind the one Step 3/4 actually committed (in one run, a commit that predated
the epic's own planning-sequence commit). Guard against this explicitly rather
than relying on an agent to notice: capture the epic branch's current HEAD SHA
in main context right before launching this workflow, pass it via `args`
together with a bucket branch name, and make every bucket agent's **first
command**

```bash
git switch -c <bucket-branch> <epic-head-sha>
```

so it works on a fresh branch that starts exactly at the epic branch's tip.
Never `git merge <epic-head-sha>` into the worktree's own branch instead: when
that branch started from the trunk, the merge drags trunk commits the epic
branch does not have into the bucket branch, and from there into the epic branch
at merge-back. Never hand-reconstruct the plan file from `git show` either: a
reconstructed file matches content but has no git ancestry to the epic branch,
which then conflicts on merge-back even when both sides agree (see below). Name
the bucket branches `chore/wp-apply-<task-id>-<n>`; they are temporary, and the
Step 2 gate's approval covers creating them.

Have each agent commit its own change to the plan file on its own worktree
branch before returning — report that branch name in its structured result
so a main-context step can find it:

```js
const buckets = splitDecisionsByDisjointSection(decisions); // e.g. 2 buckets
const results = await parallel(buckets.map((bucket, i) => () =>
  agent(applyBucketPrompt(planFile, bucket, epicHeadSha, `chore/wp-apply-${task.id}-${i}`), {
    label: `apply-${task.id}-bucket${i}`, phase: 'Apply',
    model: 'sonnet', effort: 'medium',
    isolation: 'worktree', schema: APPLY_BUCKET_SCHEMA, // includes branch_name
  })));
```

**The merge happens back in main context, after the workflow returns** —
workflow scripts have no Bash/filesystem access, so this step cannot run
inside the script itself.

First verify each branch's ancestry before merging — do not assume the
sync guard above caught every case:

```bash
git merge-base --is-ancestor <epic-branch-head-sha> <bucket-branch>
```

**If it is an ancestor**, a plain merge is safe:

```bash
git merge <bucket-0-branch>
git merge <bucket-1-branch>
```

Because the two buckets touched disjoint sections, this is usually a clean
line-based merge. **If git reports a conflict anyway, the bucketing wasn't
actually line-disjoint** — resolve it by hand: read what each side actually
changed relative to the plan *before* Step 6, and combine each side's real
edit rather than picking one side wholesale (a bullet one bucket didn't
touch is still the pre-edit original text, not a competing decision — the
other bucket's edited version of that same bullet is the one that's real).

**If it is not an ancestor** (the worktree was still stale despite the
guard), do **not** `git merge` — git will report a spurious "both added
this file" conflict on the plan file even when the two sides' content fully
agrees, since neither branch's history actually contains the other's base
commit. Instead do a content-level three-way merge, using the plan file as
it existed right after Step 3/4 (before any Step 6 edits) as the merge base:

```bash
git show <pre-step6-commit>:<plan-file-path> > /tmp/original.md
git merge-file -p <bucket-branch-file> /tmp/original.md <other-side-file> > <plan-file-path>
```

This combines both sides' real edits from content directly, independent of
whichever commit each worktree happened to branch from. Resolve any
remaining conflict markers by hand exactly as above. This is the same
recovery procedure regardless of which bucket is stale, or whether both are.

Delete the worktree branches (and any leftover worktrees) after a clean
merge, whichever path was used.

**End-of-step labels (per task):** `wp:applied-r1` → `wp:approved` + plan
frontmatter `status: approved`.

This is the **plan-ready handoff**: `/workflow-commands:workflow-execute-plans` requires both
`wp:approved` and `status: approved` before it will execute a plan. **Deferred
(`wp:deferred`) tasks are not approved** — they are reported as blocked and
picked up on a later run once their upstream is executed. A task deferred for
its depth or effort (its notes say so) is picked up once the owner
re-classifies it or overrides it at Step 2. If
`/workflow-commands:workflow-execute-plans` is not yet installed, **stop at `wp:approved`** — the
plannable plans are complete; execution is handed off separately.

---

## Step 7: Epic Status & Next-Steps Summary [main ctx]

After Step 6 completes, give the user a plain-language status report on the
**whole epic** — not just the tasks this run touched. Pull every task's
current stage (`wp:*`, and `sk:*`/`ex:*` if execution already started on an
earlier wave) via `beads:show` / `beads:list`, and explain:

- **What's approved and ready** — every task now `wp:approved` + plan
  `status: approved`, whether from this run or a prior one.
- **What's still deferred, and why** — for every `wp:deferred` task, name its
  blocking upstream and say plainly whether that upstream is a spike waiting
  on `/workflow-commands:workflow-execute-spikes`, or a task waiting on `/workflow-commands:workflow-execute-plans`
  to actually build it. This is expected pipeline behavior, not an error —
  say so plainly rather than presenting it as a problem. A task deferred for its
  depth or effort is different: it needs the owner's call — re-classify it with
  `/workflow-commands:workflow-planning-sequence`, or override it at the next
  preview — so present it as a decision, not a wait.
- **Whether execution-sequence will matter** — if any approved task has a
  cross-epic `blocks`-predecessor with no `exec:<slug>` label yet, note that
  `/workflow-commands:workflow-execution-sequence` will be needed before `/workflow-commands:workflow-execute-plans`
  can run on the full closure; otherwise say plainly that this epic is
  self-contained and doesn't need it.
- **The single next command** — if there's a plannable spike,
  `/workflow-commands:workflow-execute-spikes <epic-id>`; if the currently-approved set is ready
  to build, `/workflow-commands:workflow-execute-plans <epic-id>`; if nothing more can happen
  until an earlier wave executes, say that plainly and name what's blocking it.

Keep this conversational, not a wall of tables — the goal is the same kind of
walkthrough a human would want after checking an epic's status mid-pipeline.

---

## Beads Label Lifecycle (writing-plans)

Per-task stage labels, advancing at the **end** of each step:

```
wp:drafted | wp:skipped | wp:carded | wp:deferred
      → wp:refined-r1          (PLAN-FULL plans only)
      → wp:applied-r1          (PLAN-FULL plans only)
      → wp:approved            (+ plan frontmatter status: approved — every route ends here)
```

`wp:carded` marks a `TDD-DIRECT` task card. `PLAN-LITE` plans, task cards and
spike plans go from their Step 3 label straight to `wp:approved`. `wp:deferred`
marks an exec-gated task whose upstream has not executed yet, or a task whose
depth was found plainly wrong while drafting. A deferred task stays out of the
refine/apply flow until a re-run finds it unblocked; it then re-enters Step 3
and takes the label its **current** depth produces — `wp:drafted` or
`wp:skipped` for a full or lite plan, `wp:carded` for a task card. Labels are
append-only history: the re-entering task keeps `wp:deferred`, and its furthest
stage wins (the router's *Label Ladders — Append-Only, Furthest Wins* section).

Use the `beads:label` / `beads:update` skills to read and advance labels — never
raw `bd` in Bash (per `.claude/rules/0_Beads x Superpowers/skill-usage.md`).
These labels are the checkpoint + idempotency mechanism (Step 0): crashed runs
resume, re-runs are incremental, and there is intentionally **no separate
status/resume command.**

---

## Artifacts — `docs/plans/<epic-slug>/`

| File | Contents |
|------|----------|
| `<task-id>-<slug>.md` | One file per task: a full plan, a short (lite) plan, a `TDD-DIRECT` task card, or a spike plan. Frontmatter: `smoke_test: required\|none`, `smoke_steps: "..."`, `bead_id: <id>`, `plan_depth: full\|lite\|tdd-direct` (spike plans omit it and carry `spike_probe` / `probe_steps` / `needs_human_verdict` instead), `status: draft\|approved` |
| `refinements.md` | Full Round-1 refinement analysis + auto-selected decisions. Verbatim options, pros/cons, reasoning, recommendation, auto-selection, confidence per decision. |
| `<spike-id>-findings.md` *(optional, external)* | Written during execution of a spike; supplies the measured contract that unblocks `EXEC-GATED` dependents. Read, not written, by this command. |

The sequence file itself (`*-planning-sequence.md`) is produced by
`/workflow-commands:workflow-planning-sequence` and consumed here. Plans are **permanent** under
`docs/plans/` (`Git Best Practices/protect_plans_and_commit_all.md` Rule 2) — never deleted after execution.

There is intentionally **no `cross-plan-verification.md`** — convergence is
handled upstream by `SEQ-PLAN` pipelining and the shared-conventions constraints,
not by a downstream cross-check.

---

## Notifications

Fire a **push notification** via the `PushNotification` tool **once** — at the
single review gate (after Step 4 → Review #1). Long workflow runs then don't
require babysitting the console. Do not notify for purely automated transitions.

---

## CRITICAL — Honor Project Rules

- **Beads router** (`.claude/rules/0_Beads x Superpowers/beads-workflow-router.md`):
  operates on the sequence file's tasks under one epic, using `wp:*` stage
  labels. Scope all task listing to that epic.
- **Plans location** (`.claude/rules/Git Best Practices/protect_plans_and_commit_all.md`): every artifact lives
  under `docs/plans/<epic-slug>/`. Plans are permanent.
- **Writing plans**: when authoring a full or lite plan in Step 3, **always**
  use `superpowers:writing-plans` — never hand-roll plan prose. A `TDD-DIRECT`
  task card is not a plan; it follows the card format in Step 3.
- **Beads via skills**: use `beads:*` skills, never raw `bd` in Bash.
- **No worktrees here, with one exception**: planning is non-conflicting on
  one shared epic branch. Full execution, QA, and smoke gates still belong to
  `/workflow-commands:workflow-execute-plans`. The one exception is Step 6's optional split-apply
  path, which uses short-lived per-bucket worktrees purely to keep two
  sonnet / medium agents from racing on the same plan file — those are merged
  back into the shared epic branch before the step ends, never left standing.
- **Obey the sequence**: never flat-fan-out all tasks at once; plan by wave,
  pipeline `SEQ-PLAN`, defer `EXEC-GATED`. The precomputed `wave:n` from the
  sequence file is authoritative — do not recompute it.
- **Budget gate first**: never start the Step 3 workflow before the Step 2
  confirmation.
- **Draft/refine effort by difficulty**: Opus at each task's assigned effort —
  `medium` for task cards, `high` for lite and spike plans, and `high` for full
  plans, rising to `xhigh` with a hard trigger; ties go to `xhigh`. Never a
  blanket xhigh. Step 6 apply stays Sonnet at medium.
- **Depth is read, never re-derived**: `plan_depth` comes from the sequence
  block; a missing depth means `PLAN-FULL`, and a plainly wrong one is deferred
  and reported, never silently upgraded.
- **Step 6 cost control**: Sonnet at medium effort, batched edits (plan all
  changes before editing, one Edit call per section not per decision), and
  split across worktree-isolated agents above ~400 plan lines, merged back in
  main context. Never default Step 6 to Opus/xhigh — that pairing has
  already produced a 190k-token, 15-minute apply run for what should be a
  mechanical copy-edit pass.
- **Step 6 worktree base-drift guard**: an isolated worktree is not guaranteed
  to start at the epic branch's current tip. Every split-apply agent's first
  command is `git switch -c <bucket-branch> <epic-head-sha>` (the SHA passed via
  `args`) — never `git merge <sha>`, which can drag trunk commits in, and never a
  hand-reconstructed file. In main context, verify each bucket branch's ancestry
  before merging; if it isn't an ancestor, use a content-level `git merge-file`
  against the pre-Step-6 original instead of `git merge` (which would report a
  spurious conflict even on agreeing content). See Step 6 for the full procedure
  — this has already happened in practice, not a hypothetical.
