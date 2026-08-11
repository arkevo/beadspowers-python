---
description: Execute every approved plan in a beads epic with per-task worktree fan-out, TDD, python-verification QA gates, and batched manual smoke gates (FastAPI service) using segmented Claude Workflows
---

# Workflow: Executing Plans for an Epic (Python)

Execute the **approved** implementation plans for **every task in a beads
epic**. Per-task work fans out across **Claude Workflows** (the `Workflow`
tool): autonomous tasks run in parallel, each in its own **git worktree**, and
auto-advance on green QA; attended tasks (manual smoke, shared substrate,
protected paths) are **serialized behind beads gates** and resolved in the
**main context** where the user can be involved. This command obeys the beads
workflow router (`.claude/rules/0_Beads x Superpowers/beads-workflow-router.md`)
and the hard-lock rules (`.claude/rules/critical ai agent rule.md`).

This is the **execution** half of a two-command pair. Its sibling
`/workflow-writing-plans` produced the plans this command consumes. It requires
the **`wp:approved`** beads label **and** plan-frontmatter `status: approved` on
**every currently-plannable task in the epic** before it will run —
**`wp:deferred` tasks are exempt** (they genuinely can't be planned yet; see
the precondition below).

> **This is the Python variant.** QA runs the
> **`python-verification-{quick,standard,full}`** skills (ruff + mypy + pytest).
> Smoke means running the project the way you normally run it and exercising the
> changed surface — set `<run-command>` below to your project's start command
> (`python -m <your_package>`, `uvicorn app:main`, a CLI entrypoint, …). There is
> **no visual/design-fidelity gate** here; add one if your project has a UI
> surface worth pixel-checking.

> **Spikes and cross-epic closures.** `SPIKE-FIRST` tasks are **not** executed
> here — they run through `/workflow-execute-spikes` (a lightweight prototype +
> findings pass) and are already **closed** by the time this command runs. And when
> an epic's execution closure spans **multiple epics**, this command operates on the
> `exec:<slug>`-labeled **closure**, not just the named epic's children — see
> Step 0a.

---

## Core Principle — Why This Is Segmented

**Planning is interactive + non-conflicting; execution is parallel +
conflicting.** A background Workflow **runs detached and cannot pause for
interactive input.** Therefore this command is a **segmented sequence**:

- **Workflow fan-outs** handle the parallel, autonomous, non-interactive work
  (execute via TDD, QA, auto-fix, auto-advance on green) — each conflicting task
  isolated in its **own worktree** (`opts.isolation: 'worktree'`).
- **Main-context gates** handle anything that needs the user: the **batched
  manual smoke session**, **attended-task approval**, **protected-path stops**,
  and **blocked-bug** triage.

Each step row below is tagged **[workflow]** or **[main ctx]** so the future
executor knows where each runs. Never try to collect user input — smoke
pass/fail, protected-path approval, rollback decisions — from inside a Workflow;
return to main context first.

Because execution **mutates shared files**, per-task work is **conflicting** and
each autonomous task runs in its **own worktree**, merged on green QA + passed
gates. This is the opposite of the planning command, which writes a separate
file per task on one shared branch.

---

## Model & Budget

| Setting | Value |
|---------|-------|
| Agent model | **Opus** (`opts.model: "opus"`) |
| Reasoning effort | **medium** |
| Git model | **Per-task worktree isolation** for parallel autonomous tasks; merged on green QA + passed gates |
| Budget shown as | **% of the 5-hr Opus medium usage limit** |

**Pass the tier alias, never a pinned version.** `opts.model` takes
`"opus"` / `"sonnet"` / `"haiku"` / `"fable"` — a *tier*, which resolves to
whatever generation of that tier the session is running; a versioned id like
`"claude-opus-4-8"` is not an enum member and pins the fan-out to a superseded
generation. **The tier is settled configuration, not a question for the user:**
never print it in a preview and never ask the user to confirm it.

All workflow `agent(...)` calls in this command use Opus at **medium**
effort (`opts.model` + `opts.effort: "medium"`). Autonomous tasks pass to the
workflow as a parallel pool sized to the beads ready frontier; concurrency is
capped at **min(16, cores − 2)** per workflow and the rest queue. Use the
workflow `budget` object to scale the agent count toward the user's token
target — roughly **one agent per autonomous task** in flight.

---

## Workflow Primitives (reference for the executor)

Inside a workflow script you have: `agent(prompt, opts)` (one subagent;
`opts.schema` for structured output, `opts.model`, `opts.effort`, `opts.phase`,
and **`opts.isolation: 'worktree'`** to run the agent in a fresh git worktree),
`parallel(thunks)` (barrier — waits for all), `pipeline(items, ...stages)` (no
barrier — default for multi-stage per-item work), `phase(title)`, `log(msg)`,
and the `budget` object. You do **not** need to author a full runnable script;
structure the segmented runs and gates per the steps below. A short illustrative
snippet shape:

```js
// Illustrative only — autonomous tasks, each in its own worktree,
// Opus / medium, execute → QA → auto-advance on green.
parallel(autonomousTasks.map((t) => () =>
  agent(executeAndQaPrompt(t), {
    model: "opus",
    effort: "medium",
    isolation: "worktree",   // <-- per-task git worktree isolation
    phase: "execute-qa",
  })
));
```

Attended tasks are **NOT** placed in this `parallel(...)` pool — they are handled
in main-context gates (Steps 5–7) so the user can be involved.

---

## Step Map — Segmentation at a Glance

Stage labels advance at the **END** of each step.

| # | Step | Where | End label |
|---|------|-------|-----------|
| 0 | Scope + precondition + resume check | main ctx | — |
| 1 | Route tasks (autonomous vs attended) | main ctx | — |
| 2 | Schedule + preview/budget gate | main ctx | — |
| 3 | Autonomous fan-out: execute (TDD) → QA → auto-advance | **workflow** | `ex:executing` → `ex:qa:<level>` → `ex:done` / `ex:smoke-pending` / `ex:blocked` |
| 4 | Attended tasks (serialized behind beads gates) | **main ctx** | `ex:executing` → `ex:qa:<level>` → … |
| 5 | Protected-path stops (force-attended) | **main ctx** | `ex:blocked` until approved |
| 6 | Batched manual smoke session (run the service) | **main ctx** | `ex:smoke-pending` → `ex:done` (or reopen) |
| 7 | Blocked-bug triage | **main ctx** | — |
| 8 | Epic status & next-steps summary | main ctx | — |

There is **no design-fidelity stage** in this variant — it assumes no visual
surface to check against a design source. Every task goes `ex:qa:<level>` →
`ex:done` (or `ex:smoke-pending` when smoke-flagged). If your project has a UI
worth pixel-checking, add a stage label of your own between them.

---

## Step 0: Scope + Precondition + Resume Check (idempotency) [main ctx]

### 0a — Resolve execution scope (epic vs cross-epic closure)

`$ARGUMENTS` = `<epic-id>`. Resolve **what set of tasks** this run executes — the
epic alone is **not** always its execution scope (a `blocks` edge can point at a task
in another epic; see `/workflow-execution-sequence`):

- **`exec:<slug>` label present** (applied by `/workflow-execution-sequence` when the
  closure spans epics) → the scope is **every task carrying that label** (the
  transitive `blocks`-closure). Approval (0b), routing, and waves all operate over
  this set.
- **No `exec:<slug>` label** → check the epic for **open cross-epic `blocks`-
  predecessors** (tasks outside the epic that block its children). If any exist,
  **refuse**:

  > 🛑 Epic **<epic-id>** has cross-epic blockers (`<id>` in `<other-epic>`) but no
  > `exec:<slug>` closure label. Run `/workflow-execution-sequence <epic-id>` first to
  > compute + label the closure, then re-run this command.

  If none exist (self-contained epic), the scope is the epic's own children — the
  default.

Exclude `closed` tasks from the scope (their edges are already satisfied), mirroring
`/workflow-execution-sequence` Step 2. Everywhere below, **"the epic's tasks" means
this resolved scope.**

### 0b — Approval precondition (HARD GATE, `wp:deferred` exempt)

This command requires **scope-level approval** — but only over the portion of
the resolved scope (Step 0a) that is actually plannable right now. A task
carrying **`wp:deferred`** (an `EXEC-GATED` task whose upstream hasn't been
**executed** yet — see `/workflow-writing-plans`) is **excluded from this gate
entirely**. Its absence isn't incomplete planning; it's the pipeline correctly
waiting on an earlier wave to execute. Requiring `wp:deferred` tasks to be
approved up front would make any multi-wave epic permanently unexecutable —
wave *N+1* can't be approved until wave *N* is *executed*, and executing wave
*N* is this command's own job.

Before any execution work, verify **every task in the resolved scope that is
NOT `wp:deferred`** has BOTH:

1. the beads label **`wp:approved`**, and
2. plan frontmatter **`status: approved`** in its `docs/plans/<epic-slug>/<task-id>-<slug>.md`.

It will still **NOT execute a partial trickle among the plannable set** — a
task that is genuinely mid-planning (drafted but not yet approved, and **not**
`wp:deferred`) still blocks the whole run, since planning could still change
any plan. Only `wp:deferred` tasks are exempt. If **any non-deferred task** is
unapproved:

> ⚠️ Epic **<epic-id>** is not fully approved. These tasks are missing
> `wp:approved` / `status: approved`:
> - <task-id> "<Title>" — <missing signal>
>
> `/workflow-execute-plans` runs only when every currently-plannable task is
> approved. Finish planning with `/workflow-writing-plans` first, or pick a
> different epic.

**Refuse to execute the unapproved (non-deferred) tasks; warn on the rest.**
Read `wp:approved` (+ scope-level approval, `wp:deferred` tasks excluded) on
start → only run approved tasks. Report every `wp:deferred` task in the
Step 8 summary as "will run on a future pass, once `<upstream>` executes" —
never as a blocker to fix.

### 0c — Resume in-flight tasks

Read each task's `ex:*` stage label (via `beads:show` / `beads:list`) and
**resume each task from its furthest stage** — skip steps already completed. A
crashed/interrupted run resumes from the last `ex:*` label written; there is
intentionally **no separate status/resume command** — the `ex:*` labels are the
resumability mechanism.

```bash
# Inspect ex:* stage labels for the epic's approved tasks
# (use beads:* skills, not raw bd):
#   ex:executing → ex:qa:<level> → ex:smoke-pending → ex:done   (or ex:blocked)
```

Use the `beads:label` / `beads:show` / `beads:list` skills — never raw `bd` in
Bash (per `.claude/rules/0_Beads x Superpowers/skill-usage.md`).

---

## Step 1: Route Tasks — Autonomous vs Attended (risk classifier) [main ctx]

Classify **each approved task** as **autonomous** (runs in parallel, auto-advances
on green QA) or **attended** (serialized behind a beads gate, needs the user).

### Classifier inputs (autonomous vs attended)

| Input | Source | Effect |
|-------|--------|--------|
| `smoke-needed` | plan frontmatter (`smoke_test: required`) | → **attended** (needs a manual smoke gate — run the service, verify endpoints) |
| shared-substrate touch | plan's files-touched vs substrate set | → **attended** (conservative — see Step 6 overlap) |
| protected-path touch | plan's files-touched vs protected set (Step 5) | → **attended** (force-attended, never auto-merged) |
| diff-size | estimated lines changed | **QA depth only — NOT a risk signal** |

`task-type` is **dropped** — it is not a routing signal.

> Diff-size sets *how deep* QA runs (Step 3, quick/standard/full); it never makes
> a task attended on its own.

### Scheduler inputs (ordering + parallelism)

| Input | Effect |
|-------|--------|
| existing beads dependency graph | the **ready frontier** = the parallel pool for this wave |
| **write-set overlap** | overlapping write-sets → **serialize** or **worktree-isolate** |
| **QA outcome** | hard gate: **green → dependents proceed**; **red** handled per the disposition matrix (Step 3) |

### Config

- **concurrency cap** (defaults to min(16, cores − 2))
- **failure-handling policy** (how a red QA / blocked bug affects siblings)

**Optional config:** beads **priority** (ordering within the frontier) · user
**attention override** (force a task attended).

Produce the routed split: `{ autonomous: [...], attended: [...] }`.

---

## Step 2: Schedule + Preview / Budget Gate [main ctx]

Before committing any workflow run, show a preview and require confirmation. The
estimate is a **heuristic band, not an exact meter.**

```
🚀 Execute workflow for epic **<epic-id> "<Epic Title>"**

Approved tasks: M  (resuming K from prior ex:* stages, J already ex:done)
  • Autonomous (parallel, worktree-isolated): A
  • Attended (serialized — smoke / substrate / protected path): B
Deferred (wp:deferred, waiting on an earlier wave): D  ← not part of this run
Smoke gates to batch at the end: S
Concurrency cap: min(16, cores−2)
Estimated cost: ~X–Y% of the 5-hr usage limit

Autonomous tasks run to completion in parallel; smoke + attended work is
collected and presented as one batched session (walk-away batching).

Proceed? (yes / adjust scope / cancel)
```

Do not start the Step 3 workflow until the user confirms.

---

## Step 3: Autonomous Fan-Out — Execute (TDD) → QA → Auto-Advance [workflow]

Fan out the **ready frontier** of autonomous tasks as a `parallel(...)` pool,
**each task in its own worktree** (`opts.isolation: 'worktree'`). Per task, in
order:

1. **Execute following TDD.** Drive implementation via
   `superpowers:test-driven-development` — **tests first** (pytest), then
   implementation. This is genuine TDD, not just post-hoc QA. Use `superpowers`
   execution (`superpowers:executing-plans` /
   `superpowers:subagent-driven-development`) to work the plan file.
   *(End label: `ex:executing`.)*
2. **Analyze the actual diff → choose QA level** (NOT the plan's estimate).
   Compute the real diff and **record it** — this number is a required output,
   not an internal judgement:
   - **quick** < 50 lines · **standard** 50–200 · **full** 200+ / new modules /
     shared substrate (your package's core modules — `config.py`, `errors.py`,
     shared interfaces — plus service, API, and data-access layers, and any
     database `migrations/`).
   - Run `git diff --numstat <base>...<task-tip>` (or the worktree diff) and
     write the count into the **QA ledger** (see below). If you cannot state the
     diff size, you have not done this step.
3. **Run the recommended verification level — the SKILL, in MAIN CONTEXT:**
   `workflow-commands:python-verification-quick` /
   `workflow-commands:python-verification-standard` /
   `workflow-commands:python-verification-full`.
   - **This is the orchestrator's responsibility and runs in MAIN CONTEXT
     after the task's code lands** — post-merge for autonomous worktree tasks,
     inline for attended tasks — **regardless of whether a subagent
     implemented the task.** A subagent doing TDD + scoped pytest does **NOT**
     satisfy this step.
   - **No substitution (HARD RULE):** running `ruff check` / `mypy` / `pytest`
     by hand, a subagent's scoped tests, or an end-of-run full *test suite* do
     **NOT** count as "quick/standard/full verification." Only invoking the
     named `python-verification-{level}` **skill** counts. "Quick" means the
     quick *skill* ran, not "I ran tests."
   - **Record the level in the label:** advance to **`ex:qa:<level>`**
     (`ex:qa:quick` / `ex:qa:standard` / `ex:qa:full`) — never a bare `ex:qa`.
     The level must be auditable after the fact.
   - **Append a QA-ledger line** (one per task) and surface it in the final
     summary:
     `<task-id> · diff +X/-Y · level=<quick|standard|full> · skill=<name> · result=<green|red>`
   *(End label: `ex:qa:<level>`.)*
4. **Disposition of QA findings (two-axis matrix):**

   | | Minor | Significant |
   |---|---|---|
   | **Easy** | auto-apply (silent) | auto-apply (**flagged** in summary) |
   | **Hard** | beads **bug** + highlight | beads **bug** + highlight |

   Rule: *easily-fixed* → **auto-apply** (severity sets only silent vs. flagged);
   *not-easily-fixed* → **always a beads bug + highlight** (severity sets the bug
   priority). A hard finding sets the task **`ex:blocked`** and files the bug
   (Step 7).
5. **QA auto-fixes are committed separately** from the task implementation, so
   the fix can be reverted independently of the feature work. (Two commits: the
   plan implementation, then the QA auto-fix.)
6. **Auto-advance on green:** when QA is green and the task touches no smoke flag
   / no protected path, **merge the worktree** and mark **`ex:done`**; dependents
   proceed.
   - A **smoke-flagged** task does **not** auto-merge to done — it advances to
     **`ex:smoke-pending`** and its merge waits on the batched smoke session
     (Step 6).

**End-of-step labels (per task):** `ex:executing` → `ex:qa:<level>` →
`ex:done` (green, no smoke) / `ex:smoke-pending` (green, smoke flagged) /
`ex:blocked` (hard QA bug). A task may **not** reach `ex:done` until it carries
an `ex:qa:<level>` label and a QA-ledger line (a bare `ex:qa` means
"verification did not run").

> **Lane symmetry (both are HARD gates).** This per-task `ex:qa:<level>` label is
> the fan-out lane's embodiment of the router's *Hard Stop: Verification Before
> Ship / "Done"*. The single-task lane's analog is the `.beads/.verification-done`
> marker written by the `python-verification-{level}` skill and checked by
> `beads-ship-task` Step 0. Same rule, two mechanisms: **no path ships without a
> named `python-verification-{level}` skill having run** — auto-selected from the
> real diff here, level-detected by `beads-post-execution` there.

> **Smoke-gate creation happens here too:** when a task is `smoke_test:
> required`, create its dedicated **"Smoke gate: <task-id>"** beads issue and wire
> downstream substrate-overlapping tasks onto it — see Step 6's overlap rules.

---

## Step 4: Attended Tasks — Serialized Behind Beads Gates [main ctx]

Attended tasks (smoke-flagged, shared-substrate, protected-path, or
attention-overridden) run **serialized** in main context, behind their beads
dependency gates, so the user can be involved. Per attended task, run the **same
execute → QA flow** as Step 3 (TDD-first, diff-sized QA level via the **named
`python-verification-{level}` skill** — no ad-hoc-test substitution —
`ex:qa:<level>` label + QA-ledger line, the disposition matrix, separate QA-fix
commit), but:

- It is **not** in the parallel worktree pool; it runs one at a time on the epic
  branch (or its own worktree if write-sets overlap a concurrent task).
- A **smoke-flagged** attended task advances to **`ex:smoke-pending`** and its
  smoke verification is **collected for the batched session** (Step 6) rather
  than interrupting immediately.

🔔 If an attended task needs the user before the batched session (e.g. an
ambiguous decision the plan didn't settle), fire a push notification via the
`PushNotification` tool.

---

## Step 5: Protected-Path Guardrail (force-attended, never auto-merged) [main ctx]

Any task whose diff touches a **protected path** is **force-attended and never
auto-merged**, regardless of green QA. It **stops for explicit human approval**;
without approval it stays **`ex:blocked`** with a beads bug filed and highlighted.

**Protected paths (per `.claude/rules/critical ai agent rule.md`):**

- `migrations/` (any database migration)
- any **managed-cloud resource** mutation (tables, storage, secrets, gateways,
  deployments)
- secrets / `.env` / credentials
- production config / deploy surface (`Dockerfile`, production compose files,
  deploy manifests)
- git **history rewrites** / **force-push** / **merge to main**

When a protected-path task reaches green QA:

```
🛑 Protected-path approval needed — **<task-id> "<Title>"**
Touches: <protected path(s)>

QA is green, but this path is a hard lock — it will NOT auto-merge.
Review the worktree diff, then approve to merge, or I'll leave it ex:blocked.

Approve merge? (approve / leave blocked / inspect diff)
```

🔔 Fire a push notification via the `PushNotification` tool — the pipeline needs
the user. Do not merge a protected-path task without explicit approval, even on
green QA. Cloud mutations and migrations require the explicit approval mandated
by `.claude/rules/critical ai agent rule.md`.

---

## Step 6: Batched Manual Smoke Session (run the service) [main ctx]

Smoke is **manual by decision** (automated/e2e smoke is out of scope as a gate,
though an existing e2e suite may be used as an aid). Autonomous
tasks run to completion in parallel; smoke gates are **collected and presented
as one batched session** (walk-away batching) rather than interrupting per gate.

### Smoke-gate beads wiring (created in Step 3/4)

- A `smoke_test: required` task creates a dedicated **"Smoke gate: <task-id>"**
  beads issue.
- Downstream **substrate-overlapping** tasks are wired onto that gate via the
  `beads:dep` skill so they stay blocked until the smoke passes.

### Overlap detection (conservative hybrid)

- **Leaf-file overlaps** — cheap **path intersection** of write-sets.
- **Shared substrate** — any edit to your package's core modules (config,
  errors, shared interfaces), its service / API / data-access layers, or
  `migrations/` makes that gate **block the whole epic** (conservative: treat
  shared-substrate edits as affecting everything downstream).

### The batched session

When all autonomous work has run and one or more tasks are `ex:smoke-pending`:

🔔 Fire a push notification via the `PushNotification` tool (the pipeline needs
the user for the smoke session). Then, in main context:

1. **Start the project locally** with `<run-command>` — your project's normal
   start command. Confirm it came up (health endpoint / logs / first output).
2. Present **one batched checklist** — for each pending gate, tell the user
   exactly **what to verify** (from the plan's `smoke_steps`): exercise the
   route, command, or screen the task changed. Where a gate has e2e coverage you
   may run that suite as an aid, but the user's pass/fail is the gate.
3. **Wait for pass/fail** per gate.

```
🔥 Batched smoke session — epic **<epic-id>** (S gates)

Running via <run-command>. Verify each, then tell me pass/fail:

  [Smoke gate: A] <task-id> — <smoke_steps>
  [Smoke gate: B] <task-id> — <smoke_steps>
  ...

Reply e.g.: "A pass, B fail" (or "all pass").
```

### On pass

Close the smoke gate, **merge** the `ex:smoke-pending` worktree, mark the task
**`ex:done`**; gated dependents unblock.

### Smoke failure path

On **fail**:

- File a beads **bug** (via `beads:create`) describing the failure.
- Keep the **smoke gate open** — dependents stay blocked.
- **Reopen the task** for a fix pass (back to `ex:executing`).
- **No auto-rollback of the merge** — the **user decides rollback explicitly**.
  Do not revert merged work on your own.

---

## Step 7: Blocked-Bug Triage [main ctx]

When a task is set **`ex:blocked`** (a hard, not-easily-fixed QA finding, or an
unapproved protected-path task), the bug is filed (`beads:create`) and
highlighted. 🔔 Fire a push notification via the `PushNotification` tool so the
long run doesn't need babysitting. Present blocked bugs to the user with the
filed bead IDs; dependents of a blocked task stay blocked until it is resolved.

---

## Step 8: Epic Status & Next-Steps Summary [main ctx]

After the run completes — whether every task reached `ex:done`, some are
`ex:blocked`, or the epic wasn't fully approved and nothing ran (Step 0b) —
give the user a plain-language status report, not just the QA ledger. Pull
every task's `ex:*` / `wp:*` label via `beads:show` / `beads:list` and say:

- **Fully executed** — if every task in the resolved scope (Step 0a) is
  `ex:done`, say so and name the next command: `/workflow-ship-epic <epic-id>`.
- **Blocked bugs** — name every `ex:blocked` task and its filed bug id; these
  need a fix pass before shipping is possible.
- **Refused at Step 0b** — if the run refused to start because a non-deferred
  task was unapproved, restate which tasks are missing approval and point to
  `/workflow-writing-plans`.
- **Waiting on an earlier wave** — list every `wp:deferred` task excluded from
  this run (per Step 0b) and name what it's waiting on. This is expected
  behavior, not a failure — present it that way, and note that a fresh
  `/workflow-writing-plans` run will pick each one up once its upstream
  executes.
- **Cross-epic scope** — if this run operated on an `exec:<slug>` closure
  (Step 0a), say so and scope the "fully executed" check to that whole
  closure, not just the named epic.

State the single next command plainly — `/workflow-ship-epic <epic-id>` when
fully done, the fix/plan command otherwise — rather than a menu of every
possibility.

---

## Beads Label Lifecycle (execute-plans)

Per-task stage labels, advancing at the **end** of each step:

```
ex:executing
   → ex:qa:<level>         (level ∈ {quick, standard, full} — NEVER a bare ex:qa)
   → ex:smoke-pending      (only smoke-flagged tasks)
   → ex:done
   ( → ex:blocked          on a hard QA bug or unapproved protected-path task )
```

When read / what they do:

- **On start**, this command reads **`wp:approved`** (+ scope-level approval over the
  resolved closure) → **only runs approved tasks; refuses/warns on the rest** (Step
  0). It reads **`ex:*`** to **resume in-flight tasks** (Step 0c).
- **During the run**, it advances `ex:*`, **creates smoke-gate issues + deps**,
  and on a hard bug sets **`ex:blocked`** + files the bug.
- **`ex:qa:<level>` is the QA-depth audit record.** The level suffix encodes
  which `python-verification-{level}` **skill** actually ran (chosen from the
  task's real diff, Step 3 item 2). A task carrying a bare `ex:qa` — or `ex:done`
  with no `ex:qa:<level>` — means the verification skill was skipped; that is a
  workflow violation, not a pass. On resume, a task at `ex:qa:<level>` has its
  named verification already done; a task at `ex:executing` has not.

### QA ledger (required output)

Maintain a per-task QA ledger and print it in the final summary — it is the
proof that the warranted level ran for every task:

```
QA ledger
  <task-id> · diff +X/-Y · level=<quick|standard|full> · skill=<name> · result=<green|red>
  ...
  cumulative epic diff +X/-Y · full-sweep=<yes|n/a> · result=<green|red>
```

### Cumulative full-sweep backstop (before epic close)

Per-task levels can each be quick/standard yet still miss **cross-task
integration** defects (e.g. a schema authored in one task drifting from a
service contract authored in another — exactly the class of bug a per-task quick
pass cannot see). Therefore: **before closing the epic, if the cumulative epic
diff is 200+ lines OR touches new modules / shared substrate (your package's
core modules, service / API / data-access layers, `migrations/`), run ONE
`python-verification-full` over the aggregate changed set** — even when every
individual task was quick/standard. Record it on the ledger's cumulative line.

Use the `beads:label` / `beads:update` / `beads:create` / `beads:dep` skills to
read/advance labels and wire gates — never raw `bd` in Bash (per
`.claude/rules/0_Beads x Superpowers/skill-usage.md`). These labels are the
checkpoint + idempotency mechanism (Step 0): they make crashed runs resumable,
and there is intentionally **no separate status/resume command.**

---

## Notifications

Fire a **push notification** via the `PushNotification` tool whenever the
pipeline actually needs the user, so long runs don't require babysitting:

- the **batched manual smoke session** (Step 6),
- a **protected-path approval** stop (Step 5),
- a **blocked bug** (Step 7),
- an attended task that needs an unplanned decision (Step 4).

Do not notify for purely automated transitions (autonomous execute/QA/auto-merge).

---

## Out of Scope

- **Automated / e2e smoke as the gate** — smoke is **manual** by decision (Step
  6); an e2e suite is an *aid*, not the gate.
- **Visual / design-fidelity gate** — not included; add one if your project has a
  UI surface worth pixel-checking against a design source.
- **Risk-classifier v2** (reverse-dependency / import-graph overlap) — the
  conservative hybrid in Step 6 is the version to implement.
- **A separate status/resume command** — resumability is via the `ex:*` beads
  labels (Step 0c).

---

## CRITICAL — Honor Project Rules

- **Scope + approval precondition (Steps 0a–0b):** resolve the execution scope first
  — consume the `exec:<slug>` closure label when present; **refuse a bare cross-epic
  run that has no closure label** (run `/workflow-execution-sequence` first so the
  enablers aren't silently skipped). Then never execute a partial trickle among the
  **plannable** set: require `wp:approved` + `status: approved` on every non-deferred
  task in that scope; refuse the unapproved ones. **`wp:deferred` tasks are exempt**
  from this gate — they can't be planned until an earlier wave executes, and this
  command is what executes it.
- **Spikes run elsewhere:** `SPIKE-FIRST` tasks are executed by
  `/workflow-execute-spikes` (lightweight prototype + findings) and are closed before
  this command runs — never execute a spike through this command.
- **Hard locks (`.claude/rules/critical ai agent rule.md`):** protected-path
  tasks are **force-attended, never auto-merged** — stop for explicit human
  approval even on green QA (Step 5). Migrations, managed-cloud mutations,
  secrets/`.env`, production deploy config, history rewrites/force-push, and
  merge-to-trunk always stop for approval.
- **TDD first (Step 3):** drive every task via
  `superpowers:test-driven-development` — pytest tests before implementation,
  not post-hoc QA only.
- **Per-task QA level is mandatory and enforced (Step 3, items 2–3):** for
  EVERY task, compute the real diff, pick quick/standard/full from it, and run
  the **named `python-verification-{level}` skill in main context** after the
  code lands — even when a subagent implemented the task. **Ad-hoc
  `ruff`/`mypy`/`pytest`, a subagent's scoped tests, and an end-of-run full
  *test suite* do NOT count** — only the named skill does. Stamp `ex:qa:<level>`
  (never a bare `ex:qa`) and add the QA-ledger line. A task at `ex:done` without
  an `ex:qa:<level>` label is a violation, not a pass. This rule exists because
  lint+tests assert behavior, not values — a config/schema value can drift
  undetected without the structured review the skill performs.
- **Cumulative full-sweep before epic close:** if the epic's aggregate diff is
  200+ lines or touches your package's core modules / service / API /
  data-access layers / `migrations/`, run ONE `python-verification-full` over the whole
  changed set before closing the epic — it catches cross-task integration
  defects per-task passes miss.
- **Separate QA-fix commits (Step 3, item 5):** QA auto-fixes commit
  independently of the task implementation so they can be reverted on their own.
- **No auto-rollback (Step 6):** on smoke failure, file a bug + reopen + keep the
  gate open; the **user** decides rollback explicitly.
- **Worktree isolation:** parallel autonomous tasks each run in their own
  worktree (`opts.isolation: 'worktree'`) and merge only on green QA + passed
  gates.
- **Beads router** (`.claude/rules/0_Beads x Superpowers/beads-workflow-router.md`):
  scope all task listing to the chosen epic; use the `ex:*` stage labels.
- **Beads via skills:** use `beads:*` skills, never raw `bd` in Bash.
- **Budget gate first:** never start the Step 3 workflow before the Step 2
  confirmation.
- **Smoke launch:** start the project with `<run-command>`; smoke verifies the
  changed surface per each task's `smoke_steps`.
