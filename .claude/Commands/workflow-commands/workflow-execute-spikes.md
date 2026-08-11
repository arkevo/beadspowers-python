---
description: Execute the approved SPIKE-FIRST tasks of a beads epic — run each lightweight prototype (exercising it against a running instance or headless as the unknown requires), record its findings + evidence to docs/plans/<epic-slug>/<spike-id>-findings.md, and close the spike task (the unblock signal for EXEC-GATED dependents). The lightweight bridge between /workflow-writing-plans and /workflow-execute-plans. NOT a clone of execute-plans — no epic-wide approval gate, no python-verification levels, no smoke gate, no merge.
---

# Workflow: Execute Spikes for an Epic (Python)

Run the **approved `SPIKE-FIRST` tasks** of a beads epic, prototype-only: resolve
each spike's unknown — **exercising the prototype against a running instance when
that's the only way to learn** — **record findings + evidence** to
`docs/plans/<epic-slug>/<spike-id>-findings.md`, and **close the spike task** —
which is the unblock signal that lets `EXEC-GATED` dependents rejoin
`/workflow-writing-plans` on its next run.

This is the **bridge** the pipeline depends on:
`/workflow-planning-sequence` → `/workflow-writing-plans` (spikes get a lightweight
plan; `EXEC-GATED` dependents are deferred) → **this command** (execute the spikes,
record findings) → `/workflow-writing-plans` re-run (now-unblocked dependents plan
against the findings) → `/workflow-execution-sequence` → `/workflow-execute-plans`.

This command obeys the beads workflow router
(`.claude/rules/0_Beads x Superpowers/beads-workflow-router.md`), the hard-lock rules
(`.claude/rules/critical ai agent rule.md`), and the plan-location rule
(`.claude/rules/Git Best Practices/protect_plans_and_commit_all.md` → findings live
under `docs/plans/`). It uses the **beads plugin skills** for all issue operations
(`.claude/rules/0_Beads x Superpowers/skill-usage.md`), never ad-hoc `bd` CLI.

> **Why this is a separate command (not `/workflow-execute-plans --spikes`).**
> `/workflow-execute-plans` has a **hard epic-level approval gate** — it refuses
> unless *every* task in the epic is `wp:approved`. At spike time the `EXEC-GATED`
> dependents are deliberately `wp:deferred`, so the epic is never fully approved and
> that command would refuse to run the spikes. It is also the wrong weight: a spike
> is a **throwaway prototype** whose only durable deliverable is a measured contract
> (the findings file). This command is deliberately lightweight and gates only on the
> **selected spikes**, not the whole epic.

---

## Core Principle — Throwaway Code, Durable Findings (Run to Learn)

A spike exists to **answer an unknown** (a real library/module interface, a measured
latency or throughput budget, the quality of some non-deterministic output, a
feasibility yes/no), not to ship code. So:

- **The prototype code is disposable.** It runs in a throwaway worktree and is
  **never merged** to the epic branch.
- **The findings file is the deliverable.** It captures the measured contract the
  now-unblocked `EXEC-GATED` plan will read. Permanent under `docs/plans/`.
- **Run to learn.** Many unknowns can *only* be resolved by **exercising the prototype
  against a running instance** (real latency, real output shape). This
  command runs it and records what it observed — but this is an **observation, NOT the
  formal smoke *gate***: nothing merges, there is no `python-verification` level
  (those belong to `/workflow-execute-plans`).
- **Closing the spike task is the unblock signal.** Do not close a spike until its
  findings are recorded.

---

## Input

`$ARGUMENTS` = `<epic-id>` — or a planning-sequence file path.
Optional `--tasks <id,id>` for an explicit subset. **No arg** → show in-progress epics
and ask; never infer-and-run. Derive `<epic-slug>` for the findings path.

---

## Probe Modes (how a spike is exercised)

Each spike declares — in its plan frontmatter, **or inferred here from its unknown**
when absent — **how** it must be exercised to produce findings:

| `spike_probe` | What runs | Use when the unknown is… |
|---|---|---|
| `headless` | a throwaway `pytest` harness / a direct call into the target module | a pure logic / module-interface / data-shape question (no running instance needed) |
| `running` | start the project with `<run-command>`, then drive it the way a real caller would | real request/response shape, end-to-end latency, integration behavior |
| `none` | library/API docs / static analysis only | answerable on paper |

Optional spike-plan frontmatter (read if present, else inferred):

```yaml
spike_probe: headless | running | none
probe_steps: "what to run + exactly what to observe/measure"
needs_human_verdict: true | false   # true → exercised ATTENDED (Step 4), a person judges
```

`needs_human_verdict: true` marks unknowns a machine can't judge — output *quality*,
subjective correctness, "does this feel right" — exercised **attended** in main context
(a detached Workflow can't get a human verdict).

> **Cost & data safety (always):** stub or mock any **paid/metered external API** unless
> the spike's unknown is specifically about that API's real behavior — then flag the cost
> in the Step 2 preview and get approval first. Probes run against a **test/scratch
> database**, never a dev or production one, and **MUST clean up all test data** they
> create before the spike closes.

---

## Model & Budget

| Setting | Value |
|---------|-------|
| Agent model | **Opus** (`opts.model: "opus"` — a tier alias, never a pinned version) |
| Reasoning effort | **high** (unknown-resolution is reasoning-heavy) |
| Git model | **Throwaway worktree per spike** (`opts.isolation: 'worktree'`); prototype **discarded**, never merged. Only the findings file + evidence land on the epic branch. |
| Budget shown as | **% of the 5-hr Opus high usage limit** |

Auto-observe spikes fan out one agent each (concurrency `min(16, cores − 2)`);
human-verdict spikes run serialized in main context.

---

## Step Map — Segmentation at a Glance

Labels advance at the **END** of each step.

| # | Step | Where | End label |
|---|------|-------|-----------|
| 0 | Resume check (idempotency) | main ctx | — |
| 1 | Select + gate + route (auto-observe vs human-verdict) | main ctx | — |
| 2 | Preview / budget gate | main ctx | — |
| 3 | Auto-observe fan-out (throwaway worktrees) — exercise per probe mode, capture evidence | **workflow** | `sk:running` |
| 4 | Attended observation (human-verdict spikes) | **main ctx** | `sk:running` |
| 5 | Record findings (+ evidence) + clean up test data | main ctx | `sk:findings-recorded` |
| 6 | Close spikes (unblock signal) | main ctx | `sk:done` |
| 7 | Epic status & next-steps summary | main ctx | — |

---

## Step 0: Resume Check (idempotency) [main ctx]

Read each spike's `sk:*` label and resume from the furthest stage: `sk:done` → skip;
`sk:findings-recorded` → skip to Step 6 (close); `sk:running` → continue at Step 5.
The `sk:*` labels are the resume mechanism — no separate status command.

## Step 1: Select + Gate + Route [main ctx]

Select the epic's **`spike-first`** + **`wp:approved`** + still-**open** tasks (layered
spikes run in wave order, or run the ready ones and re-run). **Gate only on the
selected spikes** — never require the rest of the epic approved.

Then **resolve each spike's probe mode** (read `spike_probe` frontmatter; if absent,
infer from the spike's unknown using the Probe Modes table) and **route**:
- **`needs_human_verdict: true`** → **attended** (Step 4, serialized, main ctx).
- otherwise → **auto-observe** (Step 3, parallel workflow pool).

If no ready spikes exist, say so and stop.

## Step 2: Preview / Budget Gate [main ctx]

```
🔬 Spike workflow for epic **<epic-id> "<Title>"**

Ready spikes:  S   (auto-observe: A · human-verdict/attended: H)
  by probe: headless×… · running×… · none×…
Probes hitting a paid external API (incurs cost): …  (else stubbed)
Deferred (later layer / blocked): D
Resuming: R from prior sk:* stages · skipping J already sk:done

Agents: ≈A (one per auto-observe spike, throwaway worktree; cap min(16, cores−2))
Est. cost: ~X–Y% of the 5-hr limit
Deliverable: docs/plans/<epic-slug>/<spike-id>-findings.md (+ evidence) per spike; code discarded

Proceed? (yes / adjust scope / cancel)
```

Do not start the Step 3 workflow until the user confirms.

## Step 3: Auto-Observe Fan-Out (throwaway worktrees) [workflow]

Fan out the auto-observe spikes as a `parallel(...)` pool, **each in its own throwaway
worktree** (`opts.isolation: 'worktree'`). Per spike, the agent:

1. Reads the spike plan — its **goal**, the **unknown**, the **prototype steps**, the
   **contract to produce**, and `probe_steps`.
2. Builds the **minimum prototype** (exploratory, not production-quality — **no TDD
   requirement, no `python-verification` level, no merge**).
3. **Exercises it per its probe mode:**
   - `headless` → a throwaway `pytest` harness or a direct call into the target module,
     external APIs stubbed; capture the interface shape + output values.
   - `running` → start the project with `<run-command>` against a **test/scratch
     database** with external APIs stubbed, then drive the changed surface the way a real
     caller would; **measure whatever budget the spike is about** (latency, throughput,
     memory) and capture the raw output; stop it after.
   - `none` → library/API docs / static analysis.
4. **Captures evidence** into `docs/plans/<epic-slug>/<spike-id>-findings/` (response
   JSON, latency numbers, log excerpts) and returns structured findings: the measured
   contract, the numbers, the feasibility verdict, and gotchas the downstream plan must
   honor.

The worktree (and prototype code) is **discarded** when the agent returns.

**End-of-step label:** `sk:running`.

> Protected paths still apply: a spike must **not** mutate `migrations/`, managed-cloud
> resources, secrets/`.env`, or production deploy config (`critical ai agent rule.md`).
> Probes use a test/scratch database + stubbed external APIs, never dev or production. A
> spike that genuinely needs a protected resource is **human-verdict/attended** — ask
> first.

## Step 4: Attended Observation (human-verdict spikes) [main ctx]

For spikes a machine can't judge (`needs_human_verdict: true` — chiefly **output
quality/relevance**), exercise **attended** — 🔔 fire a `PushNotification`, then in main
context:

1. Start the project with `<run-command>` (external APIs stubbed unless the unknown is
   about them; test/scratch database) and drive the prototype per `probe_steps`.
2. Present **exactly what to judge** (from `probe_steps`): "is this output correct and
   relevant?", "does this behave right for this input?".
3. **Capture the user's verdict + observations** (and the raw output) into the findings
   evidence dir.

This is a **feasibility observation, not a merge gate** — nothing merges; you're
recording what was judged so the downstream plan can rely on it.

## Step 5: Record Findings (+ evidence) + Clean Up Test Data [main ctx]

Write `docs/plans/<epic-slug>/<spike-id>-findings.md`:

```yaml
---
spike: <spike-id>
epic: <epic-id>
probe: headless | running | none
status: complete
---
```

Body: the **measured contract** (module/endpoint signatures, request/response shape),
**numbers** (measured latency/throughput, sizes, costs), the **feasibility
verdict**, **constraints for the dependent plan**, and an **evidence** list linking the
captured artifacts under `<spike-id>-findings/`. Be concrete — this is what the
now-unblocked `EXEC-GATED` plan reads. Permanent under `docs/plans/`.

**Then clean up all test data** any `running`/attended probe created: delete the rows
it wrote and **verify the counts are 0** before closing the spike. A spike that created
test data may **not** reach `sk:done` with artifacts left in the database.

**End-of-step label:** `sk:findings-recorded`.

## Step 6: Close the Spike (unblock signal) [main ctx]

**Only after findings are recorded and test data is cleaned**, `beads:close` each spike
with a reason referencing the findings file. Closing is the **unblock signal**. **Never
close a spike without recorded findings.**

**End-of-step label:** `sk:done`.

## Step 7: Epic Status & Next-Steps Summary [main ctx]

Don't just report which spikes closed — give the user a plain-language read on
the **whole epic's** state now that this run's findings exist (and its test
data is cleaned up). Pull every task's current stage (`wp:*` / `sk:*`) via
`beads:show` / `beads:list` and say:

- **Which `EXEC-GATED` tasks just unblocked** — every task whose upstream spike
  is now `sk:done`, and what it needs next (a `/workflow-writing-plans` re-run
  to actually draft it — `EXEC-GATED` tasks are never planned until this
  moment).
- **Whether there's a next layer of spikes** — if some spikes are themselves
  gated on the ones that just closed, say so and note that this command
  should be re-run once they become plan-ready.
- **Anything still genuinely blocked** — tasks whose upstream is a spike that
  hasn't run yet, or a task waiting on execution further downstream. Say so
  plainly; it's expected pipeline behavior, not an error.

State the single next command plainly:

```
/workflow-writing-plans <epic-id>
```

and mention re-running this command instead if a further spike layer is next.

---

## Beads Label Lifecycle (execute-spikes)

```
sk:running              (prototype exercised — auto-observe or attended)
   → sk:findings-recorded  (docs/plans/<epic-slug>/<spike-id>-findings.md + evidence written; test data cleaned)
   → sk:done               (spike task closed — unblock signal emitted)
```

Use `beads:label` / `beads:close` / `beads:show` / `beads:list` skills — never raw `bd`.

---

## Out of Scope

- **The formal smoke *gate*** (human pass/fail before merge), **`python-verification`
  levels**, **merge**, and the **cumulative full-sweep** — all belong to
  `/workflow-execute-plans`. Here you *exercise to learn*, not *verify to ship*.
- **The epic-wide approval gate** — gated only on the selected spikes.
- **A separate status/resume command** — resumability is via the `sk:*` labels.

---

## CRITICAL — Honor Project Rules

- **Findings before close (Step 6):** never close a spike without recorded `findings.md`.
- **Test-data cleanup is mandatory (Step 5):** any `running`/attended probe MUST delete
  all test data it created and verify counts are 0 before the spike closes.
- **Run to learn, not to ship (Steps 3–4):** exercise a running instance when the
  unknown needs it and capture evidence — but it is **not** a merge gate; no
  `python-verification`, no merge.
- **Human-verdict spikes are attended (Step 4):** machine-unjudgeable unknowns (output
  quality/relevance) run in main context with a person's verdict captured into findings.
- **Cost (always):** stub paid/metered external APIs unless the unknown is specifically
  about their real behavior — then flag the cost in the Step 2 preview and get approval.
- **Throwaway code (Step 3):** prototype in an isolated worktree; never merge it.
- **Spike-only gate (Step 1):** require `spike-first` + `wp:approved` on the selected
  tasks only.
- **Protected paths (`critical ai agent rule.md`):** never touch `migrations/`,
  managed-cloud resources, secrets/`.env`, or production deploy config; probes use a
  test/scratch database, never dev or production.
- **Beads via skills; plans/findings permanent under `docs/plans/`; budget gate first.**

---

> The bridge logic here is portable: throwaway prototype → recorded findings → close the
> spike as the unblock signal. Only the **probe mechanics** are project-specific — if your
> project has a UI, a device target, or a simulator, add probe modes for them and leave the
> rest as written.
