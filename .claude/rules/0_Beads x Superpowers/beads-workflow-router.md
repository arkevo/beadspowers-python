# Beads Workflow Router

**Section:** Task Management
**Applies to:** a single Python repo tracked with Beads

## Repo Context (read first)

This router is the authority document for the whole task workflow. It assumes:

- **One repo, one local Beads store.** Beads operations run against the local
  store under `.beads/` via the `beads:*` plugin skills. There is **no multi-repo
  read hub** and no `bd repo sync` step.
- **Beads syncs however your project syncs it.** The default is `issues.jsonl`
  committed with your code. If you have set up a Dolt remote instead, sync at
  session/task start and again at ship/close, and treat code and beads as **two
  separate channels** — `git push` ships code, the beads sync ships beads. Never
  `--force` a beads push except a deliberate, agreed re-baseline.
- **Beads is the only tracker.** Never use TodoWrite / TaskCreate / markdown task
  files. If you mirror to an external tracker (Jira, Linear), that mirror is
  **downstream** — you still create and close work only in Beads.
- **Never commit or push directly to the trunk** (`master` / `main`) — see
  `.claude/rules/Git Best Practices/no-direct-push-to-master.md`. Always work on
  a feature branch; **shipping goes through a PR**. Branch prefixes (see
  `Git Best Practices/Git Best Practices.md`): `feat/`, `fix/`, `refactor/`, `exp/`, `hotfix/`,
  `chore/`.
- **Python project.** Verification uses the `python-verification-*` skills
  (ruff + mypy + pytest). Substitute your own package path wherever these files
  say `src/<your_package>/`.

> **Adapting this router:** placeholders in angle brackets — `<owner>/<repo>`,
> `src/<your_package>/`, `<project>_test`, `<epic-id>`, `<task-id>` — are meant
> to be replaced with your project's real values. Everything else is intended to
> work as written.

## Two Workflow Modes (single-task vs epic-batch)

This router dispatches **two parallel lifecycles**. Pick the lane by **scope**,
not by phrasing:

- **Single-task (interactive).** One Beads task, with the user live in the loop.
  This is the default and everything in the "Natural Language → Skill Routing"
  table below (start → branch → plan → **refine** → summary → execution gate →
  execute → verify → ship via `beads-ship-task`).
- **Epic-batch (autonomous fan-out).** A whole epic — or a spec that becomes an
  epic — fanned out across detached `Workflow` runs (one agent per task, Opus,
  worktree-isolated where it mutates files). The user is involved only at budget
  gates and the few main-context review/smoke/ship gates. These are the
  `workflow-commands:workflow-*` commands (the six `workflow-*` files).

| Axis | Single-task (interactive) | Epic-batch (autonomous fan-out) |
|---|---|---|
| Scope | one Beads task | a whole epic / a spec |
| Refinement | `plan-refinement-qa` — live Q&A in main ctx, honest/anti-quota question budget | `workflow-writing-plans` Step 4 — autonomous, fixed 5+5 quota, auto-selects |
| Execution | Execution Gate → `superpowers:executing-plans` / `subagent-driven-development` | `workflow-execute-plans` — worktree fan-out, TDD, `python-verification-*`, batched smoke |
| Spikes | handled inline in the one task | `workflow-execute-spikes` (throwaway prototype → findings) |
| Ship | `workflow-commands:beads-ship-task` (one task's branch) | `workflow-commands:workflow-ship-epic` (one shared epic branch) |
| Resume state | `.beads/.workflow-step` file | per-task / per-epic Beads labels (`wp:*` / `sk:*` / `ex:*` / `sh:*`) |

**Decision rule:** one task + live involvement → single-task. A whole epic or a
spec + walk-away fan-out → epic-batch. The batch lane spends real Opus budget
across many agents — **when scope is ambiguous, ask before fanning out.** Full
order + gates: see **Epic-Batch Pipeline: Order & Hard Stops** below.

## CRITICAL: Router Overrides Skill Handoffs

Skills loaded via the Skill tool often end with "next step" or "handoff" instructions (e.g., "offer execution choice"). **These skill-internal handoffs are ALWAYS subordinate to this router.** After ANY skill completes, check this router's mandatory sequence before following the skill's own handoff. The skill was loaded later in context — that does NOT give it priority. This router defines the canonical workflow order:

**Mandatory sequence:** start task → branch → plan → **refine plan** → execute → verify

If you are about to offer execution options and have not yet run plan refinement, STOP — you are violating the sequence.

---

## Hard Stop: No Direct Coding After Task Start

When a Beads task is started (marked `in_progress`), Claude MUST NOT write code directly. Mandatory sequence: mark in_progress → create branch → check for plan → plan → refine plan → execute → verify. Never skip execution or verification steps, even for "simple" tasks.

The branch is a feature branch off the trunk using a `Git Best Practices/Git Best Practices.md` prefix (`feat/`, `fix/`, `refactor/`, `exp/`, `hotfix/`, `chore/`) — never commit directly to `master` / `main`.

## Hard Stop: Systematic Debugging for Bug Tasks

When starting a Beads task whose type is `bug`, ALWAYS invoke `superpowers:systematic-debugging` immediately after marking the task `in_progress` and creating the branch — before writing any plan or code. This applies to any trigger phrase ("I'm starting [task]", "Let's work on [task]", "Let's do [task]") when the resolved task has `type: bug`.

The only way to skip this is if the user explicitly says "skip debugging skill" or "just plan it."

**Closing the bug lifecycle:** this Hard Stop opens it; the **Hard Stop: Verification Before Ship / "Done"** (below) closes it. The bug path (`systematic-debugging → TDD`) still ends with `beads-post-execution` + a `python-verification-{level}` skill before ship/"done" — it is NOT exempt just because it skipped the plan/refine steps. This gap is how a bug fix reaches "done" unverified: the bug lane skips planning, so it also skips the place where verification usually gets remembered.

## Hard Stop: Bootstrap Beads After EnterWorktree

The batch lane runs worktree-isolated agents (`opts.isolation: 'worktree'` in
`workflow-execute-plans` / `workflow-execute-spikes`). Under **beads embedded mode**
(the current default — check yours with `bd dolt status`) there is **no required
per-worktree bootstrap step**: a bare `git worktree add` checkout sees the FULL parent store via
git-common-dir auto-detection, inheriting the git-tracked `.beads/metadata.json` and
sharing the parent's `.beads/embeddeddolt/`. Do not invent a setup step.

Two things that WILL bite:

- **`bd doctor` is a NO-OP here — never use it as the readiness gate.** A clean
  `bd doctor` in a worktree proves nothing. Verify with a real read (`bd ready -n 3`
  / `beads:list` returning the parent's issues) instead.
- **Never stop the beads store from inside a worktree** (`bd dolt stop` in server
  mode). It targets the shared parent store and takes beads down for every
  concurrent agent. Start/stop only from the main repo root, and only when
  something is actually wrong.

## Hard Stop: Scope Ready Tasks to Current Epic

When showing ready tasks, ALWAYS check `bd list --status=in_progress` for an active epic first. If one exists, show only tasks under that epic. Only show cross-epic tasks if no epic is in progress or the current epic has no ready children.

---

## Natural Language → Skill Routing

| User Says | Skill to Invoke |
|-----------|----------------|
| "What's ready?" / "What should I work on?" | Scope to current epic first (`bd list --status=in_progress`), then `beads:ready` |
| "I'm starting [task]" / "Let's work on [task]" / "Let's do [task]" | `workflow-commands:beads-start-task` |
| "Plan this task" / "Write a plan" / "Start planning" | Load Beads context → `superpowers:writing-plans` (save the plan under `docs/plans/`) |
| "Refine the plan" / "Review the plan" / "Plan Q&A" / "Improve the plan" / "Question the plan" | `workflow-commands:plan-refinement-qa` (interactive mode — single-task path) |
| "Summarize the plan" / "Plan summary" / "Show me the plan" / "Recap the plan" | `workflow-commands:plan-summary-console` |
| "Execute the plan" / "Run the plan" | `superpowers:executing-plans` (via Execution Gate) |
| "Execute with subagents" / "Subagent-driven" | `superpowers:subagent-driven-development` (via Execution Gate) |
| "Ship it" / "Send it" / "Commit and push" / "Create a PR" / "PR this" | `workflow-commands:beads-ship-task` (see **PR-policy note** below) |
| "Quick verify" / "just test" | `workflow-commands:python-verification-quick` |
| "Standard verify" / "verify without agents" | `workflow-commands:python-verification-standard` |
| "Full verify" / "complete verification" | `workflow-commands:python-verification-full` |
| "Verify" / "Verify this task" (no level) | Auto-detect level from session state, invoke the matching `python-verification-*` skill |
| "I found a critical bug" / "This needs a hotfix" | `workflow-commands:hotfix-interrupt` |
| "Build check" / "run build validator" | `workflow-commands:P11.5-build-validation-[F]` |
| "Export progress" / "progress report" | `workflow-commands:beads-export-progress` |
| "How's the project looking?" | `beads:stats` |
| "What's blocked?" | `beads:blocked` |
| "Show me [epic/task]" | `beads:show` |
| "Create an epic/task/bug for [description]" | `beads:create` |
| "lint" / "run linter" | `ruff check .` (+ `mypy` if configured) — or `workflow-commands:P02-lint-issues-fix-[QSF]` to fix what it finds |
| "run tests" / "test this" | `pytest -x -q` |
| "format" / "format this" | `ruff format .` |
| "review this code" / "review my changes" | `workflow-commands:P03-code-review-checks-[SF]` |

> **PR-policy note:** Per `Git Best Practices/no-direct-push-to-master.md`, **PRs
> are required** — `beads-ship-task` commits, pushes the feature branch, and opens
> a PR via `commit-commands:commit-push-pr`. Never commit or push directly to
> `master` / `main`. If your project prefers optional PRs, relax it there and in
> `beads-ship-task` together — the router and the ship skill must agree.

---

## Natural Language → Skill Routing (Epic-Batch / Autonomous Fan-Out)

These route to the autonomous pipeline. They all operate on an **epic** (or a
spec), fan out via the `Workflow` tool, and gate on budget before spending.

| User Says | Skill to Invoke |
|-----------|----------------|
| "Decompose this spec" / "Sequence the spec" / "Classify the epic" / "Plan order" / "Planning waves" | `workflow-commands:workflow-planning-sequence` (spec mode → new epic+tasks; `--epic <id>` → classify existing) |
| "Plan the epic" / "Plan all the tasks" / "Batch plan" / "Fan out planning" / "Write all the plans" | `workflow-commands:workflow-writing-plans` (consumes the planning-sequence file; self-refines autonomously) |
| "Run the spikes" / "Execute spikes" / "Prototype the unknowns" / "Resolve the spike-first tasks" | `workflow-commands:workflow-execute-spikes` |
| "What order do I ship this epic?" / "Execution order" / "Execution sequence" / "Plan-coverage check" | `workflow-commands:workflow-execution-sequence` |
| "Execute the epic" / "Build the whole epic" / "Run all the approved plans" / "Fan out execution" | `workflow-commands:workflow-execute-plans` (requires `wp:approved` + `status: approved` epic-wide) |
| "Ship the epic" / "Integrate the epic" / "Ship the whole epic" | `workflow-commands:workflow-ship-epic` (explicit invoke + ship-gate only — never auto-runs) |

> **Scope picks the lane, not the verb.** "Plan / execute / ship" alone defaults
> to the **single-task** table above; the word **"epic"** (or a spec input) routes
> here. See **Hard Stop: Mode Disambiguation**.

---

## Hard Stop: Mode Disambiguation

Three verbs now exist in **both** lanes. Default to **single-task**; switch to the
batch command only when the user names an **epic** (or passes a spec), or has an
epic-batch run already in flight (a task carrying `wp:*` / `ex:*` labels):

| Ambiguous phrase | Single-task (default) | Epic-batch (needs "epic"/spec) |
|---|---|---|
| "Plan this" | `superpowers:writing-plans` → `plan-refinement-qa` | `workflow-commands:workflow-writing-plans` |
| "Execute the plan" | Execution Gate → `superpowers:executing-plans` / `subagent-driven-development` | `workflow-commands:workflow-execute-plans` |
| "Ship it" / "Send it" | `workflow-commands:beads-ship-task` | `workflow-commands:workflow-ship-epic` |

When the scope is genuinely unclear ("plan it" with both a single ready task and an
active epic in play), **ask which** before committing — the batch lane spends
multi-agent budget and a wrong guess is expensive.

---

## Epic-Batch Pipeline: Order & Hard Stops

Canonical order of the six `workflow-*` commands:

```
/workflow-planning-sequence   (spec → new epic+tasks, OR --epic → classify existing;
                               emits the planning-sequence file + wp deps/labels)
   → /workflow-writing-plans   (plan wave-by-wave; SEQ-PLAN pipelines; defers EXEC-GATED) → wp:approved
        ↘ /workflow-execute-spikes  (run SPIKE-FIRST → record findings → close)           → sk:done
          └─ closing a spike is the UNBLOCK SIGNAL → re-run /workflow-writing-plans
             so EXEC-GATED dependents plan against the findings ────────────────────────────┘
   → /workflow-execution-sequence  (blocks-closure → execution waves → plan-coverage gate;
                                    labels exec:<slug> when the closure spans epics)
   → /workflow-execute-plans   (worktree fan-out, TDD, python-verification, batched smoke) → ex:done
   → /workflow-ship-epic       (integrate the one shared epic branch; close tasks + epic)  → sh:shipped
```

**Hard stops (these live inside the commands; the router restates them as the authority doc):**

- **Budget gate before every fan-out.** No `Workflow` run starts before its Step-2
  preview/confirm. Cost is shown as **% of the 5-hr usage limit**. The model **tier**
  (`opus` / `sonnet` — never a pinned version like `claude-opus-4-8`) is settled
  configuration inside each command: never printed in a preview, never a question
  for the user.
- **`execute-plans` refuses a bare cross-epic run with no `exec:<slug>` label.** If
  the epic has open cross-epic `blocks`-predecessors, run
  `/workflow-execution-sequence` first to compute + label the closure — otherwise the
  enablers are silently skipped.
- **Spikes never run through `execute-plans`.** Its epic-wide approval gate refuses
  while EXEC-GATED dependents are deliberately `wp:deferred`. Use
  `/workflow-execute-spikes` (lightweight, gates only on the selected spikes).
- **`execute-plans` ends at `ex:done`; it never auto-ships.** `/workflow-ship-epic`
  **never auto-runs** and **never merges to the trunk** without explicit owner
  confirmation (EXECUTION LOCK + `critical ai agent rule.md`).
- **EXEC-GATED defer→spike→re-run loop.** `EXEC-GATED` tasks are not planned until
  their upstream is *executed* (a spike closed / a task `ex:done`); a `writing-plans`
  re-run picks them up once the upstream's findings exist.
- **Protected paths stay force-attended** even in the batch lane (database
  migrations, any managed-cloud resource, secrets/`.env`, production deploy
  config, merge-to-trunk) — never auto-merged on green QA (`execute-plans`
  Step 5).
- **Worktree agents connect to the parent's embedded store automatically** (beads
  1.0.4 embedded default). The batch lane's worktree-isolated agents
  (`execute-plans` / `execute-spikes`, `opts.isolation: 'worktree'`) reach beads
  from a fresh worktree with **no required per-worktree step** — see
  **Hard Stop: Bootstrap Beads After EnterWorktree** above for the two foot-guns
  (`bd doctor` is a no-op; never stop the store from inside a worktree).

---

## Workflow Step Tracking

Claude updates `.beads/.workflow-step` on each phase transition. Full phase-to-name mapping is defined within each skill. Includes `Plan Refinement` during Q&A phase. Delete the file when no task is active: `rm -f .beads/.workflow-step`.

The `.beads/.workflow-step` file tracks the **single-task** lane only. The
**epic-batch** lane has no step file and **no separate status/resume command** —
its state lives entirely in **Beads labels**, which are the checkpoint +
idempotency mechanism (a crashed or re-run pipeline resumes from the furthest
label per task/epic):

| Command | Label progression | Terminal |
|---|---|---|
| `workflow-writing-plans` | `wp:drafted` \| `wp:skipped` \| `wp:deferred` → `wp:refined-r1` → `wp:applied-r1` | `wp:approved` (+ plan `status: approved`) |
| `workflow-execute-spikes` | `sk:running` → `sk:findings-recorded` | `sk:done` |
| `workflow-execute-plans` | `ex:executing` → `ex:qa:<level>` → `ex:smoke-pending` | `ex:done` (or `ex:blocked`) |
| `workflow-ship-epic` | `sh:pushed` | `sh:shipped` |
| `workflow-execution-sequence` | `exec:<slug>` — durable cross-epic closure scope `execute-plans` consumes | — |

Read/advance these via the `beads:label` / `beads:update` skills — never raw `bd`
in Bash (per `skill-usage.md`).

---

## Standing Posture: Named Scope Is Authorization

When the user has **explicitly named targets and scope** (specific files,
specific versions, specific directories, specific branches), treat the
naming as authorization and proceed without a second confirmation. This
is the default posture and applies to every task — the hard locks in
`critical ai agent rule.md` define the boundaries.

Examples of "named scope" authorization (proceed without re-asking):
- "Delete `venv/` and `.pytest_cache/`" → delete those directories
- "Add `httpx` to requirements" → run `pip install httpx` + edit `requirements.txt`
- "Update the three files I listed" → edit exactly those
- "Ship it" → run `beads-ship-task` per its own steps
- "Remove `docs/plans/2026-01-old-thing.md`" → **reject** (plans are never
  deleted, per `Git Best Practices/protect_plans_and_commit_all.md` Rule 2)

Examples where confirmation is still required (hard locks in
`critical ai agent rule.md` apply regardless of named scope):
- Any managed-cloud / production data mutation
- **Creating a branch** (`git checkout -b` / `git switch -c`) — always ask first,
  including as an implicit step inside an approved plan, skill, or workflow
- Force push, history rewrite, `--no-verify`, `git reset --hard`, merge to trunk
- Deleting anything under `docs/plans/`
- Deleting files the user did not name
- Publishing to external services (issue trackers, Slack, GitHub comments)
- Any **paid/metered API call** — a test marked as hitting a real paid API, or an
  ad-hoc script that does (one approval = one run)

If a user-named operation ambiguously overlaps a hard-lock category,
resolve toward the lock and ask. Full hard-lock boundaries live in
`critical ai agent rule.md`.

---

## Hard Stop: Plan Refinement Before Execution

After `superpowers:writing-plans` completes (plan saved + reviewer approved), ALWAYS invoke `workflow-commands:plan-refinement-qa` before offering execution.

**WARNING — Known failure mode:** The writing-plans skill ends with an "Execution Handoff" section that says to offer execution options immediately. DO NOT FOLLOW IT. That handoff is superseded by this router. The skill's instructions were loaded later in context, which makes them feel more "current" — but this router has higher authority. Invoke `workflow-commands:plan-refinement-qa` FIRST. Always.

The only way to skip refinement is if the user explicitly says "skip refinement" or "let's just execute."

> **One methodology, two modes.** Refinement logic lives in
> `workflow-commands/references/refinement-methodology.md`. The **single-task** path
> uses `plan-refinement-qa` (**interactive** mode — live Q&A here in main context). The
> **batch** pipeline's `workflow-commands:workflow-writing-plans` performs refinement
> itself in **autonomous** mode (its Step 4 — auto-select inside a `Workflow`, reviewed
> at one end gate), because a detached Workflow cannot pause for input. The caller's
> context picks the mode; both share the one engine. This interactive-vs-autonomous
> split is not unique to refinement — it runs the **whole lifecycle** (plan, execute,
> ship): see **Two Workflow Modes** and **Epic-Batch Pipeline: Order & Hard Stops**.

---

## Auto-Invoke: Plan Summary In Console After Refinement

After `workflow-commands:plan-refinement-qa` completes and the plan `.md` file is updated with the refined decisions, IMMEDIATELY invoke `workflow-commands:plan-summary-console` **before** presenting the execution gate. Do NOT ask the user — just invoke it. The command itself prints the numbered + bulleted plan summary in the Claude Code console so the user can review without opening the file, then hands off to the execution gate.

**Sequence:**
1. `workflow-commands:plan-refinement-qa` → plan file updated
2. `workflow-commands:plan-summary-console` → numbered + bulleted summary printed in console (this auto-invoke)
3. Execution gate options presented

The only bypass is if the user explicitly says "skip summary" or "just execute" — then go straight to the execution gate. Claude must never auto-skip the summary on its own.

Manual triggers for the summary command: "summarize the plan", "plan summary", "show me the plan", "recap the plan".

---

## Auto-Invoke: Post-Execution Verification

IMMEDIATELY invoke `workflow-commands:beads-post-execution` — without asking the
user ("Want me to verify?" is wrong; just do it) — as soon as **any**
implementation path finishes, i.e. the moment code is written and you are about
to report the task done or ship it. This fires for **every** path, not only plan
execution:

- `superpowers:executing-plans` / `superpowers:subagent-driven-development` completing, **and**
- the **bug path** `superpowers:systematic-debugging → superpowers:test-driven-development` completing, **and**
- **any direct TDD** implementation of a task (a small fix with no separate plan).

`beads-post-execution` does the level detection (quick < 50 / standard 50–200 /
full 200+ lines) and runs the matching `python-verification-{level}` skill.

**No substitution (HARD RULE — mirrors `workflow-execute-plans` Step 3):** running
`pytest` / `ruff` / `mypy` by hand, a live smoke test, or a subagent's scoped
tests do **NOT** count as verification. Only invoking the named
`python-verification-{quick,standard,full}` **skill** counts — it writes the
`.beads/.verification-done` marker the ship gate below checks. "I ran the tests"
is not "I verified."

---

## Hard Stop: Verification Before Ship / "Done"

Before invoking `workflow-commands:beads-ship-task` **or** telling the user a task
is "done / complete / fixed", a `python-verification-{level}` skill MUST have run
for this task's changes in this session — proven by the `.beads/.verification-done`
marker (single-task lane) or an `ex:qa:<level>` label (fan-out lane). If the
marker/label is absent, STOP and run `workflow-commands:beads-post-execution`
first. This is symmetric to the bug-start Hard Stop: `systematic-debugging` opens
the bug lifecycle; verification closes it.

- Applies to EVERY implementation path — plan execution, subagent-driven, and the
  bug (`systematic-debugging → TDD`) path.
- The ONLY bypass is an explicit real-time user instruction naming the skip
  ("skip verification", "I'm confident, ship it"). Claude's own judgement that a
  change is "too small to verify" is NOT a valid bypass.
- Ad-hoc `pytest`/smoke runs do not satisfy this gate (see the HARD RULE above).

---

## Execution Gate

When a plan is refined (or refinement is explicitly skipped) and ready to execute, ALWAYS ask before proceeding:
> How would you like to execute this plan?
> 1. **Subagent-Driven** — `/superpowers:subagent-driven-development`
> 2. **Sequential** — `/superpowers:executing-plans`

This gate is the **single-task** execution path (one refined plan). For a fully
`wp:approved` **epic** (the batch lane), there is no per-task gate — execution is
`workflow-commands:workflow-execute-plans` (worktree fan-out), gated by its own
budget preview. Don't offer the two options above for an epic-scoped run.

---

## Error Handling

- **No task in progress:** Ask user which task, or suggest "What's ready?"
- **Task not found:** Run `beads:list` to show available tasks
- **Empty description:** Ask user for requirements before proceeding

---

## Response Formatting

**Ready tasks:** Table with ID, Task, Priority, Epic columns.

**Task details:** ID, Status, Priority, Epic, Dependencies.
