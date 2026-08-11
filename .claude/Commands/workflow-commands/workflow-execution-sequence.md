---
description: Given a beads epic, compute its transitive blocks-dependency closure (cross-epic), topologically sort it into execution waves with per-task predecessors, flag every task missing an approved plan, drive /workflow-writing-plans per owning epic for the gaps, and label the closure (exec:<slug>) when it spans epics so /workflow-execute-plans executes the enablers too. The execution-order analog of /workflow-planning-sequence; the precursor that makes an epic safe to hand to /workflow-execute-plans.
---

# Workflow: Execution Sequence for an Epic

Given a beads epic, answer the question `/workflow-execute-plans` cannot answer on
its own: **"in what order, across which epics, and with which plans, do I actually
ship this?"** This command computes the epic's full **execution dependency closure**
(following `blocks` edges, which routinely cross epic boundaries), topologically
sorts it into **execution waves**, reports which tasks have **no approved plan
yet**, and — on approval — runs `/workflow-writing-plans` for each owning epic so
the closure becomes execution-ready.

This is the **execution-order** sibling of `/workflow-planning-sequence` (which
decomposes a *spec* into an epic + *planning* waves). This command starts from an
**existing epic** and produces *execution* waves + a plan-coverage gate.

This command obeys the beads workflow router
(`.claude/rules/0_Beads x Superpowers/beads-workflow-router.md`), saves its artifact
under `docs/plans/` (`.claude/rules/Git Best Practices/protect_plans_and_commit_all.md`), and uses the **beads plugin
skills** for all issue reads (`.claude/rules/0_Beads x Superpowers/skill-usage.md`) — never ad-hoc `bd`
CLI for mutations.

**Input:** `$ARGUMENTS` = `<epic-id>` (e.g. `<epic-id>`). No arg → pick from
in-progress / recent epics (Step 1).

---

## Core Principle — Execution Closure ≠ Epic Membership

An epic's task list is **not** its execution scope. A `blocks` edge can point at a
task in a **different epic** (e.g. a UI epic's screens depend on Repository/ViewModel
tasks owned by data-layer epics). Executing the epic alone silently skips those
enablers and the dependents fail at runtime.

So this command operates on the **transitive `blocks`-closure** of the epic's
tasks — every task that must be done first, wherever it lives — and orders *that*.
Two derived facts matter:

1. **Execution waves** — topological layers; every task in wave *N* has all its
   `blocks`-predecessors in waves `< N`. Wave 1 = tasks with zero open blockers.
2. **Plan coverage** — `/workflow-execute-plans` requires `wp:approved` +
   plan `status: approved` per task. Any closure task lacking that is a **gap** that
   must be planned (via `/workflow-writing-plans`) before execution.

---

## Model & Budget

| Setting | Value |
|---------|-------|
| This command's own work | Cheap: read-only graph analysis (one `bd export` + a local topo-sort). No agents. |
| The planning it triggers | `/workflow-writing-plans` per gap-epic — **Opus / xhigh**, ~one agent per task. Gated (Step 5). |
| Git | No code changes; writes one analysis doc under `docs/plans/` and (via the planning sub-command) plan files. |

---

## Steps

Each step is tagged **[main ctx]** (needs the user / orchestrates) or **[script]**
(deterministic local computation — no subagents).

### 1. [main ctx] Resolve the epic
- **Explicit `<epic-id>` arg** → use it.
- **No arg** → show in-progress epics (`beads:list --status=in_progress --type=epic`),
  else the last 10 created epics, and ask the user to pick. Never infer-and-run.

Derive `<epic-slug>` (lowercase kebab from the title) for the artifact path.

### 2. [script] Compute the transitive blocks-closure
Refresh the graph (`bd export --no-auto-import` writes `.beads/issues.jsonl`), then
traverse `dependencies[]` where `type == "blocks"` (ignore `parent-child`), starting
from the epic's children, collecting every reachable task — **including cross-epic
ones**. Exclude `closed` tasks (their edges are already satisfied).

```python
import json, collections
EPIC = "$ARGUMENTS"                      # e.g. <epic-id>
issues = {}
for line in open(".beads/issues.jsonl"):
    line = line.strip()
    if not line: continue
    try: o = json.loads(line)
    except: continue
    iid = o.get("id")
    if not iid: continue
    issues[iid] = {
        "status": o.get("status"),
        "title": (o.get("title") or "").strip(),
        "type": o.get("issue_type"),
        "deps": [d["depends_on_id"] for d in o.get("dependencies", []) if d.get("type") == "blocks"],
    }
children = [i for i in issues if i.startswith(EPIC + ".") and issues[i]["status"] != "closed"]
# transitive closure over open tasks
S, stack = set(children), list(children)
while stack:
    cur = stack.pop()
    for dep in issues.get(cur, {}).get("deps", []):
        if issues.get(dep, {}).get("status") == "closed": continue   # satisfied edge
        if dep not in S:
            S.add(dep); stack.append(dep)
pred = {i: sorted(d for d in issues[i]["deps"] if d in S) for i in S}
```

### 3. [script] Topologically sort into waves + detect cycles
Cycle-check first (`bd dep cycles` — must be clean), then longest-path layering:

```python
level = {}
def lvl(i):
    if i in level: return level[i]
    ps = pred[i]
    level[i] = 0 if not ps else 1 + max(lvl(p) for p in ps)
    return level[i]
for i in S: lvl(i)
waves = collections.defaultdict(list)
for i in S: waves[level[i]].append(i)
```
A non-empty `bd dep cycles` result is a **hard stop** — report the cycle; do not
emit a partial order.

### 4. [main ctx] Plan-coverage check
For every task in `S`, it **has a plan** iff BOTH:
- the task carries the **`wp:approved`** label (`beads:label list <id>`), and
- a file `docs/plans/<owning-epic-slug>/<task-id>-*.md` exists with frontmatter
  `status: approved`.

Otherwise it is a **gap**. Group gaps by **owning epic** (the prefix before the
last `.`, mapped to its epic id). This grouping is what drives Step 6.

> **"Gap" = missing the execute-gate, NOT missing design coverage.** Most tasks
> already reference a design spec in their description (epic spec, per-model plan,
> design doc). That is *input* to planning, not the `wp:approved` gate.
> `/workflow-execute-plans` refuses to run without `wp:approved`, so even a
> well-specified task must pass through `/workflow-writing-plans` once — but that
> command's Step 3 **skip-gate** stamps a sufficiently-detailed description
> `wp:skipped` (the description *becomes* the plan) instead of re-writing it.
> Classify each gap so the Step 5 cost preview is honest:
> - **`needs-ratify`** — description already references a rich spec / has the
>   structural floor → likely skip-validated (cheap).
> - **`needs-plan`** — thin/one-line description → a real plan gets written from its
>   referenced source (the real cost).

### 5. [main ctx] Present sequence + coverage + GATE
Print:
- the **execution-wave table** (`wave · id · type · title · after: predecessors`),
- the **closure summary** (`N tasks across K epics; cycles: none`),
- the **plan-coverage report** — gaps grouped by owning epic, with counts.

Then **save the analysis** to `docs/plans/<date>-<epic-slug>-execution-sequence.md`.

Because the next step launches **expensive Opus-4.8/xhigh planning workflows**,
show a budget/scope preview and require explicit confirmation (mirror
`/workflow-writing-plans` Step 2):

```
📋 Execution sequence for **<epic-id> "<Title>"**
Closure: N tasks across K epics · M waves · no cycles
Plan gaps: G tasks in E epics  →  will run /workflow-writing-plans on: <epic-a>, <epic-b>, …
Est. planning cost: ~X–Y% of the 5-hr usage limit (≈ one agent per gap task)
Proceed with planning? (yes / pick a subset of epics / sequence only — skip planning / cancel)
```

If the user chooses **sequence only**, stop here — the doc is the deliverable.

### 6. [main ctx] Drive planning for the gap-epics
On approval, for **each owning epic with gaps** (in execution-wave order so
upstream enablers are planned first), invoke:

```
/workflow-writing-plans <epic-id>
```

`/workflow-writing-plans` is now **sequence-file-driven**: passing `<epic-id>`
resolves that epic's planning-sequence file under `docs/plans/<epic-slug>/`. If
no sequence file exists yet, first generate one non-destructively with
`/workflow-planning-sequence --epic <epic-id>` (epic mode classifies the existing
tasks and emits the file), then run `/workflow-writing-plans <epic-id>`.

Run them **one epic at a time**, honoring that command's own preview/budget gate
and its `wp:*` resume labels (already-approved tasks are skipped, so re-runs are
incremental). Do **not** plan inside this command — always delegate to
`/workflow-writing-plans` (never hand-roll plan prose).

> Note on naming: this command computes **execution** waves; `/workflow-planning-sequence`
> computes **planning** waves and emits the sequence file `/workflow-writing-plans`
> consumes. In **epic mode** (`--epic <id>`) `/workflow-planning-sequence` applies to
> *existing* epic tasks; in spec mode it decomposes a *spec* into a new epic.

### 7. [main ctx] Label the closure (if cross-epic) + Epic Status & Next-Steps Summary
Once every closure task is `wp:approved`:

- **If the closure spans more than one epic**, apply the shared label
  **`exec:<epic-slug>`** to **every task in the closure** (via the `beads:label`
  skill). This is the durable, inspectable scope `/workflow-execute-plans` consumes
  (its Step 0a). It is **required, not optional**: without it a bare
  `/workflow-execute-plans <epic-id>` builds only the named epic's children and
  **silently skips the cross-epic enablers** — and `/workflow-execute-plans` now
  **refuses** a bare cross-epic run that has no `exec:<slug>` label.
- **If the closure is self-contained** (closure == the epic's own children), no label
  is needed — the bare epic-id is an unambiguous scope.

Then give the user a plain-language status report, not just the wave table:
state whether the closure is self-contained or spans multiple epics (and, if
so, which ones), whether every closure task actually reached full approval
this run or some are still gaps, and flag any `spike-first` task in the
closure that still needs `/workflow-execute-spikes` before it counts as
executed. Restate the **execution-wave order**, then hand off with the single
next command:

```
/workflow-execute-plans <epic-id>
```

---

## Artifact — `docs/plans/<date>-<epic-slug>-execution-sequence.md`

| Section | Contents |
|---|---|
| Closure | task count, epics spanned, cycle status |
| Execution waves | the topological order with per-task predecessors |
| Plan coverage | gaps grouped by owning epic |
| How to run | the plan-then-execute handoff |

Permanent under `docs/plans/` (Git Best Practices/protect_plans_and_commit_all.md).

---

## Guardrails

- **Closure, not epic.** Always order the transitive `blocks`-closure; never assume an
  epic is self-contained. Call out cross-epic enablers explicitly.
- **Cycles are a hard stop.** `bd dep cycles` must be clean before emitting an order.
- **Label cross-epic closures.** When the closure spans epics, apply `exec:<slug>` to
  the whole closure (Step 7) so `/workflow-execute-plans` executes the enablers, not
  just the named epic. A bare cross-epic hand-off is a silent-skip bug, and the
  executor refuses it without the label.
- **Exclude closed tasks** from the closure (their edges are satisfied) but report them
  if the user asks "why is this already unblocked?".
- **Budget gate before planning.** Never launch `/workflow-writing-plans` runs before
  the Step 5 confirmation — they are the expensive part.
- **Don't plan here.** Decompose + sequence + detect gaps only; delegate planning to
  `/workflow-writing-plans` and execution to `/workflow-execute-plans`.
- **Beads via skills**, plans under `docs/plans/`, user always picks the epic.
