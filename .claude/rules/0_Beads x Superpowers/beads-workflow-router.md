# Beads Workflow Router

**Section:** Task Management
**Applies to:** a single Python repo tracked with Beads

Maps what the user says to the skill that runs, and holds the gates every task passes
through. This router is the authority document: when a skill's own handoff disagrees
with it, the router wins (*Workflow Rules*). Two lanes:

- **Single-task (default):** one beads task with the user live in the loop — start →
  branch → plan → refine → summary → execution gate → execute → verify → ship.
- **Epic-batch:** a whole epic, or a spec that becomes one, fanned out across detached
  `Workflow` runs, one worktree-isolated agent per task. Route here only when the user
  names an epic or hands over a spec, or a batch run is already in flight (`wp:*` /
  `ex:*` labels on tasks); when scope is genuinely ambiguous, ask — the batch lane
  spends multi-agent budget.

| Axis | Single-task (interactive) | Epic-batch (autonomous fan-out) |
|---|---|---|
| Scope | one beads task | a whole epic, or a spec |
| Refinement | `workflow-commands:plan-refinement-qa` — live Q&A, honest question budget | `workflow-commands:workflow-writing-plans` Step 4 — autonomous, auto-selects |
| Execution | Execution Gate → `superpowers:executing-plans` or `superpowers:subagent-driven-development` | `workflow-commands:workflow-execute-plans` — worktree fan-out, TDD, `python-verification-*`, batched smoke |
| Spikes | handled inline in the one task | `workflow-commands:workflow-execute-spikes` — throwaway prototype → findings |
| Ship | `workflow-commands:beads-ship-task` — one PR for the task's branch | `workflow-commands:workflow-ship-epic` — one PR for the shared epic branch |
| Resume state | the `.beads/.workflow-step` file | beads labels (`wp:*`, `sk:*`, `ex:*`, `sh:*`) |

**Repo context.** The rest of this router assumes:

- **One repo, one local beads store** under `.beads/`, reached through the `beads:*`
  plugin skills, each of which runs the `bd` command it names
  (`beads-plugin-cli-only.md`). There is no multi-repo hub and no `bd repo sync`.
- **Two sync channels.** Git carries code; `bd dolt` carries beads, over the project's
  own git remote. Pull first, push last: `bd dolt pull` at session or task start,
  `git push` plus `bd dolt push` at ship or session close; never `--force` a beads push
  except a deliberate, agreed re-baseline. `.beads/issues.jsonl` is an untracked,
  readable export, not a sync channel. With no Dolt remote yet, the pull step says so in
  one line and continues (`beads.md`).
- **Beads is the only tracker.** Never TodoWrite, TaskCreate or markdown task lists. If
  you mirror beads to an external tracker, the mirror is downstream: work is created and
  closed only in beads, and the mirror never writes bead status back.
- **Never commit or push to the trunk** (`master` / `main`). Work on a branch prefixed
  `feat/`, `fix/`, `refactor/`, `exp/`, `hotfix/` or `chore/`
  (`Git Best Practices/Git Best Practices.md`), ship through a PR
  (`Git Best Practices/no-direct-push-to-master.md`), and ask before creating any branch
  (`critical ai agent rule.md`).
- **Python verification** runs through the `python-verification-{quick,standard,full}`
  skills — ruff, mypy and pytest, plus review agents at the full level — and writes only
  to the files the task changed (`verification-write-scope.md`). Substitute your package
  path wherever these files say `src/<your_package>/`.
- **Placeholders** in angle brackets — `<owner>/<repo>`, `src/<your_package>/`,
  `<project>_test`, `<epic-id>`, `<task-id>` — stand for your project's real values;
  everything else works as written.

## Single-Task Routing

| User says | Invoke |
|---|---|
| "What's ready?" / "What should I work on?" | scope to the active epic (*Workflow Rules*), then `beads:ready` |
| "I'm starting [task]" / "Let's work on [task]" / "Let's do [task]" | `workflow-commands:beads-start-task` |
| "Plan this task" / "Write a plan" / "Start planning" | load the beads context → `superpowers:writing-plans`, saved under `docs/plans/` |
| "Refine / review / improve / question the plan" / "Plan Q&A" | `workflow-commands:plan-refinement-qa` (interactive mode) |
| "Summarize / recap / show me the plan" / "Plan summary" | `workflow-commands:plan-summary-console` |
| "Execute the plan" / "Run the plan" | Execution Gate → `superpowers:executing-plans` |
| "Execute with subagents" / "Subagent-driven" | Execution Gate → `superpowers:subagent-driven-development` |
| "Ship it" / "Send it" / "Commit and push" / "Create a PR" / "PR this" | `workflow-commands:beads-ship-task` — atomic, in PR form (note below) |
| "Quick verify" / "just test" | `workflow-commands:python-verification-quick` |
| "Standard verify" / "verify without agents" | `workflow-commands:python-verification-standard` |
| "Full verify" / "complete verification" | `workflow-commands:python-verification-full` |
| "Verify" / "Verify this task" (no level) | `workflow-commands:beads-post-execution` — records the changed set, picks the level, runs the matching `python-verification-*` skill |
| "I found a critical bug" / "This needs a hotfix" | `workflow-commands:hotfix-interrupt` |
| "Build check" / "run build validator" | `workflow-commands:P11.5-build-validation-[F]` |
| "Export progress" / "progress report" | `workflow-commands:beads-export-progress` |
| "How's the project looking?" / "What's blocked?" | `beads:stats` / `beads:blocked` |
| "Show me [epic/task]" / "Create an epic/task/bug for [description]" | `beads:show` / `beads:create` |
| "lint" / "run linter" | `ruff check --no-fix .` (plus `mypy` if configured) — read-only; to fix what it finds, `workflow-commands:P02-lint-issues-fix-[QSF]` |
| "run tests" / "test this" | `pytest -x -q` |
| "format" / "format this" | Run the `scoped-ruff-format` block in `.claude/Commands/workflow-commands/references/scoped-ruff.md` — the task's changed set only (`verification-write-scope.md`); formatting the whole project is its own task |
| "review this code" / "review my changes" | `workflow-commands:P03-code-review-checks-[SF]` |

> **PR-policy note.** PRs are required (`Git Best Practices/no-direct-push-to-master.md`):
> `workflow-commands:beads-ship-task` commits, pushes the feature branch and opens a PR
> through `commit-commands:commit-push-pr`; never commit or push to `master` / `main`.
> If your project prefers optional PRs, relax it there and in
> `workflow-commands:beads-ship-task` together — the router and the ship skill must agree.

## Epic-Batch Routing

| User says | Invoke |
|---|---|
| "Decompose / sequence / classify the spec (or epic)" / "Plan order" / "Planning waves" | `workflow-commands:workflow-planning-sequence` — `--spec <path>` makes a new epic and tasks; `--epic <epic-id>` classifies the existing ones |
| "Plan the epic" / "Plan all the tasks" / "Batch plan" / "Write all the plans" | `workflow-commands:workflow-writing-plans` — reads the planning-sequence file; refines full plans autonomously |
| "Run the spikes" / "Prototype the unknowns" / "Resolve the spike-first tasks" | `workflow-commands:workflow-execute-spikes` |
| "What order do I ship this epic?" / "Execution order" / "Plan-coverage check" | `workflow-commands:workflow-execution-sequence` |
| "Execute the epic" / "Build the whole epic" / "Run all the approved plans" | `workflow-commands:workflow-execute-plans` — needs `wp:approved` and plan `status: approved` epic-wide |
| "Ship the epic" / "Integrate the epic" | `workflow-commands:workflow-ship-epic` — explicit invoke only, never auto-runs; opens one PR |

**Scope picks the lane, not the verb.** "Plan", "execute" and "ship" exist in both
lanes. Default to single-task; switch to the batch command only when the user names an
epic or passes a spec, or a batch run is already in flight:

| Ambiguous phrase | Single-task (default) | Epic-batch (needs "epic" or a spec) |
|---|---|---|
| "Plan this" | `superpowers:writing-plans` → `workflow-commands:plan-refinement-qa` | `workflow-commands:workflow-writing-plans` |
| "Execute the plan" | Execution Gate → `superpowers:executing-plans` / `superpowers:subagent-driven-development` | `workflow-commands:workflow-execute-plans` |
| "Ship it" / "Send it" | `workflow-commands:beads-ship-task` | `workflow-commands:workflow-ship-epic` |

When scope is genuinely unclear — "plan it" with a single ready task and an active epic
both in play — ask which before committing; a wrong guess in the batch lane is costly.

Pipeline order:

```
/workflow-commands:workflow-planning-sequence   spec → new epic + tasks, or --epic → classify;
                                                writes the sequence file, wave:<n>, depth:*
→ /workflow-commands:workflow-writing-plans     wave by wave, at each task's depth → wp:approved
  ↘ /workflow-commands:workflow-execute-spikes  approved SPIKE-FIRST tasks         → sk:done
      a closed spike unblocks its EXEC-GATED dependents → re-run writing-plans for them
→ /workflow-commands:workflow-execution-sequence  waves + plan-coverage gate; exec:<slug>
→ /workflow-commands:workflow-execute-plans     worktree fan-out, TDD, QA, smoke   → ex:done
→ /workflow-commands:workflow-ship-epic         opens the PR, closes tasks + epic  → sh:pushed
→ merge the PR, then re-run /workflow-commands:workflow-ship-epic                  → sh:shipped
```

Each batch command enforces its own gates, budget preview included, so read a command
before running it — and put `/clear` between phases (*Completion Report*).

**Batch hard stops.** They live inside the commands; the router restates them:

- **Surface a finished-but-unshipped epic before starting new epic work:** every child
  `ex:done` but no `sh:shipped`, or a closed epic still at `sh:pushed` (PR opened, not
  merged). Planning-sequence, writing-plans and execute-plans check at Step 0 and
  surface-and-ask (`surface-unshipped-epics.md`).
- **Budget gate before every fan-out.** No `Workflow` run starts before its preview and
  confirm: cost as a % of the 5-hr usage limit, never the model tier
  (`never-ask-about-agent-model.md`), plus the temporary worktree branches it creates.
- **No bare cross-epic run.** Execute-plans refuses an epic with open cross-epic
  `blocks` predecessors and no `exec:<slug>` label; run
  `/workflow-commands:workflow-execution-sequence` first, or enablers are silently skipped.
- **Spikes never run through execute-plans** — its epic-wide approval gate refuses while
  EXEC-GATED dependents sit at `wp:deferred`. Use
  `/workflow-commands:workflow-execute-spikes`, which gates only on the chosen spikes.
- **Execute-plans ends at `ex:done` and never ships.** Ship-epic never auto-runs and
  never merges to the trunk; it opens the PR behind its own ship gate.
- **EXEC-GATED defer → spike → re-run loop.** An EXEC-GATED task is planned only after
  its upstream is executed (a spike closed, or a task `ex:done`); a writing-plans re-run
  picks it up once the findings exist.
- **Protected paths stay attended** even in the batch lane — migrations, managed-cloud
  resources, secrets and `.env`, production deploy config, merges to the trunk — and are
  never auto-merged on green QA (execute-plans Step 5).
- **Worktree agents need no beads bootstrap:** in embedded mode a fresh worktree shares
  the parent store automatically (`beads.md`).

## Never Recommend Shipping an Unfinished Epic

Do not recommend, offer or ask about `/workflow-commands:workflow-ship-epic` — in a
Completion Report "Next", an options list, a closing question, anywhere — while any task
in the epic is left. "Left" means any open child that is not `ex:done`, any open
"Smoke gate:" bead, any `wp:deferred`, unplanned or unstarted child, and any open
attended or ops child (a migration apply, a cloud console step, a release gate). Read
these from `bd list` in the same turn.

Recommend the step that finishes the remaining work instead. A smoke that needs the
epic's code running somewhere — a staging service, a preview environment — is finished
by deploying the epic branch there, a managed-cloud change, so ask first
(`critical ai agent rule.md`); shipping only opens the integration PR and closes the
tasks — it deploys nothing. The full gate lives in `workflow-commands:workflow-execute-plans`
Step 8 (the ship-recommendation gate); `workflow-commands:workflow-ship-epic` Step 1
refuses a partial epic regardless.

## Recommending What's Next — Batch Beats Single-Task

**When Claude proposes the next step unprompted** — the Completion Report's "Next", a
"you could start X" line, an options list, or any answer to "what should I work on?" —
**it must not recommend `workflow-commands:beads-start-task` whenever a batch command is
a legal next step.** Recommend the batch command instead:

- Tasks lack a planning sequence → `/workflow-commands:workflow-planning-sequence`.
- Sequenced but not yet planned, or plans not `wp:approved` →
  `/workflow-commands:workflow-writing-plans`.
- Two or more tasks at `wp:approved` with nothing executed →
  `/workflow-commands:workflow-execute-plans`.

Every such recommendation is preceded by the **Epic Status Table** (*Completion
Report*), so the owner sees the whole epic it is drawn from.

**The one case where `workflow-commands:beads-start-task` is right: exactly one task is
actually available** — one unblocked task, or one task left in scope; then the batch lane
has nothing to fan out. Count *available* tasks, not open ones: a task blocked by an
open dependency is not available, and neither is one whose owner question is
unanswered. With two or more, recommend the batch command for where they sit in the
pipeline — when they sit at different stages, the command for the EARLIEST stage
holding two or more of them.

Why: the batch lane exists to run a whole epic's worth of work in parallel behind its
own gates. Recommending one task at a time when five are ready quietly discards that,
and the owner ends up driving five rounds of a loop that was built to run once.

This governs Claude's **recommendations** only: a direct request ("I'm starting
<task-id>", "let's work on X") still routes to `workflow-commands:beads-start-task`, and
Claude does not second-guess the owner's pick or re-pitch the batch lane.

**The Sizing Gate applies here too, once per task.**
`workflow-commands:workflow-planning-sequence` gives every task a plan depth as its
third classification axis — `PLAN-FULL`, `PLAN-LITE` or `TDD-DIRECT`, matching Lanes C,
B and A below. Its critic may only promote, and the owner can re-assign depth at the
review gate. `workflow-commands:workflow-writing-plans` then **reads** that depth and
never re-derives it: full plans get the refinement round, lite plans skip it, and
TDD-direct tasks get a task card (`wp:carded`) instead of a plan. The single-task lane
decides depth as each task starts; the batch lane decides it for the whole epic up
front — same criteria, same tie-break toward more planning.

## Sizing Gate — Claude picks the lane

Once a task is `in_progress`, Claude decides how much process the work actually needs.
Big plans for one-line bugs waste the owner's time; TDD-on-the-fly for architectural
work loses decisions that should have been recorded.

**Announce the call in one line before starting** — the lane and the one reason for
it — so the owner can override cheaply:

> Lane: **TDD-direct** — root cause known, one file, no contract change.

The owner overrides at any time with "plan it" or "just TDD it", and that always wins.

### Lane A — TDD-direct

Straight to `superpowers:test-driven-development`: no plan file, no refinement, no
Execution Gate. Requires **all** of:

- The root cause (bug) or the shape (feature) is already known and named — you can point
  at the file(s) and state the behaviour change.
- Contained: roughly 2–3 production files and about 50 lines at most.
- No database migration, no public API or client↔server contract change, no new
  dependency, no infrastructure or cloud-console step.
- No real design alternatives worth the owner choosing between.
- Existing tests cover the area, so one failing pytest test can be written first.
- Finishable this session, and reversible.

### Lane B — Plan-lite

Write the plan file under `docs/plans/` (`protect_plans_and_commit_all.md` Rule 1), then
go straight to execution, skipping `workflow-commands:plan-refinement-qa` and the
Execution Gate. Use it for multi-step or multi-file work whose approach is settled, with
no alternatives worth debating — the plan is a record and a checklist, not a decision.

### Lane C — Full lane

`superpowers:writing-plans` → `workflow-commands:plan-refinement-qa` →
`workflow-commands:plan-summary-console` → Execution Gate. Use it when **any** of these
is true:

- It touches auth, security, payments, permissions or user data.
- A schema, a migration, or anything against production data or infrastructure.
- A client↔server contract, a public API, or a new dependency.
- Real alternatives exist that the owner should choose between.
- It spans more than one session, or more than about 3 files or 150 lines.
- Acceptance is ambiguous, or the task description is thin.
- You are unsure which lane applies. **Ties go to Lane C.**

A mid-flight escalation — Lane A turns out to be Lane C — means stop, say so, and
switch; never push on because you already started.

## Fan-Out Gate

**Assess isolation on every multi-task unit; prefer parallel.** Before executing a plan,
an epic wave or a batch of fixes, decide whether its tasks can run as a **parallel,
worktree-isolated fan-out** instead of one after another. Default to the fan-out
whenever it is possible and safe; serial execution is the fallback, and choosing it
needs a stated reason. Announce the call in one line, the way the Sizing Gate does —
for a fan-out, or when it is genuinely serial:

> Fan-out: **3 waves, max 4 parallel** — Tasks 2/3/4 share no files; Task 5 uses all three.
> Fan-out: **not viable** — every task edits the same two files.

### The three questions, in order

1. **Shared index?** Agents committing into ONE checkout share a `.git/index`;
   concurrent `git add` / `git commit` pairs can produce a commit carrying another
   task's files, which corrupts the `BASE..HEAD` ranges every review package is built
   from. Worktree isolation (`opts.isolation: 'worktree'`) removes the hazard — its own
   checkout, index and branch, merged back on green — so this question forces
   serialization only when isolation is NOT used. It is the reason to isolate, not a
   reason to refuse a fan-out.
2. **Write-set overlap?** Two isolated agents editing the same FILE conflict at merge:
   same file, different waves. Derive each write set from the task's STEPS, not only its
   "Files:" block — blocks under-report (in a downstream project, one task's real sweep
   hit five files its block never listed).
3. **Interface dependency?** A task that consumes a type, function, constant or
   signature another task creates waits for it. Separate HARD dependencies (it will not
   import or run without it) from SOFT ones (it only needs the thing designed, not
   built); soft dependencies can often share a wave.

Group the tasks into waves where every task's write set is disjoint from its
wave-mates' and every hard dependency sits in an earlier wave.

### Two checks, run rather than assumed

- **Base commit.** Isolated agents start from the trunk (`origin/master` or
  `origin/main`), not the current feature branch. On a long-lived branch carrying work
  the task builds on, each agent's FIRST command is `git switch -c <branch> <sha>` at
  the right commit — never `git merge <sha>`, which can drag trunk commits in.
- **Disk.** Each committing worktree is a full checkout of the repo. Run `df -h .` and
  cap concurrency on what is actually free; a fan-out filled a disk this way in a
  downstream project.

A fan-out creates temporary worktree branches, merged back and removed as each agent
finishes. The batch commands' budget previews say so, which makes approving the gate the
branch approval `critical ai agent rule.md` requires.

### When serial genuinely wins, say which

Fan-out buys nothing on an inherently linear chain, and a false promise of parallelism
is worse than none. Name the reason: every task edits the same file; each consumes the
last one's output; or the tasks are attended and need the owner between them.

**Attended tasks are exempt from the fan-out, not from the assessment.**
`workflow-commands:workflow-execute-plans` routes `smoke_test: required`,
shared-substrate and protected-path tasks to serialized main-context execution by its
own classifier, so they never enter the parallel pool. Do the assessment anyway and
report the verdict — the fix rounds and independent sub-tasks inside an attended plan
are often parallelizable even when the plan as a whole is not.

## Workflow Rules

- **No direct coding after a task starts.** Once a task is `in_progress`, Claude does
  not write code directly: it runs the *Sizing Gate* and follows the lane it picks. Lane
  A goes branch → TDD → verify; Lanes B and C add a plan (and, for C, refinement)
  between branch and execute. No lane skips execution or verification, however simple
  the task looks.
- **Bug tasks start with systematic debugging.** Starting a task of type `bug`, by any
  trigger phrase, invoke `superpowers:systematic-debugging` right after marking it
  `in_progress` and settling the branch, before any plan or code; skip only on an
  explicit "skip debugging skill" or "just plan it". The bug path still ends with
  `workflow-commands:beads-post-execution` — skipping the plan does not skip verification.
- **Ready tasks are scoped to the active epic.** Check `bd list --status=in_progress`
  for an active epic first and, if one exists, show only its children; show cross-epic
  tasks only when no epic is in progress or the current epic has no ready children.
- **IMPORTANT — the router outranks skill handoffs.** Skills often end with their own
  "next step" or handoff instructions, and those are always subordinate to this router.
  After any skill completes, check the sequence here before following its handoff —
  being loaded later in context gives a skill no priority. Known failure mode:
  `superpowers:writing-plans` ends with an "Execution Handoff" section that offers
  execution options at once. In Lane C, do NOT follow it.
- **IMPORTANT — Lane C runs refinement, then the plan summary, then the Execution
  Gate.** After `superpowers:writing-plans`, always invoke
  `workflow-commands:plan-refinement-qa` before offering execution (skip only on an
  explicit "skip refinement" or "let's just execute", or because the Sizing Gate chose
  Lane B). After refinement updates the plan file, immediately invoke
  `workflow-commands:plan-summary-console` without asking (skip only on an explicit
  "skip summary" or "just execute"), then show the Execution Gate. The summary also runs
  on request: "summarize the plan", "plan summary", "show me the plan", "recap the plan".
- **One methodology, two modes.** Refinement logic lives in
  `.claude/Commands/workflow-commands/references/refinement-methodology.md`. The
  single-task lane runs it **interactively** through
  `workflow-commands:plan-refinement-qa` (live Q&A, honest question budget); the batch
  lane's `workflow-commands:workflow-writing-plans` runs it **autonomously** in Step 4
  (auto-select inside a `Workflow`, reviewed at one end gate), because a detached
  Workflow cannot pause for input. The same split runs plan, execute and ship.
- **IMPORTANT — post-execution runs after every implementation path.** The moment code
  is written and you are about to report a task done or ship it — after
  `superpowers:executing-plans`, after `superpowers:subagent-driven-development`, after
  the bug path (`superpowers:systematic-debugging` → TDD), after any direct TDD fix —
  immediately invoke `workflow-commands:beads-post-execution` without asking ("Want me
  to verify?" is wrong). It records the changed set, detects the level and runs the
  matching `python-verification-{level}` skill (*Verification Before Ship / "Done"*).
- **Ship is atomic, in PR form.** "Ship it", "send it", "commit and push" and "create a
  PR" run the whole `workflow-commands:beads-ship-task` sequence end to end — never a
  partial subset, never a narrowing "push only?" question. The spec is *Ship Is Atomic
  (PR form)* in `Git Best Practices/no-direct-push-to-master.md`.
- **Worktrees need no beads bootstrap.** In beads' embedded mode a fresh worktree shares
  the parent store automatically; `bd doctor` proves nothing there, and the store is
  never stopped from inside a worktree. Checks and troubleshooting: `beads.md`.
- **Step tracking.** The single-task lane records its phase in `.beads/.workflow-step`
  on each transition — including `Plan Refinement` during the Q&A — with phase names set
  by each skill; delete the file when no task is active (`rm -f .beads/.workflow-step`).
  The batch lane has no step file and no separate status or resume command: its state
  lives in labels (*Label Ladders*), and a crashed or re-run command resumes from the
  furthest label per task or epic.
- **One bead-status writer per lane.** In the single-task lane,
  `workflow-commands:beads-start-task` sets `in_progress` and
  `workflow-commands:beads-ship-task` closes the task when it opens the PR. In the batch
  lane nothing calls `bd update --status`: `workflow-commands:workflow-execute-plans`
  never writes status — the `ex:*` labels are the only progress record — and
  `workflow-commands:workflow-ship-epic` makes the single transition, open → closed,
  when it opens the epic's PR; there, `beads:update` is for labels and fields only.

  Why: "mark `in_progress` when starting" is a single-task rule. In a batch run it adds
  a second status writer nothing ever clears, and the epic ends up reading as a mix of
  `open` and `in_progress` that reflects which writes landed, not what is finished
  (observed in a downstream project). So mid-epic, `bd ready` and `bd list --status`
  do not show batch work as in flight — read the `ex:*` labels instead. There is no
  external-tracker status writer; a mirror never writes bead status.

## Named Scope Is Authorization

When the user has **explicitly named targets and scope** — specific files, versions,
directories or branches — treat the naming as authorization and proceed without a
second confirmation. This is the default posture for every task; the hard locks in
`critical ai agent rule.md` set its limits.

Named scope, so proceed without re-asking:

- "Delete `venv/` and `.pytest_cache/`" → delete those directories.
- "Add `httpx` to requirements" → `pip install httpx` and edit `requirements.txt`.
- "Update the three files I listed" → edit exactly those.
- "Ship it" → run `workflow-commands:beads-ship-task` per its own steps.
- "Remove `docs/plans/2026-01-old-thing.md`" → **reject**: plans are never deleted
  (`protect_plans_and_commit_all.md` Rule 2).

Still confirm first, whatever was named — these hard locks hold regardless:

- any managed-cloud or production data mutation;
- **creating a branch** (`git checkout -b`, `git switch -c`) — always ask, including as
  an implicit step inside an approved plan, skill or workflow (a batch budget gate that
  discloses its temporary worktree branches is that ask);
- force push, history rewrite, `--no-verify`, `git reset --hard`, a merge to the trunk;
- deleting anything under `docs/plans/`, or files the user did not name;
- publishing to external services (issue trackers, Slack, GitHub comments);
- any **paid or metered API call** — a test marked as hitting a real paid API, or an
  ad-hoc script that does (one approval covers one run).

If a named operation ambiguously overlaps a hard-lock category, resolve toward the lock
and ask.

## Verification Before Ship / "Done"

Before invoking `workflow-commands:beads-ship-task`, or telling the user a task is
"done", "complete" or "fixed", a `python-verification-{level}` skill MUST have run on
this task's changes in this session — proven by the `.beads/.verification-done` marker
(single-task lane) or an `ex:qa:<level>` label (batch lane). If the proof is missing,
stop and run `workflow-commands:beads-post-execution` first.

- It applies to every implementation path: plan execution, subagent-driven, the bug
  path and direct TDD.
- **No substitution (hard rule).** Running `pytest`, `ruff` or `mypy` by hand, a live
  smoke test, or a subagent's scoped tests does NOT count. Only the named
  `python-verification-{quick,standard,full}` skill counts — it writes the marker the
  ship gate checks. "I ran the tests" is not "I verified."
- **The only bypass** is an explicit, real-time instruction naming the skip — "skip
  verification", "I'm confident, ship it" — recorded in the commit or PR body. Claude's
  own judgement that a change is "too small to verify" is not a bypass.

## Label Ladders — Append-Only, Furthest Wins

The batch lane's labels are a HISTORY, not a current-state field. A step appends its
label and never removes an earlier one; a reader ranks what is present and takes the
FURTHEST stage — which is what the Completion Report's "furthest label" means:

```
wp:  drafted | skipped | carded > refined-rN > applied-rN > approved
sk:  running > findings-recorded > done
ex:  executing > qa:<level> > smoke-pending > done
sh:  pushed > shipped
```

- **Never remove a label to "correct" a bead.** A bead carrying both `ex:executing` and
  `ex:done` is finished and needs no cleanup — `ex:done` is furthest; the same goes for
  `wp:drafted` alongside `wp:approved`. Removing the earlier label destroys the only
  record of how the work actually went.
- **`wp:deferred` and `ex:blocked` are flags, not stages.** They do not rank:
  `wp:deferred` together with `wp:approved` reads "was deferred, later approved" —
  approved wins, nothing is owed.
- **`smoke:passed` is a flag that discharges `ex:smoke-pending`.** No command writes
  it — execute-plans moves a smoked task straight to `ex:done` — so it appears only
  when someone records a smoke run by hand with `beads:label`. A bead carrying
  `smoke:passed` whose furthest `ex:*` is still below `ex:done` is a real defect: the
  smoke ran and nobody closed the ladder. Fix it by ADDING `ex:done` after verifying in
  the tree that the work landed — never by editing the earlier labels.
- **`sh:pushed` is not shipped.** It means the epic's PR is open and its tasks and epic
  are closed; only a re-run of `workflow-commands:workflow-ship-epic` that confirms the
  merge adds `sh:shipped` (`surface-unshipped-epics.md`).

Who writes what:

| Command | Labels it appends | Terminal |
|---|---|---|
| `workflow-commands:workflow-planning-sequence` | `track:<name>`, `wave:<n>`, `depth:full` \| `depth:lite` \| `depth:tdd` — current classifications, not a ladder: a re-classification replaces them | — |
| `workflow-commands:workflow-writing-plans` | `wp:drafted` \| `wp:skipped` \| `wp:carded` \| `wp:deferred` → `wp:refined-r1` → `wp:applied-r1` (full plans only) | `wp:approved` (+ plan `status: approved`) |
| `workflow-commands:workflow-execute-spikes` | `sk:running` → `sk:findings-recorded` | `sk:done` |
| `workflow-commands:workflow-execution-sequence` | `exec:<slug>` — the cross-epic closure scope execute-plans consumes | — |
| `workflow-commands:workflow-execute-plans` | `ex:executing` → `ex:qa:<level>` → `ex:smoke-pending` | `ex:done` (or the `ex:blocked` flag) |
| `workflow-commands:workflow-ship-epic` | `sh:pushed` (PR opened) | `sh:shipped` (merge confirmed) |

Read and advance them through the `beads:label` and `beads:update` skills — one `bd`
command at a time, read back after every write (`beads.md`).

## Execution Gate

When a plan is refined (or refinement is explicitly skipped) and ready to execute,
always ask before proceeding:

> How would you like to execute this plan?
> 1. **Subagent-Driven** — `/superpowers:subagent-driven-development`
> 2. **Sequential** — `/superpowers:executing-plans`

This gate belongs to the single-task lane (one refined plan). A fully `wp:approved` epic
has no per-task gate — execution is `/workflow-commands:workflow-execute-plans`, behind
its own budget preview — so don't offer the two options above for an epic-scoped run.

Lanes A and B have no Execution Gate: A has no plan to execute, and B's lane choice
already settled that there is nothing to choose between.

## Completion Report

When a task closes or a batch command finishes, end the turn with, unprompted:

1. **Done** — the **Epic Status Table** (below) for the current epic, then a short
   prose list of what actually landed this run.
2. **Left** — what remains and why, per item: blocked, deferred by decision, or not
   reached — never collapsed into one bucket.
3. **Next** — the recommended command sequence, flagging attended versus background
   steps, plus any open decisions or user actions. Show `/clear` as its own numbered
   step before the next phase's command; each phase reads its state from files and
   labels, not the conversation. Every command shown — here, at the Execution Gate, or
   in any "run this next" line — is the full slash form with its namespace
   (`/workflow-commands:workflow-execute-plans`, `/commit-commands:commit-push-pr`,
   `/superpowers:executing-plans`), never a bare `/workflow-execute-plans`: the user
   pastes it verbatim, and a bare name fails with "Unknown command". Pick it per
   *Recommending What's Next — Batch Beats Single-Task*, and never recommend ship-epic
   while anything is left (*Never Recommend Shipping an Unfinished Epic*).

Run a mandated next step first — `workflow-commands:beads-post-execution` after
execution, `workflow-commands:plan-summary-console` after refinement — then the report.
Skip only on an explicit "skip summary" or "just execute".

### Epic Status Table — always the WHOLE epic

Whenever Claude reports status or recommends what's next — the Completion Report, a
"Next" section, an answer to "what's ready?", or any "you could do X next" line — it
prints a table of the **entire current epic**, not just the tasks touched this turn: one
row per child task, including ones not started, closed, deferred, blocked or never
touched. A table of only this turn's work hides the rest of the epic, and the owner has
to ask for it separately.

Columns, in this order:

| Column | Source |
|---|---|
| **Task** | bead id |
| **Name** | title (shortened if long) |
| **Description** | first line of the bead description, one short clause |
| **Plan** | furthest `wp:*` label (`wp:deferred` / `spike-first` shown when present) |
| **Wave** | `wave:<n>` label |
| **Executed** | furthest `sk:*` / `ex:*` / `sh:*` label, plus the `ex:blocked` and `smoke:*` flags |
| **Status** | open / in_progress / closed |

- Read every value from `bd list` / `bd show` in this turn — never from memory or an
  earlier table.
- When a run spans a cross-epic closure (`exec:<slug>`), print the named epic's table
  and the closure's outside members in a second, short table. When the turn created a
  side epic (for example fixes split out of a smoke gate), print its table below too.
- Sort by wave, then by id. List every open blocker bead (bugs, smoke gates) that blocks
  a child in a short "Blockers" list under the table.

## Errors & Formatting

- **No task in progress** → ask which task, or suggest "What's ready?".
- **Task not found** → run `beads:list` to show the available tasks.
- **Empty description** → ask the user for requirements before proceeding.
- **Ready tasks** render as a table (ID, Task, Priority, Epic); **task details** show ID,
  Status, Priority, Epic, Dependencies.
