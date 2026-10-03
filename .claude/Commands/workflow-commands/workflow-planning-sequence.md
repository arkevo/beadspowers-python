---
description: Compute a planning sequence from EITHER a design spec OR an existing beads epic — classifying each task by plan-readiness (plan-ready vs spike-first), dependency type (parallel / sequential-plan / execution-gated) and plan depth (full plan / lite plan / TDD-direct task card), then emitting a planning-sequence file (machine block + human table) and writing the dependencies/labels. Precursor to /workflow-commands:workflow-writing-plans, which consumes the emitted file.
---

# Workflow: Planning Sequence

Compute a **planning sequence** from EITHER a design spec OR an existing beads
epic: analyze the tasks, produce a **planning strategy** for each (plan-readiness
+ dependency type), then **emit a planning-sequence file** and write the
dependency edges + classification labels onto the epic.

This is the **decomposition + sequencing** step that runs **before**
`/workflow-commands:workflow-writing-plans`. It answers: *what are the tasks, which need a spike before
they can be planned, which can be planned in parallel, which must be planned
sequentially, and which must be planned AND executed before a downstream task can
even be planned.* The emitted planning-sequence file is the **contract**
`/workflow-commands:workflow-writing-plans` consumes.

This command obeys the beads workflow router
(`.claude/rules/0_Beads x Superpowers/beads-workflow-router.md`) and the plan-location
rule (`.claude/rules/Git Best Practices/protect_plans_and_commit_all.md` → plans live under `docs/plans/`). It uses
the **beads plugin skills** for all issue operations (per
`.claude/rules/0_Beads x Superpowers/skill-usage.md`), never ad-hoc `bd` CLI.

## Input — Spec OR Epic

`$ARGUMENTS` accepts two modes. **Prefer explicit flags:**

- `--spec <path>` → **spec mode**: decompose the spec into a *new* epic + tasks.
- `--epic <epic-id>` → **epic mode (non-destructive)**: classify the epic's
  *existing* tasks; never create, split, or merge tasks.

A **bare argument** falls back to a heuristic: a path that exists on disk → spec
mode; otherwise an argument that resolves as a beads epic → epic mode. **Fail
loud** with a clear message when a bare argument resolves as **neither** (no such
file and no such epic) **or both** (ambiguous) — never silently pick a branch.
Spec-mode default when no argument at all: most recent `docs/plans/*.md`.

---

## Core Principle — Plan-Strategy ≠ Build-Order

A naive epic is a flat, dependency-ordered list. That hides three things that
matter for *planning effort*:

1. **Some tasks cannot be planned yet** — their interface/feasibility/throughput is
   unknown, so a plan would be fiction. These need a **spike** (prototype) first.
2. **Dependencies come in two strengths.** A task may depend on an upstream task's
   *design decision* (available once the upstream is **planned**) or on its *actual
   behavior/interface* (available only once the upstream is **executed**). Conflating
   these serializes work that could pipeline, and pipelines work that must not.
3. **Tasks need different amounts of plan.** A one-file fix and a schema migration
   in the same epic should not attract the same authoring and refinement spend.

This command classifies every task on **three axes** — plan readiness, dependency
type and plan depth — and derives **planning waves** from the first two, so you
plan only what is plannable, spike unknowns before building on them, and spend
planning effort in proportion to each task's risk.

---

## The Three Classification Axes

### Axis 1 — Plan readiness

| Value | Meaning | Triggers (any one) |
|---|---|---|
| `PLAN-READY` | A faithful plan can be written now from the spec. | Algorithm/constants fully specified in spec; reuses a known library/pattern; interface is decidable on paper. |
| `SPIKE-FIRST` | Prototype first; a plan written now would be guesswork. | New external dependency whose feasibility is unproven; performance/throughput/latency unknown; platform/binding maturity unknown (beta SDK); the module's **output contract can't be specified** until prototyped; spec itself flags it "highest risk". |

### Axis 2 — Dependency type (for each edge)

| Value | Meaning | Use when |
|---|---|---|
| `PARALLEL` | No shared artifacts/decisions with other unplanned tasks. Plan anytime, any order. | Self-contained module; constants/algorithm in spec; isolated I/O. |
| `SEQ-PLAN` | Needs an upstream task's **design decision** (schema, interface contract defined in its plan) — but NOT its execution. | Depends on a data model, an API contract, or a shared type that the upstream **plan** pins down. Pipelines fine once upstream is *planned*. |
| `EXEC-GATED` | Needs the upstream task **executed/proven** (real interface, measured behavior, spike findings) before it can be planned at all. | Anything **downstream of a SPIKE**; integration/orchestration tasks that wire real modules; tasks whose plan references measured latency/throughput. |

> **Heuristic for EXEC-GATED:** "If I tried to write this task's plan today, would I be
> inventing the upstream's interface or numbers?" If yes → EXEC-GATED on that upstream.

### Axis 3 — Plan depth (the Sizing Gate)

**How much plan this task actually needs.** This is the batch mirror of the
single-task Sizing Gate (the router's *Sizing Gate — Claude picks the lane*
section in `.claude/rules/0_Beads x Superpowers/beads-workflow-router.md`); the
values map `PLAN-FULL` → Lane C, `PLAN-LITE` → Lane B and `TDD-DIRECT` → Lane A.
It exists so that a one-file bug in a 30-task epic does not attract the same
authoring and refinement spend as a schema migration.

| Value | Meaning | Assign when |
|---|---|---|
| `PLAN-FULL` | A full plan, then a refinement round. | **Any** of: it touches auth, security, payments, permissions or user data; a schema, a migration, or anything against production data or infrastructure; a client–server or service contract, a public API, or a new dependency; real alternatives the owner should choose between; more than about 3 files or 150 lines; the acceptance criteria are ambiguous or the description is thin. |
| `PLAN-LITE` | A short plan — goal, steps, files, tests, risks. **No refinement round.** | Multi-step or multi-file work whose approach is settled, with no alternatives worth debating. The plan is a record and a checklist, not a decision. |
| `TDD-DIRECT` | No plan. A minimal task card, executed test-first. | **All** of: the cause or shape is already known (you can point at the files and state the behaviour change); roughly 2–3 production files and about 50 lines; no schema or migration, public API or contract change, new dependency, or cloud/infra step; no real alternatives; existing tests cover the area, so a failing pytest test can be written first; reversible. |

> **Ties go to `PLAN-FULL`.** Under-planning a big task costs far more than
> over-planning a small one. `SPIKE-FIRST` (Axis 1) always overrides this axis —
> a spike gets its lightweight spike plan regardless of depth, and is never
> refined.

> **Depth is independent of the other two axes.** It changes only how much is
> written for a task, never *when* it is written: a `TDD-DIRECT` task with a
> `SEQ-PLAN` edge still waits for its upstream, and depth never moves a task
> between waves.

---

## Derived Outputs

From Axes 1 and 2, compute (plan depth changes none of these):

- **Planning tracks** — weakly-connected chains that can progress independently
  (e.g. a capture track, a data/algorithms track, an independent track).
- **Planning waves** — topological layers where every task in a wave is plannable given
  prior waves' *completed* state (a `SEQ-PLAN` parent must be **planned**; an
  `EXEC-GATED` parent must be **executed**).
- **Spike gates** — the explicit "plan + execute this before planning its dependents"
  checkpoints.

---

## Model & Budget

| Setting | Value |
|---------|-------|
| Agent model | **Opus** (`opts.model: "opus"` — a tier alias, never a pinned version) |
| Reasoning effort | **medium** for the classifier, synthesis and critic agents |
| Git | No code changes; this command reads the spec/epic, writes beads issues + labels/deps, and emits the planning-sequence file under `docs/plans/` |

---

## Steps

Each step is tagged **[workflow]** (detached, non-interactive) or **[main ctx]**
(needs the user). Never collect user input inside a Workflow.

### 1. [main ctx] Load input (spec mode or epic mode)
Resolve the mode (flags first, then the fail-loud heuristic above).

- **Spec mode:** read the spec at the resolved path (or newest `docs/plans/*.md`).
  Note its module inventory, build order, risks, open questions, and any
  **Source Reference Map**. Derive the **candidate task list** (one task per
  module/logical unit; let small pure modules ride along with their phase).
- **Epic mode:** load the epic's **existing** tasks via `beads:list` /
  `beads:show`. The candidate task list **is** those tasks, taken as-is — do not
  invent, split, or merge. Each candidate carries its real `bead_id`.

Everything downstream (classify → synthesize → present) is identical for both
modes; only task **creation** (Step 5) differs.

### 2. [workflow] Classify every candidate task
Fan out **one agent per candidate task** (`Workflow` tool, Opus, effort `medium`).
Each agent reads the spec (and the referenced source, if a Source Reference Map exists)
and returns the task's classification against `TASK_SCHEMA` below. Pass all tasks at once;
concurrency is capped at `min(16, cores−2)`.

`TASK_SCHEMA`:
```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "id_slug": {"type": "string"},
    "bead_id": {"type": "string"},
    "title": {"type": "string"},
    "plan_readiness": {"type": "string", "enum": ["PLAN-READY", "SPIKE-FIRST"]},
    "spike_reason": {"type": "string"},
    "plan_depth": {"type": "string", "enum": ["PLAN-FULL", "PLAN-LITE", "TDD-DIRECT"]},
    "depth_reason": {"type": "string"},
    "deps": {"type": "array", "items": {"type": "object", "additionalProperties": false,
      "properties": {
        "on": {"type": "string"},
        "type": {"type": "string", "enum": ["PARALLEL", "SEQ-PLAN", "EXEC-GATED"]},
        "why": {"type": "string"}
      }, "required": ["on", "type", "why"]}},
    "source_ref": {"type": "string"},
    "rationale": {"type": "string"}
  },
  "required": ["id_slug", "title", "plan_readiness", "plan_depth", "depth_reason", "deps", "rationale"]
}
```

`plan_depth` is **required**: a classifier that cannot justify a depth has not
understood the task, and a missing value must not silently become the cheapest
option. `depth_reason` is one sentence naming the specific Axis 3 trigger —
"touches the session schema", "two files, no contract change" — never a bare
restatement of the value.

### 3. [workflow] Synthesize tracks + waves (+ adversarial check)
One synthesis agent (Opus, `medium`) takes all task classifications and returns:
tracks, planning waves, spike gates, and a cycle/consistency check. Then **one critic
agent** (Opus, `medium`) adversarially reviews: *is any `PLAN-READY` actually a hidden
spike? Is any `SEQ-PLAN` really `EXEC-GATED` (would planning it invent the parent's
interface)? Any dependency cycle? Any task that could move earlier/parallel?* Apply
the critic's fixes.

The critic also attacks **plan depth in one direction only — upward.** For every
`TDD-DIRECT` and `PLAN-LITE` task it asks: *does it in fact touch auth, a schema, a
contract, a new dependency, or production data? Are there alternatives the owner
should be choosing between? Is the file/line estimate believable, or is it the
optimism of someone who has not opened the files?* Anything that survives with
doubt is **promoted**, never demoted. The critic must not downgrade a `PLAN-FULL`
to save effort — that trade is the owner's to make at the Step 4 gate, where they
can see it.

`EPIC_SCHEMA`:
```json
{
  "type": "object", "additionalProperties": false,
  "properties": {
    "tracks": {"type": "array", "items": {"type": "object", "additionalProperties": false,
      "properties": {"name": {"type": "string"}, "tasks": {"type": "array", "items": {"type": "string"}}},
      "required": ["name", "tasks"]}},
    "waves": {"type": "array", "items": {"type": "object", "additionalProperties": false,
      "properties": {"wave": {"type": "number"}, "tasks": {"type": "array", "items": {"type": "string"}},
        "gate": {"type": "string"}}, "required": ["wave", "tasks"]}},
    "spike_gates": {"type": "array", "items": {"type": "string"}},
    "notes": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["tracks", "waves", "spike_gates"]
}
```

### 4. [main ctx] Present recommendation + review gate
Print, in console:
- The **task table** (title · plan-readiness · **plan depth** · dependency type ·
  depends-on · source ref).
- A one-line **depth summary** — "n full · n lite · n TDD-direct" — plus the
  `depth_reason` for every `TDD-DIRECT` task, spelled out. Those are the ones the
  owner is most likely to want promoted, so they must not be buried in a table
  cell.
- The **tracks** and the **planning-wave order**, with spike gates called out as
  "🔬 plan + execute before its dependents are planned".
- Any **notes / open questions** the classification surfaced.

Ask the user to approve, adjust task granularity, **re-assign plan depth**, or
re-classify specific tasks. Iterate until approved. **Do not create beads issues
before approval.** Depth is a recommendation until this gate passes — the owner
raises or lowers any task here, and their call stands over the classifier's.

### 5. [main ctx] Persist to beads (mode-dependent, beads plugin skills)
On approval:

- **Spec mode — create epic + tasks:**
  - `beads:create` the **epic** (title from spec, description = spec path + one-line goal).
  - `beads:create` each **task** under the epic; capture the assigned `bead_id`.
- **Epic mode — non-destructive:** the epic and tasks already exist. **Do not
  create, split, or merge anything.** Operate on the existing `bead_id`s.

Then, **in both modes**, write the classification onto the tasks:
- Encode classification as **labels**: `plan-ready` | `spike-first`,
  `depth:full` | `depth:lite` | `depth:tdd`, and `track:<name>`, `wave:<n>`. For
  `SPIKE-FIRST` tasks in spec mode, prefix the title `SPIKE: …`; in epic mode,
  add a `spike-first` label without retitling. A task carries exactly one
  `depth:*` label: when a re-run re-classifies it, remove the old one and add
  the new — unlike the `wp:*` and `ex:*` ladders, depth is a current
  classification, not history.
- Record `depth_reason` in the task's notes alongside the edge types, so the
  reason survives into `bd show` and a later reader can challenge the call
  without re-deriving it.
- Add dependencies with `beads:dep`: a `SEQ-PLAN` or `EXEC-GATED` edge → the
  dependent task `depends-on` the parent. Record the **edge type** in the
  dependent task's notes (`EXEC-GATED on <id>` / `SEQ-PLAN on <id>`) so
  `/workflow-commands:workflow-writing-plans` knows a spike must be **executed**, not merely
  planned, before it plans the dependent.
- Echo the epic id + task ids + the wave order.

### 6. [main ctx] Emit the planning-sequence file (both modes)
Write `docs/plans/<epic-slug>/<date>-<epic-slug>-planning-sequence.md` with **two
synchronized representations, in one step:**

1. **Machine-readable block** (frontmatter YAML or a fenced ```json) — the
   authoritative contract `/workflow-commands:workflow-writing-plans` parses. It
   carries `epic` (the epic id) plus a `tasks` array of `TASK_SCHEMA` objects
   **extended with** the real `bead_id`, `track`, and computed `wave` (`wave:n`) —
   `track` and `wave` augment the base TASK_SCHEMA fields. This is the single
   authoritative planning toposort — writing-plans consumes `wave:n` and never
   recomputes it. It also carries `plan_depth` + `depth_reason` per task;
   `/workflow-commands:workflow-writing-plans` **reads** the depth and never
   re-derives it, so the owner's Step 4 adjustments are what actually take
   effect.
2. **Human-readable body** — the classification-axes legend (all three), the
   task table (title · plan-readiness · plan depth · dependency type ·
   depends-on · source ref), the depth summary line, the tracks, the wave order
   with spike gates called out, and a "what changed" note. Mirror the layout of
   `docs/plans/.../*-planning-sequence.md` examples.

Both halves are written together so they cannot drift.

### 7. [main ctx] Handoff — Epic Status & Next-Steps Summary
Don't just print the wave table — walk the user through it in plain language,
the way you'd explain it out loud: what's plannable right now, what's blocked
and why, and the exact next command. Cover:

- **Wave 1 is always plannable now** — name which tasks are in it (the
  `PLAN-READY` + `PARALLEL`/already-satisfied ones).
- **Spike gates** — name every `SPIKE-FIRST` task and what it roots. Its
  `EXEC-GATED` dependents are **not** planned until the spike is planned AND
  **executed** (via `/workflow-commands:workflow-execute-spikes`, later in the pipeline) — this
  is expected pipeline behavior, not an error state.
- **Cross-epic dependencies (epic mode only)** — if any task's `blocks`-predecessor
  lives outside this epic, say so plainly; resolving that is
  `/workflow-commands:workflow-execution-sequence`'s job, not something this command does.

State the single next command plainly:

```
/workflow-commands:workflow-writing-plans <epic-id-or-sequence-file-path>
```

and remind the user this first run only drafts the plannable wave(s) — later
waves reappear automatically on a future `workflow-commands:workflow-writing-plans` re-run once
their upstream spikes/tasks are executed.

---

## Guardrails

- **Never plan inside this command** — it only decomposes, classifies, persists,
  and emits the sequence file. Planning is `/workflow-commands:workflow-writing-plans`.
- **Epic mode is non-destructive** — classify and label existing tasks only;
  never create, split, or merge them. Task granularity changes are the user's
  call, made before running this command in epic mode.
- **Always emit the planning-sequence file** (Step 6) in both modes — it is the
  contract `/workflow-commands:workflow-writing-plans` consumes, with the authoritative `wave:n`.
- **Spikes are first-class tasks**, not informal asides — they get a beads task, a
  lightweight plan, and an execution before their dependents are planned.
- **Prefer fewer, well-bounded tasks** (spec mode). Fold trivial pure modules into
  their phase; give standalone tasks only to modules with their own interface and risk.
- **One open meeting / one epic in progress** — respect the router's epic-scoping rule.
