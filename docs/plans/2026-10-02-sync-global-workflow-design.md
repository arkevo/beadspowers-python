# Sync the Global Workflow Updates into the Python Template — Design

- **Date:** 2026-10-02
- **Status:** design approved in brainstorming; this written spec awaits owner review
- **Branch:** `chore/sync-global-workflow-2026-10`
- **Next step after approval:** `superpowers:writing-plans` →
  `docs/plans/2026-10-02-sync-global-workflow.md`

## 1. Goal

Bring this template level with the changes the owner has made to their global
(user-level) Flutter workflow since the template was last ported. Translate those
changes to Python and to project-agnostic wording, lose nothing the template does
on purpose, and leave a clean baseline for the next sync.

**Success criteria**

1. Every portable change from the global files is in the template.
2. Nothing Python-specific or template-specific is lost — checked against the
   preservation checklist in §11.
3. No file points at a rule, section, skill or command the template doesn't have.
4. The README is a short, numbered recipe of exact, verified commands, with each
   recommended `/clear` as its own step.

## 2. How the owner's changes were identified

- **Global workflow, as of 2026-10-02:** `~/.claude/commands/workflow-commands/`,
  `~/.claude/rules/`, `~/.claude/agents/`, `~/.claude/skills/`.
- **Merge base:** the template's last port (commit `6cf223a`, 2026-08-11) was taken
  from the owner's Flutter repo as it stood on 2026-07-31. That snapshot
  was extracted and used as the base of a three-way comparison:
  - base → global = the owner's changes (what this sync carries over);
  - base → template = the Python conversion and generification (what must survive).
- **Pairing:** same-named files, plus `flutter-verification-{quick,standard,full}` ↔
  `python-verification-{quick,standard,full}`.
- **Unchanged globally since the base (nothing to carry):** `beads-ship-task`,
  `hotfix-interrupt` (one knock-on line, W3), `P06`, `P07`, `P08`, `P11.5`, `P12`,
  `references/refinement-methodology.md`, and the comment-analyzer, test-coverage
  and type-analyzer agents. `tdd-test-writer` and `beads-start-task` changed only
  in owner-specific tool names, which are skipped.

## 3. Decisions taken in brainstorming

1. **Scope:** all five workstreams — fixes and naming, verification write scope,
   verification trim, plan depth, router governance.
2. **Side fixes:** problems found that the global changes didn't cause are fixed in
   the same PR, as their own commits.
3. **Beads sync:** mirror the owner's setup — Dolt sync to the project's own git
   remote, `issues.jsonl` as an untracked readable export, auto-import off.
4. **Ship closure:** beads still close when the PR opens; the epic then carries
   `sh:pushed`, and only a re-run of ship-epic after the merge adds `sh:shipped`.
   The single-task lane's closure is unchanged.
5. **Diagram:** restore the deleted process diagram and update it.
6. **Router:** re-lay it out to mirror the global router's sections, order and
   names, carrying the template-only content as compact sections.
7. **README:** as short as possible — numbered steps of exact commands, with each
   `/clear` as its own step.
8. Design sections 1–6 were approved in chat on 2026-10-02; decision 7 amended
   section 6.

## 4. Ground rules for every change

1. Carry only what changed in the global files since the base, plus the approved
   side fixes. Everything else in the template stays as it is.
2. Translate, don't copy. Flutter tooling becomes ruff, mypy, pytest and
   `python -m build`. Owner-project names, bead ids and dates become generic
   wording, and incidents are retold as "observed in a downstream project", the
   way `surface-unshipped-epics.md` already does it.
3. Leave out what is private or platform-bound (§8).
4. New files keep their global names so the next sync lines up. When the template
   already has a home for the content under another name, it goes there.
5. Every deliberate difference from the global files is recorded (§7).

## 5. File map (36 files)

**Edited — commands (19):** `workflow-planning-sequence`, `workflow-writing-plans`,
`workflow-execute-spikes`, `workflow-execution-sequence`, `workflow-execute-plans`,
`workflow-ship-epic`, `beads-post-execution`, `beads-start-task`,
`beads-ship-task`, `beads-export-progress`, `P02-lint-issues-fix-[QSF]`,
`P03-code-review-checks-[SF]`, `P14-security-review-[SF]`, `plan-refinement-qa`,
`plan-summary-console`, `hotfix-interrupt`, `python-verification-quick`,
`python-verification-standard`, `python-verification-full`.

**Deleted (2):** `P04-architecture-validation-[SF]`, `P05-code-simplification-[SF]`.

**Edited — other (8):** `agents/verification-silent-failure.md`;
`rules/0_Beads x Superpowers/` `beads-workflow-router.md`, `skill-usage.md`,
`surface-unshipped-epics.md`; `rules/Git Best Practices/` `Git Best Practices.md`,
`no-direct-push-to-master.md`; `hooks/validate-bash.sh`; `README.md`.

**New (5):** `rules/0_Beads x Superpowers/` `no-skipping-workflow-steps.md`,
`never-ask-about-agent-model.md`, `beads.md`; `rules/verification-write-scope.md`;
`skills/beads-worktree-troubleshooting/SKILL.md`.

**Restored and updated (2):** `docs/workflow-process-flow.drawio` and its `.png`.

**Untouched:** P06, P07, P08, P11.5, P12, `tdd-test-writer`,
`references/refinement-methodology.md`, the other three agents, `write-safety.sh`,
`settings.json`, `critical ai agent rule.md`, `beads-plugin-cli-only.md`,
`bug-must-have-epic.md`, `protect_plans_and_commit_all.md`.

## 6. Workstreams (one commit each, in this order)

### W1 — Naming sweep and stale references

- Every command a reader might paste uses its full slash form,
  `/workflow-commands:<name>`; prose that names a skill uses
  `workflow-commands:<name>`. This covers the router (including its pipeline block),
  the six workflow-* commands, `surface-unshipped-epics.md`, `plan-refinement-qa`,
  `plan-summary-console`, the three tiers and the README — about 120 occurrences.
- P03's examples call `/python-code-review`, which doesn't exist; they use
  `/workflow-commands:P03-code-review-checks-[SF]`, keeping the Python paths.
- writing-plans cites a "git-workflow rule" (and "git-workflow Rule 2") the template
  doesn't have → `Git Best Practices/protect_plans_and_commit_all.md`.
- P02 cites `.claude/rules/lint_rules/`, which doesn't exist → the project's
  `[tool.ruff]` settings in `pyproject.toml`.
- Pinned model names become tier names: "Opus-4.8/xhigh" (execution-sequence) →
  "Opus"; "Sonnet-5-medium" (writing-plans) → "sonnet / medium".
- "% of the 5-hr Opus xhigh usage limit" → "% of the 5-hr usage limit"
  (writing-plans, execute-plans, execute-spikes).
- execute-plans' frontmatter drops its leftover "(FastAPI service)".

### W2 — Verification only rewrites what the task changed

**beads-post-execution, new Step 2a — record the changed set.**

- Changed set = uncommitted tracked edits (deletions excluded) + untracked files +
  files changed on the branch since `git merge-base <trunk> HEAD`.
- Trunk = `git symbolic-ref --short refs/remotes/origin/HEAD` (origin/main or
  origin/master); if that is unset, run `git remote set-head origin --auto` once.
- The line count covers the same range plus the untracked files' lengths.
- Written to `.beads/.session-state.json` as `modified_files` (a plain list of path
  strings) and `total_lines_changed`, by read-modify-write, so `task_id`,
  `plan_file` and `verification.*` survive.

**Level detection.** Under 50 lines → quick; 50–200 → standard; over 200, or a new
module under `src/` → full. A new test file no longer forces full. Full is described
as "review agents + Codex adversarial pass", not "all 14 phases". The "which files
did you change?" question appears only if the set is still empty, and it only picks
a level. A volunteered file list becomes the set and is echoed back; a level-only
answer leaves the set **unknown**. The question's authority citation points at the
router's "Named Scope Is Authorization" section.

**New always-loaded rule, `rules/verification-write-scope.md`.**

- Read wide, write narrow: analysis may read the whole project; anything that
  writes — `ruff check --fix`, `ruff format`, edits proposed by review agents —
  touches only the changed set.
- Unknown set → auto-fix is skipped and the report says so. Never widen to the
  project root; never ask for a file list just to justify a fix.
- Never auto-fixed: `.venv/`, `vendor/`, `third_party/`, generated code (for
  example `*_pb2.py`), and `migrations/` (a protected path). `.ipynb` files are
  linted and reported only.
- Phase 12 may create new test files under `tests/` that mirror a changed module.
- A whole-project cleanup is its own task, with its own bead and review.
- Why: an unscoped auto-fix observed in a downstream project rewrote 17 files,
  including read-only exports and a dependency manifest. Because "ship it" stages
  every changed file (`protect_plans_and_commit_all.md` Rule 3), such a fix rides
  into an unrelated commit.

**The sequence, everywhere something writes:**

1. Snapshot `git status --short`.
2. `ruff check --diff --force-exclude <files>` — a preview that writes nothing.
3. `ruff check --fix --force-exclude <files>`.
4. Compare with the snapshot. Tracked files outside the set that moved are
   reverted with `git checkout HEAD -- <path>` (they were clean before, so nothing
   is lost) and reported. Untracked leaks are reported, never deleted without
   approval.

Formatting is `ruff format --force-exclude <files>` followed by
`ruff format --check --force-exclude <files>`, with the same leak check, and no new
hook. `--force-exclude` matters because ruff ignores its own exclude list for files
named on the command line.

**Where it lands.**

- **P02:** Step 1 reads the changed set (whole-project analysis is read-only, a
  last resort); Step 4 applies the sequence; dead-code findings (vulture, F401)
  outside the set are reported, not fixed; Step 6 and the tools list are scoped.
- **python-verification-quick:** the Phase 1 unknown-set rule; Step 2's dry run,
  `--force-exclude` and leak check; report lines; quick-reference rows.
- **python-verification-standard:** Phase 1; Phase 2 Step 3, which fixes today's
  bare `ruff check --fix`; report lines.
- **python-verification-full:** Phase 1 Step 1; Phase 2 Step 3; Phase 8.5 step 6,
  which fixes today's bare `ruff format`; Phase 12.5 step 1; Scope Control split
  into a read scope and a write scope; report lines ("Auto-fixed: N across M changed
  files" or "SKIPPED (changed set unknown)", plus "no files outside the changed set"
  or "LEAK: [list]").
- **P14:** `jq '.modified_files[].path'` → `jq '.modified_files[]'`.
- The tiers and P02 cite the rule and keep a short inline summary.

### W3 — Trimming verification and fixing the Codex pass

- **Retire P04 and P05** from standard and full: their phase sections, report
  blocks, the Architecture Score, checks-completed lines, quick-reference rows,
  scope bullets and diagram boxes. Phase 9 sources "3, 6–8". Each tier gets a
  retirement note: they found nothing in any recorded run, and an architecture
  review a task genuinely needs is its own task with its own bead. Delete both
  files. Remove phase counts ("13-phase", "all 14 phases") from descriptions.
- **Full Phase 3** keeps rules compliance and historical intent (with a "respect
  TODO/FIXME and don't-modify guidance" bullet), reports only findings at ≥80%
  confidence, and drops its bug scan. The test-presence check moves to Phase 11.
- **verification-silent-failure agent, new Step 1.5 bug scan,** plus an updated
  description. Classes:
  - None handling: attribute access, indexing or calls on a value that can be
    `None` on a real path; `cast()` or `# type: ignore` hiding it; `assert` as the
    only runtime guard; attributes first assigned outside `__init__`; falsy values
    treated as missing.
  - Async misuse: coroutines never awaited; `create_task()` results not kept;
    blocking calls inside `async def`; `CancelledError` swallowed; resources used
    after their `with` block closed them.
  - Resource lifecycle: files, sockets, connections, sessions, HTTP clients,
    `subprocess.Popen`, executors or pools opened without `with`/`finally`; locks
    without a release in `finally`; threads never joined.
  - Shared mutable state: mutable default arguments and class attributes; unlocked
    state shared across threads or tasks; a collection mutated while iterating it;
    late-binding closures in loops.
  - Silent wrong results: a generator consumed twice; naive and aware datetimes
    mixed.
  It ignores what ruff and mypy already report under the project's configuration
  and reports through the existing JSON contract.
- **Full Phase 7 section** gains a short bug-scan step, so the in-context fallback
  still covers it if the agent fails.
- **Standard Phase 3** keeps its bug scan (standard runs no agents), with its list
  aligned to the agent's classes, dropping the duplicate "resource leaks" and the
  mypy-territory "type annotation issues".
- **Phase 6 gate (full):** the type-design agent launches only when the change adds
  a type under `src/` — `class`, `TypeAlias`, `type X =`, `NewType`, `TypedDict`,
  `NamedTuple` — found by grepping added lines across committed (`<trunk>...HEAD`),
  staged and unstaged (`HEAD`) and untracked changes, ignoring comments. Test
  classes don't count. An unknown set launches it anyway. Otherwise the report says
  "Skipped (no new types)" and the launch count reads "2–3 invocations".
- **Phase 14 gate (full and standard):** runs only when its triggers match, and the
  triggers widen to everything its checks look for: `eval(`, `exec(`, `pickle`,
  `yaml.load`, `subprocess`, `shell=True`, `verify=False`, `DEBUG`, `random.`;
  `**/migrations/**`, `alembic/versions/**`, `**/*.sql`, settings modules; `GRANT`,
  `REVOKE`, `CREATE POLICY`, `ROW LEVEL SECURITY`, `SECURITY DEFINER`. It reports
  "Skipped (no sensitive files)" or "Triggered (files)". The full tier's line that
  says both "auto-triggers" and "always runs" is fixed, and standard regains the
  Phase 14 report-format block the original port dropped.
- **Codex pass (full Phase 8.7):**
  - The companion script is found by version:
    `ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs | sort -V | tail -1`.
    Today's pinned 1.0.2 path can't run; 1.0.6 is installed.
  - Explicit scope: dirty tree → `--scope working-tree`; clean tree →
    `--scope branch --base <trunk>`; commits plus uncommitted edits → two passes,
    merged. Never `--base` with `working-tree`.
  - Each result is collected with `result <jobId> --json` and checked against the
    scope launched (`target.label`); the scope is recorded in the report.
  - Runtime rules: check `codex --version` before blaming the plugin; relaunch once
    on a config rejection; don't retry on a usage limit (note the reset time); no
    `bd` writes while a pass runs; a reply that isn't JSON is a failed run.
  - Model-neutral wording ("the model configured in your Codex config"); the report
    gains an optional effort field.
- Skill invocations inside the tiers use full names; hotfix-interrupt's trigger
  becomes "Phase 7 bug scan".

### W4 — Router and rules

**Router layout** — the same sections, order and names as the global router:

1. **Intro** — the two lanes, plus the template's repo context in a few bullets: one
   repo and one local beads store; Dolt sync (pull first, push last); beads is the
   only tracker, and any external mirror is downstream; never commit or push to the
   trunk, ship through a PR, with the branch prefixes; Python verification through
   `python-verification-*`; the placeholder note.
2. **Single-Task Routing** — the global rows plus the template's Python rows
   (verification tiers, ruff, pytest, review, export progress, build check).
3. **Epic-Batch Routing** — the rows, the pipeline order, "scope picks the lane,
   not the verb", and the batch hard stops as compact bullets: the unshipped-epic
   check; the budget gate (no model line, and it discloses temporary worktree
   branches); the `exec:<slug>` refusal; spikes never run through execute-plans;
   execute-plans ends at `ex:done`; the EXEC-GATED loop; protected paths stay
   attended; worktree agents need no beads bootstrap.
4. **Never Recommend Shipping an Unfinished Epic.**
5. **Recommending What's Next — Batch Beats Single-Task.**
6. **Sizing Gate — Claude picks the lane** (Lanes A, B, C).
7. **Fan-Out Gate.**
8. **Workflow Rules.**
9. **Named Scope Is Authorization** (template-only).
10. **Verification Before Ship / "Done"** (template-only).
11. **Label Ladders — Append-Only, Furthest Wins.**
12. **Execution Gate.**
13. **Completion Report** (with the Epic Status Table).
14. **Errors & Formatting.**

**What the new governance sections say (generified):**

- **Never recommend shipping an unfinished epic.** "Left" means any open child that
  isn't `ex:done`, any open "Smoke gate:" bead, any deferred, unplanned or
  unstarted child, and any open attended or ops child (a migration apply, a cloud
  console step, a release gate). A smoke that needs the epic's code running
  somewhere is finished by a deploy to that environment — a managed-cloud change, so
  ask first — never by shipping. Shipping opens the integration PR and closes tasks;
  it doesn't deploy anything.
- **Batch beats single-task.** When two or more tasks are available, recommend the
  batch command for the earliest pipeline stage holding two or more of them.
  Recommend beads-start-task only when exactly one task is available. A direct "I'm
  starting X" always routes to beads-start-task.
- **Sizing Gate.**
  - Lane A, TDD-direct: straight to test-first coding, with no plan file,
    refinement or execution gate. All must hold: the cause or shape is known;
    roughly 2–3 production files and about 50 lines; no migration, public API or
    contract change, new dependency or cloud step; no real alternatives; existing
    tests cover the area; finishable this session and reversible.
  - Lane B, plan-lite: write the plan file, then execute, skipping refinement and
    the execution gate. For multi-step work whose approach is settled.
  - Lane C, full: writing-plans → plan-refinement-qa → plan-summary-console →
    Execution Gate. When it touches auth, security, payments or user data; a schema,
    migration or production data; a contract, public API or new dependency; real
    alternatives; more than about 3 files or 150 lines; thin acceptance criteria; or
    when unsure. Ties go to C.
  - Announce the lane in one line with its reason; "plan it" or "just TDD it" from
    the owner always wins; a mid-flight escalation means stop, say so, and switch.
- **Fan-Out Gate.** Assess every multi-task unit before executing it: a shared git
  index (solved by worktree isolation), write-set overlap (derived from each task's
  steps, not only its "Files:" block) and interface dependencies (hard versus
  soft). Group into waves and announce the call in one line. Two checks run rather
  than assumed: each isolated agent's first command is
  `git switch -c <branch> <sha>` at the right base, never `git merge <sha>`, which
  can drag trunk commits in; and `df -h .` caps concurrency, since each worktree is
  a full checkout. Attended tasks are exempt from the fan-out, not from the
  assessment. Budget previews say that a fan-out creates temporary worktree branches
  that get merged back and removed, so approving the gate is the branch approval
  `critical ai agent rule.md` requires.
- **Workflow Rules.**
  - No direct coding after a task starts: run the Sizing Gate.
  - Bug tasks start with systematic debugging.
  - Ready tasks are scoped to the active epic.
  - The router outranks skill-internal handoffs (IMPORTANT, keeping the
    writing-plans warning).
  - In Lane C: refinement, then the plan summary, then the Execution Gate.
  - Post-execution runs after every implementation path: plan execution,
    subagent-driven, the bug path, direct TDD.
  - Ship is atomic, in PR form; the spec lives in `no-direct-push-to-master.md`.
  - Worktrees need no beads bootstrap (`beads.md`).
  - Step tracking: `.beads/.workflow-step` for the single-task lane, labels for the
    batch lane.
  - **One bead-status writer per lane:** start-task sets in progress and ship-task
    closes; in the batch lane execute-plans never writes status and ship-epic makes
    the only transition. Mid-epic, read the `ex:*` labels, not status. There is no
    external-tracker status writer.
- **Label Ladders.** Labels are history: append, never remove; the furthest wins.
  `wp: drafted | carded > refined-rN > applied-rN > approved`;
  `ex: executing > qa:<level> > smoke-pending > done`; `sh: pushed > shipped`.
  `wp:deferred` and `ex:blocked` are flags; `smoke:passed` discharges
  `ex:smoke-pending`. The per-command label table moves here.
- **Execution Gate** adds "Lanes A and B have no Execution Gate".
- **Completion Report.** Done: the Epic Status Table — Task, Name, Description, Plan,
  Wave, Executed, Status — read fresh every time, then what landed. Left: blocked,
  deferred or not reached, never one bucket. Next: full slash commands, `/clear` as
  its own step before the next phase, batch beats single-task.

**Command-side guardrails the router points at:**

- **execute-plans Step 8:** the ship-recommendation gate — ship-epic is named only
  when nothing is left, read fresh this turn; otherwise name the step that finishes
  the work. "Still in force" is defined inline.
- **execute-plans CRITICAL:** never change bead status (`beads:update --status`);
  read back every label write with `beads:show`, retry once serially, then surface
  it; keep bead writes serial; after a fan-out returns, re-read its labels.
- **ship-epic Step 6:** "skip if already closed — execute-plans never touches
  status, so this is the batch lane's only status transition; children reading open
  with `ex:done` before ship is expected."
- **writing-plans Step 6 base-drift guard:** `git switch -c <bucket-branch>
  <epic-head-sha>` instead of `git merge <sha>`; the existing ancestry check and the
  content-level fallback stay as a safety net.
- **Budget previews** in writing-plans, execute-plans and execute-spikes carry the
  temporary-worktree-branch disclosure.

**New rules and skill:**

- **`no-skipping-workflow-steps.md`:** perform every mandated step; pause only for
  an unauthorized destructive action or genuinely conflicting instructions (quote
  both, ask which wins); skip authority comes only from explicit words this turn;
  the Sizing Gate, and planning-sequence's depth axis, is the one standing
  exception; if Claude disagrees, it runs the step and proposes a rule change
  afterwards.
- **`never-ask-about-agent-model.md`:** the model tier is configuration — never in a
  budget gate, an option or a question; tier aliases only, never a versioned id;
  answer plainly if asked.
- **`beads.md`:**
  - Two channels: `bd dolt pull` at the start; `git push` plus `bd dolt push` at
    the close. Pull first, push last; never `--force`.
  - The JSONL export is a readable artifact: flush it with
    `bd export -o .beads/issues.jsonl` after write bursts; never re-track it; never
    auto-import it. The revert story is retold generically.
  - Read back mutating commands, and compare `updated_at` if a verified write later
    looks wrong.
  - Never run two `bd` commands at once — chain them, reads included — and diagnose
    a revert with `bd history <id> --json` and `bd diff`.
  - Worktrees need no bootstrap in embedded mode; never stop the store from inside a
    worktree.
  - `bd doctor` proves nothing; verify with `bd list -n 0 | wc -l` plus the store
    files.
  - Load the troubleshooting skill when a worktree sees `[]` or a lock error.
  - `bd remember` for cross-session knowledge.
- **`skills/beads-worktree-troubleshooting/SKILL.md`:** the global skill, with the
  critical-rule path retargeted and its contention numbers labelled as beads 1.0.4
  observations.
- **`Git Best Practices/no-direct-push-to-master.md`** gains "Ship Is Atomic (PR
  form)": "ship it", "send it", "commit and push" and "create a PR" run the whole
  sequence — stage, commit, push the feature branch, open the PR — never a partial
  subset or a narrowing "push only?" question. One legitimate pause, decided up
  front: a long-lived branch whose work shouldn't be proposed yet. Never force-push
  past a rejected push; never `git checkout HEAD -- .`.
- **`Git Best Practices/Git Best Practices.md`** gains: run `git fetch origin` before
  claiming a branch is ahead or behind; a bare "create a worktree" request ends once
  the worktree exists — no installs, tests or builds until real work starts.

### W5 — Plan depth in the batch commands

- **planning-sequence:** a third classification axis, plan depth — PLAN-FULL,
  PLAN-LITE, TDD-DIRECT — using the Lane C, B and A criteria. Ties go to PLAN-FULL;
  SPIKE-FIRST overrides depth; depth never moves a task between waves. The
  classifier must return `plan_depth` and a `depth_reason` naming the trigger. The
  critic can only promote. The review gate shows a depth column, a
  "n full · n lite · n TDD-direct" line and each TDD-direct task's reason, and the
  owner can re-assign depth. Depth is saved as `depth:full | depth:lite | depth:tdd`
  labels with the reason in the notes, and the sequence file carries it.
  Classifier, synthesis and critic run at medium effort. The heading becomes "Three
  Classification Axes", the Core Principle and description mention depth, and the
  template's tier-alias note stays.
- **writing-plans:**
  - Reads depth and never re-derives it. A task with no depth is treated as
    PLAN-FULL and named in the preview. A clearly wrong depth found while drafting
    → `wp:deferred`, never a silent upgrade.
  - Full → plan plus refinement. Lite → short plan, no refinement. TDD-direct → a
    **task card**: the behaviour change, acceptance criteria, files expected to
    change and the first failing pytest test, at the normal plan path with
    `plan_depth: tdd-direct`, labelled `wp:carded`.
  - Lite plans, task cards and spike plans skip Steps 4–5 and enter Step 6 for the
    approval stamp only.
  - Updated: the step map, Step 0 resume routes, the Step 2 preview (depth mix,
    agent count including refinement agents, effort mix naming each xhigh trigger,
    per-run depth and effort overrides), the Step 3 table and card spec, the label
    lifecycle, the artifacts table and the frontmatter example.
  - **Effort by difficulty:** medium for task cards; high for lite plans, spike plans
    and full plans with no hard trigger; xhigh for full plans touching a sensitive
    area, data or infra, a contract or dependency, the head of a sequential chain,
    or open design. Ties and missing depth go to xhigh.
- **execute-plans:** a task card is executed test-first — write the named failing
  test, watch it fail, implement, stop. Never rebuild a plan from the card.
- **execution-sequence:** its planning-effort wording matches.

### W6 — Beads sync

- **skill-usage:** the sync section and table become `bd dolt pull` at session or
  task start and `bd dolt push` at ship or close, alongside `git pull` and
  `git push` for code.
- **beads-start-task:** `bd dolt pull` before reading beads; the "git pull carries
  beads" default goes.
- **beads-ship-task and workflow-ship-epic, Step 6.5:** `bd dolt push` after the
  code push; the "issues.jsonl in git" branch goes.
- If a project has no Dolt remote yet, the pull and push steps say so in one line
  and continue rather than fail.
- **beads-export-progress:** `issues.jsonl` is a readable export — refresh it with
  `bd export -o .beads/issues.jsonl` before reading.
- **workflow-execution-sequence:** `bd export --no-auto-import` (not a beads 1.0.4
  flag, and without `-o` it writes to stdout) → `bd export -o .beads/issues.jsonl`.
- The router intro and `beads.md` (W4) already carry the same wording; the README
  setup steps (W8) carry the commands.

### W7 — Ship and safety fixes

- **workflow-ship-epic:** opening the PR closes the tasks and epic as before, but
  the epic gets only `sh:pushed`. On a re-run, Step 0 sees `sh:pushed` and checks
  the merge — `gh pr view <url> --json state,mergedAt` first, because squash merges
  break plain ancestry checks, and `git merge-base --is-ancestor` against the
  fetched trunk as the fallback — then adds `sh:shipped`, or reports "PR open,
  awaiting merge" and stops. The ship gate's text says "marked shipped after the PR
  merges". The leftover "integration choice" and "push only" wording from the
  original port goes.
- **`surface-unshipped-epics.md`:** the Rule 1 check also flags a closed epic sitting
  at `sh:pushed` ("PR opened on <date>, not merged"), and Rule 3 is restated with
  the new labels. The check is wired into Step 0 of planning-sequence, writing-plans
  and execute-plans, and execute-plans' final handoff says the epic and its tasks
  stay open until ship-epic runs and count as shipped only once the PR merges.
- **`validate-bash.sh`:** the quick-allow list applies only to a single simple
  command. A command containing `;`, `&&`, `||`, `|`, `$(`, a backtick or a newline
  gets no auto-allow and falls through to the normal permission prompt. The
  dangerous-pattern check runs first, unchanged.

### W8 — README, diagram and `/clear` steps

**The README, rewritten as short as possible:**

1. A two-sentence intro.
2. **Set up (once per project)** — numbered, exact commands:
   1. System tools: `brew install jq gh`, `gh auth login`, and the `bd` CLI with
      `npm install -g @beads/bd` (the workflow is verified with beads 1.0.4).
   2. Plugins, inside Claude Code: `/plugin marketplace add steveyegge/beads`,
      `/plugin install beads@beads-marketplace`,
      `/plugin install superpowers@claude-plugins-official`,
      `/plugin install commit-commands@claude-plugins-official`,
      `/plugin marketplace add openai/codex-plugin-cc`,
      `/plugin install codex@openai-codex`.
   3. Copy the workflow: `cp -rn /path/to/beadspowers-python/.claude/ .claude/`,
      merging an existing `settings.json` by hand.
   4. `chmod +x .claude/hooks/*.sh`.
   5. Beads: `bd init`; `bd config set export.git-add false`; auto-import off;
      `issues.jsonl` added to `.beads/.gitignore` (with `git rm --cached` if it was
      already staged); `bd dolt remote add origin git+https://github.com/<owner>/<repo>.git`.
   6. Find and replace the placeholders, with one `grep` command.
   7. Start a new Claude Code session in the project.
3. **One task** — numbered:
   1. `/beads:ready`
   2. `/workflow-commands:beads-start-task <task-id>` — Claude announces the lane;
      in Lane C it asks the refinement questions and the execution choice.
   3. Verification runs automatically after execution.
   4. `/workflow-commands:beads-ship-task` — opens the PR and closes the bead.
   5. Merge the PR.
   6. `/clear`
4. **An epic** — numbered, with the restored diagram:
   1. `git worktree add ../<project>-<epic> -b feat/<epic-slug>`, then
      `cd ../<project>-<epic> && claude`
   2. `/superpowers:brainstorming` — the approved spec lands in `docs/plans/`.
   3. `/clear`
   4. `/workflow-commands:workflow-planning-sequence --spec docs/plans/<date>-<topic>-design.md`
      — creates the epic; note its id.
   5. `/clear`
   6. `/workflow-commands:workflow-writing-plans <epic-id>`
   7. `/clear`
   8. Only if the epic has spike tasks:
      `/workflow-commands:workflow-execute-spikes <epic-id>`, then `/clear`, then
      `/workflow-commands:workflow-writing-plans <epic-id>` again (it plans the tasks
      the spikes unblocked), then `/clear`.
   9. `/workflow-commands:workflow-execution-sequence <epic-id>`
   10. `/clear`
   11. `/workflow-commands:workflow-execute-plans <epic-id>`
   12. `/clear`
   13. `/workflow-commands:workflow-ship-epic <epic-id>` — opens the PR.
   14. Merge the PR.
   15. `/workflow-commands:workflow-ship-epic <epic-id>` again — confirms the merge
       and marks the epic shipped.
   16. `/clear`

   One line on leftovers: unplanned tasks go back to step 6, unordered ones to
   step 9.

   **Spike order is corrected.** The current README and diagram run spikes *before*
   writing-plans, but execute-spikes only selects spike tasks that are already
   `wp:approved`. The real order is writing-plans → execute-spikes → writing-plans
   again for the unblocked tasks, which is what the router's pipeline already says.
5. One context tip: past roughly 30–50% of the context window mid-phase, ask for a
   handoff doc, `/clear`, and paste it back.
6. **What's inside** — five one-line pointers: rules, commands, agents, skills,
   hooks.

**Removed from the README** (all of it lives in the rules and commands): the
features tour, the trigger-phrase tables, the verification tier and phase tables,
the Architecture Layers section (nothing enforces it once P04 is retired; this
supersedes the earlier "keep it as suggested layering" note), the customization
notes and the long file tree.

**Every README command is verified, not assumed:** the plugin commands against
Claude Code's plugin syntax and the marketplace ids installed on this machine; the
`bd` commands by running the setup sequence in a scratch repo, which also settles
the exact auto-import command; each workflow command's argument form read from its
Input section.

**Batch commands' "Next" lines** show the same `/clear` step before the next phase,
so the commands and the README agree.

**Diagram:** restored from git; step 2 adds plan depth; the spike branch is re-wired
so writing-plans comes first, the "Any SPIKE-FIRST tasks?" decision follows it, and
the spike step loops back to writing-plans; step 6 becomes "PR opened (sh:pushed) →
sh:shipped after merge"; command names in full; the PNG re-exported with the diagram
XML embedded, using the installed draw.io app.

## 7. Deliberate differences from the global files

- PR-only shipping; "ship is atomic" in PR form; no direct merge to the trunk.
- `sh:pushed` at PR open, `sh:shipped` only after a confirmed merge.
- No external-tracker status writer (the global workflow's tracker pull); external
  trackers stay downstream.
- Step 2a also counts the branch's commits and untracked lines; "new files" means
  new modules under `src/`.
- `--force-exclude` on every ruff write; notebooks are report-only; migrations are
  never auto-fixed.
- Formatting stays a scoped write plus a check, with no format hook.
- Phase 12 may create mirrored test files under `tests/`.
- The full tier's Phase 7 section keeps a fallback bug scan.
- Python bug classes, including mutable defaults, since Phase 6 no longer always
  runs.
- Codex: model-neutral wording, the trunk looked up from git, the companion found by
  version.
- Fan-out budget previews disclose temporary worktree branches.
- writing-plans Step 6 uses `git switch -c`, matching the Fan-Out Gate.
- Spike plans are not refined, which resolves an ambiguity in the global version.
- Batch commands' Next lines include `/clear` between phases.
- The router keeps two template-only sections: Named Scope Is Authorization, and
  Verification Before Ship.
- A project with no Dolt remote keeps working; the sync steps say so and continue.

## 8. Left out on purpose

- A local-model profile: concurrency caps, effort ladders, an escalation helper,
  delegation and compaction rules, explicit agent collection.
- Mobile-platform tooling: the simulator and platform toolchain, a forked-plugin lint,
  device rules.
- The external-tracker integration: its status-pull writer, its tool names and its
  quick-sync command.
- User-level paths (`~/.claude/rules/...`).
- The owner's Codex model, quota policy and version floor.
- The direct merge to master in the global ship rule.
- Planning-context and beads-import-prd, which were removed from the template
  earlier on purpose.
- Tool names in `tdd-test-writer` for an MCP server the template doesn't use, a
  personal gitignore-audit skill reference, and a per-file formatting hook.
- The owner's personal `CLAUDE.md` preferences.
- Owner-project bead ids, dates and incident specifics (retold generically).
- The push-to-master hook patterns and deny rules removed from the template in
  April stay removed.

## 9. Problems found in the global files (for the owner; not changed here)

- execute-plans: the Step 2 preview says "or 2" on the local profile, while
  elsewhere it is 3. Its read-back rationale ("bd printed ✓ Updated on a write it
  didn't keep") contradicts the later `beads.md` diagnosis. Whitespace leftover:
  "frontier.  On a local".
- execute-spikes: a local-profile effort bullet with no mechanism behind it; stray
  blank lines in Model & Budget.
- writing-plans: the label-lifecycle block lacks `wp:carded` and says deferred tasks
  re-enter at `wp:drafted` (wrong for task cards); the artifacts table and the
  Step 3 frontmatter example don't mention task cards; Step 3's heading still says
  "(conditional)"; Step 6 uses `git merge <sha>`, which the router's Fan-Out Gate
  forbids; "Sonnet-5-medium" is a pinned name.
- planning-sequence: the Core Principle still says "two axes"; the description
  doesn't mention depth; the tier-alias note the template has is missing.
- execution-sequence: `bd export --no-auto-import` isn't a beads 1.0.4 flag, and
  without `-o` it writes to stdout.
- flutter-verification-full: the bug scan moved into the agent brief but not into
  the Phase 7 section, so the in-context fallback loses it; Phase 9's source list
  still says "bug scan"; the diagram says "3" agent invocations; Phase 11 points at
  "Step 8's dart fix loop" (it is Phase 2 Step 3).
- flutter-verification-quick: its Notes still mention architecture validation.
- hotfix-interrupt: still triggers on a "Phase 3 Bug Scan".
- beads-post-execution: Step 2a misses committed work on the branch and untracked
  line counts; "new files → full" counts test files; its trigger paragraph is
  narrower than the template's; its Named Scope citation points at a project file.

## 10. Delivery

- **Branch:** `chore/sync-global-workflow-2026-10`, created from master.
- **Tracking:** `bd init --stealth` — a beads store excluded through
  `.git/info/exclude`, so nothing reaches the public template — holding one epic
  with a child task per workstream (W1–W8).
- **Commits:** this spec, then the implementation plan, then one commit per
  workstream in W1–W8 order. The router is written once, in W4, which is why it
  lands before the plan-depth commands in W5. The PR is consistent as a whole, and
  the reference sweep runs on the final tree.
- **Execution mode:** sequential, with a review between workstreams. Fan-out is not
  viable: the README, the router, ship-epic, execute-plans and the verification tiers
  are each edited by three or more workstreams.
- **Ship:** `/workflow-commands:beads-ship-task` — one PR to master.
- **Sync marker:** the PR description records "synced with the global workflow as of
  2026-10-02". Offered separately, and only with the owner's OK because it is
  outside the repo: a snapshot of today's global workflow files under
  `~/.claude/backups/`, as the exact base for the next sync.

## 11. Verification

**Behaviour checks** (scratch git repo, nothing pushed):

- **Step 2a:** a repo with committed, staged, unstaged, untracked and deleted
  changes yields exactly the expected file list and line count, and the other
  session-state keys survive.
- **The ruff sequence:** with a vendored file excluded in `pyproject.toml` and named
  on the command line, `--force-exclude` leaves it untouched; a deliberately leaked
  change is caught and reverted.
- **Phase 6 gate:** a new class in `src/` triggers it; a new test class doesn't.
- **Codex companion lookup** resolves the installed version (no review launched).
- **validate-bash.sh**, fed hook JSON: `ls -la` → allow; `cd x && git reset --hard`,
  `echo hi; rm f` and `cat a | sh` → no decision (falls through); `rm -rf /` → ask.
- **README setup:** the beads init and config commands run in a scratch repo and
  produce the expected config and git status.

**Reference sweep** (final tree):

- Every `workflow-commands:<name>`, rule path, skill name and router section name
  mentioned under `.claude/` and in the README exists.
- No bare `/workflow-` command names remain.
- No leaks: `Flutter`, `Dart`, `dart `, `Jira` (outside generic tracker examples),
  `127.0.0.1`, `~/.claude/rules`, versioned model ids, and the owner's private terms —
  project names, bead-id prefixes, model and host settings — which live outside the
  repo, in the owner's private notes, and are read by the checks at run time.
- No mention of P04, P05 or a phase count in the tiers.

**Router preservation checklist** — each template-only item of the old router is
found in the new one:

- [ ] Repo context: one repo and store, no `bd repo sync`; the sync channels; beads
      as the only tracker with any mirror downstream; never the trunk, with the
      branch prefixes; Python verification and `src/<your_package>/`; the
      placeholder note.
- [ ] The two-lane summary (scope, refinement, execution, spikes, ship, resume
      state).
- [ ] Router overrides skill handoffs, with the writing-plans warning.
- [ ] No direct coding after a task starts.
- [ ] Systematic debugging for bug tasks, with its skip phrases and the verification
      close.
- [ ] Worktree beads notes (`bd doctor` is a no-op; never stop the store from a
      worktree) — now in `beads.md`.
- [ ] Ready tasks scoped to the current epic.
- [ ] Every single-task route, including the Python ones, and the PR-policy note.
- [ ] Every epic-batch route; mode disambiguation.
- [ ] The pipeline order and its eight hard stops.
- [ ] Step tracking and the label table.
- [ ] Named scope is authorization, with its examples and still-confirm list
      (including branch creation and paid API calls).
- [ ] Plan refinement before execution: the failure-mode warning, skip phrases, and
      "one methodology, two modes".
- [ ] The plan-summary auto-invoke: bypass phrases, manual triggers.
- [ ] The post-execution auto-invoke on every path, with the no-substitution rule.
- [ ] Verification before ship: the marker, the label, the bypass phrases.
- [ ] The Execution Gate with its batch note.
- [ ] Error handling and response formatting.

**Workflow gate:** beads-post-execution and the python-verification skill it
selects, run as the rules require. The template has no Python code, so that skill
has little to check; its report says so plainly, and the checks above are the real
evidence.

## 12. Size

Roughly 1,800–2,000 lines touched across 36 files, plus the two deletions (about
270 lines). The router ends near 520–560 lines; the README shrinks to roughly a
quarter of its current length.
