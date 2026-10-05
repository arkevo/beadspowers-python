# Sync the Global Workflow Updates into the Python Template — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring this template level with the owner's global workflow as of 2026-10-02, translated to Python and to project-agnostic wording, without losing anything the template does on purpose, and leave a clean baseline for the next sync.

**Architecture:** Eight workstreams (W1–W8), each one task and one commit, applied strictly in order to the template's markdown commands, rules and agents, one bash hook, the README and the process diagram, on the existing branch `chore/sync-global-workflow-2026-10`. Most of the "code" is runnable bash inside markdown, so every piece of it that decides something (the changed set, the scoped ruff writes, the Phase 6 gate, the Codex companion lookup, the Dolt pull guard, the bash hook and the README setup) gets a behaviour check that pulls the bash out of the file and runs it in a scratch repo. Task 0 sets up tracking; Task 9 sweeps the final tree for dangling references and leaks, runs the verification gate and ships one PR.

**Tech Stack:** Markdown commands, rules, agents and skills for Claude Code; bash and zsh; git and `gh`; beads `bd` 1.0.4 (embedded Dolt); ruff 0.11.11, mypy and pytest; `jq`; the Codex companion from the openai-codex plugin (1.0.6 installed); the draw.io desktop app's command line.

**Spec:** `docs/plans/2026-10-02-sync-global-workflow-design.md`. Read it alongside this plan: every task cites the spec section it implements, and the spec's §7 (deliberate differences) and §8 (left out on purpose) bind every task.

**Lane:** C, the full lane — 36 files and roughly 2,000 lines, including the router and workflow contracts.
**Fan-out:** not viable — the README, the router, ship-epic, execute-plans and the verification tiers are each edited by three or more tasks, so the tasks run one after another, in order, with a review between them (spec §10).

## Global Constraints

- Branch: `chore/sync-global-workflow-2026-10` (exists and is checked out). Nothing is committed or pushed to `master`; the work reaches `master` through one pull request opened in Task 9 (project rule `Git Best Practices/no-direct-push-to-master.md`; spec §10). The owner's global direct-to-master ship sequence does not apply in this repo.
- Commit sequence: the spec (already committed), this plan (Task 0), then exactly one commit per workstream, W1 to W8, in Tasks 1 to 8. Task 9 adds a commit only if its sweep finds something to fix.
- Stage explicit, quoted paths only — several paths contain spaces (`0_Beads x Superpowers/`, `Git Best Practices/`, `critical ai agent rule.md`). Bracketed file names (`P02-lint-issues-fix-[QSF].md`, `P14-security-review-[SF].md`, …) are glob character classes to git, so stage them with the `:(literal)` prefix: `git add -- ':(literal).claude/Commands/workflow-commands/P14-security-review-[SF].md'`. Never `git add -A`. Never stage anything under `.claude/worktrees/` (a local worktree folder; it shows in `git status` only while it holds a worktree). The only deletions in this PR are `P04-architecture-validation-[SF].md` and `P05-code-simplification-[SF].md` (Task 3).
- Every commit message ends with the attribution trailer lines (`Co-Authored-By: …`, `Claude-Session: …`) from the executing session's system reminder. The commit heredocs below end with the line `<attribution trailer>`; replace it with those lines.
- Carry only what changed in the global files since the base, plus the approved side fixes; everything else in the template stays as it is (spec §4.1). Translate, don't copy: Flutter tooling becomes ruff, mypy, pytest and `python -m build`; owner-project names, bead ids and dates become generic wording; incidents are retold as "observed in a downstream project" (spec §4.2).
- Leave out everything in spec §8 and keep every deliberate difference in spec §7.
- Naming: a command a reader might paste is written `/workflow-commands:<name>`; prose naming a skill is written `workflow-commands:<name>`.
- Model choice is configuration: tier aliases only (`opus`, `sonnet`, `haiku`), never a versioned id, and never a `Model:` line in a budget gate. Cost is shown as "% of the 5-hr usage limit".
- Verified on 2026-10-02 against: bd 1.0.4, ruff 0.11.11, the Codex companion 1.0.6 (found by version sort, never pinned), draw.io desktop at `/Applications/draw.io.app`.
- Beads 1.0.4 facts this plan relies on: `bd config set` rejects `no-auto-import`, so the key is appended with `printf '\nno-auto-import: true\n' >> .beads/config.yaml` (the leading newline matters, because `bd config set` leaves the file without a trailing newline) — and beads 1.0.4 does not read the key at all; it mirrors the owner's setup, and what actually prevents stale-export reverts is keeping `.beads/issues.jsonl` untracked. `bd dolt pull` exits 1 when no Dolt remote exists, while `bd dolt push` prints "No remote is configured — skipping." and exits 0. A plain `bd init` commits its own files to the current branch; `bd init --stealth` commits nothing.
- Beads in this repo is a stealth store (`bd init --stealth`, spec §10): `.beads/` is excluded through `.git/info/exclude` and is already ignored by `.gitignore`, so nothing in it is ever committed.
- Never run two `bd` commands at the same time: chain a step's `bd` calls in one Bash call, and read every write back with `bd show`.
- Untouched (spec §5): P06, P07, P08, P11.5, P12, `tdd-test-writer`, `references/refinement-methodology.md`, the comment-analyzer, test-coverage and type-analyzer agents, `write-safety.sh`, `settings.json`, `critical ai agent rule.md`, `beads-plugin-cli-only.md`, `bug-must-have-epic.md`, `protect_plans_and_commit_all.md`.
- Create every check script with the **Write tool**, never with a shell heredoc, and keep `rm` out of Bash steps. A user-level PreToolUse hook can rewrite shell commands before they run, heredoc bodies included (one common hook turns `rm` into a move to the Trash), so a heredoc could silently change a script, and a rewritten `rm -f` on a missing file would fail and break an `&&` chain.
- Private names stay out of everything this plan writes or publishes: this plan, the spec, the template, commit messages and the PR (the template repo is public). The two leak checks — `check-router.sh` (Task 4) and `check-references.sh` (Task 9) — read the owner's private terms at run time from `$CHECKS/private-terms.txt`, one extended regex per line, which Task 0 Step 7 writes from the owner's private memory note `private-leak-terms`. Both checks fail if that file is missing or empty. Never copy its contents into the repo.
- Behaviour checks live outside the repo in `$CHECKS`, which is the executing session's scratchpad directory plus `/sgw-checks`. Shell state does not carry between Bash calls, so steps write `CHECKS="<scratchpad>/sgw-checks"`; substitute the absolute scratchpad path from your system prompt. Checks are never committed. If a new session finds a check missing, re-run the step that writes it (Task 9 Step 2 lists them).
- Size targets (spec §12): the router ends near 520–560 lines; the README shrinks to roughly a quarter of its current 374 lines.
- No file outside the repo changes, except the optional snapshot under `~/.claude/backups/` in Task 0 Step 8, and only with the owner's yes.

## Review Focus

The spec says what the workflow must do; these are the inputs it doesn't mention that are most likely to bite someone using the template. Each has a test in the task that owns the code.

1. **A changed set with no Python files left after filtering** (a docs-only change, or only notebooks, migrations or vendored files). A reasonable person expects verification to skip the auto-fix and say so. The danger is that `ruff check --fix` with no paths rewrites the whole project, which is the exact failure the write-scope rule exists to prevent. Test: Task 2, `check-ruff-scope.sh` (docs-only case).
2. **Paths with spaces** — this template's own rule folders have them. A reasonable person expects such a file to be recorded intact in `modified_files`, fixed as one argument, and reverted correctly by the leak check. Test: Task 2, both checks.
3. **No `origin` remote, an unset `origin/HEAD`, or a trunk called `main`** (a brand-new local project, or a GitHub default branch of `main`). A reasonable person expects Step 2a to still record uncommitted and untracked files and say the branch range was skipped, and the trunk lookup to find `origin/main`. Test: Task 2, `check-changed-set.sh`; Task 3, `check-phase6-gate.sh`.
4. **Renames and deletions in the changed set.** A reasonable person expects deleted paths to be left out and a renamed file to be recorded under its new path only. Test: Task 2, `check-changed-set.sh`.
5. **Compound shell commands that start with an auto-allowed word.** Today `ls && git push --force`, `echo hi; rm f`, `ls & rm -rf build` and `echo hi > notes.txt` are all auto-approved because their first word is on the hook's quick-allow list. A reasonable person expects any command that chains, pipes, substitutes, backgrounds or redirects to lose that automatic approval and fall through to the normal permission prompt, a command containing a dangerous pattern (`ls; rm -rf /`) to still be asked about, and a single simple command (`ls -la`) to stay auto-approved. Test: Task 7, `check-validate-bash.sh`.

## How to read the steps

- Each edit step names one file and one operation: **replace section** (from one heading up to, not including, the next named heading), **replace passage** (quoted first and last words), **delete**, **insert after** an exact line, **create** a whole file, or **run** a command with its expected output. Anchors are headings or text no earlier task changes — never line numbers, because every task shifts lines.
- New text inside a 4-backtick (````) fence contains its own ``` fences; copy everything between the outer fences.
- A bash block that a check executes starts with the marker line `# snippet: <name>`. The marker is part of the file's content; keep it.
- Bead ids live in `.beads/sgw-ids.env` (written in Task 0): `source .beads/sgw-ids.env` gives `$EPIC` and `$W1` to `$W8`. Each workstream bead goes `in_progress` when its task starts and gets a "Landed in <sha>" note when its commit lands; all of them close together when the PR opens in Task 9 (the single-task lane's only status writers are start and ship).
- Resuming in a new session: `git log --oneline master..HEAD` shows which workstream commits exist; the next task is the first one without its commit.

## Files Touched, by Task

| File | Tasks |
|---|---|
| `.claude/Commands/workflow-commands/workflow-planning-sequence.md` | 1, 5, 7, 8 |
| `.claude/Commands/workflow-commands/workflow-writing-plans.md` | 1, 4, 5, 7, 8 |
| `.claude/Commands/workflow-commands/workflow-execute-spikes.md` | 1, 4, 8 |
| `.claude/Commands/workflow-commands/workflow-execution-sequence.md` | 1, 5, 6, 8 |
| `.claude/Commands/workflow-commands/workflow-execute-plans.md` | 1, 4, 5, 7, 8 |
| `.claude/Commands/workflow-commands/workflow-ship-epic.md` | 1, 4, 6, 7, 8 |
| `.claude/Commands/workflow-commands/beads-post-execution.md` | 1, 2, 4 |
| `.claude/Commands/workflow-commands/beads-start-task.md` | 4, 6 |
| `.claude/Commands/workflow-commands/beads-ship-task.md` | 1, 4, 6 |
| `.claude/Commands/workflow-commands/beads-export-progress.md` | 6 |
| `.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md` | 1, 2 |
| `.claude/Commands/workflow-commands/P03-code-review-checks-[SF].md` | 1 |
| `.claude/Commands/workflow-commands/P14-security-review-[SF].md` | 2, 3 |
| `.claude/Commands/workflow-commands/plan-refinement-qa.md`, `plan-summary-console.md` | 1 (and 4 for the refinement citation) |
| `.claude/Commands/workflow-commands/hotfix-interrupt.md` | 3 |
| `.claude/Commands/workflow-commands/python-verification-quick.md`, `-standard.md`, `-full.md` | 1, 2, 3, 4 |
| `.claude/Commands/workflow-commands/P04-architecture-validation-[SF].md`, `P05-code-simplification-[SF].md` | 3 (deleted) |
| `.claude/agents/verification-silent-failure.md` | 3 |
| `.claude/rules/0_Beads x Superpowers/beads-workflow-router.md` | 1, 4 (rewritten) |
| `.claude/rules/0_Beads x Superpowers/skill-usage.md` | 6 |
| `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md` | 1, 7 |
| `.claude/rules/0_Beads x Superpowers/beads.md`, `no-skipping-workflow-steps.md`, `never-ask-about-agent-model.md` | 4 (new) |
| `.claude/rules/verification-write-scope.md` | 2 (new) |
| `.claude/skills/beads-worktree-troubleshooting/SKILL.md` | 4 (new) |
| `.claude/rules/Git Best Practices/Git Best Practices.md` | 4 |
| `.claude/rules/Git Best Practices/no-direct-push-to-master.md` | 1, 4 |
| `.claude/hooks/validate-bash.sh` | 7 |
| `README.md` | 1, 8 (rewritten) |
| `docs/workflow-process-flow.drawio`, `.png` | 0 (restored), 8 |

---

### Task 0: Tracking, a clean start, and the plan commit

Spec: §3 decisions 3 and 5, §10 (tracking, commits, sync marker).

**Files:**
- Restore: `docs/workflow-process-flow.drawio`, `docs/workflow-process-flow.drawio.png` (deleted in the working tree; restored unchanged from `HEAD` here, updated in Task 8)
- Create (local only, never committed): the stealth beads store under `.beads/`, including `.beads/sgw-ids.env`, `.beads/.session-state.json`, `.beads/.workflow-step`
- Commit: `docs/plans/2026-10-02-sync-global-workflow.md` (this plan)

**Interfaces:**
- Consumes: nothing.
- Produces: `.beads/sgw-ids.env` defining `EPIC` and `W1`…`W8` (one bead per workstream); `.beads/.session-state.json` with `task_id` = the epic id and `plan_file` = this plan; `.beads/.workflow-step` = `Starting Work`; the `$CHECKS` directory every later task writes its checks into.

- [ ] **Step 1: Confirm the starting state**

Run:
```bash
git rev-parse --abbrev-ref HEAD && git status --short && git log -1 --format=%s
```
Expected:
```
chore/sync-global-workflow-2026-10
 D docs/workflow-process-flow.drawio
 D docs/workflow-process-flow.drawio.png
?? docs/plans/2026-10-02-sync-global-workflow.md
docs(plans): design for syncing the global workflow updates into the template
```
A `?? .claude/worktrees/` line may also appear when that local folder holds a worktree; it is never staged. If any other line appears, stop and ask the owner what it is. Do not stage, restore or delete it.

- [ ] **Step 2: Restore the process diagram from git**

The spec restores the deleted diagram and updates it (decision 5); Task 8 does the update. Restoring it now means no later `git add` can pick up the deletions by accident.

Run:
```bash
git restore docs/workflow-process-flow.drawio docs/workflow-process-flow.drawio.png && git status --short && ls -l docs/workflow-process-flow.drawio docs/workflow-process-flow.drawio.png
```
Expected: the two ` D` lines are gone; the files are 19132 and 603463 bytes.

- [ ] **Step 3: Initialise the stealth beads store the way the owner's setup works**

Mirror the owner's beads setup (spec §3 decision 3): the export is never auto-staged, and `no-auto-import: true` sits in `config.yaml`. Beads 1.0.4 does not actually read that key; what protects a store from stale-export reverts is an untracked export, and stealth mode already keeps the whole `.beads/` folder out of git. Stealth mode also keeps the store out of the public template, and unlike a plain `bd init` it makes no commits.

Run:
```bash
bd init --stealth -p bpy --non-interactive && bd config set export.git-add false && printf '\nno-auto-import: true\n' >> .beads/config.yaml && cat .beads/config.yaml && grep -v '^#' .git/info/exclude && git status --short
```
Expected `config.yaml`:
```
no-git-ops: true

export.git-add: false
no-auto-import: true
```
Expected in `.git/info/exclude`: `.beads/` and `.claude/settings.local.json`. `git status --short` shows the same lines as after Step 2, possibly plus ` M .gitignore`; `git log -1 --format=%s` still shows the spec commit.

- [ ] **Step 4: Undo `bd init`'s edit to the root `.gitignore`, if it made one**

`bd init` appends `.dolt/`, `*.db` and `.beads-credential-key` to the root `.gitignore`. This repo's `.gitignore` already ignores all three, and `.beads/` too, so the edit is noise that must not reach the PR.

Run:
```bash
git diff -- .gitignore
```
If the diff only adds lines from this set — `# Beads / Dolt files (added by bd init)`, `.dolt/`, `*.db`, `.beads-credential-key`, blank lines — run `git restore .gitignore`. If it shows anything else, stop and ask the owner.

Then run `git status --short`. Expected: only `?? docs/plans/2026-10-02-sync-global-workflow.md` (plus `?? .claude/worktrees/` if that folder holds a worktree).

- [ ] **Step 5: Create the epic and one bead per workstream, and record their ids**

The beads are not chained by dependencies on purpose: every workstream bead stays `in_progress` until the single ship in Task 9, so a dependency chain would hide every later workstream from `bd ready`.

Run (one Bash call — the `bd` commands run serially in it):
```bash
EPIC=$(bd create "Sync the global workflow updates into the Python template" -t epic -p 1 --silent -d "Spec: docs/plans/2026-10-02-sync-global-workflow-design.md. Plan: docs/plans/2026-10-02-sync-global-workflow.md. One bead per workstream (W1-W8), one commit each, shipped as one PR.") && \
W1=$(bd create "W1 — Naming sweep and stale references" -t task -p 1 --parent "$EPIC" --silent -d "Plan Task 1; spec §6 W1.") && \
W2=$(bd create "W2 — Verification only rewrites what the task changed" -t task -p 1 --parent "$EPIC" --silent -d "Plan Task 2; spec §6 W2.") && \
W3=$(bd create "W3 — Trim verification and fix the Codex pass" -t task -p 1 --parent "$EPIC" --silent -d "Plan Task 3; spec §6 W3.") && \
W4=$(bd create "W4 — Router and rules" -t task -p 1 --parent "$EPIC" --silent -d "Plan Task 4; spec §6 W4.") && \
W5=$(bd create "W5 — Plan depth in the batch commands" -t task -p 1 --parent "$EPIC" --silent -d "Plan Task 5; spec §6 W5.") && \
W6=$(bd create "W6 — Beads sync" -t task -p 1 --parent "$EPIC" --silent -d "Plan Task 6; spec §6 W6.") && \
W7=$(bd create "W7 — Ship and safety fixes" -t task -p 1 --parent "$EPIC" --silent -d "Plan Task 7; spec §6 W7.") && \
W8=$(bd create "W8 — README, diagram and /clear steps" -t task -p 1 --parent "$EPIC" --silent -d "Plan Task 8; spec §6 W8.") && \
printf 'EPIC=%s\nW1=%s\nW2=%s\nW3=%s\nW4=%s\nW5=%s\nW6=%s\nW7=%s\nW8=%s\n' "$EPIC" "$W1" "$W2" "$W3" "$W4" "$W5" "$W6" "$W7" "$W8" > .beads/sgw-ids.env && \
cat .beads/sgw-ids.env
```
Expected: nine lines, `EPIC=bpy-…` then `W1=bpy-…` to `W8=bpy-…`, all different ids.

- [ ] **Step 6: Mark the epic in progress, set up session state, and read everything back**

Run:
```bash
source .beads/sgw-ids.env && bd update "$EPIC" --status in_progress && bd list --parent "$EPIC" --all -n 0 && bd show "$EPIC" | head -8 && \
{ cat .beads/.session-state.json 2>/dev/null || echo '{}'; } | jq --arg id "$EPIC" '. + {task_id: $id, task_requirements: "docs/plans/2026-10-02-sync-global-workflow-design.md", plan_created: true, plan_file: "docs/plans/2026-10-02-sync-global-workflow.md", modified_files: [], total_lines_changed: 0}' > .beads/.session-state.json.new && \
mv .beads/.session-state.json.new .beads/.session-state.json && \
echo "Starting Work" > .beads/.workflow-step && cat .beads/.session-state.json
```
<!-- Refined: Data Flow -->
Expected: eight child beads listed as `open`; the epic shows `IN_PROGRESS`; the session state prints with `task_id` equal to `$EPIC`, and keeps the `plan_refinement` block that plan refinement wrote before this task (the merge never overwrites other keys).

- [ ] **Step 7: Create the check directory and the private term list**

Run:
```bash
CHECKS="<scratchpad>/sgw-checks"; mkdir -p "$CHECKS" && ls -ld "$CHECKS"
```
Expected: one `drwx…` line for the directory.

Then create `<scratchpad>/sgw-checks/private-terms.txt` with the Write tool: copy the extended regexes listed in the owner's private memory note `private-leak-terms` (in your Claude memory, outside the repo), one per line. The leak checks in Task 4 and Task 9 read this file and fail if it is missing or empty. If the note is not in your memory, ask the owner for the list. Never copy these terms into the repo, a commit message or the PR. A new session re-creates the file the same way.

Run (it prints a count, never the terms):
```bash
CHECKS="<scratchpad>/sgw-checks"; test -s "$CHECKS/private-terms.txt" && echo "private terms: $(grep -c . "$CHECKS/private-terms.txt") patterns"
```
Expected: `private terms: N patterns`, with N at least 1.

- [ ] **Step 8: Offer the snapshot of today's global workflow (outside the repo — ask first)**

Spec §10 offers a snapshot of the global workflow files as the exact base for the next sync. It is outside the repo, so it happens only on the owner's explicit yes. At plan refinement (2026-10-02, 08:04 UTC) no global file had changed since the spec was written. <!-- Refined: File Organization --> It is only the exact base if the global files have not changed since the spec was written, so check that first:
```bash
find ~/.claude/commands/workflow-commands ~/.claude/rules ~/.claude/agents ~/.claude/skills/beads-worktree-troubleshooting -type f -not -name '*.bak*' -newer docs/plans/2026-10-02-sync-global-workflow-design.md
```
- No output → ask: "Snapshot today's global workflow files to `~/.claude/backups/global-workflow-2026-10-02/` as the exact base for the next sync? It writes outside this repo." On yes, run:
  ```bash
  D=~/.claude/backups/global-workflow-2026-10-02 && mkdir -p "$D/rules" "$D/skills" && rsync -a --exclude '*.bak*' ~/.claude/commands/workflow-commands ~/.claude/agents "$D/" && rsync -a --exclude '*.bak*' ~/.claude/rules/ "$D/rules/" && rsync -a ~/.claude/skills/beads-worktree-troubleshooting "$D/skills/" && find "$D" -type f | wc -l
  ```
  Expected: a file count of about 40.
- Any output → tell the owner which global files changed after the spec was written, and that a snapshot taken now would not be the exact base; take it only if they still want it.

- [ ] **Step 9: Commit the plan**

Run:
```bash
git add docs/plans/2026-10-02-sync-global-workflow.md && git diff --cached --stat && git commit -F- <<'EOF'
docs(plans): implementation plan for syncing the global workflow updates

Ten tasks: tracking, one task and one commit per workstream (W1-W8), and a
final reference sweep, verification gate and ship.

<attribution trailer>
EOF
```
Expected: `1 file changed`, then the commit summary line.

---

### Task 1: W1 — Naming sweep and stale references

Spec: §6 W1.

**Files:**
- Modify (scripted sweep, 17 files): `README.md`; in `.claude/Commands/workflow-commands/`: `beads-post-execution.md`, `beads-ship-task.md`, `plan-refinement-qa.md`, `plan-summary-console.md`, `python-verification-full.md`, `python-verification-quick.md`, `python-verification-standard.md`, `workflow-execute-plans.md`, `workflow-execute-spikes.md`, `workflow-execution-sequence.md`, `workflow-planning-sequence.md`, `workflow-ship-epic.md`, `workflow-writing-plans.md`; `.claude/rules/0_Beads x Superpowers/beads-workflow-router.md`, `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md`, `.claude/rules/Git Best Practices/no-direct-push-to-master.md` — every unqualified command reference gets its namespace.
- Modify (explicit edits): `.claude/Commands/workflow-commands/P03-code-review-checks-[SF].md` (nonexistent `/python-code-review`), `.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md` (nonexistent `lint_rules/`), plus stale references in `workflow-writing-plans.md`, `workflow-execution-sequence.md`, `workflow-execute-plans.md`, `workflow-execute-spikes.md` and `python-verification-full.md` (already in the sweep list).
- Not committed: `$CHECKS/check-w1-names.sh` (Task 9 re-runs it on the final tree) and `$CHECKS/w1-sweep.py` (a one-off tool).
- Total: 19 files modified, 208 lines changed each way; nothing created or deleted in the repo.

**Interfaces:**
- Consumes: Task 0's tree — diagram files restored, plan committed, the only untracked entry `.claude/worktrees/` (never staged).
- Produces: the naming every later task writes in — a command a reader might paste is `/workflow-commands:<name>`, prose naming a skill is `workflow-commands:<name>`. Later tasks' anchors that this task changes: the three `| Budget shown as |` rows now read `**% of the 5-hr usage limit**`; `workflow-writing-plans.md` says "sonnet / medium" in Step 6 and in its CRITICAL block, and cites `protect_plans_and_commit_all.md` (Rule 1 in the intro, Rule 2 under Artifacts); `workflow-execution-sequence.md` Step 5 says "**expensive Opus planning workflows**". The check `check-w1-names.sh`, which must still pass after Tasks 2–8: any task that rewrites one of these passages keeps the new wording, and all new text uses full names.

**What the sweep deliberately leaves alone** (each was checked by hand on 2026-10-02):

- The files the spec marks untouched (§5). Two of them mention commands bare on purpose and stay as they are: `.claude/rules/critical ai agent rule.md` ("e.g. `beads-start-task`") and `.claude/Commands/workflow-commands/references/refinement-methodology.md` (four adapter names). The script skips every file on the untouched list.
- `.claude/rules/0_Beads x Superpowers/skill-usage.md`: its "Wrong | Correct" table shows the bare name as the wrong form, and its namespace table lists each namespace's skills without the prefix. Both are deliberate. (Task 6 edits this file's sync section.)
- Already-qualified skill references such as "Invoke `workflow-commands:beads-ship-task`" (50 of them): they are skill invocations, so they correctly carry no leading slash.
- File paths (`.claude/Commands/workflow-commands/<name>.md`), frontmatter `name:` keys, and words that merely contain a name ("hotfix-interrupted").
- Informal nicknames such as `execute-plans`, `writing-plans` or `ship-epic` (14 backticked uses): shorthand, not skill names, the same as in the owner's global files.
- "GPT-5.4" in the full tier's Codex phase: Task 3 rewrites that phase in model-neutral wording and anchors on its current headings.
- `claude-opus-4-8`, `"opus-4.8"` and "Opus 4.8" in the tier-alias notes of `workflow-writing-plans.md` and `workflow-execute-plans.md`: those notes warn against pinned ids, so they are not pins.
- `docs/plans/`: permanent history, never swept.

- [ ] **Start: mark the W1 bead in progress**

```bash
source .beads/sgw-ids.env && bd update "$W1" --status in_progress && bd show "$W1" | head -6
```
Expected: the bead shows `IN_PROGRESS`. (If `.beads/sgw-ids.env` is missing, Task 0 has not run.)

- [ ] **Step 1: Write the failing check**

The check asserts that no command is referenced without its namespace and that each stale reference this task fixes stays fixed. It deliberately asserts "nothing bare remains" rather than exact router or README lines, because Tasks 4 and 8 rewrite those files; Task 9 re-runs it on the final tree. Create `<scratchpad>/sgw-checks/check-w1-names.sh` with the Write tool, not a shell heredoc (see Global Constraints), with exactly this content:

````bash
#!/usr/bin/env bash
# check-w1-names.sh <repo-root>
# Task 1 (W1) check: every workflow-commands reference carries its namespace,
# and the stale references W1 fixes stay fixed. Re-run by Task 9 on the final tree.
set -u
repo="${1:?usage: check-w1-names.sh <repo-root>}"
cd "$repo" || exit 2
fail=0
pass() { echo "PASS: $1"; }
flunk() { echo "FAIL: $1"; fail=1; }

# Scan with python3: regex lookbehind is needed and macOS grep has no -P.
scan_out=$(python3 - <<'PY'
import os, re
root = "."
cmd_dir = os.path.join(root, ".claude", "Commands", "workflow-commands")
names = sorted((f[:-3] for f in os.listdir(cmd_dir) if f.endswith(".md")), key=len, reverse=True)
alt = "|".join(re.escape(n) for n in names)
slash = re.compile(r"(?<![\w.:/\-])/(" + alt + r")(?![\w\-\[])(?!\.md)")
tick = re.compile(r"`(" + alt + r")`")
# Files whose bare names are deliberate: the spec leaves two of them untouched,
# and skill-usage.md's tables show bare names on purpose.
tick_ok = {
    ".claude/rules/critical ai agent rule.md",
    ".claude/rules/0_Beads x Superpowers/skill-usage.md",
    ".claude/Commands/workflow-commands/references/refinement-methodology.md",
}
files = ["README.md"]
for dp, dn, fn in os.walk(os.path.join(root, ".claude")):
    dn[:] = [d for d in dn if d != "worktrees"]
    files += [os.path.relpath(os.path.join(dp, f), root) for f in fn if f.endswith((".md", ".sh", ".json"))]
for rel in sorted(files):
    if not os.path.exists(rel):
        continue
    for i, line in enumerate(open(rel, encoding="utf-8"), 1):
        # The router's Completion Report shows the wrong form on purpose
        # ("never a bare `/workflow-execute-plans`"), like skill-usage.md's "Wrong" column.
        if "never a bare" not in line:
            for m in slash.finditer(line):
                print(f"SLASH\t{rel}:{i}\t/{m.group(1)}")
        if rel not in tick_ok:
            for m in tick.finditer(line):
                print(f"TICK\t{rel}:{i}\t`{m.group(1)}`")
PY
)

n_slash=$(printf '%s\n' "$scan_out" | grep -c '^SLASH' || true)
n_tick=$(printf '%s\n' "$scan_out" | grep -c '^TICK' || true)
if [ "$n_slash" -eq 0 ]; then pass "no bare /<command> names"
else flunk "$n_slash bare /<command> names, first: $(printf '%s\n' "$scan_out" | grep '^SLASH' | head -1 | cut -f2-)"; fi
if [ "$n_tick" -eq 0 ]; then pass "no bare backticked command names"
else flunk "$n_tick bare backticked command names, first: $(printf '%s\n' "$scan_out" | grep '^TICK' | head -1 | cut -f2-)"; fi

# Plain-text assertions over the same file set (README + .claude/, minus worktrees).
search() { grep -rn --include='*.md' --include='*.sh' --include='*.json' --exclude-dir=worktrees "$@" .claude README.md; }

if search -e 'workflow-commands:workflow-commands:' -e '//workflow-commands:' >/dev/null; then flunk "double namespace prefix present"
else pass "no double namespace prefix"; fi

psc=".claude/Commands/workflow-commands/plan-summary-console.md"
if grep -E '(^|[^:])plan-refinement-qa' "$psc" >/dev/null; then flunk "plan-summary-console.md names plan-refinement-qa without its namespace"
else pass "plan-summary-console.md names workflow-commands:plan-refinement-qa in full"; fi

if search -F 'python-code-review' >/dev/null; then flunk "P03 still calls /python-code-review"
elif grep -qF '/workflow-commands:P03-code-review-checks-[SF] src/auth/login.py' ".claude/Commands/workflow-commands/P03-code-review-checks-[SF].md"; then pass "P03 examples use /workflow-commands:P03-code-review-checks-[SF]"
else flunk "P03 examples missing /workflow-commands:P03-code-review-checks-[SF]"; fi

if search -F 'git-workflow' >/dev/null; then flunk "a 'git-workflow' rule is still cited: $(search -F 'git-workflow' | head -1 | cut -c1-120)"
else pass "no citation of a nonexistent git-workflow rule"; fi

if search -F 'lint_rules' >/dev/null; then flunk "P02 still cites .claude/rules/lint_rules/"
else pass "no citation of .claude/rules/lint_rules/"; fi

if search -e 'Opus-4\.' -e 'Sonnet-[0-9]' >/dev/null; then flunk "pinned model name present: $(search -e 'Opus-4\.' -e 'Sonnet-[0-9]' | head -1 | cut -c1-120)"
else pass "no pinned Opus-4.x / Sonnet-N model names"; fi

if search -i 'usage limit' | grep -qi 'opus'; then flunk "a budget line still names an Opus-specific usage limit"
else pass "budgets read '% of the 5-hr usage limit'"; fi

if search -F 'FastAPI service' >/dev/null; then flunk "'(FastAPI service)' leftover present"
else pass "no '(FastAPI service)' leftover"; fi

if search -F '`/P11.5-build-validation`' >/dev/null; then flunk "full tier still invokes /P11.5-build-validation"
else pass "build validator invoked by its full skill name"; fi

exit "$fail"
````

- [ ] **Step 2: Run the check and watch it fail**

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-w1-names.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
```

Expected — every W1 assertion fails except the double-prefix one, which passes trivially before the sweep:

```text
FAIL: 144 bare /<command> names, first: .claude/Commands/workflow-commands/python-verification-full.md:911	/python-verification-quick
FAIL: 59 bare backticked command names, first: .claude/Commands/workflow-commands/beads-post-execution.md:13	`beads-ship-task`
PASS: no double namespace prefix
FAIL: plan-summary-console.md names plan-refinement-qa without its namespace
FAIL: P03 still calls /python-code-review
FAIL: a 'git-workflow' rule is still cited: .claude/Commands/workflow-commands/workflow-writing-plans.md:19:artifacts under `docs/plans/<epic-slug>/` per the git-wo
FAIL: P02 still cites .claude/rules/lint_rules/
FAIL: pinned model name present: .claude/Commands/workflow-commands/workflow-writing-plans.md:386:split signal; plan *length* is. Below the threshold, on
FAIL: a budget line still names an Opus-specific usage limit
FAIL: '(FastAPI service)' leftover present
FAIL: full tier still invokes /P11.5-build-validation
exit=1
```

If any count differs, stop: the tree is not the one this plan was written against, and the expected per-file counts in Step 4 will not hold either.

- [ ] **Step 3: Write the sweep script**

A one-off tool, kept outside the repo. It derives the command list from the files in `.claude/Commands/workflow-commands/`, rewrites `/<name>` to `/workflow-commands:<name>` and a backticked `` `<name>` `` to `` `workflow-commands:<name>` ``, qualifies the four unbackticked mentions in `plan-summary-console.md` by exact replacement, and skips the files listed above. Create `<scratchpad>/sgw-checks/w1-sweep.py` with the Write tool, not a shell heredoc (see Global Constraints), with exactly this content:

````python
#!/usr/bin/env python3
"""W1 naming sweep: give every workflow-commands reference its full name.

Usage: python3 w1-sweep.py <repo-root>

- A pasteable command `/<name>` becomes `/workflow-commands:<name>`.
- A backticked prose mention `` `<name>` `` becomes `` `workflow-commands:<name>` ``.
- Four unbackticked prose mentions in plan-summary-console.md are qualified by
  exact literal replacement.

Rewrites files in place, prints one line per changed file plus a total, and is
idempotent: a second run changes nothing and reports a total of 0.
"""
import os
import re
import sys

root = sys.argv[1]
cmd_dir = os.path.join(root, ".claude", "Commands", "workflow-commands")
names = sorted(
    (f[:-3] for f in os.listdir(cmd_dir) if f.endswith(".md")),
    key=len,
    reverse=True,
)
alt = "|".join(re.escape(n) for n in names)

# `/<name>` not preceded by a path or word character, and not part of a longer
# name or a file path such as `<name>.md`.
SLASH = re.compile(r"(?<![\w.:/\-])/(" + alt + r")(?![\w\-\[])(?!\.md)")
# A backticked token that is exactly a bare command name.
TICK = re.compile(r"`(" + alt + r")`")

# Files the spec leaves untouched, plus skill-usage.md, whose tables show bare
# names on purpose (the "Wrong" column and the per-namespace skill list).
SKIP = {
    ".claude/rules/critical ai agent rule.md",
    ".claude/rules/0_Beads x Superpowers/skill-usage.md",
    ".claude/rules/0_Beads x Superpowers/beads-plugin-cli-only.md",
    ".claude/rules/0_Beads x Superpowers/bug-must-have-epic.md",
    ".claude/rules/Git Best Practices/protect_plans_and_commit_all.md",
    ".claude/Commands/workflow-commands/references/refinement-methodology.md",
    ".claude/Commands/workflow-commands/tdd-test-writer.md",
    ".claude/hooks/write-safety.sh",
    ".claude/settings.json",
}

LITERALS = {
    ".claude/Commands/workflow-commands/plan-summary-console.md": [
        ("Auto-invoked after plan-refinement-qa completes.",
         "Auto-invoked after workflow-commands:plan-refinement-qa completes."),
        ("produced by writing-plans and updated by plan-refinement-qa)",
         "produced by superpowers:writing-plans and updated by workflow-commands:plan-refinement-qa)"),
        ("(appended by plan-refinement-qa)",
         "(appended by workflow-commands:plan-refinement-qa)"),
        ("(same wording as plan-refinement-qa handoff)",
         "(same wording as the workflow-commands:plan-refinement-qa handoff)"),
    ],
}


def targets():
    yield "README.md"
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, ".claude")):
        dirnames[:] = sorted(d for d in dirnames if d != "worktrees")
        for f in sorted(filenames):
            if f.endswith((".md", ".sh", ".json")):
                yield os.path.relpath(os.path.join(dirpath, f), root)


total = 0
for rel in targets():
    if rel in SKIP:
        continue
    path = os.path.join(root, rel)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    new, n_slash = SLASH.subn(r"/workflow-commands:\1", text)
    new, n_tick = TICK.subn(r"`workflow-commands:\1`", new)
    n_lit = 0
    for old, repl in LITERALS.get(rel, []):
        if old in new:
            new = new.replace(old, repl)
            n_lit += 1
    n = n_slash + n_tick + n_lit
    if n:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)
        print(f"{n:4d}  {rel}  (slash {n_slash}, backtick {n_tick}, literal {n_lit})")
        total += n
print(f"TOTAL {total}")
````

- [ ] **Step 4: Run the sweep, then run it again**

```bash
CHECKS="<scratchpad>/sgw-checks"
python3 "$CHECKS/w1-sweep.py" "$(git rev-parse --show-toplevel)"
```

Expected, exactly (144 slash forms + 59 backticked prose mentions + 4 literal replacements):

```text
  31  README.md  (slash 6, backtick 25, literal 0)
   1  .claude/Commands/workflow-commands/beads-post-execution.md  (slash 0, backtick 1, literal 0)
   1  .claude/Commands/workflow-commands/beads-ship-task.md  (slash 0, backtick 1, literal 0)
   1  .claude/Commands/workflow-commands/plan-refinement-qa.md  (slash 0, backtick 1, literal 0)
   4  .claude/Commands/workflow-commands/plan-summary-console.md  (slash 0, backtick 0, literal 4)
   3  .claude/Commands/workflow-commands/python-verification-full.md  (slash 2, backtick 1, literal 0)
   1  .claude/Commands/workflow-commands/python-verification-quick.md  (slash 0, backtick 1, literal 0)
   2  .claude/Commands/workflow-commands/python-verification-standard.md  (slash 1, backtick 1, literal 0)
  19  .claude/Commands/workflow-commands/workflow-execute-plans.md  (slash 15, backtick 4, literal 0)
  14  .claude/Commands/workflow-commands/workflow-execute-spikes.md  (slash 14, backtick 0, literal 0)
  31  .claude/Commands/workflow-commands/workflow-execution-sequence.md  (slash 31, backtick 0, literal 0)
  11  .claude/Commands/workflow-commands/workflow-planning-sequence.md  (slash 10, backtick 1, literal 0)
  23  .claude/Commands/workflow-commands/workflow-ship-epic.md  (slash 23, backtick 0, literal 0)
  22  .claude/Commands/workflow-commands/workflow-writing-plans.md  (slash 22, backtick 0, literal 0)
  30  .claude/rules/0_Beads x Superpowers/beads-workflow-router.md  (slash 10, backtick 20, literal 0)
  10  .claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md  (slash 10, backtick 0, literal 0)
   3  .claude/rules/Git Best Practices/no-direct-push-to-master.md  (slash 0, backtick 3, literal 0)
TOTAL 207
```

Run the same command a second time. Expected: `TOTAL 0` and nothing else — the sweep is idempotent and never produces `workflow-commands:workflow-commands:`.

- [ ] **Step 5: Read the sweep's diff**

```bash
git diff --word-diff=plain --unified=0 | grep -E '^\+\+\+|\{\+' | cut -c1-220
```

Every `{+…+}` must be a command or skill reference gaining `workflow-commands:`. Some of them sit inside the frontmatter `description:` lines of four files (`workflow-execute-spikes.md`, `workflow-execution-sequence.md`, `workflow-planning-sequence.md` and `workflow-ship-epic.md`); those lines stay valid YAML because the inserted colon is never followed by a space. The router's pipeline code block loses its column alignment, which is fine: Task 4 rewrites the router. Revert and fix the script if any change touches a path, a frontmatter `name:` key, or a file from the leave-alone list.

- [ ] **Step 6: P03 usage examples call the real command**

In `.claude/Commands/workflow-commands/P03-code-review-checks-[SF].md`, section `### Local Mode Input Options`, inside the **Examples:** code block, replace:

```text
/python-code-review                              → reviews git diff only
/python-code-review src/auth/login.py          → reviews only login.py
/python-code-review src/auth/ src/core/utils.py → reviews auth dir + utils.py
```

with:

```text
/workflow-commands:P03-code-review-checks-[SF]                             → reviews git diff only
/workflow-commands:P03-code-review-checks-[SF] src/auth/login.py           → reviews only login.py
/workflow-commands:P03-code-review-checks-[SF] src/auth/ src/core/utils.py → reviews auth dir + utils.py
```

Why: `/python-code-review` does not exist; the command these examples describe is P03 itself. The paths stay.

- [ ] **Step 7: P03 Step 1 example calls the real command**

In `.claude/Commands/workflow-commands/P03-code-review-checks-[SF].md`, section `### Step 1: Determine Files to Review`, replace:

```text
   - Example: `/python-code-review src/features/auth/login.py`
```

with:

```text
   - Example: `/workflow-commands:P03-code-review-checks-[SF] src/features/auth/login.py`
```

Why: Same nonexistent command as the previous step.

- [ ] **Step 8: writing-plans cites the plan rule the template actually has (intro)**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section the opening paragraph under `# Workflow: Writing Plans from a Sequence File` (it begins "This command obeys the beads workflow router"), replace:

```text
artifacts under `docs/plans/<epic-slug>/` per the git-workflow rule
```

with:

```text
artifacts under `docs/plans/<epic-slug>/` per Rule 1 of the plan-protection rule
```

Why: The template has no "git-workflow rule". Saving plans under `docs/plans/` is Rule 1 of `protect_plans_and_commit_all.md`, which the very next line already names.

- [ ] **Step 9: writing-plans cites the plan rule the template actually has (Artifacts)**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Artifacts — `docs/plans/<epic-slug>/``, replace:

```text
`docs/plans/` (git-workflow Rule 2) — never deleted after execution.
```

with:

```text
`docs/plans/` (`Git Best Practices/protect_plans_and_commit_all.md` Rule 2) — never deleted after execution.
```

Why: "Never delete a plan" is Rule 2 of `protect_plans_and_commit_all.md`.

- [ ] **Step 10: P02 points at ruff's real settings**

In `.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md`, section `### Step 5: Manual Fixes`, replace:

```text
3. Apply the fix following project lint rules in `.claude/rules/lint_rules/` and `pyproject.toml [tool.ruff]`
```

with:

```text
3. Apply the fix following the project's `[tool.ruff]` settings in `pyproject.toml`
```

Why: `.claude/rules/lint_rules/` does not exist; a Python project's lint rules are its `[tool.ruff]` settings. (Task 2 rescopes P02's other steps; it does not touch this line's meaning.)

- [ ] **Step 11: execution-sequence drops a pinned model name**

In `.claude/Commands/workflow-commands/workflow-execution-sequence.md`, section `### 5. [main ctx] Present sequence + coverage + GATE`, replace:

```text
Because the next step launches **expensive Opus-4.8/xhigh planning workflows**,
```

with:

```text
Because the next step launches **expensive Opus planning workflows**,
```

Why: "Opus-4.8" pins a model version; the tier is configuration (see `never-ask-about-agent-model.md`, added in Task 4).

- [ ] **Step 12: writing-plans Step 6 names a tier, not a model version**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Step 6: Apply #1 → Approve [workflow]`, replace:

```text
split signal; plan *length* is. Below the threshold, one Sonnet-5-medium
```

with:

```text
split signal; plan *length* is. Below the threshold, one sonnet / medium
```

Why: "Sonnet-5-medium" pins a model generation.

- [ ] **Step 13: writing-plans CRITICAL block names a tier, not a model version**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## CRITICAL — Honor Project Rules`, replace:

```text
  Sonnet-5-medium agents from racing on the same plan file — those are merged
```

with:

```text
  sonnet / medium agents from racing on the same plan file — those are merged
```

Why: Same pinned name as the previous step.

- [ ] **Step 14: writing-plans budget row: one usage limit**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Model & Budget`, replace:

```text
| Budget shown as | **% of the 5-hr Opus xhigh usage limit** — Step 6 runs on Sonnet and isn't separately metered against that limit |
```

with:

```text
| Budget shown as | **% of the 5-hr usage limit** — Step 6 runs on Sonnet and isn't separately metered against that limit |
```

Why: Budgets are shown against the one 5-hour usage limit, not a per-model one. This matches the owner's current global wording word for word.

- [ ] **Step 15: execute-plans budget row: one usage limit**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, section `## Model & Budget`, replace:

```text
| Budget shown as | **% of the 5-hr Opus medium usage limit** |
```

with:

```text
| Budget shown as | **% of the 5-hr usage limit** |
```

Why: Same generalisation (the spec lists all three batch commands that print a budget).

- [ ] **Step 16: execute-spikes budget row: one usage limit**

In `.claude/Commands/workflow-commands/workflow-execute-spikes.md`, section `## Model & Budget`, replace:

```text
| Budget shown as | **% of the 5-hr Opus high usage limit** |
```

with:

```text
| Budget shown as | **% of the 5-hr usage limit** |
```

Why: Same generalisation.

- [ ] **Step 17: execute-plans description drops "(FastAPI service)"**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, section the frontmatter `description:` line (line 2 of the file), replace:

```text
and batched manual smoke gates (FastAPI service) using segmented Claude Workflows
```

with:

```text
and batched manual smoke gates using segmented Claude Workflows
```

Why: A leftover from the project the template was generified from; the template targets any Python project.

- [ ] **Step 18: Full tier invokes the build validator by its real name**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Phase 11.5: Build Validation (from P11.5-build-validation)` → `### Step 1: Invoke Build Validator Skill`, replace:

```text
Invoke `/P11.5-build-validation` to perform comprehensive build checks:
```

with:

```text
Invoke `workflow-commands:P11.5-build-validation-[F]` to perform comprehensive build checks:
```

Why: `/P11.5-build-validation` is not a command; the skill is `workflow-commands:P11.5-build-validation-[F]`. Not in the spec's W1 list, but it is a stale reference of exactly the kind W1 exists to remove (spec §1 success criterion 3).

- [ ] **Step 19: Run the check and watch it pass**

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-w1-names.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
```

Expected:

```text
PASS: no bare /<command> names
PASS: no bare backticked command names
PASS: no double namespace prefix
PASS: plan-summary-console.md names workflow-commands:plan-refinement-qa in full
PASS: P03 examples use /workflow-commands:P03-code-review-checks-[SF]
PASS: no citation of a nonexistent git-workflow rule
PASS: no citation of .claude/rules/lint_rules/
PASS: no pinned Opus-4.x / Sonnet-N model names
PASS: budgets read '% of the 5-hr usage limit'
PASS: no '(FastAPI service)' leftover
PASS: build validator invoked by its full skill name
exit=0
```

- [ ] **Step 20: Confirm the change set is exactly this task's**

```bash
git diff --name-only && git diff --shortstat && git status --short | grep -v '^ M '
```

Expected: these 19 paths, then the stat line, then nothing else — or one `?? .claude/worktrees/` line, if that local folder holds a worktree (never stage it):

```text
.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md
.claude/Commands/workflow-commands/P03-code-review-checks-[SF].md
.claude/Commands/workflow-commands/beads-post-execution.md
.claude/Commands/workflow-commands/beads-ship-task.md
.claude/Commands/workflow-commands/plan-refinement-qa.md
.claude/Commands/workflow-commands/plan-summary-console.md
.claude/Commands/workflow-commands/python-verification-full.md
.claude/Commands/workflow-commands/python-verification-quick.md
.claude/Commands/workflow-commands/python-verification-standard.md
.claude/Commands/workflow-commands/workflow-execute-plans.md
.claude/Commands/workflow-commands/workflow-execute-spikes.md
.claude/Commands/workflow-commands/workflow-execution-sequence.md
.claude/Commands/workflow-commands/workflow-planning-sequence.md
.claude/Commands/workflow-commands/workflow-ship-epic.md
.claude/Commands/workflow-commands/workflow-writing-plans.md
.claude/rules/0_Beads x Superpowers/beads-workflow-router.md
.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md
.claude/rules/Git Best Practices/no-direct-push-to-master.md
README.md
 19 files changed, 208 insertions(+), 208 deletions(-)
```

Anything else in the list means a step touched the wrong file; find it with `git diff <path>` before staging.

- [ ] **Finish 1: Confirm this task's change set**

```bash
git status --short
```
Expected: exactly the files in this task's **Files** list above (`M` modified, `??` new, `D` deleted), and nothing else — apart from a `?? .claude/worktrees/` line if that local folder holds a worktree, which is never staged. Anything else means a step touched the wrong file: find it with `git diff <path>` before staging.

- [ ] **Finish 2: Commit W1**

```bash
git add -- \
  ':(literal).claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md' \
  ':(literal).claude/Commands/workflow-commands/P03-code-review-checks-[SF].md' \
  ".claude/Commands/workflow-commands/beads-post-execution.md" \
  ".claude/Commands/workflow-commands/beads-ship-task.md" \
  ".claude/Commands/workflow-commands/plan-refinement-qa.md" \
  ".claude/Commands/workflow-commands/plan-summary-console.md" \
  ".claude/Commands/workflow-commands/python-verification-full.md" \
  ".claude/Commands/workflow-commands/python-verification-quick.md" \
  ".claude/Commands/workflow-commands/python-verification-standard.md" \
  ".claude/Commands/workflow-commands/workflow-execute-plans.md" \
  ".claude/Commands/workflow-commands/workflow-execute-spikes.md" \
  ".claude/Commands/workflow-commands/workflow-execution-sequence.md" \
  ".claude/Commands/workflow-commands/workflow-planning-sequence.md" \
  ".claude/Commands/workflow-commands/workflow-ship-epic.md" \
  ".claude/Commands/workflow-commands/workflow-writing-plans.md" \
  ".claude/rules/0_Beads x Superpowers/beads-workflow-router.md" \
  ".claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md" \
  ".claude/rules/Git Best Practices/no-direct-push-to-master.md" \
  "README.md" && \
git diff --cached --stat && git commit -F- <<'EOF'
chore(workflow): give every workflow command its full name, fix stale references

Sweep 207 command references to /workflow-commands:<name> (pasteable) or
workflow-commands:<name> (prose). Point P03's examples at P03 itself, P02 at
[tool.ruff], writing-plans at protect_plans_and_commit_all.md and the full tier
at the real build-validator skill; replace pinned model names and per-model
usage limits with tiers and the one 5-hr limit; drop '(FastAPI service)'.

<attribution trailer>
EOF
```
Expected: the stat lists only this task's files, then the commit summary line. Replace `<attribution trailer>` with the attribution lines from your session's system reminder before running it.

- [ ] **Finish 3: Record the commit on the W1 bead**

```bash
source .beads/sgw-ids.env && bd update "$W1" --append-notes "Landed in $(git rev-parse --short HEAD): chore(workflow): give every workflow command its full name, fix stale references" && bd show "$W1" | sed -n '1,20p'
```
Expected: the notes end with the "Landed in" line and the status is still `IN_PROGRESS` — all eight workstream beads close together when the PR opens (Task 9).

---

### Task 2: W2 — Verification only rewrites what the task changed

Spec: §6 W2; §7 (Step 2a also counts the branch's commits and untracked lines; `--force-exclude` on every ruff write; notebooks are report-only; migrations are never auto-fixed; formatting is a scoped write plus a check, with no hook; Phase 12 may create mirrored test files).

**Files:**
- Create: `.claude/rules/verification-write-scope.md` — the always-loaded "read wide, write narrow" rule (policy only)
- Create: `.claude/Commands/workflow-commands/references/scoped-ruff.md` — the two runnable write blocks, loaded only when a step runs them
- Modify: `.claude/Commands/workflow-commands/beads-post-execution.md` — Step 2a records the changed set; Step 2b picks the level
- Modify: `.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md`, `.claude/Commands/workflow-commands/P14-security-review-[SF].md`
- Modify: `.claude/Commands/workflow-commands/python-verification-quick.md`, `.claude/Commands/workflow-commands/python-verification-standard.md`, `.claude/Commands/workflow-commands/python-verification-full.md`

**Interfaces:**
- Consumes: the post-Task-1 naming; `.beads/.session-state.json` as `workflow-commands:beads-start-task` creates it; the router heading text "Named Scope Is Authorization" (present in both the old and the new router).
- Produces: `modified_files` (a plain list of path strings) and `total_lines_changed`, written only by Step 2a (snippet `changed-set`); the snippets `scoped-ruff-fix` and `scoped-ruff-format` in `.claude/Commands/workflow-commands/references/scoped-ruff.md`; the report lines `Auto-fixed: …` and `Scope check: …` every tier uses.

Each part below lists its own files, interfaces and steps; run the parts in order, A first.

- [ ] **Start: mark the W2 bead in progress**

```bash
source .beads/sgw-ids.env && bd update "$W2" --status in_progress && bd show "$W2" | head -6
```
Expected: the bead shows `IN_PROGRESS`. (If `.beads/sgw-ids.env` is missing, Task 0 has not run.)

#### Part A: Record the changed set, add the write-scope rule, scope every auto-fix (all files except the full tier)

Task 1's naming sweep does not touch any anchor quoted below. Every new text is already in its
post-Task-1 form.

**Files:**
- Create: `.claude/rules/verification-write-scope.md` — the always-loaded "read wide, write narrow" rule (policy only)
- Create: `.claude/Commands/workflow-commands/references/scoped-ruff.md` — the two runnable write blocks (`scoped-ruff-fix`, `scoped-ruff-format`), loaded only when a step runs them
- Modify: `.claude/Commands/workflow-commands/beads-post-execution.md` — Step 2 becomes Step 2a (record the changed set, snippet `changed-set`) and Step 2b (pick the level); two lines of the Step 5 prompt
- Modify: `.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md` — Steps 1, 2, 4, 5 and 6 and the tools list read wide but write only the changed set
- Modify: `.claude/Commands/workflow-commands/python-verification-quick.md` — Phase 1 unknown-set rule, Phase 2 Steps 1–2, report lines, quick-reference rows
- Modify: `.claude/Commands/workflow-commands/python-verification-standard.md` — Phase 1 Step 1, Phase 2 Steps 1, 3 and 4, report lines
- Modify: `.claude/Commands/workflow-commands/P14-security-review-[SF].md` — reads `modified_files` as plain strings
- Test (scratch, never committed): `<scratchpad>/sgw-checks/check-changed-set.sh`, `<scratchpad>/sgw-checks/check-ruff-scope.sh`

**Interfaces:**
- Consumes: `.beads/.session-state.json` as `workflow-commands:beads-start-task` creates it (keys `task_id`, `task_requirements`, `plan_created`, `plan_file`, `modified_files`, `total_lines_changed`); the router's *Named Scope Is Authorization* section, cited by that heading text (the current router's heading "Standing Posture: Named Scope Is Authorization" also contains it, so the citation holds before and after Task 4).
- Produces:
  - `modified_files`: a plain JSON list of repo-root-relative path strings, and `total_lines_changed`: an integer, both written only by beads-post-execution Step 2a and read by every tier, P02 and P14. Every other key in the file is preserved.
  - Step 2a's printed line `New modules under src/: <list or none>`, which Step 2b's level rule uses.
  - `.claude/rules/verification-write-scope.md` (the policy) and `.claude/Commands/workflow-commands/references/scoped-ruff.md`, whose fenced blocks start with `# snippet: scoped-ruff-fix` and `# snippet: scoped-ruff-format`. Part B (the full tier), P02 and the quick and standard tiers tell Claude to run these blocks unchanged.
  - The report lines every tier uses: `Auto-fixed: N across M changed files` / `Auto-fixed: SKIPPED (changed set unknown)` / `Auto-fixed: SKIPPED (no Python files in the changed set)`, and `Scope check: no files outside the changed set` / `Scope check: LEAK: [list]`.

- [ ] **Step 1: Write the Step 2a check (it must fail for now)**

`<scratchpad>` below is your session's scratchpad directory (the absolute path in your system prompt); the checks are never committed. Create the file `<scratchpad>/sgw-checks/check-changed-set.sh` with the Write tool, not a shell heredoc (see Global Constraints), with exactly this content. It covers Review Focus items 2, 3 and 4: committed, staged, unstaged, untracked and deleted files, a rename, paths with spaces, a repository with no `origin`, an `origin/HEAD` that has to be looked up (and resolves to `origin/main`), and a repository with no commits yet.

````bash
#!/usr/bin/env bash
# Behaviour check for beads-post-execution Step 2a (snippet "changed-set").
# Usage: bash check-changed-set.sh <repo-root>
set -u
REPO="${1:?usage: check-changed-set.sh <repo-root>}"
SRC="$REPO/.claude/Commands/workflow-commands/beads-post-execution.md"
WORK="$(cd "$(dirname "$0")" && pwd)/changed-set-work"
fails=0
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; fails=$((fails + 1)); }

extract_snippet() {   # extract_snippet <file> <name>
  awk -v want="# snippet: $2" '
    /^[[:space:]]*```/ { if (inb) { if (hit) exit; inb=0 } else { inb=1; first=1 }; next }
    inb && first { first=0; t=$0; sub(/^[[:space:]]+/, "", t); if (t == want) hit=1; next }
    inb && hit { print }
  ' "$1"
}

[ -f "$SRC" ] || { echo "FAIL: $SRC does not exist"; exit 1; }
SNIP="$(extract_snippet "$SRC" changed-set)"
if [ -z "$SNIP" ]; then
  echo "FAIL: snippet 'changed-set' not found in $SRC"
  exit 1
fi
rm -rf "$WORK"; mkdir -p "$WORK"
export GIT_AUTHOR_NAME=check GIT_AUTHOR_EMAIL=check@example.com
export GIT_COMMITTER_NAME=check GIT_COMMITTER_EMAIL=check@example.com
export GIT_CONFIG_NOSYSTEM=1

state_get() {   # state_get <repo> <python expression over s>
  python3 -c 'import json,sys; s=json.load(open(sys.argv[1])); print(eval(sys.argv[2]))' \
    "$1/.beads/.session-state.json" "$2"
}

# ---------------------------------------------------------------------------
# Scenario 1: origin with default branch main, origin/HEAD unset; committed,
# staged (a rename with spaces), unstaged, deleted, untracked; a .beads/ file.
# ---------------------------------------------------------------------------
git init -q --bare -b main "$WORK/origin.git"
R1="$WORK/repo1"
git init -q -b main "$R1"
(
  cd "$R1" || exit 1
  mkdir -p src/pkg docs
  printf 'a = 1\nb = 2\nc = 3\n' > src/pkg/a.py
  printf 'x = 1\ny = 2\n' > src/pkg/b.py
  printf 'line one\nline two\n' > "docs/old name.md"
  printf 'gone = 1\n' > gone.py
  printf 'stays = 1\n' > stays.py
  git add -A && git commit -q -m base
  git remote add origin "$WORK/origin.git"
  git push -q origin main
  git remote set-head origin -d >/dev/null 2>&1
  git switch -q -c feat/x
  printf 'd = 4\n' >> src/pkg/a.py
  printf 'def f():\n    return 1\n' > src/pkg/new_mod.py
  git add -A && git commit -q -m "branch work"
  git mv "docs/old name.md" "docs/new name.md"
  printf 'z = 3\n' >> src/pkg/b.py
  rm gone.py
  mkdir -p "notes dir" tests .beads
  printf 'one\ntwo\nthree\n' > "notes dir/todo list.txt"
  printf 'def test_x():\n    assert True\n' > tests/test_new.py
  printf '{"task_id": "bp-1", "plan_file": "docs/plans/x.md", "verification": {"level": "quick"}, "modified_files": [], "total_lines_changed": 0}\n' > .beads/.session-state.json
) || { echo "FAIL: scenario 1 setup"; exit 1; }
OUT1="$(cd "$R1/src/pkg" && bash -c "$SNIP" 2>&1)"
echo "$OUT1" | sed 's/^/    | /'

files1="$(state_get "$R1" 's["modified_files"]')"
expect1="['docs/new name.md', 'notes dir/todo list.txt', 'src/pkg/a.py', 'src/pkg/b.py', 'src/pkg/new_mod.py', 'tests/test_new.py']"
[ "$files1" = "$expect1" ] && pass "scenario 1 records committed, staged-rename, unstaged and untracked files; drops deletions, the old rename path and .beads/" \
  || fail "scenario 1 modified_files: got $files1, expected $expect1"
lines1="$(state_get "$R1" 's["total_lines_changed"]')"
[ "$lines1" = "10" ] && pass "scenario 1 line count covers branch + uncommitted + untracked lines (10)" \
  || fail "scenario 1 total_lines_changed: got $lines1, expected 10"
keys1="$(state_get "$R1" '(s["task_id"], s["plan_file"], s["verification"]["level"])')"
[ "$keys1" = "('bp-1', 'docs/plans/x.md', 'quick')" ] && pass "scenario 1 keeps task_id, plan_file and verification" \
  || fail "scenario 1 other keys: got $keys1"
head1="$(git -C "$R1" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)"
[ "$head1" = "origin/main" ] && pass "scenario 1 trunk lookup set origin/HEAD to origin/main" \
  || fail "scenario 1 trunk: origin/HEAD is '$head1', expected origin/main"
echo "$OUT1" | grep -q 'branch range skipped' && fail "scenario 1 wrongly skipped the branch range" \
  || pass "scenario 1 used the branch range"
echo "$OUT1" | grep -q '^New modules under src/: src/pkg/new_mod.py$' && pass "scenario 1 names the new src module and not the new test file" \
  || fail "scenario 1 new-module line missing or wrong"

# ---------------------------------------------------------------------------
# Scenario 2: no origin remote at all.
# ---------------------------------------------------------------------------
R2="$WORK/repo2"
git init -q -b main "$R2"
(
  cd "$R2" || exit 1
  printf 'c = 1\nc2 = 2\n' > c.py
  printf 'd = 1\n' > d.py
  git add -A && git commit -q -m base
  printf 'c3 = 3\n' >> c.py
  git commit -q -am "local commit"
  printf 'd2 = 2\n' >> d.py
  printf 'e = 1\nf = 2\n' > "e f.py"
) || { echo "FAIL: scenario 2 setup"; exit 1; }
OUT2="$(cd "$R2" && bash -c "$SNIP" 2>&1)"
echo "$OUT2" | sed 's/^/    | /'
echo "$OUT2" | grep -q 'branch range skipped' && pass "scenario 2 says the branch range was skipped" \
  || fail "scenario 2 did not report the skipped branch range"
files2="$(state_get "$R2" 's["modified_files"]')"
[ "$files2" = "['d.py', 'e f.py']" ] && pass "scenario 2 still records uncommitted and untracked files" \
  || fail "scenario 2 modified_files: got $files2, expected ['d.py', 'e f.py']"
lines2="$(state_get "$R2" 's["total_lines_changed"]')"
[ "$lines2" = "3" ] && pass "scenario 2 line count (3)" || fail "scenario 2 total_lines_changed: got $lines2, expected 3"

# ---------------------------------------------------------------------------
# Scenario 3: a repository with no commits yet.
# ---------------------------------------------------------------------------
R3="$WORK/repo3"
git init -q -b main "$R3"
(
  cd "$R3" || exit 1
  printf 's = 1\n' > s.py && git add s.py
  printf 'u = 1\nv = 2\n' > u.py
) || { echo "FAIL: scenario 3 setup"; exit 1; }
OUT3="$(cd "$R3" && bash -c "$SNIP" 2>&1)"
echo "$OUT3" | sed 's/^/    | /'
files3="$(state_get "$R3" 's["modified_files"]' 2>/dev/null)"
[ "$files3" = "['s.py', 'u.py']" ] && pass "scenario 3 (no commits yet) records staged and untracked files" \
  || fail "scenario 3 modified_files: got '$files3', expected ['s.py', 'u.py']"

echo
if [ "$fails" -eq 0 ]; then echo "check-changed-set: ALL PASS"; else echo "check-changed-set: $fails FAILED"; exit 1; fi
````

- [ ] **Step 2: Write the write-sequence check (it must fail for now)**

Create the file `<scratchpad>/sgw-checks/check-ruff-scope.sh` with the Write tool, not a shell heredoc (see Global Constraints), with exactly this content. It covers Review Focus items 1 and 2: a file excluded in `pyproject.toml` and named on the command line stays untouched; `migrations/` and generated `*_pb2.py` files are never fixed; a docs-only or unknown changed set never invokes ruff at all (a logging ruff stand-in proves it); a `.py` path with a space is fixed as one argument; a leaked change to a clean tracked file is reverted and reported; an untracked leak is reported and left in place; a file that already had uncommitted edits is reported, not reverted; and formatting stays inside the changed set.

````bash
#!/usr/bin/env bash
# Behaviour check for the write blocks in .claude/Commands/workflow-commands/references/scoped-ruff.md
# (snippets "scoped-ruff-fix" and "scoped-ruff-format").
# Usage: bash check-ruff-scope.sh <repo-root>
set -u
REPO="${1:?usage: check-ruff-scope.sh <repo-root>}"
SRC="$REPO/.claude/Commands/workflow-commands/references/scoped-ruff.md"
WORK="$(cd "$(dirname "$0")" && pwd)/ruff-scope-work"
fails=0
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; fails=$((fails + 1)); }

extract_snippet() {   # extract_snippet <file> <name>
  awk -v want="# snippet: $2" '
    /^[[:space:]]*```/ { if (inb) { if (hit) exit; inb=0 } else { inb=1; first=1 }; next }
    inb && first { first=0; t=$0; sub(/^[[:space:]]+/, "", t); if (t == want) hit=1; next }
    inb && hit { print }
  ' "$1"
}

[ -f "$SRC" ] || { echo "FAIL: $SRC does not exist"; exit 1; }
FIX="$(extract_snippet "$SRC" scoped-ruff-fix)"
FMT="$(extract_snippet "$SRC" scoped-ruff-format)"
[ -n "$FIX" ] || { echo "FAIL: snippet 'scoped-ruff-fix' not found in $SRC"; exit 1; }
[ -n "$FMT" ] || { echo "FAIL: snippet 'scoped-ruff-format' not found in $SRC"; exit 1; }
REAL_RUFF="$(command -v ruff)" || { echo "FAIL: ruff is not installed"; exit 1; }

rm -rf "$WORK"; mkdir -p "$WORK/bin"
export GIT_AUTHOR_NAME=check GIT_AUTHOR_EMAIL=check@example.com
export GIT_COMMITTER_NAME=check GIT_COMMITTER_EMAIL=check@example.com
export GIT_CONFIG_NOSYSTEM=1

# A ruff stand-in that logs every call, can simulate a tool writing outside the
# changed set (LEAK_TO / LEAK_NEW, on the --fix call only), then runs real ruff.
cat > "$WORK/bin/ruff" <<'EOF'
#!/usr/bin/env bash
echo "ruff $*" >> "$RUFF_LOG"
case " $* " in *" --fix "*)
  [ -n "${LEAK_TO:-}" ] && printf '# leaked\n' >> "$LEAK_TO"
  [ -n "${LEAK_NEW:-}" ] && printf 'leaked = 1\n' > "$LEAK_NEW"
esac
exec "$REAL_RUFF" "$@"
EOF
chmod +x "$WORK/bin/ruff"
export REAL_RUFF RUFF_LOG="$WORK/ruff.log"
export PATH="$WORK/bin:$PATH"

FIXABLE='import os
import sys

print(sys.argv)
'
R="$WORK/repo"
git init -q -b main "$R"
(
  cd "$R" || exit 1
  printf '[tool.ruff]\nextend-exclude = ["external"]\n\n[tool.ruff.lint]\nselect = ["F401"]\n' > pyproject.toml
  mkdir -p external src/pkg "src/dir with space" src/gen migrations .beads docs
  for f in external/vendored.py src/pkg/mod.py "src/dir with space/my mod.py" src/gen/thing_pb2.py \
           migrations/0001_init.py src/other.py src/dirty.py; do
    printf '%s' "$FIXABLE" > "$f"
  done
  printf 'x=1\n' > src/pkg/fmt.py
  printf 'y=2\n' > src/other_fmt.py
  printf '# Readme\n' > README.md
  printf '# Guide\n' > docs/guide.md
  printf '.beads/\n' > .gitignore
  git add -A && git commit -q -m base
) || { echo "FAIL: setup"; exit 1; }

state() {   # state <json list of paths>
  printf '{"task_id": "bp-1", "modified_files": %s, "total_lines_changed": 9}\n' "$1" > "$R/.beads/.session-state.json"
}
reset_repo() { git -C "$R" checkout -q -- . && git -C "$R" clean -qfd -e .beads && : > "$RUFF_LOG"; }
clean() { git -C "$R" diff --quiet HEAD -- "$1"; }
has_f401() { grep -q '^import os$' "$R/$1"; }

# --- Case A: scoped lint fix ------------------------------------------------
reset_repo
state '["external/vendored.py", "src/pkg/mod.py", "src/dir with space/my mod.py", "src/gen/thing_pb2.py", "migrations/0001_init.py", "README.md"]'
OUT="$(cd "$R/src" && bash -c "$FIX" 2>&1)"; echo "$OUT" | sed 's/^/    | /'
has_f401 src/pkg/mod.py && fail "A: src/pkg/mod.py was not fixed" || pass "A: a changed file is fixed"
has_f401 "src/dir with space/my mod.py" && fail "A: path with spaces was not fixed" || pass "A: a path with spaces is fixed as one argument"
clean external/vendored.py && pass "A: a file excluded in pyproject.toml and named on the command line stays untouched (--force-exclude)" \
  || fail "A: external/vendored.py was rewritten"
clean migrations/0001_init.py && pass "A: migrations/ is never auto-fixed" || fail "A: migrations/0001_init.py was rewritten"
clean src/gen/thing_pb2.py && pass "A: generated *_pb2.py is never auto-fixed" || fail "A: src/gen/thing_pb2.py was rewritten"
clean src/other.py && pass "A: a file outside the changed set stays untouched" || fail "A: src/other.py was rewritten"
grep -q -- '--diff' "$RUFF_LOG" && pass "A: previews with --diff before writing" || fail "A: no --diff preview call"
grep -v -- '--force-exclude' "$RUFF_LOG" | grep -q . && fail "A: a ruff call lacked --force-exclude" || pass "A: every ruff call uses --force-exclude"
echo "$OUT" | grep -q 'Scope check: no files outside the changed set' && pass "A: reports a clean scope check" || fail "A: scope-check line missing"

# --- Case B: docs-only changed set -> ruff never runs ------------------------
reset_repo
state '["README.md", "docs/guide.md"]'
OUT="$(cd "$R" && bash -c "$FIX" 2>&1)"; echo "$OUT" | sed 's/^/    | /'
[ -s "$RUFF_LOG" ] && fail "B: ruff was invoked for a docs-only change" || pass "B: a docs-only changed set never invokes ruff"
[ -z "$(git -C "$R" status --porcelain)" ] && pass "B: nothing changed" || fail "B: the tree changed"
echo "$OUT" | grep -q 'SKIPPED (no Python files in the changed set)' && pass "B: says why it skipped" || fail "B: skip line missing"

# --- Case C: unknown changed set -> ruff never runs --------------------------
reset_repo
state '[]'
OUT="$(cd "$R" && bash -c "$FIX" 2>&1)"; echo "$OUT" | sed 's/^/    | /'
[ -s "$RUFF_LOG" ] && fail "C: ruff was invoked with an unknown changed set" || pass "C: an unknown changed set never invokes ruff"
echo "$OUT" | grep -q 'SKIPPED (changed set unknown)' && pass "C: says the changed set is unknown" || fail "C: skip line missing"

# --- Case D: a tracked leak is reverted, an untracked leak is only reported --
reset_repo
state '["src/pkg/mod.py"]'
OUT="$(cd "$R" && LEAK_TO="$R/src/other.py" LEAK_NEW="$R/src/leaked_new.py" bash -c "$FIX" 2>&1)"; echo "$OUT" | sed 's/^/    | /'
clean src/other.py && pass "D: a leaked change to a clean tracked file is reverted" || fail "D: src/other.py still differs from HEAD"
echo "$OUT" | grep -q 'LEAK:.*src/other.py (reverted)' && pass "D: the reverted leak is reported" || fail "D: reverted leak not reported"
[ -f "$R/src/leaked_new.py" ] && pass "D: an untracked leak is left in place" || fail "D: the untracked leak was deleted"
echo "$OUT" | grep -q 'src/leaked_new.py (untracked, left in place)' && pass "D: the untracked leak is reported" || fail "D: untracked leak not reported"

# --- Case E: a file that was already dirty and changes again is reported, not reverted
reset_repo
printf '# my own edit\n' >> "$R/src/dirty.py"
state '["src/pkg/mod.py"]'
OUT="$(cd "$R" && LEAK_TO="$R/src/dirty.py" bash -c "$FIX" 2>&1)"; echo "$OUT" | sed 's/^/    | /'
grep -q '^# my own edit$' "$R/src/dirty.py" && pass "E: the user's own uncommitted edit survives" || fail "E: the user's edit was lost"
echo "$OUT" | grep -q 'src/dirty.py (had uncommitted edits before; NOT reverted' && pass "E: the change is reported, not reverted" || fail "E: not reported as an unreverted leak"

# --- Case F: scoped formatting ----------------------------------------------
reset_repo
state '["src/pkg/fmt.py"]'
OUT="$(cd "$R" && bash -c "$FMT" 2>&1)"; echo "$OUT" | sed 's/^/    | /'
grep -q '^x = 1$' "$R/src/pkg/fmt.py" && pass "F: a changed file is formatted" || fail "F: src/pkg/fmt.py was not formatted"
clean src/other_fmt.py && pass "F: a file outside the changed set is not formatted" || fail "F: src/other_fmt.py was formatted"
grep -q 'format --check' "$RUFF_LOG" && pass "F: re-checks formatting after writing" || fail "F: no format --check call"
echo "$OUT" | grep -q 'Scope check: no files outside the changed set' && pass "F: reports a clean scope check" || fail "F: scope-check line missing"

echo
if [ "$fails" -eq 0 ]; then echo "check-ruff-scope: ALL PASS"; else echo "check-ruff-scope: $fails FAILED"; exit 1; fi
````

- [ ] **Step 3: Run both checks and watch them fail for the right reason**

From the repository root:

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-changed-set.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
bash "$CHECKS/check-ruff-scope.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
```

Expected (with your repository path in place of `<repo>`):

```
FAIL: snippet 'changed-set' not found in <repo>/.claude/Commands/workflow-commands/beads-post-execution.md
exit=1
FAIL: <repo>/.claude/Commands/workflow-commands/references/scoped-ruff.md does not exist
exit=1
```

- [ ] **Step 4: Create the write-scope rule**

Create `.claude/rules/verification-write-scope.md` with exactly this content. It is loaded into every session, so it holds only the policy; the two runnable blocks it points to live in a reference file that loads only when a step runs them (Step 4b). <!-- Refined: Architecture -->

````markdown
# Verification Writes Only What the Task Changed

**Section:** Verification (always loaded)

## Read Wide, Write Narrow

Verification may **read** anything. Analysis, search and review can look at the
whole project. Anything that **writes** — `ruff check --fix`, `ruff format`, an
edit a review agent proposes — touches only the task's **changed set**: the paths
in `modified_files` in `.beads/.session-state.json`, which
`workflow-commands:beads-post-execution` Step 2a records.

- **Changed set unknown → no auto-fix.** When the session state is missing or
  unreadable, or `modified_files` is empty, skip every automatic fix and say so in
  the report: `Auto-fixed: SKIPPED (changed set unknown)`. Never widen to the
  project root, and never ask the user for a file list just to justify a fix. A
  list the user volunteers is a valid changed set; echo it back in the report.
- **Never auto-fixed, even inside the changed set:** anything under `.venv/`,
  `vendor/` or `third_party/`; generated code (for example `*_pb2.py`); and
  `migrations/`, which is a protected path in this workflow. Notebooks (`.ipynb`)
  are linted and reported, never rewritten.
- **One exception for tests:** Phase 12 may create new test files under `tests/`
  that mirror a module in the changed set. It adds each one to `modified_files`,
  so the write blocks cover it — never pass a file list to a block instead.
- **A whole-project cleanup is its own task**, with its own bead and its own
  review — never a side effect of verifying something else.

## Why

Observed in a downstream project: an unscoped auto-fix during verification
rewrote 17 files, including read-only exports and a dependency manifest. Because
"ship it" stages every changed file (`Git Best Practices/protect_plans_and_commit_all.md`
Rule 3), a fix like that rides into an unrelated commit under a message about
something else.

## The Write Sequence

Every step that rewrites files runs one of two blocks, unchanged: `scoped-ruff-fix`
for lint fixes, `scoped-ruff-format` for formatting. Both live in
`.claude/Commands/workflow-commands/references/scoped-ruff.md`, which loads only when a step
needs it: open it and run the block exactly as written — never retype or
paraphrase it. Each block reads the changed set itself, keeps only the files that
are safe to rewrite, and never calls ruff with an empty file list
(`ruff check --fix` with no paths rewrites the whole project). Then it:

1. snapshots `git status`;
2. previews the lint fixes with `ruff check --diff`, which writes nothing (lint
   block only);
3. writes, with `--force-exclude`, because ruff ignores the project's own
   `exclude` settings for files named on the command line unless that flag is set;
4. compares `git status` with the snapshot. A tracked file outside the changed set
   that changed was clean before, so it is restored with
   `git checkout HEAD -- <path>` (nothing is lost) and reported. An untracked file
   that appeared is reported and left for the user to decide about. A file outside
   the set that already had uncommitted edits and changed again is reported, never
   reverted.

Report what they print in the verification report:

- `Auto-fixed: N across M changed files` (N from ruff's own summary), or
  `Auto-fixed: SKIPPED (changed set unknown)`, or
  `Auto-fixed: SKIPPED (no Python files in the changed set)`;
- `Scope check: no files outside the changed set`, or `Scope check: LEAK: [list]`.
````

- [ ] **Step 4b: Create the runnable write blocks**

<!-- Refined: Architecture -->
Create `.claude/Commands/workflow-commands/references/scoped-ruff.md` with exactly this content. It sits next to `refinement-methodology.md`, the template's home for shared reference material, and like that file it also appears as a skill (`workflow-commands:references:scoped-ruff`); nothing loads it until a step runs one of its blocks.

````markdown
# Scoped Ruff Blocks

**This is a reference, not a slash command.** It holds the two runnable blocks that
`.claude/rules/verification-write-scope.md` requires every auto-fix and format step
to use: P02, and the verification tiers' Phase 2 (plus, in the full tier, Phases 8.5
and 12.5). Run a block exactly as written, from anywhere inside the repository.
Each block reads the changed set (`modified_files` in `.beads/.session-state.json`)
itself; to cover a file the task added later, such as a test Phase 12 created, add
it to `modified_files` first — never pass a file list. The two blocks differ only in
their `SCOPED_RUFF_MODE=` line; keep them identical otherwise.

## Lint auto-fix

```bash
# snippet: scoped-ruff-fix
cd "$(git rev-parse --show-toplevel)" || exit 1
SCOPED_RUFF_MODE=fix python3 - <<'PY'
import hashlib, json, os, subprocess, sys
from pathlib import Path

MODE = os.environ["SCOPED_RUFF_MODE"]
NEVER = ("/.venv/", "/vendor/", "/third_party/", "/migrations/")
GENERATED = ("_pb2.py", "_pb2_grpc.py", "_pb2.pyi")

def status():
    raw = subprocess.run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                         capture_output=True, check=True).stdout.decode().split("\0")
    entries, i = {}, 0
    while i < len(raw) and raw[i]:
        entries[raw[i][3:]] = raw[i][:2]
        i += 2 if raw[i][0] in "RC" else 1  # a rename is followed by its old path
    return entries

def digest(path):
    try:
        return hashlib.sha1(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None

try:
    changed = json.loads(Path(".beads/.session-state.json").read_text()).get("modified_files") or []
except (OSError, ValueError, AttributeError):
    changed = []
if not changed:
    print("Auto-fixed: SKIPPED (changed set unknown)")
    sys.exit(0)
files = [p for p in changed
         if p.endswith((".py", ".pyi")) and not p.endswith(GENERATED)
         and not any(d in "/" + p for d in NEVER) and Path(p).is_file()]
notebooks = [p for p in changed if p.endswith(".ipynb") and Path(p).is_file()]

before = status()
hashes = {p: digest(p) for p in before if p not in files}
if notebooks:  # report only: lint or check, never write
    check = ["check", "--no-fix"] if MODE == "fix" else ["format", "--check"]
    subprocess.run(["ruff", *check, "--force-exclude", "--", *notebooks])
if not files:
    print("Auto-fixed: SKIPPED (no Python files in the changed set)")
    sys.exit(0)
if MODE == "fix":
    subprocess.run(["ruff", "check", "--diff", "--force-exclude", "--", *files])
    subprocess.run(["ruff", "check", "--fix", "--force-exclude", "--", *files])
else:
    subprocess.run(["ruff", "format", "--force-exclude", "--", *files])
    subprocess.run(["ruff", "format", "--check", "--force-exclude", "--", *files])

leaks = []
for path, xy in status().items():
    if path in files:
        continue
    if path not in before:
        if xy == "??":
            leaks.append(f"{path} (untracked, left in place)")
        else:
            subprocess.run(["git", "checkout", "HEAD", "--", path], check=True)
            leaks.append(f"{path} (reverted)")
    elif digest(path) != hashes.get(path):
        leaks.append(f"{path} (had uncommitted edits before; NOT reverted, review it)")
print(f"Auto-fix ran on {len(files)} changed file(s).")
print("Scope check: no files outside the changed set" if not leaks
      else "Scope check: LEAK: " + "; ".join(leaks))
PY
```

## Formatting

The same block in format mode: it writes with `ruff format`, then re-checks with
`ruff format --check`.

```bash
# snippet: scoped-ruff-format
cd "$(git rev-parse --show-toplevel)" || exit 1
SCOPED_RUFF_MODE=format python3 - <<'PY'
import hashlib, json, os, subprocess, sys
from pathlib import Path

MODE = os.environ["SCOPED_RUFF_MODE"]
NEVER = ("/.venv/", "/vendor/", "/third_party/", "/migrations/")
GENERATED = ("_pb2.py", "_pb2_grpc.py", "_pb2.pyi")

def status():
    raw = subprocess.run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                         capture_output=True, check=True).stdout.decode().split("\0")
    entries, i = {}, 0
    while i < len(raw) and raw[i]:
        entries[raw[i][3:]] = raw[i][:2]
        i += 2 if raw[i][0] in "RC" else 1  # a rename is followed by its old path
    return entries

def digest(path):
    try:
        return hashlib.sha1(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None

try:
    changed = json.loads(Path(".beads/.session-state.json").read_text()).get("modified_files") or []
except (OSError, ValueError, AttributeError):
    changed = []
if not changed:
    print("Auto-fixed: SKIPPED (changed set unknown)")
    sys.exit(0)
files = [p for p in changed
         if p.endswith((".py", ".pyi")) and not p.endswith(GENERATED)
         and not any(d in "/" + p for d in NEVER) and Path(p).is_file()]
notebooks = [p for p in changed if p.endswith(".ipynb") and Path(p).is_file()]

before = status()
hashes = {p: digest(p) for p in before if p not in files}
if notebooks:  # report only: lint or check, never write
    check = ["check", "--no-fix"] if MODE == "fix" else ["format", "--check"]
    subprocess.run(["ruff", *check, "--force-exclude", "--", *notebooks])
if not files:
    print("Auto-fixed: SKIPPED (no Python files in the changed set)")
    sys.exit(0)
if MODE == "fix":
    subprocess.run(["ruff", "check", "--diff", "--force-exclude", "--", *files])
    subprocess.run(["ruff", "check", "--fix", "--force-exclude", "--", *files])
else:
    subprocess.run(["ruff", "format", "--force-exclude", "--", *files])
    subprocess.run(["ruff", "format", "--check", "--force-exclude", "--", *files])

leaks = []
for path, xy in status().items():
    if path in files:
        continue
    if path not in before:
        if xy == "??":
            leaks.append(f"{path} (untracked, left in place)")
        else:
            subprocess.run(["git", "checkout", "HEAD", "--", path], check=True)
            leaks.append(f"{path} (reverted)")
    elif digest(path) != hashes.get(path):
        leaks.append(f"{path} (had uncommitted edits before; NOT reverted, review it)")
print(f"Auto-fix ran on {len(files)} changed file(s).")
print("Scope check: no files outside the changed set" if not leaks
      else "Scope check: LEAK: " + "; ".join(leaks))
PY
```
````

- [ ] **Step 5: Replace beads-post-execution Step 2 with Step 2a + Step 2b**

In `.claude/Commands/workflow-commands/beads-post-execution.md`, replace everything from the heading `## Step 2: Level Detection` up to (not including) the heading `## Step 3: Build Validator Check` with:

````markdown
## Step 2: Record the Changed Set, Then Pick the Level

### Step 2a: Record the changed set first (never skip this)

Nothing else in the workflow writes `modified_files`.
`workflow-commands:beads-start-task` creates `.beads/.session-state.json` with an
empty list, and every verification skill only reads it. Left empty, every task
would route to Quick (because `total_lines_changed` stays 0) and every scoped
auto-fix would be skipped. So derive the changed set here, once. It is:

- tracked files with uncommitted edits, staged or not (deleted files are left out);
- untracked files (nested repositories and worktrees are left out);
- files the branch changed since it left the trunk, that is since
  `git merge-base <trunk> HEAD`.

Workflow state under `.beads/` is not task work, so it is left out too, and a
renamed file is recorded under its new path. `total_lines_changed` covers the same
range (lines added plus lines removed) plus the full length of every untracked
file. The trunk is whatever `origin/HEAD` points at, normally `origin/main` or
`origin/master`; when that is unset, the block asks git to set it once. When the
repository has no `origin` at all, the branch's own commits cannot be measured,
so the block records the uncommitted and untracked files and says the branch
range was skipped.

Run the block from anywhere inside the repository. It rewrites only
`modified_files` (a plain list of path strings) and `total_lines_changed`, and
keeps every other key in the file (`task_id`, `plan_file`, `verification`, …):

```bash
# snippet: changed-set
cd "$(git rev-parse --show-toplevel)" || exit 1
trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null) || {
  git remote set-head origin --auto >/dev/null 2>&1
  trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
}
base=""
[ -n "$trunk" ] && base=$(git merge-base "$trunk" HEAD 2>/dev/null)
if [ -z "$base" ]; then
  echo "Changed set: branch range skipped (no trunk to compare with) - uncommitted and untracked files only."
  base=$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)
fi
BASE="$base" python3 - <<'PY'
import json, os, subprocess
from pathlib import Path

def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout.decode()

def keep(path):
    return bool(path) and not path.endswith("/") and not path.startswith(".beads/")

base = os.environ["BASE"]
tracked = {p for p in git("diff", "--name-only", "-z", "--diff-filter=d", base).split("\0") if keep(p)}
untracked = {p for p in git("ls-files", "--others", "--exclude-standard", "-z").split("\0") if keep(p)}
added = {p for p in git("diff", "--name-only", "-z", "--diff-filter=A", base).split("\0") if keep(p)}

lines, parts, i = 0, git("diff", "--numstat", "-z", base).split("\0"), 0
while i < len(parts) and parts[i]:
    plus, minus, path = parts[i].split("\t", 2)
    if path:
        i += 1
    else:  # a rename or copy: the old path, then the new path, follow
        path, i = parts[i + 2], i + 3
    if keep(path) and plus != "-":  # "-" marks a binary file
        lines += int(plus) + int(minus)
for path in untracked:
    try:
        data = Path(path).read_bytes()
    except OSError:
        continue
    if b"\0" not in data[:8000]:  # skip binary files
        lines += data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)

files = sorted(tracked | untracked)
new_modules = sorted(p for p in added | untracked if p.startswith("src/") and p.endswith(".py"))

state_path = Path(".beads/.session-state.json")
try:
    state = json.loads(state_path.read_text())
except (OSError, ValueError):
    state = {}
if not isinstance(state, dict):
    state = {}
state["modified_files"] = files
state["total_lines_changed"] = lines
state_path.parent.mkdir(exist_ok=True)
tmp = state_path.with_name(state_path.name + ".tmp")
tmp.write_text(json.dumps(state, indent=2) + "\n")
tmp.replace(state_path)

print(f"Changed set: {len(files)} file(s), {lines} line(s) changed")
for path in files:
    print(f"  {path}")
print("New modules under src/: " + (", ".join(new_modules) if new_modules else "none"))
PY
```

The block reads a possibly-dirty tree, so it can pick up unrelated
work-in-progress. That is accepted here, and only here: it runs once, at the point
where this task is what dirtied the tree, and it prints the list so you can see
what it caught. A verification skill never re-derives the set; when the set is
unknown it skips its auto-fix instead (`.claude/rules/verification-write-scope.md`).

### Step 2b: Pick the level

Read `modified_files` and `total_lines_changed` back from
`.beads/.session-state.json`, then:

- **Under 50 lines:** Quick (lint + tests)
- **50–200 lines:** Standard (analysis phases, no agents)
- **Over 200 lines, or a new module under `src/`:** Full (review agents + Codex
  adversarial pass). Step 2a prints the new modules it found. A new test file on
  its own does not force Full.

If `modified_files` is still empty after Step 2a (outside a git repository, or a
genuinely clean tree), ask:
> What files did you change? (Or say "quick", "standard", or "full" to select level)

This question only picks the level. Never ask it in order to justify running an
auto-fix. If the answer names files, that list becomes the changed set: write it
into `modified_files` (read the file, change that one key, write it back) and echo
it back in the invoked skill's report, as the router's *Named Scope Is
Authorization* section allows. If the answer names only a level, the changed set
stays **unknown**, and the invoked skill skips its auto-fix rather than widening
it to the project root.
````

- [ ] **Step 6: Step 5 prompt: say where the change size comes from**

In `.claude/Commands/workflow-commands/beads-post-execution.md`, find this exact text:

```markdown
Changes: [N] lines across [M] files (tracked during execution)
```

and replace it with:

```markdown
Changes: [N] lines across [M] files (recorded in Step 2a)
```

- [ ] **Step 7: Step 5 prompt: describe Full without a phase count**

In `.claude/Commands/workflow-commands/beads-post-execution.md`, find this exact text:

```markdown
3. **Full verify** — all 14 phases with agents (~5+ min)
```

and replace it with:

```markdown
3. **Full verify** — review agents + Codex adversarial pass (~5+ min)
```

- [ ] **Step 8: Run both checks and watch them pass**

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-changed-set.sh" "$(git rev-parse --show-toplevel)" | grep -E '^(PASS|FAIL)|^check-'
bash "$CHECKS/check-ruff-scope.sh" "$(git rev-parse --show-toplevel)" | grep -E '^(PASS|FAIL)|^check-'
```

Expected: 10 `PASS:` lines then `check-changed-set: ALL PASS`, and 24 `PASS:` lines then `check-ruff-scope: ALL PASS`. No `FAIL:` line. Each check also prints the block's own output, indented with `|`, when run without the `grep`.

- [ ] **Step 9: P02 Step 1: analyse wide, decide writes later**

In `.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md`, replace everything from the heading `### Step 1: Run Static Analysis` up to (not including) the heading `### Step 2: Run Dead Code Analysis` with:

````markdown
### Step 1: Run Static Analysis
Analysis only reads, so it may look wide; what it may *write* is decided in
Step 4. Choose the files to analyse in this order:

1. the path given as the argument above, if there is one;
2. otherwise the task's changed set, `modified_files` in
   `.beads/.session-state.json`;
3. otherwise, as a last resort, the whole project (`src/ tests/`).

Reading the whole project never widens the write scope. Step 4's auto-fix is
still limited to the changed set, and is skipped entirely when the changed set is
unknown (`.claude/rules/verification-write-scope.md`).

```bash
# Lint errors and warnings (read-only)
ruff check <files to analyse>

# Type checking (read-only)
mypy <files to analyse>
```
````

- [ ] **Step 10: P02 Step 2: dead-code findings outside the set are reported, not fixed**

In `.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md`, find this exact text (it occurs once):

```markdown
- `__dunder__` methods (excluded by convention)
```

and replace it with the same text followed by the new lines:

```markdown
- `__dunder__` methods (excluded by convention)

Dead-code findings in files outside the changed set are reported, never fixed:
record them, and if one matters, open a bead for it.
```

- [ ] **Step 11: P02 Step 4: run the scoped lint block**

In `.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md`, replace everything from the heading `### Step 4: Auto-Fix Where Possible` up to (not including) the heading `### Step 5: Manual Fixes` with:

```markdown
### Step 4: Auto-Fix — scoped to the changed set, or skipped
Never auto-fix outside the task's changed set. Run the `scoped-ruff-fix` block
from `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged (the policy it
implements is `.claude/rules/verification-write-scope.md`). In short, it:

- reads the changed set and keeps only the Python files that are safe to rewrite
  (nothing under `.venv/`, `vendor/`, `third_party/` or `migrations/`, no
  generated `*_pb2.py`; notebooks are linted but never rewritten);
- skips entirely, without calling ruff, when the changed set is unknown or holds
  no Python files — it never widens to the project root;
- previews with `ruff check --diff`, applies `ruff check --fix --force-exclude` to
  those files only, then compares `git status` with its snapshot and restores and
  reports any file outside the set that changed.

It typically resolves unused imports, import sorting and simple style issues.

A whole-project cleanup is legitimate, but as its own task with its own bead and
its own review — never as a side effect of fixing something else.
```

- [ ] **Step 12: P02 Step 5: manual fixes stay inside the changed set**

In `.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md`, find this exact text:

```markdown
Address remaining issues one by one:
```

and replace it with:

```markdown
Address the remaining issues in the changed set one by one (an issue in a file
outside the changed set is reported, not fixed):
```

Leave the numbered list under it alone: Task 1 already fixed its item 3.

- [ ] **Step 13: P02 Step 5: dead code is only removed inside the changed set**

In `.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md`, find this exact text (it occurs once):

```markdown
**For vulture unused code:**
```

and replace it with the same text followed by the new lines:

```markdown
**For vulture unused code:**
- Only remove code in files inside the changed set; a finding anywhere else is
  recorded in the report (and, if it matters, filed as its own bead), never fixed
  here
```

- [ ] **Step 14: P02 Step 6: format through the scoped formatting block**

In `.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md`, replace everything from the heading `### Step 6: Format and Verify` up to (not including) the heading `## Priority Guidelines` with:

```markdown
### Step 6: Format and Verify
1. Format with the `scoped-ruff-format` block from
   `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged. It formats only the changed set's
   Python files with `ruff format --force-exclude`, re-checks them with
   `ruff format --check`, and reports anything that changed outside the set.
2. Run a final `ruff check --force-exclude` on the files from Step 1 to confirm
   the lint issues are resolved.
3. Re-run `mypy` on the same files to confirm the type errors are resolved.
4. Optionally re-run `vulture src/` (read-only) to confirm the unused code is gone.
5. Report a summary of the fixes applied, including the blocks' `Auto-fixed:` and
   `Scope check:` lines.
```

- [ ] **Step 15: P02 tools list: mark what reads and what writes**

In `.claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md`, replace everything from the heading `## Tools to Use` up to (not including) the heading `## Important Notes` with:

```markdown
## Tools to Use
- Bash: `ruff check <files>` — Python lint analysis (read-only, may run wide)
- Bash: the `scoped-ruff-fix` block from `.claude/Commands/workflow-commands/references/scoped-ruff.md` — automatic fixes, changed set only
- Bash: the `scoped-ruff-format` block from the same file — formatting, changed set only
- Bash: `mypy <files>` — type checking (read-only)
- Bash: `vulture src/` — detect unused code (read-only)
- Bash: `ruff check --select F401 src/` — detect unused imports (read-only)
- Grep/Glob — for targeted code search and pattern matching
- Read/Edit — for targeted code modifications inside the changed set
```

- [ ] **Step 16: Quick Phase 1: define the UNKNOWN changed set**

In `.claude/Commands/workflow-commands/python-verification-quick.md`, find this exact text:

```markdown
1. Read `modified_files` from `.beads/.session-state.json`
2. Calculate `total_lines_changed` from session state
3. If session state unavailable, ask user for file list
```

and replace it with:

```markdown
1. Read `modified_files` from `.beads/.session-state.json`
2. Read `total_lines_changed` from the same file
3. If the file is missing or unreadable, **or** `modified_files` is an empty list,
   the changed set is **UNKNOWN**. Do not ask the user for a file list in order to
   auto-fix, and do not fall back to the project root: Phase 2 Step 2 skips
   instead (`.claude/rules/verification-write-scope.md`). A list the user
   volunteers unprompted is a valid changed set; echo it back in the report.
```

- [ ] **Step 17: Quick Phase 2 Step 1: analysis may read wide when the set is unknown**

In `.claude/Commands/workflow-commands/python-verification-quick.md`, find this exact text:

```markdown
Run ruff and mypy on changed files only:
```

and replace it with:

```markdown
Run ruff and mypy on the changed files. Analysis only reads, so when the changed
set is UNKNOWN, run the same two commands on `src/ tests/` instead:
```

- [ ] **Step 18: Quick Phase 2 Step 2: run the scoped lint block**

In `.claude/Commands/workflow-commands/python-verification-quick.md`, replace everything from the heading `### Step 2: Auto-Fix` up to (not including) the heading `### Step 3: Report Remaining Issues` with:

```markdown
### Step 2: Auto-Fix — scoped to the changed set, or skipped

Never auto-fix outside the task's changed set. Run the `scoped-ruff-fix` block
from `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged (policy:
`.claude/rules/verification-write-scope.md`). In short, it reads the changed set; skips without calling ruff when the
set is UNKNOWN or holds no Python files; previews with `ruff check --diff`, a dry
run that writes nothing; applies `ruff check --fix --force-exclude` to the changed
Python files only (`--force-exclude` keeps ruff's own exclude list in force for
files named on the command line); and then compares `git status` with its
snapshot, restoring and reporting any file outside the set that changed.

Record its `Auto-fixed:` and `Scope check:` lines in the report.
```

- [ ] **Step 19: Quick report: auto-fix and scope-check lines**

In `.claude/Commands/workflow-commands/python-verification-quick.md`, find this exact text:

```markdown
**Auto-fixed:** [N] issues with ruff --fix
```

and replace it with:

```markdown
**Auto-fixed:** [N] issues across [M] changed files
*(or:* `SKIPPED (changed set unknown)` *or* `SKIPPED (no Python files in the changed set)` *)*
**Scope check:** no files outside the changed set / **LEAK: [list]**
```

- [ ] **Step 20: Quick reference: the scoped auto-fix and the unknown-set row**

In `.claude/Commands/workflow-commands/python-verification-quick.md`, find this exact text:

```markdown
| Auto-fix | `ruff check --fix <files>` via Bash |
| Run tests | `pytest <files> -v` via Bash |
| Track files | `.beads/.session-state.json` |
```

and replace it with:

```markdown
| Auto-fix | the `scoped-ruff-fix` block from `.claude/Commands/workflow-commands/references/scoped-ruff.md` — changed set only, never unscoped |
| Run tests | `pytest <files> -v` via Bash |
| Track files | `.beads/.session-state.json` (`modified_files`) |
| Changed set unknown | Skip auto-fix. Never widen to the project root. |
```

- [ ] **Step 21: Standard Phase 1 Step 1: define the UNKNOWN changed set**

In `.claude/Commands/workflow-commands/python-verification-standard.md`, find this exact text:

```markdown
- Read `modified_files` from `.beads/.session-state.json`
- If session state unavailable, ask user for file list
- Note which directories/layers were affected
- **Scope all subsequent phases to ONLY these files**
```

and replace it with:

```markdown
- Read `modified_files` from `.beads/.session-state.json`
- If the file is missing or unreadable, **or** `modified_files` is empty, the
  changed set is **UNKNOWN**. You may ask the user for a file list to guide the
  review phases, but Phase 2's auto-fix is skipped in this state — never widened
  to the project root (`.claude/rules/verification-write-scope.md`). A list the
  user volunteers is a valid changed set; echo it back in the report.
- Note which directories/layers were affected
- **Scope all subsequent phases to ONLY these files**: the review phases report
  only on them, and nothing outside them is ever written
```

- [ ] **Step 22: Standard Phase 2 Step 1: analysis may read wide when the set is unknown**

In `.claude/Commands/workflow-commands/python-verification-standard.md`, find this exact text:

```markdown
Run ruff and mypy on changed files only:
```

and replace it with:

```markdown
Run ruff and mypy on the changed files. Analysis only reads, so when the changed
set is UNKNOWN, run the same two commands on `src/ tests/` instead:
```

- [ ] **Step 23: Standard Phase 2 Step 3: replace the bare `ruff check --fix`**

In `.claude/Commands/workflow-commands/python-verification-standard.md`, replace everything from the heading `### Step 3: Auto-Fix` up to (not including) the heading `### Step 4: Manual Fixes (if needed)` with:

```markdown
### Step 3: Auto-Fix — scoped to the changed set, or skipped

Never auto-fix outside the task's changed set. Run the `scoped-ruff-fix` block
from `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged (policy:
`.claude/rules/verification-write-scope.md`) — never a bare `ruff check --fix`, which rewrites every file it can
reach. In short, the block reads the changed set; skips without calling ruff when
the set is UNKNOWN or holds no Python files; previews with `ruff check --diff`;
applies `ruff check --fix --force-exclude` to the changed Python files only; and
compares `git status` with its snapshot, restoring and reporting any file outside
the set that changed.

It typically resolves unused imports, import sorting, simple style issues and
trailing whitespace. Record the block's `Auto-fixed:` and `Scope check:` lines in
the report.
```

- [ ] **Step 24: Standard Phase 2 Step 4: manual fixes stay inside the changed set**

In `.claude/Commands/workflow-commands/python-verification-standard.md`, find this exact text:

```markdown
Address remaining errors and warnings:
```

and replace it with:

```markdown
Address the remaining errors and warnings in the changed files (an issue in a
file outside the changed set is reported, not fixed):
```

- [ ] **Step 25: Standard report: auto-fix and scope-check lines**

In `.claude/Commands/workflow-commands/python-verification-standard.md`, find this exact text:

```markdown
### Lint Results (Phase 2)
**Auto-fixed:** [N] issues
```

and replace it with:

```markdown
### Lint Results (Phase 2)
**Auto-fixed:** [N] issues across [M] changed files
*(or:* `SKIPPED (changed set unknown)` *or* `SKIPPED (no Python files in the changed set)` *)*
**Scope check:** no files outside the changed set / **LEAK: [list]**
```

- [ ] **Step 26: P14 Step 1: read `modified_files` as plain strings**

In `.claude/Commands/workflow-commands/P14-security-review-[SF].md`, find this exact text:

```markdown
cat .beads/.session-state.json | jq '.modified_files[].path'
```

and replace it with:

```markdown
cat .beads/.session-state.json | jq -r '.modified_files[]'
```

`-r` prints each path raw, so a path with spaces comes out as-is rather than as a quoted JSON string.

- [ ] **Step 27: Confirm no unscoped write survives in this part's files**

Run from the repository root:

```bash
R="$(git rev-parse --show-toplevel)"; C="$R/.claude/Commands/workflow-commands"; bad=0
grep -n -E '^[[:space:]]*ruff (check --fix|format )' "$C/python-verification-quick.md" "$C/python-verification-standard.md" "$C/P02-lint-issues-fix-[QSF].md" && bad=1
grep -rn --exclude-dir=worktrees 'modified_files\[\]\.path' "$R/.claude" && bad=1
for f in python-verification-quick.md python-verification-standard.md "P02-lint-issues-fix-[QSF].md" beads-post-execution.md; do
  grep -q 'verification-write-scope.md' "$C/$f" || { echo "no rule citation in $f"; bad=1; }
done
for f in python-verification-quick.md python-verification-standard.md "P02-lint-issues-fix-[QSF].md"; do
  grep -q 'references/scoped-ruff.md' "$C/$f" || { echo "no block-file citation in $f"; bad=1; }
done
grep -q '# snippet: scoped-ruff-fix' "$C/references/scoped-ruff.md" || { echo "block file missing scoped-ruff-fix"; bad=1; }
grep -q '# snippet:' "$R/.claude/rules/verification-write-scope.md" && { echo "the always-loaded rule still holds a runnable block"; bad=1; }
grep -q 'Named Scope Is' "$C/beads-post-execution.md" || { echo "post-execution: Named Scope citation missing"; bad=1; }
grep -n 'all 14 phases' "$C/beads-post-execution.md" && bad=1
[ "$bad" -eq 0 ] && echo "Task 2 part A: OK"
```

Expected: exactly one line, `Task 2 part A: OK`. Before this task the same command listed the bare `ruff check --fix` / `ruff format` lines in quick and P02, the `.path` jq filter in P14, five missing citations and the two "all 14 phases" lines in beads-post-execution.

#### Part B: `python-verification-full.md` — the write scope (W2)

**Files:**
- Modify: `.claude/Commands/workflow-commands/python-verification-full.md` — Phase 1 Step 1 (the changed set and the unknown-set rule), Phase 2 Step 3 (scoped auto-fix), Phase 12.5 Step 1 (scoped format), two Phase 13 report lines, Scope Control (split into a read scope and a write scope), Phase 8.5 steps 5–6, and one line of the execution-flow diagram.

**Interfaces:**
- Consumes: `.claude/rules/verification-write-scope.md` and its two sequences, `scoped-ruff-fix` and `scoped-ruff-format` (written in Part A of this task); `modified_files` as a plain list of path strings in `.beads/.session-state.json`, recorded by `workflow-commands:beads-post-execution` Step 2a (Part A).
- Produces: the `CHANGED_SET = UNKNOWN` rule used across this file; the report strings `Auto-fixed: [N] issues across [M] changed files`, `SKIPPED (changed set unknown)`, `no files outside the changed set changed` and `LEAK: [list]`; the `### Read scope` and `### Write scope` subsections, which Task 3 edits.

Anchors in this part are headings and lines that Task 1 does not change. Every step edits the same file, top to bottom.

- [ ] **Step 1: Phase 1 Step 1 — read the changed set; define the unknown-set rule**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading `### Step 1: Identify Changed Files` up to (not including) the heading `### Step 2: Gather Relevant Rules` with:

```markdown
### Step 1: Identify Changed Files
- Read `modified_files` from `.beads/.session-state.json`. That list is the
  task's changed set, recorded by `workflow-commands:beads-post-execution` in
  its Step 2a: uncommitted edits to tracked files (deletions excluded),
  untracked files, and the files this branch changed since it left the trunk.
- If the file is missing or unreadable, or `modified_files` is empty, set
  `CHANGED_SET = UNKNOWN`. You may ask which files to look at, to steer the
  review phases, but the answer only decides what gets read, never what gets
  written: Phase 2 Step 3, Phase 8.5 step 6 and Phase 12.5 step 1 skip their
  writes in this state and say so in the report, and nothing ever widens to
  the project root. A file list the user volunteers without being asked is a
  valid changed set: echo it back, then use it.
- Note which directories/layers were affected
- **Scope all subsequent phases to ONLY these files**, for reading and writing
  alike (see Scope Control)
```

- [ ] **Step 2: Phase 2 Step 3 — scoped auto-fix, or skipped**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading `### Step 3: Auto-Fix` up to (not including) the heading `### Step 4: Manual Fixes (if needed)` with:

```markdown
### Step 3: Auto-Fix — scoped to the changed set, or skipped

The binding rule is `.claude/rules/verification-write-scope.md`, which is
always loaded; follow it exactly. Run the `scoped-ruff-fix` block from
`.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged: it reads the changed
set itself, drops deleted files and the paths the rule never auto-fixes, and
skips without calling ruff when nothing is left. In short:

1. Snapshot `git status --short`.
2. Preview with `ruff check --diff --force-exclude <files>`, which writes
   nothing.
3. Fix with `ruff check --fix --force-exclude <files>`.
4. Compare `git status --short` with the snapshot. A tracked file outside the
   changed set that moved is reverted with `git checkout HEAD -- <path>` and
   reported; an untracked file that appeared is reported, never deleted
   without approval.

`--force-exclude` is required because ruff ignores its own `exclude` settings
for files named on the command line. Never run ruff with an empty file list: a
bare `ruff check --fix` rewrites the whole project. If no Python file is left
after filtering, or `CHANGED_SET = UNKNOWN`, skip this step and say so in the
report.

Typically resolves: unused imports, import sorting, and simple style fixes.
```

- [ ] **Step 3: Phase 12.5 Step 1 — format only the test files Phase 12 touched**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Phase 12.5: Run New Tests`, replace the line:

```text
3. Run `ruff format <test_files>` via Bash to normalize formatting
```

with:

```markdown
3. First add every test file Phase 12 created to `modified_files` in
   `.beads/.session-state.json` (read the file, extend that one list, write it
   back): the rule lets Phase 12 create mirrored tests, and from then on they
   are part of the task's changes. Then run the `scoped-ruff-format` block from
   `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged — it formats the
   changed set (now including those tests) and re-checks it, with the leak check.
```

- [ ] **Step 4: Phase 13 report — the auto-fix and leak-check lines**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Phase 13: Comprehensive Verification Report`, replace the line `- Auto-fixed: [N] issues with ruff check --fix` with:

```markdown
- Auto-fixed: [N] issues across [M] changed files
  *(or:* `SKIPPED (changed set unknown)` *)*
- Scope check: no files outside the changed set changed
  *(or:* **LEAK: [list]** *, with what was reverted and what was only reported)*
```

- [ ] **Step 5: Phase 13 report — the lint line under Checks Completed**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Phase 13: Comprehensive Verification Report`, replace the line `- Lint issues (analyzed and auto-fixed)` with:

```markdown
- Lint issues (analyzed; auto-fixed inside the changed set only)
```

- [ ] **Step 6: Scope Control — split into a read scope and a write scope**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading `## Scope Control` up to (not including) the heading `## Auto-Skip Logic (Session State Based)` with:

```markdown
## Scope Control

**Critical:** All phases operate ONLY on the changed set identified in Phase 1,
for reading AND for writing. The binding rule is
`.claude/rules/verification-write-scope.md`: read wide, write narrow.

### Read scope

- **Never scan the entire codebase for findings.** A phase may read other files
  for context, but it reports findings only for the changed set.
- Lint analysis: changed files only
- Code review: changed files only
- Architecture validation: changed files + immediate dependencies
- Simplification review: changed files only
- Type design analysis: new/modified types in changed files only
- Silent failure hunt: error handling in changed files only
- Comment analysis: comments in changed files only
- Test coverage: tests corresponding to changed source files in `src/` only

### Write scope

Anything that writes touches only files inside the changed set. That covers
`ruff check --fix`, `ruff format`, and every edit an agent proposes in Phases
6-8, 8.7 and 12:

- Phase 2 Step 3, Phase 8.5 step 6 and Phase 12.5 step 1 run the
  `scoped-ruff-fix` and `scoped-ruff-format` blocks from
  `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged: always with
  `--force-exclude`, never with an empty file list.
- An agent edit proposed for a file outside the changed set is reported, not
  applied.
- One exception: Phase 12 may create new test files under `tests/` that mirror
  a changed module, and adds each one to `modified_files` so the write blocks
  cover it.
- Never auto-fixed, even inside the changed set: `.venv/`, `vendor/`,
  `third_party/`, generated code such as `*_pb2.py`, and `migrations/` (a
  protected path). Notebooks (`.ipynb`) are linted and reported only.
- `CHANGED_SET = UNKNOWN` skips every write, and the report says so. Never
  widen to the project root, and never ask for a file list just to justify a
  fix.
- A whole-project cleanup is its own task, with its own bead and review.

**After every step that writes,** compare `git status --short` with the
snapshot taken before it. A tracked file outside the changed set that moved is
a leak: revert it with `git checkout HEAD -- <path>` (it was clean before, so
nothing is lost) and list it in the report. An untracked file outside the set
is reported, never deleted without approval.

---
```

The two bullets about architecture validation and simplification stay for now; Task 3 deletes them when it retires those phases.

- [ ] **Step 7: Phase 8.5 steps 5–6 — apply inside the changed set; scoped format**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `### Phase 8.5: Apply Agent Edits + Collect Codex Results`, replace the passage that begins with this line `5. **Apply non-conflicting edits** using the Edit tool` and ends with the line containing this text:

```text
6. **Run `ruff format`** to normalize formatting after edits
```

with:

```markdown
5. **Apply non-conflicting edits** using the Edit tool, to files inside the
   changed set only. An edit proposed for any other file is listed in the
   report, not applied (Scope Control, Write scope).
6. **Format inside the changed set only**: run the `scoped-ruff-format` block
   from `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged. It formats the
   changed set's Python files — which include every file step 5 may edit — and
   re-checks them with the leak check. Never a bare `ruff format`, which
   rewrites every file in the project. If step 5 edited no Python file, skip
   this.
```

- [ ] **Step 8: Execution-flow diagram — the Phase 8.5 box's format line**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Updated Execution Flow`, replace the line `| - Run ruff format to normalize      |` with:

```markdown
| - Scoped ruff format + leak check   |
```

Keep the line exactly 39 characters wide so the box stays aligned.

- [ ] **Step 9: Verify the write-scope edits**

Run from the repo root:

```bash
F=".claude/Commands/workflow-commands/python-verification-full.md"
grep -cE 'ruff check --fix <changed_files>|ruff format <test_files>|Run `ruff format`|issues with ruff check --fix' "$F"
for p in 'verification-write-scope.md' 'references/scoped-ruff.md' 'scoped-ruff-fix' 'scoped-ruff-format' 'CHANGED_SET = UNKNOWN' 'SKIPPED (changed set unknown)' 'Architecture validation: changed files + immediate dependencies'; do
  printf '%s: %s\n' "$p" "$(grep -cF -- "$p" "$F")"
done
grep -cF -- '--force-exclude' "$F"
```

Expected output, line for line:

```text
0
verification-write-scope.md: 2
references/scoped-ruff.md: 4
scoped-ruff-fix: 2
scoped-ruff-format: 3
CHANGED_SET = UNKNOWN: 3
SKIPPED (changed set unknown): 1
Architecture validation: changed files + immediate dependencies: 1
4
```
<!-- Refined: Architecture -->

The first `0` means no old unscoped write is left (bare `ruff format`, unscoped `ruff check --fix`). The architecture-validation bullet is still expected here; Task 3 removes it.

- [ ] **Finish 1: Confirm this task's change set**

```bash
git status --short
```
Expected: exactly the files in this task's **Files** list above (`M` modified, `??` new, `D` deleted), and nothing else — apart from a `?? .claude/worktrees/` line if that local folder holds a worktree, which is never staged. Anything else means a step touched the wrong file: find it with `git diff <path>` before staging.

- [ ] **Finish 2: Commit W2**

```bash
git add -- \
  ".claude/rules/verification-write-scope.md" \
  ".claude/Commands/workflow-commands/references/scoped-ruff.md" \
  ".claude/Commands/workflow-commands/beads-post-execution.md" \
  ':(literal).claude/Commands/workflow-commands/P02-lint-issues-fix-[QSF].md' \
  ':(literal).claude/Commands/workflow-commands/P14-security-review-[SF].md' \
  ".claude/Commands/workflow-commands/python-verification-quick.md" \
  ".claude/Commands/workflow-commands/python-verification-standard.md" \
  ".claude/Commands/workflow-commands/python-verification-full.md" && \
git diff --cached --stat && git commit -F- <<'EOF'
chore(workflow): verification writes only what the task changed

Add the always-loaded write-scope rule and the scoped ruff fix and format
blocks it points to (references/scoped-ruff.md); record the changed set in
beads-post-execution Step 2a; scope every auto-fix in P02 and the three tiers
to it, skipping when the set is unknown.

<attribution trailer>
EOF
```
Expected: the stat lists only this task's files, then the commit summary line. Replace `<attribution trailer>` with the attribution lines from your session's system reminder before running it.

- [ ] **Finish 3: Record the commit on the W2 bead**

```bash
source .beads/sgw-ids.env && bd update "$W2" --append-notes "Landed in $(git rev-parse --short HEAD): chore(workflow): verification writes only what the task changed" && bd show "$W2" | sed -n '1,20p'
```
Expected: the notes end with the "Landed in" line and the status is still `IN_PROGRESS` — all eight workstream beads close together when the PR opens (Task 9).

---

### Task 3: W3 — Trim verification, move the bug scan, fix the Codex pass

Spec: §6 W3; §7 (Python bug classes, including mutable defaults; the full tier keeps a fallback bug scan in Phase 7; Codex wording is model-neutral, the trunk comes from git and the companion is found by version).

**Files:**
- Modify: `.claude/Commands/workflow-commands/python-verification-standard.md`, `.claude/Commands/workflow-commands/python-verification-quick.md`, `.claude/Commands/workflow-commands/python-verification-full.md`
- Modify: `.claude/agents/verification-silent-failure.md` — new Step 1.5 bug scan
- Modify: `.claude/Commands/workflow-commands/hotfix-interrupt.md`, `.claude/Commands/workflow-commands/P14-security-review-[SF].md`
- Delete: `.claude/Commands/workflow-commands/P04-architecture-validation-[SF].md`, `.claude/Commands/workflow-commands/P05-code-simplification-[SF].md`

**Interfaces:**
- Consumes: Task 2's report-line formats, the write-scope rule and Step 2a's `modified_files`.
- Produces: one Phase 14 trigger list, identical in the standard tier, the full tier and P14; the five bug-scan classes in the agent and in the full tier's Phase 7 fallback; snippets `phase6-gate`, `codex-companion` and `codex-scope`; the hotfix trigger `Bug scan (Phase 7 in full, Phase 3 in standard)`.

Each part below lists its own files, interfaces and steps; run the parts in order, A first.

- [ ] **Start: mark the W3 bead in progress**

```bash
source .beads/sgw-ids.env && bd update "$W3" --status in_progress && bd show "$W3" | head -6
```
Expected: the bead shows `IN_PROGRESS`. (If `.beads/sgw-ids.env` is missing, Task 0 has not run.)

#### Part A: Retire P04/P05, move the bug scan into the agent, gate Phase 14 (all files except the full tier)

**Files:**
- Modify: `.claude/Commands/workflow-commands/python-verification-standard.md` — retirement note; bug-scan list aligned to the agent's classes; Phase 4 and Phase 5 removed; Phase 9 source; report blocks; Phase 14 gate with the widened triggers and its restored report-format block
- Modify: `.claude/Commands/workflow-commands/python-verification-quick.md` — Notes no longer mention architecture validation
- Modify: `.claude/agents/verification-silent-failure.md` — description and the new Step 1.5 bug scan
- Modify: `.claude/Commands/workflow-commands/hotfix-interrupt.md` — the bug-scan trigger names Phase 7 (full) and Phase 3 (standard)
- Modify: `.claude/Commands/workflow-commands/P14-security-review-[SF].md` — trigger list kept identical to the tiers' Phase 14 gate; `yaml.load` and database-authorization checks so every trigger has a check behind it
- Delete: `.claude/Commands/workflow-commands/P04-architecture-validation-[SF].md`
- Delete: `.claude/Commands/workflow-commands/P05-code-simplification-[SF].md`

**Interfaces:**
- Consumes: Task 2's report-line formats (unchanged here).
- Produces:
  - The Phase 14 trigger list. Part B's full-tier gate must carry the same paths and tokens: `src/**/auth/**`, `src/**/api/**`, `src/**/service*/**`, `src/**/repository/**`, `src/**/network/**`, `src/**/http/**`; `**/migrations/**`, `alembic/versions/**`, `**/*.sql`; settings modules (`**/settings.py`, `**/settings/**`); environment files (`.env`, `.env.*`); `apiKey`, `api_key`, `secret`, `token`, `password`, `credential`; `requests`, `httpx`, `http`; `eval(`, `exec(`, `pickle`, `yaml.load`, `subprocess`, `shell=True`, `verify=False`, `DEBUG`, `random.`; `GRANT`, `REVOKE`, `CREATE POLICY`, `ROW LEVEL SECURITY`, `SECURITY DEFINER`. Gate outcomes: `Skipped (no sensitive files)` / `Triggered (<matching files>)`; an UNKNOWN changed set counts as a match.
  - The five bug-scan classes in the agent's Step 1.5 (None handling, async misuse, resource lifecycle, shared mutable state, silent wrong results), which Part B's full-tier Phase 7 fallback step lists too.
  - The hotfix trigger line `Bug scan (Phase 7 in full, Phase 3 in standard): CRITICAL severity found`.

- [ ] **Step 1: Run this part's verification and watch it fail**

Run from the repository root:

```bash
R="$(git rev-parse --show-toplevel)"; C="$R/.claude/Commands/workflow-commands"; bad=0
grep -n -E 'Architecture Score|## Phase 4: Architecture|## Phase 5: Code Simplification|Phases 3-5|Architecture Violations|Simplification Opportunities' "$C/python-verification-standard.md" && bad=1
grep -n 'architecture validation, type analysis' "$C/python-verification-quick.md" && bad=1
grep -n 'Phase 3 Bug Scan' "$C/hotfix-interrupt.md" && bad=1
for f in "P04-architecture-validation-[SF].md" "P05-code-simplification-[SF].md"; do
  [ -e "$C/$f" ] && { echo "still present: $f"; bad=1; }
done
grep -q '^### Step 1.5: Bug Scan$' "$R/.claude/agents/verification-silent-failure.md" || { echo "agent: Step 1.5 missing"; bad=1; }
grep -q '^### Report Format$' "$C/python-verification-standard.md" || { echo "standard: Phase 14 report format missing"; bad=1; }
for t in 'eval(' 'yaml.load' 'random.' 'alembic/versions/**' '**/*.sql' '**/settings.py' '.env.*' 'GRANT' 'SECURITY DEFINER' 'credential'; do
  for f in "$C/python-verification-standard.md" "$C/P14-security-review-[SF].md"; do
    grep -qF -- "$t" "$f" || { echo "trigger '$t' missing in ${f##*/}"; bad=1; }
  done
done
[ "$bad" -eq 0 ] && echo "Task 3 part A: OK"
```

Expected now: it lists the Phase 4/5 headings, `Phases 3-5`, `Architecture Score`, the two report blocks, the quick Notes line, the hotfix `Phase 3 Bug Scan` line, `still present:` for P04 and P05, `agent: Step 1.5 missing`, `standard: Phase 14 report format missing`, and several `trigger '…' missing` lines — and it does not print `Task 3 part A: OK`.

- [ ] **Step 2: Standard: add the retirement note under the intro**

In `.claude/Commands/workflow-commands/python-verification-standard.md`, find this exact text (it occurs once):

```markdown
orchestration.
```

and replace it with the same text followed by the new lines:

```markdown
orchestration.

**Retired: Phase 4 (architecture validation) and Phase 5 (code simplification).**
Across every recorded verification run in the downstream project this workflow
comes from, neither phase produced a single finding, at standard or full level,
so both tiers dropped them and their standalone skill files were deleted. Do not
re-add them here. An architecture review that a task genuinely needs is its own
task, with its own bead.
```

- [ ] **Step 3: Standard Phase 3: align the bug scan with the agent's classes**

In `.claude/Commands/workflow-commands/python-verification-standard.md`, replace everything from the heading `### Check #2: Bug Scan` up to (not including) the heading `### Check #3: Historical Context` with:

```markdown
### Check #2: Bug Scan

Standard runs no review agents, so this shallow scan is its only bug pass. It
looks for the same classes the full tier's silent-failure agent scans for:

- **None handling:** attribute access, indexing or calls on a value that can be
  `None` on a real path; `cast()` or `# type: ignore` hiding it; `assert` as the
  only runtime guard; attributes first assigned outside `__init__`; falsy values
  treated as missing
- **Async misuse:** coroutines never awaited; `create_task()` results not kept;
  blocking calls inside `async def`; `CancelledError` swallowed; resources used
  after their `with` block closed them
- **Resource lifecycle:** files, sockets, connections, sessions, HTTP clients,
  `subprocess.Popen`, executors or pools opened without `with`/`finally`; locks
  without a release in `finally`; threads never joined
- **Shared mutable state:** mutable default arguments and class attributes;
  unlocked state shared across threads or tasks; a collection mutated while
  iterating it; late-binding closures in loops
- **Silent wrong results:** a generator consumed twice; naive and aware datetimes
  mixed
- **Swallowed errors:** bare `except:`, `except Exception: pass`, errors reported
  with `print()` (the full tier hands this to its silent-failure agent; standard
  checks it here)

**Focus on:** large bugs a senior engineer would stop the merge for, not nitpicks.
Ignore anything ruff or mypy already reports under the project's configuration.
```

- [ ] **Step 4: Standard: remove Phase 4 and Phase 5**

In `.claude/Commands/workflow-commands/python-verification-standard.md`, delete everything from the line `## Phase 4: Architecture Validation` up to (not including) the line `## Phase 9: Confidence Scoring`. Keep `## Phase 9: Confidence Scoring` and everything after it.

- [ ] **Step 5: Standard Phase 9: score Phase 3's findings only**

In `.claude/Commands/workflow-commands/python-verification-standard.md`, find this exact text:

```markdown
For each issue found (Phases 3-5), assign a confidence score:
```

and replace it with:

```markdown
For each issue found (Phase 3), assign a confidence score:
```

- [ ] **Step 6: Standard report: drop the Architecture Score**

In `.claude/Commands/workflow-commands/python-verification-standard.md`, find this exact text:

```markdown
## Standard Verification Report

### Architecture Score: X/10

### Summary
```

and replace it with:

```markdown
## Standard Verification Report

### Summary
```

- [ ] **Step 7: Standard report: drop the Phase 4 and Phase 5 blocks**

In `.claude/Commands/workflow-commands/python-verification-standard.md`, delete everything from the line `### Architecture Violations (Phase 4)` up to (not including) the line `### Test Results (Phase 11)`. Keep `### Test Results (Phase 11)` and everything after it.

- [ ] **Step 8: Standard Phase 14: gate on the widened triggers and restore its report format**

In `.claude/Commands/workflow-commands/python-verification-standard.md`, replace everything from the heading `## Phase 14: Security Review (Auto-Triggered)` up to (not including) the heading `## Phase 13: Write Verification Marker (ONLY on PASS)` with:

````markdown
## Phase 14: Security Review (Auto-Triggered)

**This phase runs only when the gate below matches.**

### Gate: Sensitive File Patterns

Check whether any file in the changed set matches. An UNKNOWN changed set counts
as a match.

**Path patterns:**
- `src/**/auth/**`, `src/**/api/**`, `src/**/service*/**`, `src/**/repository/**`,
  `src/**/network/**`, `src/**/http/**`
- `**/migrations/**`, `alembic/versions/**`, `**/*.sql`
- settings modules (`**/settings.py`, `**/settings/**`)
- environment files (`.env`, `.env.*`)

**Content patterns (the changed file contains):**
- `apiKey`, `api_key`, `secret`, `token`, `password`, `credential`
- `requests`, `httpx`, `http`
- `eval(`, `exec(`, `pickle`, `yaml.load`, `subprocess`, `shell=True`,
  `verify=False`, `DEBUG`, `random.`
- `GRANT`, `REVOKE`, `CREATE POLICY`, `ROW LEVEL SECURITY`, `SECURITY DEFINER`

**No match →** skip the checks and record `Security review: Skipped (no sensitive files)`.
**Match →** run the checks below and record `Security review: Triggered (<matching files>)`.

### If Triggered: Run Security Checks

1. **Hardcoded secrets scan** - Check for API keys, tokens in code
2. **HTTPS enforcement** - Verify no HTTP URLs (except localhost)
3. **Environment variables** - Sensitive data uses env vars or python-dotenv, not hardcoded
4. **SQL injection** - No raw SQL queries with user input
5. **Dangerous functions** - No `eval()`, `exec()`, `pickle.loads()`, or `yaml.load()` without a safe loader, on untrusted data
6. **Subprocess safety** - No `shell=True` with user input
7. **SSL verification** - No `verify=False` in requests/httpx
8. **Debug mode** - No `DEBUG=True` in production config
9. **Weak randomness** - No `random` module for tokens, passwords or IDs (use `secrets`)
10. **Database authorization** - Grants, revokes, row-level security policies and `SECURITY DEFINER` functions read for cross-user access: each policy names the requesting user, and the application-side check it backs still exists
11. **Committed secrets** - No `.env` file is tracked in git (`git ls-files | grep '\.env'`)
12. **Error exposure** - Errors don't leak internal details to users

### Report Format

```markdown
### Security Review (Phase 14)
**Status:** [Triggered (<matching files>) / Skipped (no sensitive files)]
**Findings:**
- [ ] `file:line` - [issue description] (CRITICAL/HIGH/MEDIUM)
```

---
````

- [ ] **Step 9: Quick Notes: no architecture validation to mention**

In `.claude/Commands/workflow-commands/python-verification-quick.md`, find this exact text:

```markdown
- Does not run architecture validation, type analysis, or coverage agents
```

and replace it with:

```markdown
- Does not run the review agents (type design, silent failures, comments, test
  coverage) or the Codex pass
```

- [ ] **Step 10: Hotfix trigger: the bug scan now lives in Phase 7 (full) and Phase 3 (standard)**

In `.claude/Commands/workflow-commands/hotfix-interrupt.md`, find this exact text:

```markdown
  - Phase 3 Bug Scan: CRITICAL severity found
```

and replace it with:

```markdown
  - Bug scan (Phase 7 in full, Phase 3 in standard): CRITICAL severity found
```

- [ ] **Step 11: Agent: describe the bug-scan classes**

In `.claude/agents/verification-silent-failure.md`, find this exact text:

```markdown
description: Parallel verification agent for Phase 7. Hunts silent failures, inadequate error handling, and inappropriate fallbacks in changed Python files only. Returns structured findings.
```

and replace it with:

```markdown
description: Parallel verification agent for Phase 7. Hunts silent failures, inadequate error handling, inappropriate fallbacks, and the bug-scan classes (None handling, async misuse, resource lifecycle, shared mutable state, silent wrong results) in changed Python files only. Returns structured findings.
```

- [ ] **Step 12: Agent: add Step 1.5, the bug scan**

In `.claude/agents/verification-silent-failure.md`, find this exact text (it occurs once):

```markdown
unnecessarily.
```

and replace it with the same text followed by the new lines:

```markdown
unnecessarily.

### Step 1.5: Bug Scan

The full tier's Phase 3 used to run a separate bug scan in the main context. In
the downstream project this workflow comes from, it never surfaced a defect this
agent did not also report, so the scan lives here now. Over the same changed
files, look for the large bugs that are not silent failures in the strict sense:

- **None handling:** attribute access, indexing or calls on a value that can be
  `None` on a real path; `cast()` or `# type: ignore` hiding it; `assert` as the
  only runtime guard; attributes first assigned outside `__init__`; falsy values
  (`0`, `""`, `[]`) treated as missing
- **Async misuse:** coroutines never awaited; `create_task()` results not kept, so
  the task can be garbage-collected mid-flight; blocking calls inside
  `async def`; `CancelledError` swallowed; resources used after their `with`
  block closed them
- **Resource lifecycle:** files, sockets, connections, sessions, HTTP clients,
  `subprocess.Popen`, executors or pools opened without `with`/`finally`; locks
  without a release in `finally`; threads never joined
- **Shared mutable state:** mutable default arguments and class attributes;
  unlocked state shared across threads or tasks; a collection mutated while
  iterating it; late-binding closures in loops
- **Silent wrong results:** a generator consumed twice; naive and aware
  datetimes mixed

Focus on bugs a senior engineer would stop the merge for. Ignore anything ruff or
mypy already reports under the project's configuration. Report them through the
same JSON contract below, with `pattern` naming the bug class and
`hidden_errors` describing what goes wrong at runtime.
```

- [ ] **Step 13: P14: keep its trigger list identical to the tiers' gate**

In `.claude/Commands/workflow-commands/P14-security-review-[SF].md`, replace everything from the heading `## Auto-Trigger Patterns` up to (not including) the heading `## Analysis Workflow` with:

```markdown
## Auto-Trigger Patterns

This phase runs in Standard and Full verification only when a file in the changed
set matches one of these patterns; an unknown changed set counts as a match. Both
tiers carry the same list in their Phase 14 gate, so keep all three in step.

### Path Patterns
- `src/**/auth/**`, `src/**/api/**`, `src/**/service*/**`, `src/**/repository/**`,
  `src/**/network/**`, `src/**/http/**` - code that handles auth, requests and
  data access
- `**/migrations/**`, `alembic/versions/**`, `**/*.sql` - schema and database
  authorization changes
- settings modules (`**/settings.py`, `**/settings/**`) - debug flags and secrets
- environment files (`.env`, `.env.*`) - secrets that must never be committed

### Content Patterns (file contains)
- `apiKey`, `api_key`, `secret`, `token`, `password`, `credential`
- `requests`, `httpx`, `http`
- `eval(`, `exec(`, `pickle`, `yaml.load`, `subprocess`, `shell=True`,
  `verify=False`, `DEBUG`, `random.`
- `GRANT`, `REVOKE`, `CREATE POLICY`, `ROW LEVEL SECURITY`, `SECURITY DEFINER`

---
```

- [ ] **Step 14: P14 check 2.4: name `yaml.load` as a dangerous loader**

In `.claude/Commands/workflow-commands/P14-security-review-[SF].md`, find this exact text (it occurs once):

```markdown
# data = pickle.loads(untrusted_bytes)  -- do not deserialize untrusted data
```

and replace it with the same text followed by the new lines:

```markdown
# data = pickle.loads(untrusted_bytes)  -- do not deserialize untrusted data

# BAD: yaml.load without a safe loader on untrusted data
# config = yaml.load(untrusted_text)  -- use yaml.safe_load instead
```

- [ ] **Step 15: P14: add check 2.10, database authorization**

In `.claude/Commands/workflow-commands/P14-security-review-[SF].md`, find this exact text:

```markdown
### Step 6: Error Handling Security
```

and replace it with:

````markdown
#### 2.10 Database Authorization
Read every `GRANT`, `REVOKE`, row-level security policy (`CREATE POLICY`,
`ROW LEVEL SECURITY`) and `SECURITY DEFINER` function in the changed migrations
and SQL for cross-user access:

```sql
-- BAD: any signed-in user can read every row
CREATE POLICY read_all ON documents FOR SELECT USING (true);

-- GOOD: the policy names the requesting user
CREATE POLICY read_own ON documents FOR SELECT
  USING (owner_id = current_setting('app.user_id')::int);
```

The application-side authorization check that the policy backs must still exist.

### Step 6: Error Handling Security
````

- [ ] **Step 16: Delete the retired P04 and P05 skills**

Run from the repository root. The `:(literal)` prefix matters: without it git reads `[SF]` as a character class and would also delete any sibling file ending in `-S.md` or `-F.md`.

```bash
git rm -q -- ':(literal).claude/Commands/workflow-commands/P04-architecture-validation-[SF].md' \
             ':(literal).claude/Commands/workflow-commands/P05-code-simplification-[SF].md'
git status --short -- .claude/Commands/workflow-commands/
```

Expected: the two files listed as `D ` (staged deletions) and nothing else deleted.

- [ ] **Step 17: Run this part's verification again and watch it pass**

Run the same command as Step 1. Expected: exactly one line, `Task 3 part A: OK`.

- [ ] **Step 18: Re-run Task 2's checks to confirm nothing regressed**

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-changed-set.sh" "$(git rev-parse --show-toplevel)" | tail -1
bash "$CHECKS/check-ruff-scope.sh" "$(git rev-parse --show-toplevel)" | tail -1
```

Expected: `check-changed-set: ALL PASS` and `check-ruff-scope: ALL PASS`. If this is a new session and the scripts are gone, re-create them first from Task 2 Part A Steps 1 and 2.

#### Part B: `python-verification-full.md` — trim, gates and the Codex pass (W3)

**Files:**
- Modify: `.claude/Commands/workflow-commands/python-verification-full.md` — frontmatter description; intro and retirement note; Phase 3 (two checks) with Phases 4 and 5 removed; Phase 6 gate (Step 0); Phase 7 bug-scan fallback (Step 4); Phase 8.7 Codex pass; Phase 9 sources; Phase 11 test presence; Phase 14 gate and one Step 2 row; Phase 13 report templates; hotfix trigger; Triggers note; Quick Reference; Integrated Methodologies; Scope Control and Guidelines deletions; Agent Orchestration (agent table, launch, availability handling, Phase 8.5 step 2); execution-flow diagram; Updated Report Format; Fallback Behavior.
- Test (outside the repo, never committed): `$CHECKS/check-phase6-gate.sh`, `$CHECKS/check-codex-companion.sh`.

**Interfaces:**
- Consumes: `modified_files` (a plain list of paths) in `.beads/.session-state.json` from Task 2; the trunk lookup from the plan's Global Constraints; the `verification-silent-failure` agent's new Step 1.5 bug scan (Part A of this task); the Codex companion's command line as installed (plugin 1.0.6): `adversarial-review --background [--scope working-tree|branch] [--base <ref>]`, `result <jobId> --json`, with the scope at `.storedJob.result.target.label` and the review at `.storedJob.result.result`.
- Produces: snippets `phase6-gate`, `codex-companion` and `codex-scope` (the last defines `codex_scopes`); report strings `Type design: Skipped (no new types)`, `Security review: Skipped (no sensitive files)` and `Security review: Triggered (<matching files>)`; the Phase 14 trigger lists, which `workflow-commands:python-verification-standard` (Part A) must match word for word; the hotfix trigger name "Phase 7 bug scan", which `hotfix-interrupt` (Part A) also uses.

Anchors in this part are headings and lines that neither Task 1 nor Task 2 changes. The edit steps run top to bottom through the file.

- [ ] **Step 1: Write the failing check for the Phase 6 gate**

Checks live outside the repo; set `CHECKS` to your session scratchpad plus `/sgw-checks` (see Global Constraints). Create `<scratchpad>/sgw-checks/check-phase6-gate.sh` with the Write tool, not a shell heredoc (see Global Constraints), with exactly this content:

````bash
#!/usr/bin/env bash
# check-phase6-gate.sh <repo-root>
# Behaviour check for the Phase 6 gate in python-verification-full.md
# (snippet: phase6-gate). Builds throwaway git repos next to this script.
set -u
REPO="${1:?usage: check-phase6-gate.sh <repo-root>}"
DOC="$REPO/.claude/Commands/workflow-commands/python-verification-full.md"
WORK="$(cd "$(dirname "$0")" && pwd)/phase6-gate-work"
fails=0
pass() { echo "PASS: $*"; }
fail() { echo "FAIL: $*"; fails=$((fails + 1)); }

extract_snippet() {   # extract_snippet <file> <name>
  awk -v want="# snippet: $2" '
    /^[[:space:]]*```/ { if (inb) { if (hit) exit; inb=0 } else { inb=1; first=1 }; next }
    inb && first { first=0; t=$0; sub(/^[[:space:]]+/, "", t); if (t == want) hit=1; next }
    inb && hit { print }
  ' "$1"
}

SNIPPET="$(extract_snippet "$DOC" phase6-gate)"
if [ -z "$SNIPPET" ]; then
  echo "FAIL: snippet 'phase6-gate' not found in $DOC"
  exit 1
fi

rm -rf "$WORK"
mkdir -p "$WORK"

# new_repo <name> <with-origin: yes|no> -> prints the repo path.
# Base commit on main: src/pkg/core.py, "src/my pkg/models.py", tests/test_core.py.
# With an origin, main is pushed to a bare repo but origin/HEAD is left unset,
# so the snippet's own trunk lookup has to find origin/main.
new_repo() {
  local r="$WORK/$1"
  mkdir -p "$r/src/pkg" "$r/src/my pkg" "$r/tests"
  git -C "$r" init -q -b main
  git -C "$r" config user.email check@example.com
  git -C "$r" config user.name check
  printf 'def existing():\n    return 1\n' > "$r/src/pkg/core.py"
  printf 'X = 1\n' > "$r/src/my pkg/models.py"
  printf 'def test_existing():\n    assert True\n' > "$r/tests/test_core.py"
  printf '.beads/\n' >> "$r/.git/info/exclude"
  git -C "$r" add -A
  git -C "$r" commit -q -m base
  if [ "$2" = yes ]; then
    git init -q --bare -b main "$WORK/$1-origin.git"
    git -C "$r" remote add origin "$WORK/$1-origin.git"
    git -C "$r" push -q -u origin main 2>/dev/null
  fi
  git -C "$r" switch -q -c feat/work
  echo "$r"
}

# set_changed <repo> <path>... -> writes modified_files (no paths = empty list)
set_changed() {
  local r="$1"
  shift
  mkdir -p "$r/.beads"
  python3 - "$r/.beads/.session-state.json" "$@" <<'PY'
import json, sys
out, files = sys.argv[1], sys.argv[2:]
json.dump({"task_id": "check-1", "modified_files": files, "total_lines_changed": 1}, open(out, "w"))
PY
}

# expect <label> <repo> <launch|skip>
expect() {
  local out
  out="$(cd "$2" && bash -c "$SNIPPET" 2>&1)"
  if printf '%s\n' "$out" | grep -q "^PHASE6_GATE=$3"; then
    pass "$1 -> $3"
  else
    fail "$1: expected $3, got: $out"
  fi
}

# 1. A new class committed on the branch
r=$(new_repo committed yes)
printf 'class Invoice:\n    pass\n' > "$r/src/pkg/billing.py"
git -C "$r" add -A && git -C "$r" commit -q -m "add Invoice"
set_changed "$r" src/pkg/billing.py
expect "class committed on the branch" "$r" launch
if [ "$(git -C "$r" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)" = "origin/main" ]; then
  pass "trunk lookup set origin/HEAD to origin/main"
else
  fail "trunk lookup did not set origin/HEAD to origin/main"
fi

# 2. A new class staged, not committed
r=$(new_repo staged yes)
printf '\nclass Ledger:\n    pass\n' >> "$r/src/pkg/core.py"
git -C "$r" add src/pkg/core.py
set_changed "$r" src/pkg/core.py
expect "class staged" "$r" launch

# 3. A new class unstaged
r=$(new_repo unstaged yes)
printf '\nclass Ledger(object):\n    pass\n' >> "$r/src/pkg/core.py"
set_changed "$r" src/pkg/core.py
expect "class unstaged" "$r" launch

# 4. A new class in an untracked file
r=$(new_repo untracked yes)
printf 'class Fresh:\n    pass\n' > "$r/src/pkg/fresh.py"
set_changed "$r" src/pkg/fresh.py
expect "class in an untracked file" "$r" launch

# 5. Functional and alias forms, one repo each
for form in 'UserId = NewType("UserId", int)' \
            'type Vector = list[float]' \
            'Number: TypeAlias = int | float' \
            'Movie = TypedDict("Movie", {"name": str})' \
            'Point = typing.NamedTuple("Point", [("x", int)])'; do
  r=$(new_repo "form-$RANDOM" yes)
  printf '%s\n' "$form" > "$r/src/pkg/kinds.py"
  set_changed "$r" src/pkg/kinds.py
  expect "type form: $form" "$r" launch
done

# 6. A test class in tests/ only
r=$(new_repo test-file yes)
printf '\nclass TestLedger:\n    def test_x(self):\n        assert True\n' >> "$r/tests/test_core.py"
set_changed "$r" tests/test_core.py
expect "test class under tests/" "$r" skip

# 7. A Test* class inside src/ does not count either
r=$(new_repo test-class-src yes)
printf '\nclass TestDouble:\n    pass\n' >> "$r/src/pkg/core.py"
set_changed "$r" src/pkg/core.py
expect "Test* class inside src/" "$r" skip

# 8. A commented-out class
r=$(new_repo commented yes)
printf '\n# class Ghost:\n#     pass\n' >> "$r/src/pkg/core.py"
set_changed "$r" src/pkg/core.py
expect "commented-out class" "$r" skip

# 9. Import lines only
r=$(new_repo imports yes)
printf 'from typing import NamedTuple, NewType, TypeAlias, TypedDict\n' >> "$r/src/pkg/core.py"
set_changed "$r" src/pkg/core.py
expect "import lines only" "$r" skip

# 10. A plain function, no type
r=$(new_repo no-type yes)
printf '\ndef helper():\n    return 2\n' >> "$r/src/pkg/core.py"
set_changed "$r" src/pkg/core.py
expect "function only, no type" "$r" skip

# 11. A path with a space in it (Review Focus item 2)
r=$(new_repo space-path yes)
printf '\nclass Account:\n    pass\n' >> "$r/src/my pkg/models.py"
set_changed "$r" "src/my pkg/models.py"
expect "class in 'src/my pkg/models.py'" "$r" launch

# 12. Unknown changed set: no session state, then an empty list
r=$(new_repo unknown yes)
expect "no session-state file" "$r" launch
set_changed "$r"
expect "empty modified_files" "$r" launch

# 13. No origin remote at all (Review Focus item 3): cannot see committed work
r=$(new_repo no-origin no)
printf '\ndef helper():\n    return 2\n' >> "$r/src/pkg/core.py"
set_changed "$r" src/pkg/core.py
expect "no origin remote" "$r" launch

echo
if [ "$fails" -eq 0 ]; then
  echo "ALL PASS: phase6-gate"
else
  echo "$fails FAILED: phase6-gate"
fi
[ "$fails" -eq 0 ]
````

- [ ] **Step 2: Run it and watch it fail**

Run (from the repo root):

```bash
CHECKS="<scratchpad>/sgw-checks"; bash "$CHECKS/check-phase6-gate.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
```

Expected:

```text
FAIL: snippet 'phase6-gate' not found in <repo>/.claude/Commands/workflow-commands/python-verification-full.md
exit=1
```

- [ ] **Step 3: Write the failing check for the Codex companion lookup and scope picker**

Checks live outside the repo; set `CHECKS` to your session scratchpad plus `/sgw-checks` (see Global Constraints). Create `<scratchpad>/sgw-checks/check-codex-companion.sh` with the Write tool, not a shell heredoc (see Global Constraints), with exactly this content:

````bash
#!/usr/bin/env bash
# check-codex-companion.sh <repo-root>
# Behaviour check for Phase 8.7 of python-verification-full.md:
#   snippet codex-companion — finds the newest installed companion; launches nothing
#   snippet codex-scope     — picks the review scope(s) from the tree state
# Builds throwaway homes and repos next to this script. Never starts a review.
set -u
REPO="${1:?usage: check-codex-companion.sh <repo-root>}"
DOC="$REPO/.claude/Commands/workflow-commands/python-verification-full.md"
WORK="$(cd "$(dirname "$0")" && pwd)/codex-companion-work"
fails=0
pass() { echo "PASS: $*"; }
fail() { echo "FAIL: $*"; fails=$((fails + 1)); }

extract_snippet() {   # extract_snippet <file> <name>
  awk -v want="# snippet: $2" '
    /^[[:space:]]*```/ { if (inb) { if (hit) exit; inb=0 } else { inb=1; first=1 }; next }
    inb && first { first=0; t=$0; sub(/^[[:space:]]+/, "", t); if (t == want) hit=1; next }
    inb && hit { print }
  ' "$1"
}

COMP="$(extract_snippet "$DOC" codex-companion)"
SCOPE="$(extract_snippet "$DOC" codex-scope)"
[ -n "$COMP" ] || { echo "FAIL: snippet 'codex-companion' not found in $DOC"; exit 1; }
[ -n "$SCOPE" ] || { echo "FAIL: snippet 'codex-scope' not found in $DOC"; exit 1; }

rm -rf "$WORK"
mkdir -p "$WORK"

# --- codex-companion -------------------------------------------------------
if printf '%s\n' "$COMP" | grep -qE 'adversarial-review|node '; then
  fail "codex-companion snippet launches something; it must only resolve the path"
else
  pass "codex-companion snippet launches nothing"
fi

out="$(bash -c "$COMP")"
path="${out#Codex companion: }"
if [ -f "$path" ] && [ "${path%/scripts/codex-companion.mjs}" != "$path" ]; then
  pass "resolves the installed companion: $path"
else
  fail "did not resolve an installed companion (got: $out)"
fi

# Fake home with three versions: version sort must pick 1.0.10, not 1.0.6.
H="$WORK/home-versions"
for v in 1.0.2 1.0.6 1.0.10; do
  mkdir -p "$H/.claude/plugins/cache/openai-codex/codex/$v/scripts"
  : > "$H/.claude/plugins/cache/openai-codex/codex/$v/scripts/codex-companion.mjs"
done
out="$(HOME="$H" bash -c "$COMP")"
case "$out" in
  */codex/1.0.10/scripts/codex-companion.mjs) pass "picks the newest version (1.0.10)" ;;
  *) fail "expected 1.0.10, got: $out" ;;
esac

# Fake home with no plugin at all.
H="$WORK/home-empty"
mkdir -p "$H"
out="$(HOME="$H" bash -c "$COMP")"
case "$out" in
  *"not found"*) pass "reports a missing plugin" ;;
  *) fail "expected 'not found', got: $out" ;;
esac

# --- codex-scope -----------------------------------------------------------
new_repo() {   # new_repo <name> <with-origin: yes|no> -> prints the repo path
  local r="$WORK/$1"
  mkdir -p "$r"
  git -C "$r" init -q -b main
  git -C "$r" config user.email check@example.com
  git -C "$r" config user.name check
  printf 'x = 1\n' > "$r/app.py"
  git -C "$r" add -A
  git -C "$r" commit -q -m base
  if [ "$2" = yes ]; then
    git init -q --bare -b main "$WORK/$1-origin.git"
    git -C "$r" remote add origin "$WORK/$1-origin.git"
    git -C "$r" push -q -u origin main 2>/dev/null
  fi
  git -C "$r" switch -q -c feat/work
  echo "$r"
}

# scopes_of <repo> -> the codex_scopes output, lines joined with " | "
scopes_of() {
  (cd "$1" && bash -c "$SCOPE"$'\n'"codex_scopes" 2>/dev/null) | paste -sd '|' - | sed 's/|/ | /g'
}

# expect_scopes <label> <repo> <expected joined output>
expect_scopes() {
  local got
  got="$(scopes_of "$2")"
  if [ "$got" = "$3" ]; then pass "$1 -> $got"; else fail "$1: expected '$3', got '$got'"; fi
}

r=$(new_repo clean yes)
printf 'y = 2\n' >> "$r/app.py"
git -C "$r" commit -qam "branch work"
expect_scopes "clean tree, commits on the branch" "$r" "--scope branch --base origin/main"

r=$(new_repo dirty yes)
printf 'y = 2\n' >> "$r/app.py"
expect_scopes "dirty tree, no commits yet" "$r" "--scope working-tree"

r=$(new_repo untracked-only yes)
printf 'z = 3\n' > "$r/new_module.py"
expect_scopes "untracked file only" "$r" "--scope working-tree"

r=$(new_repo mixed yes)
printf 'y = 2\n' >> "$r/app.py"
git -C "$r" commit -qam "branch work"
printf 'z = 3\n' >> "$r/app.py"
expect_scopes "mixed: commits plus uncommitted edits" "$r" "--scope working-tree | --scope branch --base origin/main"

r=$(new_repo no-origin-clean no)
printf 'y = 2\n' >> "$r/app.py"
git -C "$r" commit -qam "branch work"
expect_scopes "no origin, clean tree" "$r" "--scope branch"

r=$(new_repo no-origin-dirty no)
printf 'y = 2\n' >> "$r/app.py"
expect_scopes "no origin, dirty tree" "$r" "--scope working-tree"

# Never --base together with working-tree, on any line the snippet can print.
if printf '%s\n' "$SCOPE" | grep -E 'working-tree' | grep -q -- '--base'; then
  fail "a working-tree line also carries --base"
else
  pass "no line pairs --base with --scope working-tree"
fi

echo
if [ "$fails" -eq 0 ]; then
  echo "ALL PASS: codex-companion"
else
  echo "$fails FAILED: codex-companion"
fi
[ "$fails" -eq 0 ]
````

- [ ] **Step 4: Run it and watch it fail**

Run (from the repo root):

```bash
CHECKS="<scratchpad>/sgw-checks"; bash "$CHECKS/check-codex-companion.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
```

Expected:

```text
FAIL: snippet 'codex-companion' not found in <repo>/.claude/Commands/workflow-commands/python-verification-full.md
exit=1
```

- [ ] **Step 5: Frontmatter — describe the tier without a phase count**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `frontmatter`, replace the line `description: Full 13-phase verification with parallel agents. Use for 200+ line changes or new modules.` with:

```markdown
description: Full verification with parallel review agents and a Codex adversarial pass. Use for 200+ line changes or new modules.
```

- [ ] **Step 6: Intro — the methodology list after the trim, plus the retirement note**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading `# Python Full Verification Workflow` up to (not including) the heading `## Integration with Superpowers Verification` with:

```markdown
# Python Full Verification Workflow

**Section:** Code Quality

When running verification before completion in this Python project, use the
combined methodologies from P02-lint-issues-fix, P03-code-review-checks (rules
compliance and historical intent only), P06-type-design-analysis (only when the
change adds a type), P07-silent-failure-hunt (which now carries the bug scan),
P08-comment-analysis, the Codex adversarial review, P12-test-coverage-analysis,
and P14-security-review (only when sensitive files changed). This ensures
thorough quality checks before claiming work is complete.

**Retired: the architecture-validation and code-simplification phases** (once
Phases 4 and 5, which is why the numbering jumps from 3 to 6). In a downstream
project that ran this workflow, neither produced a finding in any recorded run,
at full or standard level, so both were removed from this tier and from
`workflow-commands:python-verification-standard`, and their command files were
deleted. Do not re-add them. An architecture review that a task genuinely needs
is its own task, with its own bead.

---
```

- [ ] **Step 7: Integration paragraph — drop the methodology count**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Integration with Superpowers Verification`, replace the passage that begins with this line `**IMPORTANT:** When running` and ends with the line containing this text `creating PRs in this codebase.` with:

```markdown
**IMPORTANT:** When running `/superpowers:verification-before-completion` in
**this Python project**, follow this comprehensive workflow that integrates
the project's verification methodologies. This workflow is specific to this
project and should be used whenever verifying completed work before committing
or creating PRs in this codebase.
```

- [ ] **Step 8: Phase 3 keeps two checks; Phases 4 and 5 are removed**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading `## Phase 3: Code Review Checks (from P03-code-review-checks)` up to (not including) the heading `## Phase 6: Type Design Analysis (from P06-type-design-analysis)` with:

```markdown
## Phase 3: Code Review Checks (from P03-code-review-checks)

Review ONLY the changed files identified in Phase 1. This phase keeps the two
checks nothing else covers. The rest of the old P03 checklist moved: the bug
scan runs in Phase 7 (inside the `verification-silent-failure` agent, with an
in-context fallback in the Phase 7 section), comment compliance is Phase 8, and
the test-presence check is part of Phase 11.

### Check #1: Rules Compliance
Audit the changes against `.claude/rules/`:
- Code structure and organization rules
- Naming conventions
- Documentation requirements
- Testing requirements
- Python best practices defined in rules

### Check #2: Historical Context
Review context of modified files:
- Check Beads task description for original intent
- Review `.beads/.session-state.json` for task requirements
- Verify changes align with the task's stated goals
- Respect any TODO/FIXME or "don't modify" guidance in the touched code

**Report only what reaches 80% confidence.** In the runs measured in a
downstream project, this phase never surfaced a defect that Phase 7 did not
also report, so a clean pass here is one line in the report, not a paragraph.

---
```

This one replacement removes the whole Phase 4 (architecture validation) and Phase 5 (code simplification) sections, which sit between these two headings.

- [ ] **Step 9: Phase 6 — the gate (Step 0)**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Phase 6: Type Design Analysis (from P06-type-design-analysis)`, insert after the line `**Scope:** New or modified classes/types in changed files only.`:

````markdown

### Step 0: Gate — launch only when the change adds a type

In the runs measured in a downstream project, this agent mostly returned
low-severity encapsulation notes, and the one real bug it found was also found
by Phase 7 in the same run. It earns its cost only on new types, so check the
changed set before launching it. Run this from the repository root:

```bash
# snippet: phase6-gate
# Prints PHASE6_GATE=launch or PHASE6_GATE=skip, with the reason.
changed="$(python3 -c '
import json
try:
    d = json.load(open(".beads/.session-state.json"))
except Exception:
    d = {}
for p in d.get("modified_files") or []:
    print(p["path"] if isinstance(p, dict) else p)
' 2>/dev/null)"
trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null) || {
  git remote set-head origin --auto >/dev/null 2>&1
  trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
}
if [ -z "$changed" ]; then
  echo "PHASE6_GATE=launch (changed set unknown)"
elif [ -z "$trunk" ]; then
  echo "PHASE6_GATE=launch (no origin/HEAD, so committed changes cannot be checked)"
else
  src_files=()
  while IFS= read -r f; do
    case "$f" in src/*.py) ;; *) continue ;; esac
    case "/$f" in */tests/*|*/test_*.py|*_test.py|*/conftest.py) continue ;; esac
    src_files+=("$f")
  done <<< "$changed"
  count=0
  if [ "${#src_files[@]}" -gt 0 ]; then
    count=$(
      {
        git diff --unified=0 "$trunk"...HEAD -- "${src_files[@]}"
        git diff --unified=0 HEAD -- "${src_files[@]}"
        git ls-files --others --exclude-standard -z -- "${src_files[@]}" |
          while IFS= read -r -d '' f; do git diff --unified=0 --no-index /dev/null "$f"; done
      } 2>/dev/null |
        grep -E '^\+[^+]' |
        grep -vE '^\+[[:space:]]*#' |
        grep -vE '^\+[[:space:]]*class[[:space:]]+Test' |
        grep -cE '^\+[[:space:]]*class[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*([(:]|\[)|^\+[[:space:]]*type[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*(\[[^]]*\])?[[:space:]]*=|:[[:space:]]*([A-Za-z_][A-Za-z0-9_]*\.)?TypeAlias[[:space:]]*=|=[[:space:]]*([A-Za-z_][A-Za-z0-9_]*\.)?(NewType|TypedDict|NamedTuple)[[:space:]]*\('
    )
  fi
  if [ "${count:-0}" -gt 0 ]; then
    echo "PHASE6_GATE=launch ($count added type definition(s) under src/)"
  else
    echo "PHASE6_GATE=skip (no new types)"
  fi
fi
```

- `PHASE6_GATE=skip` → do not launch the type-design agent. Report
  `Type design: Skipped (no new types)` and launch only the Phase 7 and
  Phase 8 agents, plus Codex.
- `PHASE6_GATE=launch` → launch it with the others (Agent Orchestration).

The gate counts added lines under `src/` that define a type: a `class`, a
`TypeAlias` annotation, a `type X = …` statement, or a `NewType`, `TypedDict`
or `NamedTuple` call. It reads every tree state: commits on this branch
(`<trunk>...HEAD`), staged and unstaged edits (against `HEAD`), and untracked
files. Comments, import lines and test classes (`class Test…`, and anything
under `tests/` or named `test_*.py`, `*_test.py` or `conftest.py`) don't count.
When the changed set is unknown, or there is no `origin/HEAD` to diff committed
work against, it launches the agent anyway, because it cannot rule out a new
type.
````

The existing `### Step 1: Identify Types to Analyze` follows the inserted block, after one blank line.

- [ ] **Step 10: Phase 7 — add the in-context bug-scan fallback**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading `## Phase 7: Silent Failure Hunt (from P07-silent-failure-hunt)` up to (not including) the heading `## Phase 8: Comment Analysis (from P08-comment-analysis)` with:

````markdown
## Phase 7: Silent Failure Hunt (from P07-silent-failure-hunt)

> **USE AGENT:** Launch `verification-silent-failure` agent via Task tool.
> See [Agent Orchestration](#agent-orchestration) for parallel execution details.

**Parallel Group A** - Can run simultaneously with Phases 6, 8, and Codex Adversarial Review.

**Scope:** Error handling code in changed files only, plus the bug scan in Step 4.

### Step 1: Identify Error Handling Code
In changed files, locate:
- `try-except` blocks
- Null coalescing with fallbacks (`or`, `if x is None`)
- `Result` type pattern usage
- Bare `except: pass` blocks
- `except Exception: pass` blocks

### Step 2: Audit Each Handler

| Pattern | Severity | Check |
|---------|----------|-------|
| Bare `except: pass` | **CRITICAL** | Must log or handle meaningfully |
| `except Exception: pass` | **CRITICAL** | Must log or handle meaningfully |
| Catching broad `Exception` | **HIGH** | Should catch specific types |
| Missing `logging` usage | **MEDIUM** | Should use project's logging module |
| Silent fallbacks | **HIGH** | User should know something failed |
| Async without error handling | **HIGH** | Unhandled coroutine errors |

### Step 3: Check Fallback Behavior
For each fallback value found:
- Is the fallback appropriate?
- Does the user get feedback about the failure?
- Could the failure cascade to worse problems?

### Step 4: Bug Scan
The `verification-silent-failure` agent runs this scan as its Step 1.5. When the
agent fails and this phase falls back to in-context analysis (see Fallback
Behavior), run it here instead, so the bug scan is never lost. Report real
paths, not theoretical ones, and skip anything ruff or mypy already reports
under the project's configuration:

- **None handling:** attribute access, indexing or calls on a value that can be
  `None` on a real path; `cast()` or `# type: ignore` hiding it; `assert` as
  the only runtime guard; attributes first assigned outside `__init__`; falsy
  values treated as missing.
- **Async misuse:** coroutines never awaited; `create_task()` results not kept;
  blocking calls inside `async def`; `CancelledError` swallowed; resources used
  after their `with` block closed them.
- **Resource lifecycle:** files, sockets, connections, sessions, HTTP clients,
  `subprocess.Popen`, executors or pools opened without `with`/`finally`; locks
  without a release in `finally`; threads never joined.
- **Shared mutable state:** mutable default arguments and class attributes;
  unlocked state shared across threads or tasks; a collection mutated while
  iterating it; late-binding closures in loops.
- **Silent wrong results:** a generator consumed twice; naive and aware
  datetimes mixed.

### Step 5: Report Issues
Format for each issue:
```
Location: file:line
Severity: CRITICAL/HIGH/MEDIUM
Pattern: [what was found; for a bug-scan finding, "bug scan: <class>"]
Hidden Errors: [what gets silently dropped]
User Impact: [how user is affected]
Recommendation: [how to fix]
```

---
````

- [ ] **Step 11: Phase 8.7 — the Codex pass: versioned lookup, explicit scope, results by job id**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading that begins `## Phase 8.7: Codex Adversarial Review` up to (not including) the heading `## Phase 9: Confidence Scoring` with:

````markdown
## Phase 8.7: Codex Adversarial Review

> **EXTERNAL AGENT:** Runs via the Codex CLI in parallel with Phases 6-8.
> See [Agent Orchestration](#agent-orchestration) for execution details.

**Parallel Group A** - Launches alongside the Claude verification agents.

**Purpose:** An independent adversarial review from a different AI model: the
model configured in your Codex config, run through the Codex CLI. Codex defaults
to skepticism and targets failure modes that static analysis and Claude's
agents may miss: auth boundaries, data corruption, race conditions, rollback
safety, stale state, and observability gaps.

### Execution

**1. Find the companion script.** The Codex plugin installs it in a versioned
directory, so never hard-code the path; take the newest installed version:

```bash
# snippet: codex-companion
COMPANION="$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)"
if [ -f "$COMPANION" ]; then
  echo "Codex companion: $COMPANION"
else
  COMPANION=""
  echo "Codex companion: not found (is the codex plugin installed?)"
fi
```

If it is not found, Codex is unavailable: note it (Codex Availability Handling,
in Agent Orchestration) and continue without this phase.

**2. Pick the review scope from the tree state.** Never rely on the companion's
own `auto` scope. Verification usually runs before the ship commit, so a review
that looks only at commits can approve a diff that leaves out the uncommitted
implementation; and on a clean tree, `auto` diffs against the local default
branch, which can lag or lead the trunk. This block defines `codex_scopes`,
which prints one line of scope arguments per review pass:

```bash
# snippet: codex-scope
codex_scopes() {
  local trunk dirty ahead=0
  trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null) || {
    git remote set-head origin --auto >/dev/null 2>&1
    trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
  }
  dirty=$(git status --porcelain)
  if [ -n "$trunk" ]; then
    ahead=$(git rev-list --count "$trunk..HEAD" 2>/dev/null || echo 0)
  fi
  if [ -n "$dirty" ]; then
    echo "--scope working-tree"
  fi
  if [ -n "$trunk" ]; then
    if [ -z "$dirty" ] || [ "$ahead" -gt 0 ]; then
      echo "--scope branch --base $trunk"
    fi
  elif [ -z "$dirty" ]; then
    echo "--scope branch"
  else
    echo "codex-scope: no origin/HEAD, so commits already on this branch are not reviewed" >&2
  fi
}
```

- **Dirty tree** (staged, unstaged or untracked changes): one pass with
  `--scope working-tree`.
- **Clean tree:** one pass with `--scope branch --base <trunk>`.
- **Mixed state** (uncommitted edits on top of commits this branch already
  made): both passes. Merge their findings before Phase 9.
- **No `origin/HEAD`:** a clean tree gets `--scope branch`, which diffs against
  the local default branch; a dirty tree gets only the working-tree pass, and
  the commits already on the branch go unreviewed. Say so in the report.
- **Never pass `--base` together with `--scope working-tree`.** `--base` forces
  a branch review and silently drops the uncommitted work.

**3. Launch** one background pass per scope line, in the same Bash call as
steps 1 and 2:

```bash
[ -n "$COMPANION" ] && codex_scopes | while IFS= read -r scope; do
  node "$COMPANION" adversarial-review --background $scope
done
```

Each launch prints `… started in the background as <jobId>. …`. Keep every
job id: results are collected by id.

### Collecting Results

After the Phase 6-8 agents return, collect each pass by its job id, one call
per pass, with the `codex-companion` block run first in the same Bash call so
that `$COMPANION` is set. Never call `result` without an id: it returns the
newest *finished* job, so while a second pass is still running it hands back
the first pass's verdict again and the other scope goes unreviewed.

```bash
node "$COMPANION" result <jobId> --json | jq '{status: .storedJob.status, scope: .storedJob.result.target.label, verdict: .storedJob.result.result.verdict, findings: ((.storedJob.result.result.findings // []) | length), parseError: .storedJob.result.parseError}'
```

1. If the command says the job "is still running", proceed with Phase 8.5 and
   collect it again before Phase 9.
2. Check that `scope` matches the pass you launched (`working tree diff` for
   `--scope working-tree`, `branch diff against <trunk>` for a branch pass)
   before merging its findings. A mismatch means you collected the wrong job.
3. A non-null `parseError` means Codex answered with prose instead of the JSON
   it was asked for. Treat that pass as a failed run.
4. Record each pass's scope next to its verdict in the Phase 13 report, one
   line per pass.
5. If Codex timed out or failed, follow Codex Availability Handling in Agent
   Orchestration.

### Runtime Rules

- **Run `codex --version` before blaming the plugin.** The companion runs
  whichever `codex` binary is first on `PATH`, and that binary reads your Codex
  config (`~/.codex/config.toml`). A CLI older than its config fails at
  startup, which looks like a broken plugin.
- **A config or effort rejection:** fix what `codex --version` or the error
  shows, then relaunch once. Do not loop.
- **A usage-limit message:** do not retry. Note the reset time the message
  gives in the report.
- **No `bd` writes while a pass is in flight.** The review runs inside the
  repository with its agent instructions, may run `bd` commands of its own, and
  two `bd` processes at once can overwrite each other's writes.
- **A reply that is not JSON is a failed run**, even when the job reports
  `completed`.
- **Effort comes from your Codex config.** The review command takes no effort
  flag. For a deliberately deeper pass (an auth, migration or payment diff),
  raise `model_reasoning_effort` in the Codex config for that run, put it back
  afterwards, and name the effort in the report.

### Codex Finding Format

The review sits at `.storedJob.result.result` in the `result --json` reply:
- `verdict`: `approve` or `needs-attention`
- `summary`: a short overall assessment
- `findings`: array of issues with `severity` (`critical`, `high`, `medium` or
  `low`), `title`, `body`, `file`, `line_start`, `line_end`, `confidence`
  (0-1) and `recommendation`
- `next_steps`: array of suggested follow-ups

### Merging Codex Findings

Map Codex findings into the unified findings list:
- `confidence` 0-1 → multiply by 100 for the 0-100 scale
- `needs-attention` verdict → treat findings as HIGH severity minimum
- Apply the same Phase 10 false-positive filtering to Codex findings
- Deduplicate against Claude agent findings (same file + overlapping lines)
- When two passes ran, merge both result sets before Phase 9

---
````

- [ ] **Step 12: Phase 9 — the sources after the trim**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Phase 9: Confidence Scoring`, replace the line `For each issue found (from Phases 3-8 and Codex 8.7), assign a confidence score:` with:

```markdown
For each issue found (from Phases 3, 6-8 and Codex 8.7), assign a confidence score:
```

- [ ] **Step 13: Phase 11 — the test-presence check moves here**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Phase 11: Final Verification`, insert after the line `**All must pass before claiming completion.**`:

```markdown

**Test presence (moved here from Phase 3).** For each changed module under
`src/`, confirm that a corresponding test file exists under `tests/` (mirror
structure: `tests/test_billing.py` for `src/<your_package>/billing.py`) and
that step 3 ran it. A changed module with no test file is reported here;
Phase 12 rates the gap and may propose the missing tests.
```

- [ ] **Step 14: Phase 14 — gate it, and widen the triggers to everything it checks**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading `## Phase 14: Security Review (from P14-security-review)` up to (not including) the heading `### Step 2: Python-Specific Security Checks` with:

````markdown
## Phase 14: Security Review (from P14-security-review)

**Gated: Steps 2 and 3 run only when Step 1 matches.**
`workflow-commands:python-verification-standard` uses the same gate. Run
unconditionally, this phase produced no findings in the runs measured in a
downstream project, so the gate keeps it as a backstop for the files where it
can matter. Its triggers cover everything Steps 2 and 3 look for, so a change
that only adds a `pickle.loads` call, or only edits a migration, still
triggers it.

### Step 1: Gate on Sensitive Files

Check every file in the Phase 1 changed set against these patterns.

**Path patterns:**
- `src/**/auth/**`, `src/**/api/**`, `src/**/service*/**`
- `src/**/repository/**`, `src/**/network/**`, `src/**/http/**`
- `**/migrations/**`, `alembic/versions/**`, `**/*.sql`
- Settings modules: `**/settings.py`, `**/settings/**`
- Environment files: `.env`, `.env.*`

**Content patterns** (anywhere in a changed file):
- Secrets: `api_key`, `apiKey`, `secret`, `token`, `password`, `credential`
- Network: `http`, `requests`, `httpx`
- Risky calls: `eval(`, `exec(`, `pickle`, `yaml.load`, `subprocess`,
  `shell=True`, `verify=False`, `DEBUG`, `random.`
- Database authorization: `GRANT`, `REVOKE`, `CREATE POLICY`,
  `ROW LEVEL SECURITY`, `SECURITY DEFINER`

Run this from the repository root. It prints each matching file once:

```bash
python3 -c 'import json; [print(p) for p in json.load(open(".beads/.session-state.json")).get("modified_files") or []]' 2>/dev/null |
while IFS= read -r f; do
  if printf '%s\n' "$f" | grep -qE '(^|/)src/(.*/)?(auth|api|service[^/]*|repository|network|http)/|(^|/)migrations/|(^|/)alembic/versions/|\.sql$|(^|/)settings(\.py$|/)|(^|/)\.env(\..+)?$'; then
    echo "$f"
  elif [ -f "$f" ] && grep -qE 'api_key|apiKey|secret|token|password|credential|http|requests|httpx|eval\(|exec\(|pickle|yaml\.load|subprocess|shell=True|verify=False|DEBUG|random\.|GRANT|REVOKE|CREATE POLICY|ROW LEVEL SECURITY|SECURITY DEFINER' -- "$f"; then
    echo "$f"
  fi
done
```

- **No file printed** → skip Steps 2 and 3. Report
  `Security review: Skipped (no sensitive files)` and continue.
- **Files printed** → run Steps 2 and 3 on them, and report
  `Security review: Triggered (<matching files>)`.
- **`CHANGED_SET = UNKNOWN`** → run Steps 2 and 3 on the files the review
  phases covered, and report `Security review: Triggered (changed set unknown)`.
````

- [ ] **Step 15: Phase 14 Step 2 — a check for the new database-authorization triggers**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `### Step 2: Python-Specific Security Checks`, insert after the line:

```text
| Weak randomness | `random` module used for security-sensitive values (use `secrets` instead) |
```:

```markdown
| Database authorization | `GRANT`, `REVOKE`, row-level-security policies or `SECURITY DEFINER` in a migration or `.sql` file: no grant or policy wider than the change needs, policy predicates that name the requesting user, and the application-side check the policy backs still in place |
```

- [ ] **Step 16: Phase 13 report templates — no architecture score, no P04/P05 blocks**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading `### If Issues Found:` up to (not including) the heading `## Hotfix Discovered During Verification` with:

````markdown
### If Issues Found:

```markdown
## Verification Report

### Summary
Found [N] issues before completion.

---

### Lint Fixes Applied (P02-lint-issues-fix)
- Auto-fixed: [N] issues across [M] changed files
  *(or:* `SKIPPED (changed set unknown)` *)*
- Scope check: no files outside the changed set changed
  *(or:* **LEAK: [list]** *, with what was reverted and what was only reported)*
- Manual fixes needed: [N] issues
  - `file:line` - [description]

---

### Code Review Issues (P03-code-review-checks)

#### Issue 1: [Brief description]
**Confidence:** [score]%
**Source:** [rules compliance / historical intent]
**File:** `path/to/file.py:line`
**Suggested fix:** [how to resolve]

---

### Type Design Issues (P06-type-design-analysis)

| Type | File | Encap | Invariant | Issue |
|------|------|-------|-----------|-------|
| ClassName | path:line | 5/10 | 4/10 | Description |

*Or: No type design issues found / Skipped (no new types) / Skipped (already run)*

---

### Silent Failure and Bug-Scan Issues (P07-silent-failure-hunt)

| Severity | Location | Issue | Recommendation |
|----------|----------|-------|----------------|
| CRITICAL | path:line | Bare except: pass | Add logging.exception() |

*Or: No silent failures or bugs found / Skipped (already run)*

---

### Comment Issues (P08-comment-analysis)

| Location | Issue Type | Current | Suggestion |
|----------|------------|---------|------------|
| path:line | Inaccurate | "Returns None" | "Raises ValueError" |

*Or: No comment issues found / Skipped (already run)*

---

### Codex Adversarial Review (P8.7)

**Verdict:** [approve / needs-attention / unavailable] · **Scope:** [working tree diff / branch diff against <trunk>; one line per pass] · **Effort:** [optional: the effort your Codex config ran at]

| Confidence | File | Lines | Issue | Recommendation |
|------------|------|-------|-------|----------------|
| 0.85 | path/to/file.py | 42-58 | Race condition in... | Add mutex or... |

*Or: No adversarial findings / Codex review: unavailable — [reason]*

---

### Test Coverage Gaps (P12-test-coverage-analysis)

| Source File | Test File | Gap | Rating |
|-------------|-----------|-----|--------|
| auth_service.py | test_auth_service.py | Missing error case tests | 8/10 |

*Or: Adequate test coverage / Skipped (already run)*

---

### Build Validation (P11.5-build-validation)

**Status:** [PASS | WARN | FAIL]
**Errors:** [List any build errors, or "None"]
**Warnings:** [List any build warnings, or "None"]

---

### Security Review (P14-security-review)

**Status:** [Triggered (<matching files>) | Skipped (no sensitive files)]

| Severity | Location | Issue | Recommendation |
|----------|----------|-------|----------------|
| CRITICAL | path:line | Hardcoded API key | Use environment variable |

*Or: No security issues found / Skipped (no sensitive files)*

---

**Recommendation:** Address issues before marking complete.
```

### If No Issues:

```markdown
## Verification Report

All checks passed.

### Checks Completed:
- Lint issues (analyzed; auto-fixed inside the changed set only)
- Rules compliance (.claude/rules/)
- Historical context (Beads context)
- Type design analysis (run / skipped: no new types)
- Silent failure hunt, including the bug scan
- Comment accuracy
- Codex adversarial review (independent second model; scope and effort noted)
- Build validation (environment and package build checked)
- Test presence and test coverage quality
- Security review (triggered / skipped: no sensitive files)

**Ready for:** commit / PR creation
```

---
````

This replaces both templates (If Issues Found and If No Issues). The Lint Fixes Applied lines are the ones Task 2 wrote; they are repeated here unchanged.

- [ ] **Step 17: Hotfix triggers — the bug scan now lives in Phase 7**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `### When to Trigger`, replace the line `- Phase 3 Bug Scan: CRITICAL severity issue found` with:

```markdown
- Phase 7 bug scan (moved there from Phase 3): CRITICAL severity issue found
```

- [ ] **Step 18: Triggers note — no phase count**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Triggers`, replace the line `**Note:** This 13-phase workflow is tailored to this Python project's` with:

```markdown
**Note:** This workflow is tailored to this Python project's
```

- [ ] **Step 19: Quick Reference — the phases after the trim**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading `## Quick Reference: The 14 Phases` up to (not including) the heading `## The 9 Integrated Methodologies` with:

```markdown
## Quick Reference: The Phases

| Phase | Source | Description | Execution |
|-------|--------|-------------|-----------|
| 1 | - | Gather context (changed set, rules, summary) | Main context |
| 2 | P02-lint-issues-fix | ruff check + mypy, auto-fix (**changed files only**), manual fix lint issues | Main context |
| 3 | P03-code-review-checks | Rules compliance + historical intent (bug scan moved to Phase 7) | Main context |
| 6 | `verification-type-analyzer` | Type design quality — only when the change adds a type | **AGENT (parallel, gated)** |
| 7 | `verification-silent-failure` | Error handling audit (silent failures) + bug scan | **AGENT (parallel)** |
| 8 | `verification-comment-analyzer` | Documentation accuracy verification | **AGENT (parallel)** |
| 8.7 | Codex adversarial-review | Independent adversarial review by a second model | **CODEX (parallel)** |
| 8.5 | - | Apply agent edits, collect Codex results, scoped format | Main context |
| 9 | P03-code-review-checks | Confidence scoring (0-100 scale) | Main context |
| 10 | P03-code-review-checks | False positive filtering (>=80 only) | Main context |
| 11 | - | Final Verification: ruff check + ruff format --check + pytest + test presence | Main context |
| 11.5 | P11.5-build-validation | Python build validation (environment + package) | Main context |
| 12 | `verification-test-coverage` | Test coverage quality analysis | **AGENT (sequential)** |
| 13 | Combined | Comprehensive verification report | Main context |
| 14 | P14-security-review | Security audit — only when sensitive files changed | Main context (gated) |

**Parallel Agents (6-8):** Launch in a SINGLE Task tool call with 2-3 invocations (Phase 6 only when its gate passes).
**Codex (8.7):** Launch via Bash `--background` in the SAME message as agents.
**Sequential Agent (12):** Launch after Phase 11 passes.

---
```

- [ ] **Step 20: Integrated Methodologies — no count, no P04/P05**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading `## The 9 Integrated Methodologies` up to (not including) the heading `## Scope Control` with:

```markdown
## Integrated Methodologies

| Methodology | Focus Area |
|-------------|------------|
| **P02-lint-issues-fix** | Static analysis, scoped auto-fix, manual lint fixes |
| **P03-code-review-checks** | Rules compliance, historical context, confidence scoring |
| **P06-type-design-analysis** | Type encapsulation, invariants, type hints, Python patterns (gated on new types) |
| **P07-silent-failure-hunt** | Error handling audit, silent failures, fallback behavior, bug scan |
| **P08-comment-analysis** | Documentation accuracy, docstring compliance, comment rot |
| **Codex adversarial-review** | Independent adversarial review by a second model: auth, data safety, races, rollback |
| **P12-test-coverage-analysis** | Test coverage quality, gap analysis, edge case coverage |
| **P14-security-review** | Security audit (gated): secrets, HTTPS, dynamic code execution, deserialization, database authorization |

---
```

- [ ] **Step 21: Scope Control — drop the two retired read-scope bullets**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `### Read scope`, delete exactly these lines (leave every other bullet as it is):

```text
- Architecture validation: changed files + immediate dependencies
- Simplification review: changed files only
```

- [ ] **Step 22: Guidelines — drop the simplification guideline**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Guidelines`, delete exactly these lines (leave every other bullet as it is):

```text
- **Preserve functionality** - Simplification suggestions must not change behavior
```

- [ ] **Step 23: Agent table — the Codex engine, model-neutral**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `### Available Verification Agents`, replace the line `| Codex adversarial-review | 8.7 | GPT-5.4 | Adversarial review: auth, data safety, races, rollback |` with:

```markdown
| Codex adversarial-review | 8.7 | Codex CLI (your configured model) | Adversarial review: auth, data safety, races, rollback |
```

- [ ] **Step 24: Agent Orchestration — 2–3 agents plus the Codex launch; availability handling**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading `### Phases 6-8 + 8.7: Parallel Agent + Codex Execution` up to (not including) the heading `### Agent Input Format` with:

````markdown
### Phases 6-8 + 8.7: Parallel Agent + Codex Execution

Launch the Claude agents (two, or three when the Phase 6 gate passed) AND the
Codex adversarial review concurrently.

**Claude agents** — single Task tool call with multiple invocations:

```
Task(subagent_type: "verification-type-analyzer", model: "opus", prompt: "...")   # only when the Phase 6 gate passed
Task(subagent_type: "verification-silent-failure", model: "opus", prompt: "...")
Task(subagent_type: "verification-comment-analyzer", model: "opus", prompt: "...")
```

**Codex adversarial review** — in the SAME message as the Task calls above,
one Bash call with `run_in_background: true` that runs, in order, the
`codex-companion` block, the `codex-scope` block and the launch loop from
Phase 8.7. Keep every job id it prints.

**CRITICAL:** Use a single message with multiple tool calls (2-3x Task + 1x Bash)
to ensure parallel execution. Do NOT call them sequentially.

### Codex Availability Handling

Codex is a **best-effort enhancement**, not a gate. If Codex is unavailable
(plugin not installed, not authenticated, CLI missing, network error), the
verification continues without it:

| Codex Status | Action |
|--------------|--------|
| Completed with findings | Merge findings into Phase 9 |
| Completed with `approve` | Note "Codex: no issues" in report |
| Still running at Phase 9 | Wait up to 60s, then proceed without |
| Companion not found | Note "Codex review: unavailable — plugin not installed" |
| Failed with a config or effort rejection | Run `codex --version`, fix what it shows, relaunch once; report the effort used |
| Failed with a usage-limit message | Note "Codex review: unavailable (usage limit, resets <time from the message>)"; do not retry before then |
| Reply was not JSON (`parseError` set) | Treat as failed: note "Codex review: unavailable — reply was not JSON" |
| Failed or unavailable for any other reason | Run `codex --version` first (Phase 8.7); note "Codex review: unavailable — <reason>" |
````

- [ ] **Step 25: Phase 8.5 step 2 — collect Codex results by job id**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `### Phase 8.5: Apply Agent Edits + Collect Codex Results`, replace the passage that begins with this line `2. **Collect Codex results**` and ends with the line containing this text `- If Codex failed/unavailable: note in report, continue without it` with:

````markdown
2. **Collect Codex results** by job id, one call per pass, with the
   `codex-companion` block from Phase 8.7 run first in the same Bash call:
   ```bash
   node "$COMPANION" result <jobId> --json
   ```
   - If a pass completed: check its scope (`target.label`), then parse
     `verdict` and `findings` and merge them into the unified list
   - If a pass is still running: proceed with edits, collect again before Phase 9
   - If a pass failed or Codex was unavailable: note it in the report and
     continue without it
````

- [ ] **Step 26: Execution-flow diagram — the phases after the trim**

In `.claude/Commands/workflow-commands/python-verification-full.md`, replace everything from the heading `## Updated Execution Flow` up to (not including) the heading `## Write Verification Marker (ONLY on PASS)` with:

````markdown
## Updated Execution Flow

```
Verification Triggered
        |
        v
+-------------------------------------+
| Phase 1: Gather Context             |
| - Read .beads/.session-state.json   |
| - Get modified_files (changed set)  |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phases 2-3: Sequential Analysis     |
| - Lint fixes (changed set only)     |
| - Rules + intent review (main ctx)  |
| - Phase 6 gate: new types? (grep)   |
+-------------------------------------+
        |
        v
+---------------------------------------------+
| Phases 6-8 + 8.7: PARALLEL AGENTS + CODEX   |
|                                             |
|  +-------------+ +-------------+            |
|  |verification-| |verification-|            |
|  |type-analyzer| |silent-      |            |
|  | (Claude,    | |failure +    |            |
|  |  gated)     | |bug scan     |            |
|  +-------------+ |(Claude)     |            |
|         +-------------+  +-------------+    |
|         |verification-|  |   CODEX     |    |
|         |comment-     |  | adversarial |    |
|         |analyzer     |  |  review     |    |
|         |(Claude)     |  |(2nd model)  |    |
|         +-------------+  +-------------+    |
|                                             |
|  Claude: Single Task call, 2-3 invocations  |
|  Codex:  Bash --background (concurrent)     |
|  Returns: findings + proposed_edits         |
+---------------------------------------------+
        |
        v
+-------------------------------------+
| Phase 8.5: APPLY AGENT EDITS        |
| - Collect proposed_edits from all   |
| - Group by file, detect conflicts   |
| - Apply edits inside changed set    |
| - Prompt user for conflicts         |
| - Scoped ruff format + leak check   |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phases 9-10: Combine & Filter       |
| - Merge agent findings              |
| - Apply confidence scoring          |
| - Filter false positives            |
| - Note which were auto-fixed        |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 11: Final Verification        |
| - ruff check (verify edits OK)      |
| - ruff format --check               |
| - pytest -v                         |
| - test presence (from Phase 3)      |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 11.5: Build Validation        |
| - Invoke /workflow-commands:        |
|   P11.5-build-validation-[F]        |
| - Python env + package build check  |
| - PASS / WARN / FAIL result         |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 12: TEST COVERAGE AGENT       |
| (After build/warn completes)        |
| Returns: gaps + proposed test edits |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 12.5: RUN NEW TESTS           |
| - Apply Phase 12 proposed_edits     |
| - Scoped ruff format, ruff check    |
| - pytest -v (all old + new)         |
| - Fix up to 3x, then revert         |
| (Skip if no edits were applied)     |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 14: Security Review (gated)   |
| - Only when sensitive files changed |
| - Hardcoded secrets scan            |
| - HTTPS/auth/storage checks         |
| - Python-specific security checks:  |
|   dynamic code, deserialization,    |
|   shell, SQL, database grants       |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 13: Generate Report           |
| - Combine all findings              |
| - List auto-applied fixes           |
| - List remaining issues             |
| - Format verification report        |
+-------------------------------------+
```

---
````

- [ ] **Step 27: Updated Report Format — drop the architecture score**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Updated Report Format`, delete the line `### Architecture Score: X/10` and the blank line after it. It is the last copy left in the file; the other two went with the report rewrite above.

- [ ] **Step 28: Fallback Behavior — name the bug scan in the Phase 7 fallback**

In `.claude/Commands/workflow-commands/python-verification-full.md`, section `## Fallback Behavior`, replace the line `2. Fall back to sequential in-context analysis for that phase` with:

```markdown
2. Fall back to sequential in-context analysis for that phase (for Phase 7,
   that includes its Step 4 bug scan)
```

- [ ] **Step 29: Make sure every skill invocation in the file uses its full name**

Run from the repo root:

```bash
grep -nE '(^|[^:A-Za-z0-9_-])/(P[0-9][0-9.]*-|python-verification-|beads-(start|ship|post|export)|workflow-(planning|writing|execute|execution|ship)|plan-(refinement|summary)|hotfix-interrupt|tdd-test-writer)' .claude/Commands/workflow-commands/python-verification-full.md
```

Expected: no output. Task 1 should already have qualified these. If a line does print, fix it in place: `/P11.5-build-validation` becomes `/workflow-commands:P11.5-build-validation-[F]`, `/python-verification-quick` becomes `/workflow-commands:python-verification-quick`, and `/python-verification-standard` becomes `/workflow-commands:python-verification-standard`. Then run the grep again until it prints nothing.

- [ ] **Step 30: Run both checks and watch them pass**

Run from the repo root:

```bash
CHECKS="<scratchpad>/sgw-checks"; R="$(git rev-parse --show-toplevel)"
bash "$CHECKS/check-phase6-gate.sh" "$R"; echo "exit=$?"
bash "$CHECKS/check-codex-companion.sh" "$R"; echo "exit=$?"
```

Expected: 19 `PASS:` lines then `ALL PASS: phase6-gate` and `exit=0`; then 11 `PASS:` lines (one names the installed companion, for example `.../codex/1.0.6/scripts/codex-companion.mjs`) then `ALL PASS: codex-companion` and `exit=0`. Any `FAIL:` line names the assertion; fix the snippet text in the file, not the check.

- [ ] **Step 31: Confirm nothing retired or pinned is left**

Run from the repo root:

```bash
F=".claude/Commands/workflow-commands/python-verification-full.md"
grep -nE 'P0[45]|Architecture Score|13-phase|14 [Pp]hases|9 Integrated|GPT-5\.4|1\.0\.2|/Users/' "$F"
grep -n -i 'simplification' "$F"
for p in '# snippet: ' 'Skipped (no new types)' 'Skipped (no sensitive files)' 'Phase 7 bug scan'; do printf '%s: %s\n' "$p" "$(grep -cF -- "$p" "$F")"; done
```

Expected: the first grep prints nothing. The second prints exactly two lines: the retirement note (`**Retired: the architecture-validation and code-simplification phases** (once`) and the Guidelines line `- **Balance** - Avoid over-engineering and over-simplification`. Then:

```text
# snippet: : 3
Skipped (no new types): 2
Skipped (no sensitive files): 3
Phase 7 bug scan: 1
```

- [ ] **Finish 1: Confirm this task's change set**

```bash
git status --short
```
Expected: exactly the files in this task's **Files** list above (`M` modified, `??` new, `D` deleted), and nothing else — apart from a `?? .claude/worktrees/` line if that local folder holds a worktree, which is never staged. Anything else means a step touched the wrong file: find it with `git diff <path>` before staging.

- [ ] **Finish 2: Commit W3**

```bash
git add -- \
  ".claude/Commands/workflow-commands/python-verification-standard.md" \
  ".claude/Commands/workflow-commands/python-verification-quick.md" \
  ".claude/Commands/workflow-commands/python-verification-full.md" \
  ".claude/agents/verification-silent-failure.md" \
  ".claude/Commands/workflow-commands/hotfix-interrupt.md" \
  ':(literal).claude/Commands/workflow-commands/P14-security-review-[SF].md' && \
git diff --cached --stat && git commit -F- <<'EOF'
chore(workflow): retire P04/P05, move the bug scan, gate Phases 6 and 14, fix the Codex pass

Delete the architecture and simplification phases; move the full tier's bug
scan into the silent-failure agent (with an in-context fallback); gate the
type-design agent and the security review; find the Codex companion by
version and launch each pass with an explicit scope.

<attribution trailer>
EOF
```
Expected: the stat lists only this task's files, then the commit summary line. Replace `<attribution trailer>` with the attribution lines from your session's system reminder before running it.

- [ ] **Finish 3: Record the commit on the W3 bead**

```bash
source .beads/sgw-ids.env && bd update "$W3" --append-notes "Landed in $(git rev-parse --short HEAD): chore(workflow): retire P04/P05, move the bug scan, gate Phases 6 and 14, fix the Codex pass" && bd show "$W3" | sed -n '1,20p'
```
Expected: the notes end with the "Landed in" line and the status is still `IN_PROGRESS` — all eight workstream beads close together when the PR opens (Task 9).

---

### Task 4: W4 — Router and rules

Spec: §6 W4; §7 (PR-only shipping; no external-tracker status writer; budget previews disclose temporary worktree branches; writing-plans Step 6 uses `git switch -c`; the router keeps *Named Scope Is Authorization* and *Verification Before Ship*).

**Files:**
- Replace: `.claude/rules/0_Beads x Superpowers/beads-workflow-router.md` (Part A)
- Create: `.claude/rules/0_Beads x Superpowers/beads.md`, `.claude/rules/0_Beads x Superpowers/no-skipping-workflow-steps.md`, `.claude/rules/0_Beads x Superpowers/never-ask-about-agent-model.md`, `.claude/skills/beads-worktree-troubleshooting/SKILL.md` (Part A)
- Modify: `.claude/rules/Git Best Practices/no-direct-push-to-master.md`, `.claude/rules/Git Best Practices/Git Best Practices.md` (Part A)
- Modify: `.claude/Commands/workflow-commands/workflow-writing-plans.md` (Part B); `.claude/Commands/workflow-commands/workflow-execute-plans.md`, `.claude/Commands/workflow-commands/workflow-execute-spikes.md`, `.claude/Commands/workflow-commands/workflow-ship-epic.md` (Part C)
- Modify, only where an old citation remains (Part D): `.claude/Commands/workflow-commands/beads-post-execution.md`, `beads-ship-task.md`, `beads-start-task.md`, `plan-refinement-qa.md`, `python-verification-quick.md`, `python-verification-standard.md`, `python-verification-full.md`, `workflow-execute-plans.md`

**Interfaces:**
- Consumes: Task 2's write-scope rule and Step 2a; the post-Task-1 naming.
- Produces: the router's 13 section headings (cited as "the router's *<heading>* section"); `beads.md`; the two interaction rules; the troubleshooting skill; *Ship Is Atomic (PR form)*; execute-plans Step 8's ship-recommendation gate; the budget-preview branch disclosure. Old router headings stop existing, and Part D re-points every citation of them.

Each part below lists its own files, interfaces and steps; run the parts in order, A first.

- [ ] **Start: mark the W4 bead in progress**

```bash
source .beads/sgw-ids.env && bd update "$W4" --status in_progress && bd show "$W4" | head -6
```
Expected: the bead shows `IN_PROGRESS`. (If `.beads/sgw-ids.env` is missing, Task 0 has not run.)

#### Part A: Router, beads rules, troubleshooting skill, Git rules

**Files:**
- Modify (whole-file replacement): `.claude/rules/0_Beads x Superpowers/beads-workflow-router.md` — re-laid out on the global router's sections, order and names; the template-only content survives as compact sections and intro bullets (561 lines)
- Create: `.claude/rules/0_Beads x Superpowers/beads.md`
- Create: `.claude/rules/0_Beads x Superpowers/no-skipping-workflow-steps.md`
- Create: `.claude/rules/0_Beads x Superpowers/never-ask-about-agent-model.md`
- Create: `.claude/skills/beads-worktree-troubleshooting/SKILL.md`
- Modify: `.claude/rules/Git Best Practices/no-direct-push-to-master.md` — append the *Ship Is Atomic (PR form)* section
- Modify: `.claude/rules/Git Best Practices/Git Best Practices.md` — append the state-check and bare-worktree paragraphs
- Check (outside the repo, never committed): `<scratchpad>/sgw-checks/check-router.sh`

**Interfaces:**
- Consumes: `.claude/rules/verification-write-scope.md` and `workflow-commands:beads-post-execution` recording the changed set (Task 2); execute-plans Step 8's ship-recommendation gate and the worktree-branch disclosure in the writing-plans, execute-plans and execute-spikes budget previews (Task 4 Part B); planning-sequence's third classification axis with `depth:full | depth:lite | depth:tdd` labels and writing-plans' `wp:carded` (Task 5); the pull guard in beads-start-task (Task 6); ship-epic's `sh:pushed` at PR open, its confirming re-run that adds `sh:shipped`, and the Step 0 unshipped-epic checks (Task 7). Already in the template and unchanged: execute-plans Step 1 routes `smoke_test: required`, shared-substrate and protected-path tasks to attended; execute-plans Step 5 protected paths; ship-epic Step 1 refuses a partial epic; writing-plans Step 4 is the autonomous refinement; planning-sequence writes `track:<name>` and `wave:<n>`.
- Produces: the router's 13 section headings, cited elsewhere as "the router's *<heading>* section" — notably *Verification Before Ship / "Done"*, *Named Scope Is Authorization*, *Workflow Rules*, *Sizing Gate — Claude picks the lane*, *Fan-Out Gate*, *Label Ladders — Append-Only, Furthest Wins* and *Completion Report*. `beads.md` (two channels, the no-remote pull guard, the readable export and `no-auto-import`, read-backs, one `bd` at a time, worktree health). `no-skipping-workflow-steps.md`. `never-ask-about-agent-model.md`. The `beads-worktree-troubleshooting` skill. *Ship Is Atomic (PR form)* in `no-direct-push-to-master.md`. The old router headings (`Hard Stop: …`, `Auto-Invoke: …`, `Standing Posture: …`) cease to exist; Part D's re-pointing step fixes the files that cite them.

- [ ] **Step 1: Write the router check**

Create `<scratchpad>/sgw-checks/check-router.sh` (substitute your session scratchpad path) with the Write tool, not a shell heredoc (see Global Constraints), with exactly this content:

```bash
#!/usr/bin/env bash
# check-router.sh — Task 4 behaviour check; Task 9 re-runs it on the final tree.
# Verifies the rewritten router (headings, length, preservation checklist, leaks,
# command names, referenced files) and the companion rules and skill Task 4 adds.
# Usage: bash check-router.sh <repo-root>
set -u
ROOT="${1:?usage: check-router.sh <repo-root>}"
RULES="$ROOT/.claude/rules"
BXS="$RULES/0_Beads x Superpowers"
ROUTER="$BXS/beads-workflow-router.md"
fails=0
checks=0
pass() { checks=$((checks + 1)); printf 'PASS: %s\n' "$1"; }
fail() { checks=$((checks + 1)); fails=$((fails + 1)); printf 'FAIL: %s\n' "$1"; }

if [ ! -f "$ROUTER" ]; then
  echo "FAIL: router missing: $ROUTER"
  exit 1
fi

# --- 1. The 13 section headings, exactly and in order ---------------------------
expected=$(cat <<'EOF'
Single-Task Routing
Epic-Batch Routing
Never Recommend Shipping an Unfinished Epic
Recommending What's Next — Batch Beats Single-Task
Sizing Gate — Claude picks the lane
Fan-Out Gate
Workflow Rules
Named Scope Is Authorization
Verification Before Ship / "Done"
Label Ladders — Append-Only, Furthest Wins
Execution Gate
Completion Report
Errors & Formatting
EOF
)
actual=$(grep '^## ' "$ROUTER" | sed 's/^## //')
if [ "$actual" = "$expected" ]; then
  pass "router has the 13 section headings, in order"
else
  fail "router headings differ from the expected 13 (expected < > actual):"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$actual") | sed 's/^/      /'
fi

# --- 2. Length -------------------------------------------------------------------
n=$(wc -l < "$ROUTER" | tr -d ' ')
if [ "$n" -ge 520 ] && [ "$n" -le 600 ]; then
  pass "router length is $n lines (520-600)"
else
  fail "router length is $n lines, expected 520-600"
fi

# --- 3. Phrases (whitespace-normalised, so line wrapping never matters) -------------
flatten() { tr '\n' ' ' < "$1" | tr -s ' '; }
ROUTER_FLAT=$(flatten "$ROUTER")
need() {   # need <label> <exact phrase>  — searched in the router
  case "$ROUTER_FLAT" in
    *"$2"*) pass "$1" ;;
    *) fail "$1 — router lacks: $2" ;;
  esac
}
need_in() {   # need_in <file> <label> <exact phrase>
  if [ ! -f "$1" ]; then fail "$2 — file missing: ${1#"$ROOT"/}"; return; fi
  local flat
  flat=$(flatten "$1")
  case "$flat" in
    *"$3"*) pass "$2" ;;
    *) fail "$2 — ${1#"$ROOT"/} lacks: $3" ;;
  esac
}

# Spec §11 router preservation checklist, item by item.
need "repo context: one repo and store, no bd repo sync" 'There is no multi-repo hub and no `bd repo sync`'
need "repo context: the two sync channels" '**Two sync channels.**'
need "repo context: pull first, push last" '`bd dolt pull` at session or task start'
need "repo context: beads is the only tracker" '**Beads is the only tracker.**'
need "repo context: any mirror is downstream" 'the mirror is downstream'
need "repo context: never the trunk" '**Never commit or push to the trunk**'
need "repo context: branch prefixes" '`feat/`, `fix/`, `refactor/`, `exp/`, `hotfix/` or `chore/`'
need "repo context: Python verification skills" '`python-verification-{quick,standard,full}`'
need "repo context: package placeholder" 'wherever these files say `src/<your_package>/`'
need "repo context: placeholder note" '**Placeholders** in angle brackets'
for row in '| Scope |' '| Refinement |' '| Execution |' '| Spikes |' '| Ship |' '| Resume state |'; do
  need "two-lane summary row $row" "$row"
done
need "router overrides skill handoffs" '**IMPORTANT — the router outranks skill handoffs.**'
need "writing-plans handoff warning" '`superpowers:writing-plans` ends with an "Execution Handoff" section'
need "no direct coding after a task starts" '**No direct coding after a task starts.**'
need "bug tasks: systematic debugging" '**Bug tasks start with systematic debugging.**'
need "bug tasks: skip phrases" 'explicit "skip debugging skill" or "just plan it"'
need "bug tasks: verification close" 'skipping the plan does not skip verification'
need "worktree beads notes point to beads.md" '**Worktrees need no beads bootstrap.**'
need_in "$BXS/beads.md" "beads.md: bd doctor is a no-op" '**`bd doctor` proves nothing in embedded mode**'
need_in "$BXS/beads.md" "beads.md: never stop the store from a worktree" '**Never stop the store from inside a worktree.**'
need "ready tasks scoped to the epic" '**Ready tasks are scoped to the active epic.**'
need "ready tasks: cross-epic fallback" 'no epic is in progress or the current epic has no ready children'
for route in '"What'"'"'s ready?"' '"I'"'"'m starting [task]"' '"Plan this task"' '"Refine / review / improve / question the plan"' \
             '"Summarize / recap / show me the plan"' '"Execute the plan" / "Run the plan"' '"Execute with subagents"' \
             '"Ship it" / "Send it" / "Commit and push" / "Create a PR"' '"Quick verify"' '"Standard verify"' \
             '"Full verify"' '"Verify this task"' '"I found a critical bug"' '"Build check"' '"Export progress"' \
             '"How'"'"'s the project looking?"' '"What'"'"'s blocked?"' '"Show me [epic/task]"' '"Create an epic/task/bug' \
             '"run linter"' '"run tests"' '"format this"' '"review my changes"'; do
  need "single-task route $route" "$route"
done
need "PR-policy note" '**PR-policy note.**'
for cmd in workflow-planning-sequence workflow-writing-plans workflow-execute-spikes \
           workflow-execution-sequence workflow-execute-plans workflow-ship-epic; do
  need "epic-batch route $cmd" "| \`workflow-commands:$cmd\`"
done
need "mode disambiguation" '**Scope picks the lane, not the verb.**'
need "mode disambiguation table" '| Ambiguous phrase |'
need "pipeline order" 'Pipeline order:'
need "hard stop 1: unshipped epic" '**Surface a finished-but-unshipped epic before starting new epic work:**'
need "hard stop 2: budget gate" '**Budget gate before every fan-out.**'
need "hard stop 3: exec:<slug> refusal" '**No bare cross-epic run.**'
need "hard stop 4: spikes" '**Spikes never run through execute-plans**'
need "hard stop 5: execute-plans ends at ex:done" '**Execute-plans ends at `ex:done` and never ships.**'
need "hard stop 6: EXEC-GATED loop" '**EXEC-GATED defer → spike → re-run loop.**'
need "hard stop 7: protected paths" '**Protected paths stay attended**'
need "hard stop 8: worktree agents" '**Worktree agents need no beads bootstrap:**'
need "step tracking" '**Step tracking.**'
need "step tracking: Plan Refinement phase" 'including `Plan Refinement` during the Q&A'
need "step tracking: delete when idle" '`rm -f .beads/.workflow-step`'
need "label table" 'Who writes what:'
need "named scope section" '## Named Scope Is Authorization'
need "named scope: branch creation lock" '**creating a branch**'
need "named scope: paid API lock" '**paid or metered API call**'
need "named scope: resolve toward the lock" 'resolve toward the lock and ask'
need "refinement: skip phrases" '"skip refinement" or "let'"'"'s just execute"'
need "refinement: one methodology, two modes" '**One methodology, two modes.**'
need "summary: bypass phrases" '"skip summary" or "just execute"'
need "summary: manual triggers" '"recap the plan"'
need "post-execution on every path" '**IMPORTANT — post-execution runs after every implementation path.**'
need "no-substitution rule" '**No substitution (hard rule).**'
need "verification: the marker" '`.beads/.verification-done`'
need "verification: the batch label" '`ex:qa:<level>` label'
need "verification: bypass phrases" '"skip verification", "I'"'"'m confident, ship it"'
need "execution gate options" '1. **Subagent-Driven**'
need "execution gate batch note" 'don'"'"'t offer the two options above for an epic-scoped run'
need "execution gate: lanes A and B" 'Lanes A and B have no Execution Gate'
need "errors: no task in progress" '**No task in progress**'
need "errors: task not found" '**Task not found**'
need "errors: empty description" '**Empty description**'
need "formatting: ready tasks and task details" '**Ready tasks** render as a table (ID, Task, Priority, Epic); **task details**'

# Governance sections carried from the global router (spec W4).
need "never recommend: what 'left' means" 'any open "Smoke gate:" bead'
need "never recommend: shipping deploys nothing" 'it deploys nothing'
need "batch beats single-task: earliest stage" 'the command for the EARLIEST stage'
need "sizing gate: ties go to C" '**Ties go to Lane C.**'
need "sizing gate: owner override" '"plan it" or "just TDD it"'
need "fan-out: base commit" '`git switch -c <branch> <sha>`'
need "fan-out: disk" 'Run `df -h .`'
need "fan-out: worktree branch disclosure" 'the branch approval `critical ai agent rule.md` requires'
need "fan-out: attended exemption" '**Attended tasks are exempt from the fan-out, not from the assessment.**'
need "one bead-status writer per lane" '**One bead-status writer per lane.**'
need "no external-tracker status writer" 'There is no external-tracker status writer'
need "ladders: sh ladder" 'sh: pushed > shipped'
need "ladders: wp:carded" 'wp: drafted | skipped | carded > refined-rN > applied-rN > approved'
need "ladders: sh:pushed is not shipped" '**`sh:pushed` is not shipped.**'
need "ladders: smoke:passed flag" '**`smoke:passed` is a flag that discharges `ex:smoke-pending`.**'
need "completion report: /clear step" 'Show `/clear` as its own numbered step'
need "completion report: epic status table" '### Epic Status Table — always the WHOLE epic'

# --- 4. No owner or platform leaks in anything Task 4 writes -------------------------
# Generic platform patterns, plus the owner's private terms from private-terms.txt next
# to this script (one extended regex per line; never committed — see Global Constraints).
TERMS="$(cd "$(dirname "$0")" && pwd)/private-terms.txt"
PRIV=$(grep -v '^[[:space:]]*$' "$TERMS" 2>/dev/null | paste -sd'|' -)
if [ -n "$PRIV" ]; then pass "private term list loaded"; else fail "private term list missing or empty: $TERMS"; fi
LEAK="jira|flutter|(^|[^a-z])dart([^a-z]|$)|127\.0\.0\.1|~/\.claude/rules${PRIV:+|$PRIV}"
for f in "$ROUTER" "$BXS/beads.md" "$BXS/no-skipping-workflow-steps.md" \
         "$BXS/never-ask-about-agent-model.md" \
         "$ROOT/.claude/skills/beads-worktree-troubleshooting/SKILL.md" \
         "$RULES/Git Best Practices/no-direct-push-to-master.md" \
         "$RULES/Git Best Practices/Git Best Practices.md"; do
  rel=${f#"$ROOT"/}
  if [ ! -f "$f" ]; then fail "missing file: $rel"; continue; fi
  hits=$(grep -n -i -E "$LEAK" "$f")
  if [ -z "$hits" ]; then
    pass "no owner/platform leak in $rel"
  else
    fail "leak in $rel:"
    printf '%s\n' "$hits" | sed 's/^/      /'
  fi
done

# --- 5. No bare /workflow-… command (the one deliberate "never a bare" example is allowed)
bare=$(sed 's#never a bare `/workflow-execute-plans`##' "$ROUTER" \
  | grep -n -o -E '/workflow-[A-Za-z0-9._-]+[:/]?' \
  | grep -v -E ':/workflow-commands[:/]$')
if [ -z "$bare" ]; then
  pass "no bare /workflow-… command names in the router"
else
  fail "bare command names in the router:"
  printf '%s\n' "$bare" | sed 's/^/      /'
fi

# --- 6. Every workflow-commands:<name> in the router exists as a command file ------
missing=0
total=0
while IFS= read -r nm; do
  [ -z "$nm" ] && continue
  case "$nm" in *-) continue ;; esac          # brace forms such as python-verification-{…}
  total=$((total + 1))
  if [ ! -f "$ROOT/.claude/Commands/workflow-commands/$nm.md" ]; then
    fail "router names a missing command: workflow-commands:$nm"
    missing=$((missing + 1))
  fi
done <<EOF
$(grep -o -E 'workflow-commands:[A-Za-z0-9._-]+(\[[A-Z]+\])?' "$ROUTER" | sed 's/^workflow-commands://' | sort -u)
EOF
[ "$missing" -eq 0 ] && pass "all $total workflow-commands references in the router resolve"

# --- 7. Every rule, reference and skill the router points at exists ------------------
for rule in 'beads-plugin-cli-only.md' 'beads.md' 'verification-write-scope.md' \
            'surface-unshipped-epics.md' 'never-ask-about-agent-model.md' \
            'critical ai agent rule.md' 'protect_plans_and_commit_all.md' \
            'Git Best Practices.md' 'no-direct-push-to-master.md'; do
  if [ -n "$(find "$RULES" -name "$rule" -print 2>/dev/null | head -1)" ]; then
    pass "referenced rule exists: $rule"
  else
    fail "router references a missing rule: $rule"
  fi
done
if [ -f "$ROOT/.claude/Commands/workflow-commands/references/refinement-methodology.md" ]; then
  pass "referenced refinement-methodology.md exists"
else
  fail "router references a missing refinement-methodology.md"
fi

# --- 8. Companion rules, skill and Git rules -------------------------------------------
need_in "$BXS/beads.md" "beads.md: two channels" 'at ship or session close run `git push` and `bd dolt push`'
need_in "$BXS/beads.md" "beads.md: no-remote pull guard" "grep -q 'No remotes configured'"
need_in "$BXS/beads.md" "beads.md: export refresh" 'bd export -o .beads/issues.jsonl'
need_in "$BXS/beads.md" "beads.md: auto-import off with the safe append" "printf '\\nno-auto-import: true\\n' >> .beads/config.yaml"
need_in "$BXS/beads.md" "beads.md: never two bd commands at once" '## Never run two `bd` commands at the same time'
need_in "$BXS/beads.md" "beads.md: revert diagnosis" 'bd history <id> --json'
need_in "$BXS/beads.md" "beads.md: troubleshooting skill pointer" '`beads-worktree-troubleshooting` skill'
need_in "$BXS/beads.md" "beads.md: bd remember" 'bd remember "insight"'
need_in "$BXS/no-skipping-workflow-steps.md" "no-skipping: skip phrases" '"skip refinement", "skip verification", "skip summary"'
need_in "$BXS/no-skipping-workflow-steps.md" "no-skipping: not-skip phrases" 'These are NOT skip phrases: "ship it"'
need_in "$BXS/no-skipping-workflow-steps.md" "no-skipping: the sizing-gate exception" '**One standing exception: the Sizing Gate**'
need_in "$BXS/no-skipping-workflow-steps.md" "no-skipping: the plan-depth mirror" 'assigning a task `PLAN-LITE` or `TDD-DIRECT` as its plan depth'
need_in "$BXS/never-ask-about-agent-model.md" "never-ask: no Model line" 'no `Model:` line'
need_in "$BXS/never-ask-about-agent-model.md" "never-ask: tier aliases only" 'use only tier aliases'
need_in "$ROOT/.claude/skills/beads-worktree-troubleshooting/SKILL.md" "skill: frontmatter name" 'name: beads-worktree-troubleshooting'
need_in "$ROOT/.claude/skills/beads-worktree-troubleshooting/SKILL.md" "skill: critical-rule path retargeted" '`.claude/rules/critical ai agent rule.md`'
need_in "$ROOT/.claude/skills/beads-worktree-troubleshooting/SKILL.md" "skill: numbers labelled as beads 1.0.4" 'Observed with beads 1.0.4'
need_in "$RULES/Git Best Practices/no-direct-push-to-master.md" "git: Ship Is Atomic (PR form)" '## Ship Is Atomic (PR form)'
need_in "$RULES/Git Best Practices/no-direct-push-to-master.md" "git: no partial ship" 'never narrow the scope with a leading "push the branch only?" question'
need_in "$RULES/Git Best Practices/no-direct-push-to-master.md" "git: never checkout HEAD -- ." 'never run `git checkout HEAD -- .`'
need_in "$RULES/Git Best Practices/Git Best Practices.md" "git: fetch before ahead/behind" 'run `git fetch origin` in the same response'
need_in "$RULES/Git Best Practices/Git Best Practices.md" "git: bare worktree request" 'a bare "create a worktree" request'

echo
if [ "$fails" -eq 0 ]; then
  echo "RESULT: PASS ($checks checks)"
  exit 0
fi
echo "RESULT: FAIL ($fails of $checks checks failed)"
exit 1
```

- [ ] **Step 2: Run the check and watch it fail**

Run, from the repo root:

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-router.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
```

Expected: about 90 `FAIL:` lines — the heading diff, `router length is 406 lines`, dozens of `router lacks:` phrases, `file missing` for `beads.md`, the two other new rules and `SKILL.md`, a `leak in …beads-workflow-router.md` line quoting the old router's "(Jira, Linear)" example, and the Git-rule phrases. Last lines `RESULT: FAIL (… of 152 checks failed)` and `exit=1`. (Measured on the pre-sync tree: 93 of 152. If it passes, stop: the router has already been rewritten.)

- [ ] **Step 3: Replace the router**

Replace the whole content of `.claude/rules/0_Beads x Superpowers/beads-workflow-router.md` with:

````markdown
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
| "lint" / "run linter" | `ruff check .` (plus `mypy` if configured) — read-only; to fix what it finds, `workflow-commands:P02-lint-issues-fix-[QSF]` |
| "run tests" / "test this" | `pytest -x -q` |
| "format" / "format this" | `ruff format --force-exclude <changed files>` — the task's changed set only (`verification-write-scope.md`); formatting the whole project is its own task |
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
````

- [ ] **Step 4: Create `beads.md`**

Create `.claude/rules/0_Beads x Superpowers/beads.md` with:

````markdown
# Beads

**Section:** Task Management

How to run `bd` safely in this workflow. The `beads:*` plugin skills run these same
commands — the plugin has no MCP layer (`beads-plugin-cli-only.md`).

## Two channels: code and beads

- Git carries code; `bd dolt` carries beads. Pull first, push last: at session or task
  start run `git pull` and `bd dolt pull`; at ship or session close run `git push` and
  `bd dolt push`. Never `--force` a beads push except a deliberate, agreed re-baseline.
- The Dolt remote lives on the project's own git remote:
  `bd dolt remote add origin git+https://github.com/<owner>/<repo>.git`.
- A project with no Dolt remote yet keeps working. `bd dolt push` skips on its own
  ("No remote is configured — skipping."), but `bd dolt pull` fails ("no remote"), so
  every step that pulls guards it and says so in one line:

  ```bash
  if bd dolt remote list 2>/dev/null | grep -q 'No remotes configured'; then
    echo "Beads: no Dolt remote configured — skipping bd dolt pull."
  else
    bd dolt pull
  fi
  ```

## The JSONL export is a readable artifact, nothing else

- `.beads/issues.jsonl` is for reading — diffs, grep, progress reports. It is not a
  sync channel. Keep it untracked and gitignored, and never re-track it.
- After mutating `bd` commands — and always after a burst of concurrent writes, such as
  a parallel agent fan-out — refresh it with `bd export -o .beads/issues.jsonl`
  (`bd export` without `-o` writes to stdout).
- Keep the export unstaged and untracked: `.beads/config.yaml` carries
  `export.git-add: false`, and `.beads/.gitignore` lists `issues.jsonl`. The config also
  carries `no-auto-import: true`, which mirrors the setup the fix below was made on.
  Beads 1.0.4 does not read that key — the binary has no such setting, and its checkout
  hook re-exports from the database rather than importing the file — so it costs nothing
  but protects nothing on 1.0.4 either; the untracked export is what holds. `bd config
  set` rejects the key, so it is appended directly, with a leading newline, because
  `bd config set` leaves the file without a trailing one and a plain append corrupts the
  YAML:

  ```bash
  bd config set export.git-add false
  printf '\nno-auto-import: true\n' >> .beads/config.yaml
  ```

- **Why — observed in a downstream project.** Finished beads kept reverting on their
  own. `issues.jsonl` was tracked in git AND was an auto-import source. `bd import`
  upserts every row in the file over the live store; auto-import fired whenever the file
  was newer than the database; and any checkout, merge or worktree switch that rewrote
  the file armed it. A stale snapshot then silently restored old `status` and old
  `updated_at` values over rows that had moved on — more than a dozen at a time, once
  including a shipped epic and all its children. Untracking the export and stopping it
  from being auto-staged fixed it (the `no-auto-import` line was added at the same time).
  Undo neither.

## Read back what you write

- Read back every mutating command with `bd show <id>`, and never report a bead state
  you have not read back. This matters most for the batch lane's `wp:*` and `ex:*`
  labels: they are its only durable progress record, and a lost label silently un-does
  a finished wave, so a resumed run redoes it.
- Know the limit. A read-back would not have caught the reverts above: those writes did
  land and read back correctly at the time, and were undone later by an unrelated
  command, usually in another session. So if a bead looks wrong and you already
  verified the write, do not simply re-apply it. Compare its `updated_at` with when you
  wrote it: a value OLDER than your own write means something restored a snapshot, and
  the fix is upstream, not another retry.

## Never run two `bd` commands at the same time

Every worktree and session shares one embedded Dolt store, and a `bd` process that
commits a stale working set overwrites rows another process committed moments before.
Put every `bd` command of a step in one `&&` chain — reads included, since they can
create commits too — never in separate parallel tool calls. A parallel agent fan-out
has the same exposure, so read its labels back after it returns.

Observed in a downstream project: a `bd close` landed and read back closed; a
`bd create` issued as a parallel tool call in the same response committed seconds
later, and its only change was that status going from closed back to open.

To diagnose a revert, run `bd history <id> --json` (keys `CommitHash`, `CommitDate`,
`Committer`, `Issue`), then `bd diff <full-hash> <full-hash>`. Short hashes fail with
"branch not found", and the diff shows issue fields only, not dependencies. If the
reverting commit's time matches another `bd` process you ran, it is this race: re-apply
the write serially and read it back.

## Worktrees and store health

- **No bootstrap after `EnterWorktree`.** In beads' embedded mode (check yours with
  `bd dolt status`) a fresh worktree sees the full parent store automatically, through
  git-common-dir detection. There is no setup step to invent.
- **Never stop the store from inside a worktree.** In server mode, `bd dolt stop`
  targets the shared parent store and takes beads down for every concurrent agent.
  Start or stop it only from the main repo root, and only when something is actually
  wrong.
- **`bd doctor` proves nothing in embedded mode** — it exits cleanly whatever state the
  store is in, so never use it as a readiness gate. Verify a store with
  `bd list -n 0 | wc -l` against a known count (plain `bd list` stops at 50 rows), plus
  non-zero `manifest` and `journal.idx` files under `.beads/embeddeddolt/`.
- If `bd` in a worktree returns `[]`, errors, or reports "database is locked", load the
  `beads-worktree-troubleshooting` skill.

## Cross-session memory

`bd remember "insight"` persists knowledge across sessions; search it with
`bd memories <keyword>`.
````

- [ ] **Step 5: Create `no-skipping-workflow-steps.md`**

Create `.claude/rules/0_Beads x Superpowers/no-skipping-workflow-steps.md` with:

```markdown
# Perform Every Mandated Step

**Section:** Interaction Guidelines

If a rule, skill, agent, command or CLAUDE.md directive says to perform a step, perform
it — every checklist item, every auto-invoke, every numbered instruction.

There are only two legitimate pauses:

1. **A destructive or locked action the skill does not explicitly authorize** — a
   force-push, a hard reset, dropping tables, a force-merge. If the skill authorizes it
   (for example, `workflow-commands:beads-ship-task` authorizes pushing the feature
   branch and opening its PR), proceed without asking. The hard locks in
   `critical ai agent rule.md` — creating a branch, a managed-cloud mutation, a merge to
   the trunk — always pause for the owner, even when a skill names the action.
2. **Genuinely conflicting instructions** that reading the files cannot resolve. Quote
   both verbatim and ask which wins. Don't invent ambiguity to create an opt-out.

Skip authority comes only from explicit words this turn: "skip refinement", "skip
verification", "skip summary", "skip debugging skill", "just plan it", "just execute",
"let's just execute", "don't close the task", "I'm confident". These are NOT skip
phrases: "ship it", "execute the plan", "quick verify", "done", "looks good" — they run
the full workflow.

**One standing exception: the Sizing Gate** (the router's
*Sizing Gate — Claude picks the lane* section). Choosing Lane A (TDD-direct) or Lane B
(plan-lite) is a sanctioned decision, not a skip: the owner delegates that judgement so
that small fixes stop attracting full planning.

The same exception covers its batch mirror: `workflow-commands:workflow-planning-sequence`
assigning a task `PLAN-LITE` or `TDD-DIRECT` as its plan depth, and
`workflow-commands:workflow-writing-plans` therefore skipping the refinement round for
that task. That is the assigned depth taking effect, not a skipped step — and the owner
has already seen and approved the depth at two gates (the planning-sequence review and
the writing-plans budget preview).

The exception is bounded. The lane is announced in one line, with its reason, before
work starts; ties go to Lane C; and a mid-flight discovery that the work is bigger
means stop and switch lanes. It grants no authority to skip anything else —
verification, the ship steps, `workflow-commands:beads-post-execution` and the
Completion Report still run in every lane.

If Claude disagrees with a step, it runs the step anyway, raises the concern in the
final summary, and proposes a rule change in a follow-up turn.
```

- [ ] **Step 6: Create `never-ask-about-agent-model.md`**

Create `.claude/rules/0_Beads x Superpowers/never-ask-about-agent-model.md` with:

```markdown
# Never Ask Which Model an Agent Run Uses

**Section:** Interaction Guidelines

The model tier a workflow, subagent or fan-out runs on is configuration, not a user
decision. Never print it in a budget gate, list it as an option, or ask for confirmation
of it. A budget gate may show scope, agent count, artifacts and a cost band against "the
5-hr usage limit" — no `Model:` line.

In `opts.model`, use only tier aliases (`"opus"`, `"sonnet"`, `"haiku"`, `"fable"`),
never a versioned model id: a pinned version strands the fan-out on a superseded
generation and goes stale in every gate that prints it.

If the user asks, answer plainly: name the tier, or read the resolved id back from the
run.
```

- [ ] **Step 7: Create the troubleshooting skill**

Create `.claude/skills/beads-worktree-troubleshooting/SKILL.md` with:

```markdown
---
name: beads-worktree-troubleshooting
description: Use when bd in a worktree returns [] or errors, when verifying the embedded Dolt store's integrity, after a concurrent bd write burst, or on "database is locked by another dolt process".
---

# Beads Worktree Troubleshooting (embedded mode)

## Worktree sees no data (`[]` or errors)

1. Confirm it is a real worktree of the embedded-mode repo:
   `git rev-parse --git-common-dir` from the worktree should resolve to the main repo's
   `.git`.
2. Confirm the parent's `.beads/metadata.json` shows `"dolt_mode": "embedded"`.
3. Inspect `.beads/embeddeddolt/` in the MAIN repo: `manifest` and `journal.idx` must
   exist with non-zero size. Zero-byte or missing is a real corruption signal — a
   data-safety event: stop and follow `.claude/rules/critical ai agent rule.md` before
   any further mutation.

There is no `.beads/redirect` file to author, no port to discover, and no
`bd dolt start` / `stop` dance in embedded mode.

## Verifying store integrity

`bd doctor` in embedded mode always exits 0 with a static "not yet supported" note — it
never varies with the store's state, so never treat it as a gate. Instead compare an
unbounded read-back count against a known baseline (`bd list -n 0 | wc -l` — the default
`bd list` caps at 50 rows and silently truncates) plus the `manifest` / `journal.idx`
size check above.

## Lock contention ("database is locked by another dolt process")

A real storage-layer lock exists (`.beads/embeddeddolt/.lock`). Observed with beads
1.0.4 in a downstream project: at a realistic concurrency of about 2–8 parallel
writers, contention was 0%; it appeared only in an artificial stress test with about 50
cross-worktree writers (22–40% of writes), and every failure was loud — a non-zero exit
or an explicit error — with no silent loss ever observed. Re-validate these numbers
after a beads upgrade.

If it occurs, retry with a bound: 3–5 attempts, about 200–500 ms initial backoff capped
at about 5–10 s, retrying on the lock error or "context canceled". BEFORE each retry,
check whether the write already landed (`bd list` / `bd show` keyed on the title being
submitted): in that stress test roughly a quarter of the loud failures had actually
succeeded, so a blind resubmit creates a duplicate issue.

## JSONL staleness after a killed write

A killed `bd` process can land its Dolt write while its own JSONL auto-export is
cancelled mid-flight. A later write's full re-export usually heals this — but if the
killed write was the LAST in a concurrent burst, nothing triggers the heal. Flush by
hand: `bd export -o .beads/issues.jsonl`.

## Gitignore

`.beads/.gitignore` must contain `embeddeddolt/` — confirm
`git check-ignore .beads/embeddeddolt` succeeds before any broad `git add` in the main
checkout.
```

- [ ] **Step 8: Add *Ship Is Atomic (PR form)***

In `.claude/rules/Git Best Practices/no-direct-push-to-master.md`, insert after the line
`There are no exceptions to this rule. If the user asks to push directly to master, explain why this is blocked and offer to create a PR instead.`
(the last line of the file) — keeping one blank line between them:

```markdown
## Ship Is Atomic (PR form)

"Ship it", "send it", "commit and push" and "create a PR" all run the whole ship
sequence end to end — `workflow-commands:beads-ship-task` for one task,
`/workflow-commands:workflow-ship-epic` for an epic: stage every changed file explicitly
(`protect_plans_and_commit_all.md` Rule 3), commit, push the feature branch
(`git push -u origin HEAD`), and open the PR. Never run a partial subset, and never
narrow the scope with a leading "push the branch only?" question — the phrase already
chose the whole sequence (`no-skipping-workflow-steps.md` lists "ship it" as NOT a skip
phrase).

One legitimate pause, decided up front: a long-lived branch — an epic or foundation
branch — whose work should not be proposed for the trunk yet. Then ask before any ship
step and name the consequence: "Shipping `<branch>` opens a PR proposing all of its
current commits to the trunk. Open the PR now, or push the branch only?" Do exactly what
the user picks, in full. If you are unsure whether a branch is long-lived, ask; normal
`feat/`, `fix/` and `chore/` branches ship without asking.

If a push is rejected, the remote has commits you don't: fetch, merge the remote branch
(or the trunk) into yours, re-verify, and push again. Never force-push past a rejected
push — it throws away someone else's commits. And never run `git checkout HEAD -- .` to
"fix" a ship: it silently overwrites every uncommitted change in the tree.
```

- [ ] **Step 9: Add the state-check and worktree paragraphs**

In `.claude/rules/Git Best Practices/Git Best Practices.md`, insert after the line that
begins `Releases & rollback: Tag every release` (the file's last line, which has no
trailing newline) — one blank line before each paragraph, and end the file with a newline:

```markdown
State checks: `git branch -vv` and `git status` compare against the cached copy of origin, so run `git fetch origin` in the same response before claiming a branch is ahead of or behind its remote.

Worktrees: a bare "create a worktree" request (no task attached) ends once the worktree exists — no `pip install` or `uv sync`, no `pytest`, `ruff` or `mypy`, no `python -m build` until real work starts there or the user asks. Create it detached unless the user approves a branch (`critical ai agent rule.md`).
```

- [ ] **Step 10: Run the check and watch it pass**

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-router.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
```

Expected: only `PASS:` lines — among them `router has the 13 section headings, in order`,
`router length is 561 lines (520-600)`, `all 19 workflow-commands references in the router resolve`
and one `no owner/platform leak in …` per file — then `RESULT: PASS (153 checks)` and `exit=0`.
Fix any FAIL before committing; Task 9 re-runs this check on the final tree.

#### Part B: writing-plans — Step 6 base-drift guard and the branch disclosure

**Files:**
- Modify: `.claude/Commands/workflow-commands/workflow-writing-plans.md` — Step 6's bucket agents start with `git switch -c <bucket-branch> <epic-head-sha>`; the Step 2 preview discloses the temporary worktree branches.

**Interfaces:**
- Consumes: the disclosure sentence and the Fan-Out Gate rule (each isolated agent's first command is `git switch -c <branch> <sha>`, never `git merge <sha>`) that Task 4 writes into the router; `critical ai agent rule.md`'s branch-approval requirement.
- Produces: bucket branch names `chore/wp-apply-<task-id>-<n>`; a `Branches:` line in the writing-plans preview, which Task 5 keeps when it rewrites Step 2.

These steps run after Task 1, so command names in the files already read `/workflow-commands:<name>`. Every anchor below avoids the lines Task 1 rewrites, or quotes them in their post-Task-1 form; if an anchor does not match, re-read the file rather than guessing.

- [ ] **Step 1: Disclose the temporary worktree branches in the writing-plans budget preview**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Step 2: Preview & Budget Gate [main ctx]`, replace this whole line:

```text
Artifacts: docs/plans/<epic-slug>/
```

with:

```text
Artifacts: docs/plans/<epic-slug>/

Branches:  Step 6 may split a long plan across two worktree agents. This
           fan-out creates temporary worktree branches, which are merged back
           and removed as each agent finishes; approving this gate is the branch
           approval that `critical ai agent rule.md` requires.
```

This line sits inside the preview's fenced block, so keep its indentation as shown.

- [ ] **Step 2: Make Step 6's base-drift guard start each bucket branch at the epic head**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Step 6: Apply #1 → Approve [workflow]`, replace the passage that begins

```text
**Worktree base-drift guard (mandatory).**
```

and ends

```text
already caught up, the merge is a no-op.
```

(both ends included) with:

````markdown
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
````

- [ ] **Step 3: Pass the bucket branch name into each split-apply agent**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Step 6: Apply #1 → Approve [workflow]`, replace this whole line:

```text
  agent(applyBucketPrompt(planFile, bucket, epicHeadSha), {
```

with:

```js
  agent(applyBucketPrompt(planFile, bucket, epicHeadSha, `chore/wp-apply-${task.id}-${i}`), {
```

This line is inside the `js` block that follows "Have each agent commit its own change"; keep its two-space indent.

- [ ] **Step 4: Restate the base-drift guard in the CRITICAL list**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## CRITICAL — Honor Project Rules`, replace the passage that begins

```text
- **Step 6 worktree base-drift guard**: a reused worktree is not guaranteed to
```

and ends

```text
  practice, not a hypothetical.
```

(both ends included) with:

```markdown
- **Step 6 worktree base-drift guard**: an isolated worktree is not guaranteed
  to start at the epic branch's current tip. Every split-apply agent's first
  command is `git switch -c <bucket-branch> <epic-head-sha>` (the SHA passed via
  `args`) — never `git merge <sha>`, which can drag trunk commits in, and never a
  hand-reconstructed file. In main context, verify each bucket branch's ancestry
  before merging; if it isn't an ancestor, use a content-level `git merge-file`
  against the pre-Step-6 original instead of `git merge` (which would report a
  spurious conflict even on agreeing content). See Step 6 for the full procedure
  — this has already happened in practice, not a hypothetical.
```

- [ ] **Step 5: Verify Part B of Task 4**

Run from the repo root:

```bash
d=.claude/Commands/workflow-commands
printf '%s\n' \
  "switch-c=$(grep -cF 'git switch -c <bucket-branch> <epic-head-sha>' "$d/workflow-writing-plans.md")" \
  "old-merge-guard=$(grep -cF 'git merge <that-sha>' "$d/workflow-writing-plans.md")" \
  "disclosure=$(grep -cF 'approving this gate is the branch' "$d/workflow-writing-plans.md")" \
  "bucket-branch-name=$(grep -cF 'chore/wp-apply-' "$d/workflow-writing-plans.md")"
```

Expected output, exactly:

```text
switch-c=2
old-merge-guard=0
disclosure=1
bucket-branch-name=2
```

Any other number means a step above was skipped or applied to the wrong passage; re-read that file and fix it before moving on.

#### Part C: ship and status guardrails in execute-plans, execute-spikes and ship-epic

**Files:**
- Modify: `.claude/Commands/workflow-commands/workflow-execute-plans.md` — Step 2 preview discloses the temporary worktree branches; Step 8's "Fully executed" bullet defers to a new `### Ship-recommendation gate (HARD RULE)` subsection; two new CRITICAL bullets (this command never changes bead status; read back label writes and keep bead writes serial).
- Modify: `.claude/Commands/workflow-commands/workflow-execute-spikes.md` — Step 2 preview discloses the temporary worktree branches.
- Modify: `.claude/Commands/workflow-commands/workflow-ship-epic.md` — Step 6 item 2: the batch lane's only status transition.

**Interfaces:**
- Consumes: the router's *Workflow Rules* section (one bead-status writer per lane) and `.claude/rules/0_Beads x Superpowers/beads.md` (serial `bd` writes, read-backs), both written earlier in this task; the budget-preview disclosure sentence.
- Produces: execute-plans Step 8's `### Ship-recommendation gate (HARD RULE)` subsection and reworded "Fully executed" bullet (Task 7 rewrites that bullet; Task 8 rewrites the paragraph between the bullets and the gate); ship-epic Step 6 item 2.

- [ ] **Step 1: execute-plans — disclose the temporary worktree branches in the Step 2 preview**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, section `## Step 2: Schedule + Preview / Budget Gate [main ctx]`, replace the passage that begins `collected and presented as one batched session (walk-away batching).` and ends `Proceed? (yes / adjust scope / cancel)` with:

```markdown
collected and presented as one batched session (walk-away batching).

This fan-out creates temporary worktree branches, which are merged back and
removed as each agent finishes; approving this gate is the branch approval
that `critical ai agent rule.md` requires.

Proceed? (yes / adjust scope / cancel)
```

- [ ] **Step 2: execute-plans — make Step 8's "Fully executed" bullet defer to the ship gate**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, section `## Step 8: Epic Status & Next-Steps Summary [main ctx]`, replace the passage that begins `- **Fully executed**` and ends `` <epic-id>`. `` with:

```markdown
- **Fully executed** — if every task in the resolved scope (Step 0a) is
  `ex:done` and the ship-recommendation gate below finds nothing left, say so
  and name the next command: `/workflow-commands:workflow-ship-epic <epic-id>`.
```

- [ ] **Step 3: execute-plans — add the ship-recommendation gate to Step 8**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, insert after the line `possibility.`, leaving one blank line between that line and the new text:

`possibility.` is the last line of Step 8's paragraph that begins `State the single next command plainly`; the new subsection goes between that paragraph and the `---` before `## Beads Label Lifecycle (execute-plans)`.

```markdown
### Ship-recommendation gate (HARD RULE)

Never recommend, suggest, or ask about `/workflow-commands:workflow-ship-epic`
while any task in the epic is left — not as the next step, not as an option, not
as "want me to start the ship?". Name the ship only when all of these hold, read
with `beads:list` / `beads:show` in this turn, never from memory or an earlier
table:

- every open child task is `ex:done`, and no `ex:smoke-pending` or `ex:blocked`
  is still in force. A label is *still in force* when nothing later has
  discharged it: `ex:smoke-pending` stays in force until the task reaches
  `ex:done` (or carries `smoke:passed`), and `ex:blocked` stays in force while
  the bug it filed is open or the task has not reached `ex:done` since. Labels
  are append-only, so an old `ex:blocked` next to a later `ex:done` is history,
  not a blocker;
- no `Smoke gate:` bead under the epic is open;
- no child is `wp:deferred`, unplanned (no `wp:*` label), or not started (no
  `ex:*` label);
- no attended or ops child is open — a migration apply, a cloud-console step, a
  release gate.

When anything is left, name the step that finishes it instead:

- **A smoke that needs the epic's code running somewhere** — for example a
  server change whose smoke runs against a staging environment: the next step is
  a deploy of the epic branch to that environment, then the smoke. A deploy is a
  managed-cloud change, so ask the owner first
  (`.claude/rules/critical ai agent rule.md`). Never "ship so that it deploys":
  shipping opens the integration PR and closes tasks; it deploys nothing.
- **A `wp:deferred` or unplanned task:** `/workflow-commands:workflow-writing-plans <epic-id>`
  once its upstream has executed, or ask the owner whether to move it out of the
  epic. Waiting on something outside the epic means the epic is not done yet —
  say so, and do not work around it by shipping.
- **An `ex:blocked` task:** the fix pass for the bug it filed (Step 7).
- **An open attended or ops step:** name the owner action it needs.

Why: in a downstream project, a completion report once recommended shipping
while three smoke gates, a deferred release gate and a migration gate were still
open, reasoning that the ship would put the code on staging so the smokes could
run. The owner rejected it: an epic ships when its work is finished.
`/workflow-commands:workflow-ship-epic` refuses a partial epic at its Step 1
anyway; this gate stops the recommendation before that refusal is ever needed.
```

- [ ] **Step 4: execute-plans — add the status-writer and read-back rules to the CRITICAL list**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, insert after the line `` - **Beads via skills:** use `beads:*` skills, never raw `bd` in Bash. ``, as the very next line (no blank line between — it continues the list):

```markdown
- **This command never changes bead status.** Never call `beads:update --status`
  here — not to claim a task, not to finish one. The `ex:*` labels are this lane's
  only progress record, and `/workflow-commands:workflow-ship-epic` makes the
  single status transition (open → closed) at the end. "Mark `in_progress` when
  starting" is a single-task-lane rule; carried into a batch run it adds a second
  status writer that nothing ever clears, so tasks strand in `in_progress` and the
  epic reads as a mix of whichever writes happened to land (observed in a
  downstream project). "Reopen the task" in Step 6 means another fix pass on the
  code, not a status change. See the router's *Workflow Rules* section.
- **Read back every label write, and keep bead writes serial.** After each
  `beads:label` / `beads:update`, confirm the change with `beads:show`. If it is
  missing, retry once — serially, never alongside another beads command — and if
  it is still missing, stop and surface it. Never run two beads commands at the
  same time: two `bd` processes writing the shared store can revert each other's
  rows. When a fan-out returns, re-read every task's labels before trusting them:
  a lost `ex:*` label silently un-does a finished task, and a resumed run would
  redo it. See `.claude/rules/0_Beads x Superpowers/beads.md`.
```

- [ ] **Step 5: execute-spikes — disclose the temporary worktree branches in the Step 2 preview**

In `.claude/Commands/workflow-commands/workflow-execute-spikes.md`, insert after the line `Deliverable: docs/plans/<epic-slug>/<spike-id>-findings.md (+ evidence) per spike; code discarded`, leaving one blank line between that line and the new text:

Spike worktrees are discarded, not merged back, so this preview's sentence says "removed" where execute-plans and writing-plans say "merged back and removed".

```markdown
This fan-out creates temporary worktree branches, which are removed as each
agent finishes (spike code is never merged back); approving this gate is the
branch approval that `critical ai agent rule.md` requires.
```

- [ ] **Step 6: ship-epic — Step 6 is the batch lane's only status transition**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, section `## Step 6: Close Tasks + Epic (idempotent) [main ctx]`, replace the passage that begins `` 2. **Close the epic** via `beads:close` `` and ends `already closed it.` with:

```markdown
2. **Close the epic** via `beads:close` (`--reason="All child tasks completed"`).
   Skip it if it is already closed. It will not have been closed by
   `/workflow-commands:workflow-execute-plans`, which never touches bead status,
   so this step is the only status transition in the whole batch lane. Child
   tasks reaching here read `open` with `ex:done` — the expected steady state
   before ship, not a missed update.
```

- [ ] **Step 7: Verify this part's edits landed**

Run from the repo root:

```bash
C=.claude/Commands/workflow-commands
while IFS='|' read -r want f s; do
  got=$(grep -c -F -- "$s" "$C/$f")
  if [ "$got" = "$want" ]; then echo "ok   $f: $s"; else echo "MISMATCH (got $got, want $want)  $f: $s"; fi
done <<'EOF'
1|workflow-execute-plans.md|### Ship-recommendation gate (HARD RULE)
1|workflow-execute-plans.md|ship-recommendation gate below finds nothing left
1|workflow-execute-plans.md|This command never changes bead status.
1|workflow-execute-plans.md|Read back every label write, and keep bead writes serial.
1|workflow-execute-plans.md|This fan-out creates temporary worktree branches, which are merged back and
1|workflow-execute-spikes.md|This fan-out creates temporary worktree branches, which are removed as each
1|workflow-ship-epic.md|so this step is the only status transition in the whole batch lane
EOF
```

Expected: 7 lines, every one starting with `ok`. A `MISMATCH` line names the file and phrase whose edit is missing or duplicated.

#### Part D: Re-point citations of the old router headings

The rewrite drops the old "Hard Stop: …" and "Auto-Invoke: …" headings. On 2026-10-02, eight citations in seven other files still named them: seven of *Hard Stop: Verification Before Ship / "Done"* (in `beads-post-execution`, `beads-ship-task`, `beads-start-task`, the three verification tiers and `workflow-execute-plans`, the last one wrapped inside a blockquote) and one of "Auto-Invoke: Plan Summary In Console After Refinement" (in `plan-refinement-qa`). This step points them at the new headings. It is idempotent, so it is safe whatever Tasks 2 and 3 already rewrote.

**Files:**
- Modify: any of `.claude/Commands/workflow-commands/beads-post-execution.md`, `beads-ship-task.md`, `beads-start-task.md`, `plan-refinement-qa.md`, `python-verification-quick.md`, `python-verification-standard.md`, `python-verification-full.md`, `workflow-execute-plans.md` that still carries an old citation.

**Interfaces:**
- Consumes: the new router's `## Verification Before Ship / "Done"` and `## Workflow Rules` headings (Part A).
- Produces: every "the router's *<heading>*" citation in the tree names a heading the router has — Task 9's `check-references.sh` asserts it.

- [ ] **Step 1: Re-point the citations**

Run from the repo root:
```bash
find .claude -type f -name '*.md' -not -path '.claude/worktrees/*' -not -name 'beads-workflow-router.md' -print0 | \
  xargs -0 perl -0777 -i -pe '
    s/Hard\s+Stop:\s+Verification(\s+)Before(\s+(?:>[ \t]*)?)Ship/Verification$1Before$2Ship/g;
    s/\(per the beads-workflow-router "Auto-Invoke: Plan Summary In Console After Refinement" rule\)/(per the router\x27s *Workflow Rules* section)/g;
  ' && git diff --stat
```
Expected: `git diff --stat` lists only files from the list above that still had an old citation — all eight on an untouched tree — each changing one line. In the full tier the old citation is wrapped between "Hard" and "Stop:", so that one becomes a single longer line; that is fine.

- [ ] **Step 2: Confirm no old heading is cited and every citation resolves**

Run:
```bash
R=".claude/rules/0_Beads x Superpowers/beads-workflow-router.md"
find .claude README.md -type f -name '*.md' -not -path '.claude/worktrees/*' -not -name 'beads-workflow-router.md' -print0 | \
  xargs -0 perl -0777 -ne 'print "OLD  $ARGV\n" if /Hard\s+Stop:\s+[A-Z]|Auto-Invoke:\s|Standing\s+Posture:\s/'
find .claude README.md -type f -name '*.md' -not -path '.claude/worktrees/*' -print0 | \
  xargs -0 perl -0777 -ne 'while (/router(?:\x27s)?\s+\*([^*]+)\*/g) { my $s = $1; $s =~ s/\n[ \t]*>[ \t]?/ /g; $s =~ s/\s+/ /g; print "$ARGV\t$s\n" }' | \
  while IFS=$'\t' read -r f sec; do grep -qxF "## $sec" "$R" && echo "OK   $sec" || echo "MISS $f: $sec"; done | sort | uniq -c
```
Expected: no `OLD` lines, then only `OK` lines and no `MISS` — on an untouched tree, `7 OK   Verification Before Ship / "Done"` and `1 OK   Workflow Rules`, plus any citations Tasks 2 and 3 added, all `OK`.

- [ ] **Finish 1: Confirm this task's change set**

```bash
git status --short
```
Expected: exactly the files in this task's **Files** list above (`M` modified, `??` new, `D` deleted), and nothing else — apart from a `?? .claude/worktrees/` line if that local folder holds a worktree, which is never staged. Anything else means a step touched the wrong file: find it with `git diff <path>` before staging.

- [ ] **Finish 2: Commit W4**

```bash
git add -- \
  ".claude/rules/0_Beads x Superpowers/beads-workflow-router.md" \
  ".claude/rules/0_Beads x Superpowers/beads.md" \
  ".claude/rules/0_Beads x Superpowers/no-skipping-workflow-steps.md" \
  ".claude/rules/0_Beads x Superpowers/never-ask-about-agent-model.md" \
  ".claude/skills/beads-worktree-troubleshooting/SKILL.md" \
  ".claude/rules/Git Best Practices/no-direct-push-to-master.md" \
  ".claude/rules/Git Best Practices/Git Best Practices.md" \
  ".claude/Commands/workflow-commands/workflow-writing-plans.md" \
  ".claude/Commands/workflow-commands/workflow-execute-plans.md" \
  ".claude/Commands/workflow-commands/workflow-execute-spikes.md" \
  ".claude/Commands/workflow-commands/workflow-ship-epic.md" \
  ".claude/Commands/workflow-commands/beads-post-execution.md" \
  ".claude/Commands/workflow-commands/beads-ship-task.md" \
  ".claude/Commands/workflow-commands/beads-start-task.md" \
  ".claude/Commands/workflow-commands/plan-refinement-qa.md" \
  ".claude/Commands/workflow-commands/python-verification-quick.md" \
  ".claude/Commands/workflow-commands/python-verification-standard.md" \
  ".claude/Commands/workflow-commands/python-verification-full.md" && \
git diff --cached --stat && git commit -F- <<'EOF'
docs(rules): re-lay out the router on the global sections; add beads, no-skipping and model rules

Rewrite the router with the global router's sections, order and names,
keeping the template-only content; add beads.md, no-skipping-workflow-steps,
never-ask-about-agent-model and the worktree troubleshooting skill; add the
ship and status guardrails to the batch commands; re-point old citations.

<attribution trailer>
EOF
```
Expected: the stat lists only this task's files, then the commit summary line. Replace `<attribution trailer>` with the attribution lines from your session's system reminder before running it.

- [ ] **Finish 3: Record the commit on the W4 bead**

```bash
source .beads/sgw-ids.env && bd update "$W4" --append-notes "Landed in $(git rev-parse --short HEAD): docs(rules): re-lay out the router on the global sections; add beads, no-skipping and model rules" && bd show "$W4" | sed -n '1,20p'
```
Expected: the notes end with the "Landed in" line and the status is still `IN_PROGRESS` — all eight workstream beads close together when the PR opens (Task 9).

---

### Task 5: W5 — Plan depth in the batch commands

Spec: §6 W5; §7 (spike plans are not refined).

**Files:**
- Modify: `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, `.claude/Commands/workflow-commands/workflow-writing-plans.md`, `.claude/Commands/workflow-commands/workflow-execution-sequence.md` (Part A)
- Modify: `.claude/Commands/workflow-commands/workflow-execute-plans.md` (Part B)

**Interfaces:**
- Consumes: Task 4's router sections *Sizing Gate — Claude picks the lane* and *Label Ladders — Append-Only, Furthest Wins*; Task 4's `Branches:` line in the writing-plans preview.
- Produces: the plan-depth axis (`PLAN-FULL | PLAN-LITE | TDD-DIRECT`, labels `depth:full | depth:lite | depth:tdd`, one per task); the task card (`plan_depth: tdd-direct`, label `wp:carded`) and how execute-plans runs it.

Each part below lists its own files, interfaces and steps; run the parts in order, A first.

- [ ] **Start: mark the W5 bead in progress**

```bash
source .beads/sgw-ids.env && bd update "$W5" --status in_progress && bd show "$W5" | head -6
```
Expected: the bead shows `IN_PROGRESS`. (If `.beads/sgw-ids.env` is missing, Task 0 has not run.)

#### Part A: plan depth in planning-sequence, writing-plans and execution-sequence

**Files:**
- Modify: `.claude/Commands/workflow-commands/workflow-planning-sequence.md` — third classification axis (plan depth), medium effort, depth at the review gate, `depth:*` labels, depth in the sequence file.
- Modify: `.claude/Commands/workflow-commands/workflow-writing-plans.md` — reads depth and never re-derives it; effort by difficulty; depth-driven Steps 0–6; the TDD-direct task card; label lifecycle with `wp:carded`; artifacts table.
- Modify: `.claude/Commands/workflow-commands/workflow-execution-sequence.md` — planning-effort wording matches per-task effort.

**Interfaces:**
- Consumes: the router's *Sizing Gate — Claude picks the lane* section (Task 4) for the Lane A/B/C criteria; the Step 2 `Branches:` line from Task 4 Part B (kept verbatim).
- Produces: TASK_SCHEMA fields `plan_depth` (`PLAN-FULL | PLAN-LITE | TDD-DIRECT`) and `depth_reason`; labels `depth:full | depth:lite | depth:tdd` and `wp:carded`; plan frontmatter `plan_depth: full | lite | tdd-direct` (spike plans omit it); the task-card format (behaviour change, acceptance criteria, files expected to change, first failing pytest test) that execute-plans' task-card execution (Task 5, other part) runs test-first; `wp:approved` + `status: approved` as the single terminal state for every depth.

These steps run after Task 1, so command names in the files already read `/workflow-commands:<name>`. Every anchor below avoids the lines Task 1 rewrites, or quotes them in their post-Task-1 form; if an anchor does not match, re-read the file rather than guessing. Do the planning-sequence steps first, then writing-plans, then execution-sequence; within writing-plans, do the steps in the order given (Step 2 is rewritten before Step 3's heading changes).

- [ ] **Step 1: Mention plan depth in the planning-sequence description**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, replace the passage that begins

```text
description: Compute a planning sequence from EITHER a design spec OR an existing beads epic
```

and ends

```text
which consumes the emitted file.
```

(both ends included) with:

```text
description: Compute a planning sequence from EITHER a design spec OR an existing beads epic — classifying each task by plan-readiness (plan-ready vs spike-first), dependency type (parallel / sequential-plan / execution-gated) and plan depth (full plan / lite plan / TDD-direct task card), then emitting a planning-sequence file (machine block + human table) and writing the dependencies/labels. Precursor to /workflow-commands:workflow-writing-plans, which consumes the emitted file.
```

This is the frontmatter `description:` line; it stays one line.

- [ ] **Step 2: Teach the Core Principle the third axis**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, replace everything from the heading `## Core Principle — Plan-Strategy ≠ Build-Order` up to (not including) the heading `## The Two Classification Axes` with:

```markdown
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
```

- [ ] **Step 3: Rename the axes heading**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, replace this whole line:

```text
## The Two Classification Axes
```

with:

```markdown
## The Three Classification Axes
```

- [ ] **Step 4: Add Axis 3 — plan depth**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, section `## The Three Classification Axes`, insert directly after the line

```text
> inventing the upstream's interface or numbers?" If yes → EXEC-GATED on that upstream.
```

the following text:

```markdown

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
```

Keep one blank line between the EXEC-GATED heuristic quote and the new heading, and between the new text and the `---` that follows.

- [ ] **Step 5: Say which axes drive the derived outputs**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, section `## Derived Outputs`, replace this whole line:

```text
From the two axes, compute:
```

with:

```markdown
From Axes 1 and 2, compute (plan depth changes none of these):
```

- [ ] **Step 6: Run the classifier, synthesis and critic agents at medium effort**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, section `## Model & Budget`, replace this whole line:

```text
| Reasoning effort | **xhigh** for the classifier/synthesis agents |
```

with:

```markdown
| Reasoning effort | **medium** for the classifier, synthesis and critic agents |
```

- [ ] **Step 7: Classify at medium effort**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, section `### 2. [workflow] Classify every candidate task`, replace this whole line:

```text
Fan out **one agent per candidate task** (`Workflow` tool, Opus, effort `xhigh`).
```

with:

```markdown
Fan out **one agent per candidate task** (`Workflow` tool, Opus, effort `medium`).
```

- [ ] **Step 8: Add plan_depth and depth_reason to TASK_SCHEMA**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, section `### 2. [workflow] Classify every candidate task`, insert directly after the line

```text
    "spike_reason": {"type": "string"},
```

the following text:

```json
    "plan_depth": {"type": "string", "enum": ["PLAN-FULL", "PLAN-LITE", "TDD-DIRECT"]},
    "depth_reason": {"type": "string"},
```

The two lines go inside the `TASK_SCHEMA` `properties` object; keep the four-space indent.

- [ ] **Step 9: Require plan depth and explain why**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, section `### 2. [workflow] Classify every candidate task`, replace the passage that begins

```text
  "required": ["id_slug", "title", "plan_readiness", "deps", "rationale"]
```

and ends

```text
### 3. [workflow] Synthesize tracks + waves (+ adversarial check)
```

(both ends included) with:

````markdown
  "required": ["id_slug", "title", "plan_readiness", "plan_depth", "depth_reason", "deps", "rationale"]
}
```

`plan_depth` is **required**: a classifier that cannot justify a depth has not
understood the task, and a missing value must not silently become the cheapest
option. `depth_reason` is one sentence naming the specific Axis 3 trigger —
"touches the session schema", "two files, no contract change" — never a bare
restatement of the value.

### 3. [workflow] Synthesize tracks + waves (+ adversarial check)
````

The passage starts at the schema's `required` line and runs through the closing `}` and fence to the Step 3 heading, which the new text keeps.

- [ ] **Step 10: Run synthesis and critic at medium, and let the critic only promote depth**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, section `### 3. [workflow] Synthesize tracks + waves (+ adversarial check)`, replace the passage that begins

```text
One synthesis agent (Opus, `xhigh`) takes all task classifications and returns:
```

and ends

```text
dependency cycle? Any task that could move earlier/parallel?* Apply the critic's fixes.
```

(both ends included) with:

```markdown
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
```

- [ ] **Step 11: Show depth at the review gate and let the owner re-assign it**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, replace everything from the heading `### 4. [main ctx] Present recommendation + review gate` up to (not including) the heading `### 5. [main ctx] Persist to beads (mode-dependent, beads plugin skills)` with:

```markdown
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
```

- [ ] **Step 12: Persist depth as a label, with its reason in the notes**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, section `### 5. [main ctx] Persist to beads (mode-dependent, beads plugin skills)`, replace the passage that begins

```text
- Encode classification as **labels**: `plan-ready` | `spike-first`, and
```

and ends

```text
title `SPIKE: …`; in epic mode, add a `spike-first` label without retitling.
```

(both ends included) with:

```markdown
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
```

- [ ] **Step 13: Carry depth in both halves of the sequence file**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, section `### 6. [main ctx] Emit the planning-sequence file (both modes)`, replace the passage that begins

```text
1. **Machine-readable block**
```

and ends

```text
Both halves are written together so they cannot drift.
```

(both ends included) with:

```markdown
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
```

- [ ] **Step 14: Add plan depth to the sequence block example**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Input — A Planning-Sequence File`, insert directly after the line

```text
      "wave": 1,
```

the following text:

```json
      "plan_depth": "PLAN-FULL | PLAN-LITE | TDD-DIRECT",
      "depth_reason": "…",
```

The two new lines sit inside the `json` example, between `"wave": 1,` and `"deps": …`; keep the six-space indent.

- [ ] **Step 15: Read plan depth from the block and never re-derive it**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Input — A Planning-Sequence File`, replace the passage that begins

```text
Read classification (`plan_readiness`, `deps[].type`, `deps[].on`, `track`,
```

and ends

```text
single fallback prompt is allowed only if the file carries no epic id.
```

(both ends included) with:

```markdown
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
depth is also what the owner budgeted at the preview gate.
```

- [ ] **Step 16: Make draft and refine effort per task in the Model & Budget table**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Model & Budget`, replace this whole line:

```text
| Draft/Refine reasoning effort (Steps 3-4) | **xhigh** |
```

with:

```markdown
| Draft/Refine reasoning effort (Steps 3-4) | **Per task, by difficulty**: `medium`, `high` or `xhigh` — see "Effort by difficulty" below |
```

- [ ] **Step 17: Replace the blanket-xhigh paragraph with "Effort by difficulty"**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Model & Budget`, replace the passage that begins

```text
Steps 3 and 4 do judgment-heavy work — discovering unknowns, drafting
```

and ends

```text
at xhigh effort (`opts.model: "opus"`, `opts.effort: "xhigh"`).
```

(both ends included) with:

```markdown
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
  re-run it at a higher effort.

### Apply step and concurrency
```

The paragraph that follows ("Step 6 is different in kind: …") stays as it is and now sits under the new `### Apply step and concurrency` heading.

- [ ] **Step 18: Pass each task's own effort in the SEQ-PLAN pipeline example**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Workflow Primitives (reference for the executor)`, replace this exact text:

```text
// Illustrative — a SEQ-PLAN chain: plan the parent, then feed its decisions down
pipeline(
  seqChain,
  (t) => agent(draftPrompt(t), { model: "opus", effort: "xhigh", phase: "draft" }),
  (parentPlan, t) => agent(draftPrompt(t, { upstream: parentPlan }),
    { model: "opus", effort: "xhigh", phase: "draft" })
);
```

with:

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

This is the whole body of the `js` block; the fences around it stay.

- [ ] **Step 19: Route the step map by plan depth**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Step Map — Segmentation at a Glance`, replace the passage that begins

```text
| 3 | Sequence-aware draft (conditional) |
```

and ends

```text
| 7 | Epic status & next-steps summary | main ctx | — |
```

(both ends included) with:

```markdown
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
```

- [ ] **Step 20: Give Step 0 one resume route per depth**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Step 0: Resume Check (idempotency) [main ctx]`, replace the passage that begins

```text
- A task at **`wp:deferred`** is re-evaluated against its unblock signal (see
```

and ends

````text
# Per task: wp:drafted|wp:skipped|wp:deferred → wp:refined-r1 → wp:applied-r1 → wp:approved
```
````

(both ends included) with:

````markdown
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
````

- [ ] **Step 21: Assign each task its effort in Step 1**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Step 1: Load Sequence File [main ctx]`, insert directly after the line

```text
   **deferred set** (`EXEC-GATED` tasks whose upstream is not yet executed).
```

the following text:

```markdown
5. **Assign each plannable task its effort** (`medium` / `high` / `xhigh`) from
   "Effort by difficulty". For `xhigh`, note which hard trigger applied so the
   Step 2 preview can name it.
```

- [ ] **Step 22: Rewrite the Step 2 preview with the depth mix, effort mix and overrides**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, replace everything from the heading `## Step 2: Preview & Budget Gate [main ctx]` up to (not including) the heading `## Step 3: Sequence-Aware Draft (conditional) [workflow]` with:

````markdown
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
difficulty table for this run.

Show the **Branches** line only when the run includes at least one `PLAN-FULL`
plan. Only those reach Step 6's apply agents, so a run of lite plans, task cards
and spike plans creates no branch, and the line is left out.

Do not start the Step 3 workflow until the user confirms.

---
````

- [ ] **Step 23: Rewrite Step 3 to author by plan depth, including the task card**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, replace everything from the heading `## Step 3: Sequence-Aware Draft (conditional) [workflow]` up to (not including) the heading `## Step 4: Refine + Auto-Select — Round 1 [workflow]` with:

`````markdown
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
plan_depth: full | lite | tdd-direct   # from the sequence block; spike plans omit it
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
`````

- [ ] **Step 24: Scope refinement to full plans, at each task's effort**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Step 4: Refine + Auto-Select — Round 1 [workflow]`, replace the passage that begins

```text
Apply the shared Refinement Methodology (`references/refinement-methodology.md`) in
```

and ends

```text
(Step 3) and — for `SEQ-PLAN` tasks — by the **upstream plan's decisions**.
```

(both ends included) with:

```markdown
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
```

- [ ] **Step 25: Let lite plans, task cards and spike plans enter Step 6 for the stamp only**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Step 6: Apply #1 → Approve [workflow]`, replace the passage that begins

```text
Fan out per plan. Apply the (possibly user-overridden) Round 1 decisions from
```

and ends

```text
set frontmatter `status: approved`.
```

(both ends included) with:

```markdown
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
```

- [ ] **Step 26: Rewrite the label lifecycle with wp:carded and the deferred re-entry**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, replace everything from the heading `## Beads Label Lifecycle (writing-plans)` up to (not including) the heading `` ## Artifacts — `docs/plans/<epic-slug>/` `` with:

````markdown
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
````

- [ ] **Step 27: Describe task cards and plan_depth in the artifacts table**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `` ## Artifacts — `docs/plans/<epic-slug>/` ``, replace this whole line:

```text
| `<task-id>-<slug>.md` | One plan per task. Frontmatter: `smoke_test: required\|none`, `smoke_steps: "..."`, `bead_id: <id>`, `status: draft\|approved` |
```

with:

```markdown
| `<task-id>-<slug>.md` | One file per task: a full plan, a short (lite) plan, a `TDD-DIRECT` task card, or a spike plan. Frontmatter: `smoke_test: required\|none`, `smoke_steps: "..."`, `bead_id: <id>`, `plan_depth: full\|lite\|tdd-direct` (spike plans omit it and carry `spike_probe` / `probe_steps` / `needs_human_verdict` instead), `status: draft\|approved` |
```

- [ ] **Step 28: Exempt task cards from the always-use-writing-plans rule**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## CRITICAL — Honor Project Rules`, replace the passage that begins

```text
- **Writing plans**: when authoring in Step 3, **always** use
```

and ends

```text
`superpowers:writing-plans` — never hand-roll plan prose.
```

(both ends included) with:

```markdown
- **Writing plans**: when authoring a full or lite plan in Step 3, **always**
  use `superpowers:writing-plans` — never hand-roll plan prose. A `TDD-DIRECT`
  task card is not a plan; it follows the card format in Step 3.
```

- [ ] **Step 29: Add the effort and depth guardrails to the CRITICAL list**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## CRITICAL — Honor Project Rules`, replace the passage that begins

```text
- **Budget gate first**: never start the Step 3 workflow before the Step 2
```

and ends

```text
  confirmation.
```

(both ends included) with:

```markdown
- **Budget gate first**: never start the Step 3 workflow before the Step 2
  confirmation.
- **Draft/refine effort by difficulty**: Opus at each task's assigned effort —
  `medium` for task cards, `high` for lite and spike plans, and `high` for full
  plans, rising to `xhigh` with a hard trigger; ties go to `xhigh`. Never a
  blanket xhigh. Step 6 apply stays Sonnet at medium.
- **Depth is read, never re-derived**: `plan_depth` comes from the sequence
  block; a missing depth means `PLAN-FULL`, and a plainly wrong one is deferred
  and reported, never silently upgraded.
```

- [ ] **Step 30: Describe the triggered planning's effort as per-task**

In `.claude/Commands/workflow-commands/workflow-execution-sequence.md`, section `## Model & Budget`, replace the passage that begins

```text
| The planning it triggers |
```

and ends

```text
Gated (Step 5). |
```

(both ends included) with:

```markdown
| The planning it triggers | `/workflow-commands:workflow-writing-plans` per gap-epic — **Opus**, effort chosen per task by difficulty (`medium` task cards, `high` lite and spike plans, `high` or `xhigh` full plans), ~one agent per task plus one refinement agent per full plan. Gated (Step 5). |
```

This is the whole table row; it stays one line.

- [ ] **Step 31: Match the budget-gate sentence to per-task effort**

In `.claude/Commands/workflow-commands/workflow-execution-sequence.md`, section `### 5. [main ctx] Present sequence + coverage + GATE`, replace the passage that begins

```text
Because the next step launches
```

and ends

```text
Step 2):
```

(both ends included) with:

```markdown
Because the next step launches **expensive Opus planning workflows** (effort
scaled per task by difficulty, up to xhigh), show a budget/scope preview and
require explicit confirmation (mirror `/workflow-commands:workflow-writing-plans`
Step 2):
```

- [ ] **Step 32: Verify Part A of Task 5**

Run from the repo root:

```bash
d=.claude/Commands/workflow-commands
printf '%s\n' \
  "ps-three-axes-heading=$(grep -cxF '## The Three Classification Axes' "$d/workflow-planning-sequence.md")" \
  "ps-two-axes-left=$(grep -cE 'Two Classification Axes|\*\*two axes\*\*' "$d/workflow-planning-sequence.md")" \
  "ps-axis3-heading=$(grep -cxF '### Axis 3 — Plan depth (the Sizing Gate)' "$d/workflow-planning-sequence.md")" \
  "ps-xhigh-left=$(grep -cF 'xhigh' "$d/workflow-planning-sequence.md")" \
  "ps-depth-labels=$(grep -cF 'depth:full' "$d/workflow-planning-sequence.md")" \
  "ps-schema-plan-depth=$(grep -cF '"plan_depth"' "$d/workflow-planning-sequence.md")" \
  "wp-carded=$(grep -cF 'wp:carded' "$d/workflow-writing-plans.md")" \
  "wp-effort-heading=$(grep -cxF '### Effort by difficulty (Steps 3 and 4)' "$d/workflow-writing-plans.md")" \
  "wp-blanket-xhigh-opts=$(grep -cF 'effort: "xhigh"' "$d/workflow-writing-plans.md")" \
  "wp-card-frontmatter=$(grep -cF 'plan_depth: tdd-direct' "$d/workflow-writing-plans.md")" \
  "wp-step3-heading=$(grep -cxF '## Step 3: Sequence-Aware Draft (conditional, depth-driven) [workflow]' "$d/workflow-writing-plans.md")" \
  "wp-branches-line=$(grep -cF 'approving this gate is the branch' "$d/workflow-writing-plans.md")" \
  "es-opus-xhigh-left=$(grep -cF 'Opus / xhigh' "$d/workflow-execution-sequence.md")" \
  "es-per-task-effort=$(grep -cF 'effort chosen per task by difficulty' "$d/workflow-execution-sequence.md")"
```

Expected output, exactly:

```text
ps-three-axes-heading=1
ps-two-axes-left=0
ps-axis3-heading=1
ps-xhigh-left=0
ps-depth-labels=1
ps-schema-plan-depth=2
wp-carded=6
wp-effort-heading=1
wp-blanket-xhigh-opts=0
wp-card-frontmatter=2
wp-step3-heading=1
wp-branches-line=1
es-opus-xhigh-left=0
es-per-task-effort=1
```

Any other number means a step above was skipped or applied to the wrong passage; re-read that file and fix it before moving on.

#### Part B: execute-plans runs a task card test-first

**Files:**
- Modify: `.claude/Commands/workflow-commands/workflow-execute-plans.md` — Step 0b (a task card passes the approval gate with no special case) and Step 3 item 1 (how to execute a task card).

**Interfaces:**
- Consumes: from this task's writing-plans part: a `TDD-DIRECT` task's task card, written at the normal plan path with frontmatter `plan_depth: tdd-direct`, labelled `wp:carded`, and approved with the same `wp:approved` + `status: approved` stamp as a plan.
- Produces: nothing later tasks anchor on.

- [ ] **Step 1: execute-plans — say how the approval gate treats a task card**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, section `` ### 0b — Approval precondition (HARD GATE, `wp:deferred` exempt) ``, replace the passage that begins `` 2. plan frontmatter **`status: approved`** `` and ends `` <task-id>-<slug>.md`. `` with:

```markdown
2. plan frontmatter **`status: approved`** in its `docs/plans/<epic-slug>/<task-id>-<slug>.md`.

A **task card** — the short file `/workflow-commands:workflow-writing-plans`
writes instead of a plan for a `TDD-DIRECT` task, marked `plan_depth: tdd-direct`
and labelled `wp:carded` — reaches this same state (`wp:approved` +
`status: approved`) and needs no special case here. A task carrying both
`wp:carded` and `wp:approved` is approved: labels are history, and the furthest
one wins.
```

- [ ] **Step 2: execute-plans — execute a task card test-first, never rebuild a plan from it**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, section `## Step 3: Autonomous Fan-Out — Execute (TDD) → QA → Auto-Advance [workflow]`, replace the passage that begins `1. **Execute following TDD.**` and ends `` *(End label: `ex:executing`.)* `` with:

Keep one blank line between the end of this new text and the line that follows it.

```markdown
1. **Execute following TDD.** Drive implementation via
   `superpowers:test-driven-development` — **tests first** (pytest), then
   implementation. This is genuine TDD, not just post-hoc QA. Use `superpowers`
   execution (`superpowers:executing-plans` /
   `superpowers:subagent-driven-development`) to work the plan file.
   *(End label: `ex:executing`.)*

   > **A task card is not a plan.** When the plan file's frontmatter carries
   > `plan_depth: tdd-direct` (the task is labelled `wp:carded`),
   > `/workflow-commands:workflow-writing-plans` wrote a task card for a task the
   > Sizing Gate put in Lane A. There are no plan steps to work through: write
   > the failing pytest test the card names, run it and watch it fail for the
   > reason the card expects, implement until it passes, and stop. Never rebuild
   > a plan from the card — its brevity is the decision, not a gap to fill.
   > Everything after this item (the diff-based QA level, the named verification
   > skill, the labels and the QA ledger) is unchanged, and the same applies to
   > an attended task in Step 4.
```

- [ ] **Step 3: Verify this part's edits landed**

Run from the repo root:

```bash
C=.claude/Commands/workflow-commands
while IFS='|' read -r want f s; do
  got=$(grep -c -F -- "$s" "$C/$f")
  if [ "$got" = "$want" ]; then echo "ok   $f: $s"; else echo "MISMATCH (got $got, want $want)  $f: $s"; fi
done <<'EOF'
1|workflow-execute-plans.md|A **task card**
1|workflow-execute-plans.md|> **A task card is not a plan.**
EOF
```

Expected: 2 lines, every one starting with `ok`. A `MISMATCH` line names the file and phrase whose edit is missing or duplicated.

- [ ] **Finish 1: Confirm this task's change set**

```bash
git status --short
```
Expected: exactly the files in this task's **Files** list above (`M` modified, `??` new, `D` deleted), and nothing else — apart from a `?? .claude/worktrees/` line if that local folder holds a worktree, which is never staged. Anything else means a step touched the wrong file: find it with `git diff <path>` before staging.

- [ ] **Finish 2: Commit W5**

```bash
git add -- \
  ".claude/Commands/workflow-commands/workflow-planning-sequence.md" \
  ".claude/Commands/workflow-commands/workflow-writing-plans.md" \
  ".claude/Commands/workflow-commands/workflow-execution-sequence.md" \
  ".claude/Commands/workflow-commands/workflow-execute-plans.md" && \
git diff --cached --stat && git commit -F- <<'EOF'
chore(workflow): plan depth in the batch commands

Give planning-sequence a third classification axis (full, lite, TDD-direct);
writing-plans reads it, writes task cards for TDD-direct tasks, refines only
full plans and picks effort by difficulty; execute-plans runs a card test-first.

<attribution trailer>
EOF
```
Expected: the stat lists only this task's files, then the commit summary line. Replace `<attribution trailer>` with the attribution lines from your session's system reminder before running it.

- [ ] **Finish 3: Record the commit on the W5 bead**

```bash
source .beads/sgw-ids.env && bd update "$W5" --append-notes "Landed in $(git rev-parse --short HEAD): chore(workflow): plan depth in the batch commands" && bd show "$W5" | sed -n '1,20p'
```
Expected: the notes end with the "Landed in" line and the status is still `IN_PROGRESS` — all eight workstream beads close together when the PR opens (Task 9).

---

### Task 6: W6 — Beads sync

Spec: §6 W6; §3 decision 3; §7 (a project with no Dolt remote keeps working).

**Files:**
- Modify: `.claude/rules/0_Beads x Superpowers/skill-usage.md` (Part A)
- Modify: `.claude/Commands/workflow-commands/workflow-execution-sequence.md` (Part B), `.claude/Commands/workflow-commands/workflow-ship-epic.md` (Part C)
- Modify: `.claude/Commands/workflow-commands/beads-start-task.md`, `.claude/Commands/workflow-commands/beads-ship-task.md`, `.claude/Commands/workflow-commands/beads-export-progress.md` (Part D)

**Interfaces:**
- Consumes: `beads.md` (Task 4) and its no-remote pull guard.
- Produces: the `dolt-pull-guard` snippet in beads-start-task Step 0; Dolt publishing in both ship commands' Step 6.5; `issues.jsonl` refreshed with `bd export -o` wherever it is read.

Each part below lists its own files, interfaces and steps; run the parts in order, A first.

- [ ] **Start: mark the W6 bead in progress**

```bash
source .beads/sgw-ids.env && bd update "$W6" --status in_progress && bd show "$W6" | head -6
```
Expected: the bead shows `IN_PROGRESS`. (If `.beads/sgw-ids.env` is missing, Task 0 has not run.)

#### Part A: skill-usage — beads syncs over its own channel

**Files:**
- Modify: `.claude/rules/0_Beads x Superpowers/skill-usage.md` — the team-sync paragraph and the last two Skill Mapping rows describe the two channels (`bd dolt pull` / `bd dolt push` alongside `git pull` / `git push`) and the no-remote behaviour; the Examples and namespaces tables drop `commit-push`, which the official commit-commands plugin does not ship; the `beads` namespace example list swaps the deprecated `sync` for `label`.

**Interfaces:**
- Consumes: `beads.md` (Task 4), cited as the full rules; the pull guard's one-line message, worded the same as in `beads.md` and beads-start-task Step 0 (Task 6).
- Produces: nothing new for later tasks.

- [ ] **Step 1: Replace the non-existent `commit-push` example**

In `.claude/rules/0_Beads x Superpowers/skill-usage.md`, section `### Examples`, replace the table row

```markdown
| `commit-push` | `commit-commands:commit-push` |
```

with:

```markdown
| `clean_gone` | `commit-commands:clean_gone` |
```

- [ ] **Step 2: Fix the commit-commands namespace row**

In `.claude/rules/0_Beads x Superpowers/skill-usage.md`, section `### Common Skill Namespaces`, replace the passage

```markdown
| `commit-commands` | `commit`, `commit-push`, `commit-push-pr`, `clean_gone` |
```

(the start of that table row) with:

```markdown
| `commit-commands` | `commit`, `commit-push-pr`, `clean_gone` |
```

- [ ] **Step 3: Swap the deprecated `sync` example for `label`**

In `.claude/rules/0_Beads x Superpowers/skill-usage.md`, section `### Common Skill Namespaces`, replace the passage

```markdown
| `beads` | `stats`, `ready`, `list`, `show`, `create`, `update`, `close`, `sync`, etc. |
```

with:

```markdown
| `beads` | `stats`, `ready`, `list`, `show`, `create`, `update`, `close`, `label`, etc. |
```

- [ ] **Step 4: Rewrite the team-sync paragraph**

In `.claude/rules/0_Beads x Superpowers/skill-usage.md`, section `### Rule: Prefer Beads Plugin Skills`, replace the paragraph that begins
`**Team sync depends on how your project is set up.**` and ends `agreed re-baseline.` with:

```markdown
**Beads syncs over its own channel.** Code travels by `git pull` / `git push`;
beads travels by `bd dolt pull` / `bd dolt push`, through a Dolt remote on the
project's own git remote
(`bd dolt remote add origin git+https://github.com/<owner>/<repo>.git`). Pull
both at session or task start and push both at ship or session close — pull
first, push last — and never `--force` a beads push except a deliberate, agreed
re-baseline. `.beads/issues.jsonl` is an untracked, readable export (refresh it
with `bd export -o .beads/issues.jsonl`), not a sync channel. With no Dolt remote
configured yet, `bd dolt pull` fails, so the pull step prints one line saying it
skipped and continues; `bd dolt push` skips on its own. Full rules: `beads.md`.
```

- [ ] **Step 5: Rewrite the two sync rows of the Skill Mapping table**

In `.claude/rules/0_Beads x Superpowers/skill-usage.md`, section `### Skill Mapping`, replace the last two table rows

```markdown
| Pull teammate's beads (session/task START) | `git pull` — or `bd dolt pull` on a Dolt remote |
| Publish your beads (ship / session CLOSE) | `git push` — or `bd dolt push` on a Dolt remote |
```

with:

```markdown
| Pull at session/task START | `git pull` for code, then `bd dolt pull` for beads (with no Dolt remote yet: print one line and continue) |
| Publish at ship / session CLOSE | `git push` for code, then `bd dolt push` for beads (skips on its own with no remote) |
```

- [ ] **Step 6: Verify**

```bash
F=".claude/rules/0_Beads x Superpowers/skill-usage.md"
grep -nE 'commit-push([^-]|$)' "$F" || echo "OK: no commit-push"
grep -c 'bd dolt pull' "$F"
grep -c 'bd dolt push' "$F"
grep -n 'issues.jsonl` committed\|on a Dolt remote |' "$F" || echo "OK: old default gone"
grep -n '`sync`' "$F" || echo "OK: no sync example"
```

Expected output, in order: `OK: no commit-push`, `3`, `3`, `OK: old default gone`,
`OK: no sync example`. Leave the Examples table's left-hand "Wrong" column bare
(`beads-start-task`, `stats`, …) — those cells are deliberate wrong-form examples.

#### Part B: execution-sequence — a real export flag

**Files:**
- Modify: `.claude/Commands/workflow-commands/workflow-execution-sequence.md` — Step 2 refreshes `.beads/issues.jsonl` with `bd export -o`, not the non-existent `--no-auto-import` flag.

**Interfaces:**
- Consumes: W6's decision that `.beads/issues.jsonl` is an untracked, readable export (the rule `.claude/rules/0_Beads x Superpowers/beads.md`, Task 4).
- Produces: execution-sequence reads a freshly written `.beads/issues.jsonl`.

These steps run after Task 1, so command names in the files already read `/workflow-commands:<name>`. Every anchor below avoids the lines Task 1 rewrites, or quotes them in their post-Task-1 form; if an anchor does not match, re-read the file rather than guessing.

- [ ] **Step 1: Refresh the readable export with a flag beads 1.0.4 actually has**

In `.claude/Commands/workflow-commands/workflow-execution-sequence.md`, section `### 2. [script] Compute the transitive blocks-closure`, replace this whole line:

```text
Refresh the graph (`bd export --no-auto-import` writes `.beads/issues.jsonl`), then
```

with:

```markdown
Refresh the readable export first (`bd export -o .beads/issues.jsonl`; plain
`bd export` only prints to stdout), then
```

`--no-auto-import` is not a beads 1.0.4 flag, and without `-o` the export goes to stdout, so the script below would read a stale file.

- [ ] **Step 2: Verify Part B of Task 6**

Run from the repo root:

```bash
d=.claude/Commands/workflow-commands
printf '%s\n' \
  "es-no-auto-import-left=$(grep -cF 'no-auto-import' "$d/workflow-execution-sequence.md")" \
  "es-export-o=$(grep -cF 'bd export -o .beads/issues.jsonl' "$d/workflow-execution-sequence.md")"
```

Expected output, exactly:

```text
es-no-auto-import-left=0
es-export-o=1
```

Any other number means a step above was skipped or applied to the wrong passage; re-read that file and fix it before moving on.

#### Part C: ship-epic publishes beads over Dolt

**Files:**
- Modify: `.claude/Commands/workflow-commands/workflow-ship-epic.md` — Step 6.5 rewritten: guarded `bd dolt pull && bd dolt push`, then a refreshed readable export; the "issues.jsonl in git" branch is gone.

**Interfaces:**
- Consumes: the no-remote guard (`bd dolt remote list` prints `No remotes configured.`; `bd dolt pull` fails without a remote, `bd dolt push` skips); `.claude/rules/0_Beads x Superpowers/beads.md` from Task 4 (the export is a readable artifact, never committed).
- Produces: ship-epic Step 6.5, which Task 7's Step 0 re-runs on a re-run.

- [ ] **Step 1: ship-epic — publish beads over Dolt after the code push**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, replace everything from the heading `## Step 6.5: Publish Beads (team sync) [main ctx]` up to (not including) the heading `## Step 7: Report — Epic Status & Next-Steps Summary [main ctx]` with:

````markdown
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
without a remote, but `bd dolt pull` fails outright, hence the check.) Add a remote
later with `bd dolt remote add origin git+https://github.com/<owner>/<repo>.git`.
If the push is rejected as diverged, `bd dolt pull` and retry; never `--force`
except a deliberate, agreed re-baseline.

Then refresh the readable export with `bd export -o .beads/issues.jsonl`. It is a
snapshot for people and tools to read, not a sync channel, and it is never
committed (`.claude/rules/0_Beads x Superpowers/beads.md`).

> If you mirror Beads to an external tracker, reconcile it here — an epic close fires a
> per-`bd close` hook once per child task plus once for the epic, and hooks fail
> silently. The mirror is downstream; Beads remains the source of truth.
````

- [ ] **Step 2: Verify this part's edits landed**

Run from the repo root:

```bash
C=.claude/Commands/workflow-commands
while IFS='|' read -r want f s; do
  got=$(grep -c -F -- "$s" "$C/$f")
  if [ "$got" = "$want" ]; then echo "ok   $f: $s"; else echo "MISMATCH (got $got, want $want)  $f: $s"; fi
done <<'EOF'
1|workflow-ship-epic.md|bd dolt pull && bd dolt push
0|workflow-ship-epic.md|Default setup (`issues.jsonl` in git)
1|workflow-ship-epic.md|bd export -o .beads/issues.jsonl
EOF
```

Expected: 3 lines, every one starting with `ok`. A `MISMATCH` line names the file and phrase whose edit is missing or duplicated.

#### Part D: beads sync in the single-task commands (start-task, ship-task, export-progress)

**Files:**
- Modify: `.claude/Commands/workflow-commands/beads-start-task.md` — Step 0 pulls code with `git pull` and beads with `bd dolt pull` through a no-remote guard (snippet `dolt-pull-guard`); the "git pull carries beads" default goes.
- Modify: `.claude/Commands/workflow-commands/beads-ship-task.md` — Step 6.5 publishes beads with `bd dolt push` after the code push, through the same guard; the "issues.jsonl in git" branch goes.
- Modify: `.claude/Commands/workflow-commands/beads-export-progress.md` — refreshes `.beads/issues.jsonl` with `bd export -o .beads/issues.jsonl` before reading it; fixes the duplicated step number.
- Test (not committed): `$CHECKS/check-dolt-guard.sh`

**Interfaces:**
- Consumes: nothing from earlier tasks. These three regions contain no workflow command names, so Task 1's sweep leaves them untouched and the anchors below still match.
- Produces: the snippet `dolt-pull-guard` in beads-start-task Step 0 (Task 9 re-runs `check-dolt-guard.sh`). The same channel wording — code over `git push`/`git pull`, beads over the Dolt remote (`refs/dolt/data`), `.beads/issues.jsonl` a readable export that is never committed — matches the router intro and `beads.md` (Task 4) and `skill-usage.md` (Task 6, Part A).

- [ ] **Step 1: Write the failing check**

Create `<scratchpad>/sgw-checks/check-dolt-guard.sh` with the Write tool, not a Bash heredoc (see Global Constraints). The script never deletes anything; each run uses fresh `mktemp -d` directories.

````bash
#!/usr/bin/env bash
# Behaviour check for the beads pull guard in beads-start-task Step 0 (Task 6).
# Runs the shipped snippet in scratch beads repos: one with no Dolt remote (must
# print one skip line and exit 0) and one with a remote (must attempt the pull).
# Each run works in new mktemp directories, so nothing is ever deleted.
# Usage: bash check-dolt-guard.sh <repo-root>
set -u
FILE="$1/.claude/Commands/workflow-commands/beads-start-task.md"
HERE="$(cd "$(dirname "$0")" && pwd)"
fail=0

extract_snippet() {   # extract_snippet <file> <name>
  awk -v want="# snippet: $2" '
    /^[[:space:]]*```/ { if (inb) { if (hit) exit; inb=0 } else { inb=1; first=1 }; next }
    inb && first { first=0; t=$0; sub(/^[[:space:]]+/, "", t); if (t == want) hit=1; next }
    inb && hit { print }
  ' "$1"
}

SNIP=$(extract_snippet "$FILE" dolt-pull-guard)
if [ -z "$SNIP" ]; then
  echo "FAIL: snippet dolt-pull-guard not found in beads-start-task.md"
  exit 1
fi
echo "PASS: snippet dolt-pull-guard found"

fresh_repo() {  # fresh_repo <prefix> — prints the path of a new git repo with a local-only beads store
  local d
  d=$(mktemp -d "$HERE/$1.XXXXXX")
  ( cd "$d" && git init -q -b main && git commit -q --allow-empty -m init \
      && bd init --stealth --non-interactive >/dev/null 2>&1 ) || { echo "FAIL: could not set up $d" >&2; exit 1; }
  echo "$d"
}

# Case 1: no Dolt remote -> exactly one skip line, exit 0.
d=$(fresh_repo dolt-guard-noremote) || exit 1
out=$(cd "$d" && bash -c "$SNIP" 2>&1); rc=$?
if [ "$rc" -eq 0 ]; then echo "PASS: no remote -> exit 0"; else echo "FAIL: no remote -> exit $rc"; fail=1; fi
if [ "$out" = "Beads: no Dolt remote configured — skipping bd dolt pull." ]; then
  echo "PASS: no remote -> exactly one skip line"
else
  echo "FAIL: no remote -> unexpected output: $out"; fail=1
fi

# Case 2: a remote is configured -> the guard must attempt the pull, not skip.
# The remote is an empty local directory, so the pull fails fast and offline.
d=$(fresh_repo dolt-guard-remote) || exit 1
empty=$(mktemp -d "$HERE/dolt-guard-empty-remote.XXXXXX")
( cd "$d" && bd dolt remote add origin "file://$empty" >/dev/null 2>&1 )
out=$(cd "$d" && bash -c "$SNIP" 2>&1)
case "$out" in
  *"skipping bd dolt pull"*) echo "FAIL: remote configured -> guard skipped the pull"; fail=1 ;;
  *"Pulling from Dolt remote"*) echo "PASS: remote configured -> guard ran bd dolt pull" ;;
  *) echo "FAIL: remote configured -> no pull attempt seen: $out"; fail=1 ;;
esac

exit $fail
````

- [ ] **Step 2: Run the check and watch it fail**

Run it by itself (it runs `bd`, only inside its own scratch repos), from the repo root:

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-dolt-guard.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
```

Expected:

```
FAIL: snippet dolt-pull-guard not found in beads-start-task.md
exit=1
```

- [ ] **Step 3: Rewrite beads-start-task Step 0**

In `.claude/Commands/workflow-commands/beads-start-task.md`, replace everything from the heading `## Step 0: Pull Latest Beads (team sync)` up to (not including) the heading `## Step 1: Mark Task In Progress` with:

````markdown
## Step 0: Pull Latest Beads (team sync)

Before anything else, bring both channels up to date so you start from the team's
latest state. Code and beads travel separately: `git pull` carries code only, and
beads sync over the Dolt remote on your git host (`refs/dolt/data`).
`.beads/issues.jsonl` is just a readable export — it is never committed and never
carries beads between machines.

1. **Code:** `git pull` on the branch you are on (skip it if that branch has no
   upstream yet).
2. **Beads:** pull before reading or writing any bead:

```bash
# snippet: dolt-pull-guard
if bd dolt remote list 2>/dev/null | grep -q 'No remotes configured'; then
  echo "Beads: no Dolt remote configured — skipping bd dolt pull."
else
  bd dolt pull
fi
```

A project with no Dolt remote yet prints that one line and carries on. If the pull
is rejected as diverged, do **not** `--force` — coordinate with whoever pushed, or
re-pull.

````

- [ ] **Step 4: Rewrite beads-ship-task Step 6.5**

In `.claude/Commands/workflow-commands/beads-ship-task.md`, replace everything from the heading `## Step 6.5: Publish Beads (team sync)` up to (not including) the heading `## Step 7: Show Unblocked Tasks` with:

````markdown
## Step 6.5: Publish Beads (team sync)

After all beads mutations (task closed, epic closed or promoted), publish them.
Code and beads travel on separate channels: Step 2's `git push` shipped the code,
and this step ships the beads over the Dolt remote (`refs/dolt/data`).
`.beads/issues.jsonl` is only a readable export — never stage or commit it.

```bash
if bd dolt remote list 2>/dev/null | grep -q 'No remotes configured'; then
  echo "Beads: no Dolt remote configured — skipping bd dolt push."
else
  bd dolt pull && bd dolt push   # fast-forward first, then publish your beads changes
fi
```

A project with no Dolt remote yet prints that one line and carries on. If the push
is rejected as diverged, run `bd dolt pull` and retry — never `--force` (only for a
deliberate, agreed re-baseline).

````

- [ ] **Step 5: Rewrite beads-export-progress**

Replace the whole of `.claude/Commands/workflow-commands/beads-export-progress.md` with the content below. It changes the refresh to `bd export -o .beads/issues.jsonl`, says why the refresh always runs, drops the old "if it is stale" note that the refresh makes redundant, and renumbers the steps (the old file had two step 2s).

````markdown
---
description: Regenerate .beads/PROGRESS.md from issues.jsonl by running .beads/generate_progress.py
---

# Beads Export Progress

Regenerates the human-readable progress report at `.beads/PROGRESS.md` from a fresh export of the beads database. Groups issues by phase, shows completion stats, progress bar, blockers, and close dates.

`.beads/issues.jsonl` is a readable export, not a sync channel: it is untracked, beads sync over the Dolt remote, and the file is only as current as its last export. So this command always refreshes it before reading.

## Steps

1. Refresh the export from the live beads database:
   ```bash
   bd export -o .beads/issues.jsonl
   ```
   If this fails, say so and ask before reporting from the existing export, which may be stale.

2. Run the generator:
   ```bash
   python3 .beads/generate_progress.py
   ```

3. Confirm the output was written and report line count:
   ```bash
   wc -l .beads/PROGRESS.md
   ```

4. Show the user the top of the generated file (stats + first phase) so they can see the result.

## Notes

- Script location: `.beads/generate_progress.py`
- Input: `.beads/issues.jsonl`, refreshed in Step 1
- Output: `.beads/PROGRESS.md` (overwritten each run)
- Pure local script — reads JSONL, writes Markdown. No network, no DB writes.
````

- [ ] **Step 6: Run the check and watch it pass**

Run it by itself, from the repo root:

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-dolt-guard.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
```

Expected (the remote case points at an empty local directory, so its pull fails fast and offline; the check only asserts that the pull was attempted rather than skipped):

```
PASS: snippet dolt-pull-guard found
PASS: no remote -> exit 0
PASS: no remote -> exactly one skip line
PASS: remote configured -> guard ran bd dolt pull
exit=0
```

- [ ] **Step 7: Confirm the old "beads travel in git" wording is gone**

```bash
cd "$(git rev-parse --show-toplevel)/.claude/Commands/workflow-commands"
grep -n -E 'Default setup|travels as issues\.jsonl|in git\)|bd export >|# bd dolt pull' beads-start-task.md beads-ship-task.md beads-export-progress.md
grep -c 'bd export -o .beads/issues.jsonl' beads-export-progress.md
grep -c "grep -q 'No remotes configured'" beads-start-task.md beads-ship-task.md
```

Expected: the first `grep` prints nothing (before this task it printed four lines); then `1`; then `beads-start-task.md:1` and `beads-ship-task.md:1`, in either order.

- [ ] **Finish 1: Confirm this task's change set**

```bash
git status --short
```
Expected: exactly the files in this task's **Files** list above (`M` modified, `??` new, `D` deleted), and nothing else — apart from a `?? .claude/worktrees/` line if that local folder holds a worktree, which is never staged. Anything else means a step touched the wrong file: find it with `git diff <path>` before staging.

- [ ] **Finish 2: Commit W6**

```bash
git add -- \
  ".claude/rules/0_Beads x Superpowers/skill-usage.md" \
  ".claude/Commands/workflow-commands/workflow-execution-sequence.md" \
  ".claude/Commands/workflow-commands/workflow-ship-epic.md" \
  ".claude/Commands/workflow-commands/beads-start-task.md" \
  ".claude/Commands/workflow-commands/beads-ship-task.md" \
  ".claude/Commands/workflow-commands/beads-export-progress.md" && \
git diff --cached --stat && git commit -F- <<'EOF'
chore(workflow): sync beads over Dolt; issues.jsonl is a readable export

Pull and push beads with bd dolt alongside git (with a one-line skip when no
Dolt remote exists); refresh the readable export with bd export -o; fix the
non-existent bd export --no-auto-import flag.

<attribution trailer>
EOF
```
Expected: the stat lists only this task's files, then the commit summary line. Replace `<attribution trailer>` with the attribution lines from your session's system reminder before running it.

- [ ] **Finish 3: Record the commit on the W6 bead**

```bash
source .beads/sgw-ids.env && bd update "$W6" --append-notes "Landed in $(git rev-parse --short HEAD): chore(workflow): sync beads over Dolt; issues.jsonl is a readable export" && bd show "$W6" | sed -n '1,20p'
```
Expected: the notes end with the "Landed in" line and the status is still `IN_PROGRESS` — all eight workstream beads close together when the PR opens (Task 9).

---

### Task 7: W7 — Ship and safety fixes

Spec: §6 W7; §3 decision 4; §7 (`sh:pushed` at PR open, `sh:shipped` only after a confirmed merge).

**Files:**
- Modify: `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md` (Part A)
- Modify: `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, `.claude/Commands/workflow-commands/workflow-writing-plans.md` (Part B)
- Modify: `.claude/Commands/workflow-commands/workflow-ship-epic.md`, `.claude/Commands/workflow-commands/workflow-execute-plans.md` (Part C)
- Modify: `.claude/hooks/validate-bash.sh` (Part D)

**Interfaces:**
- Consumes: Task 6's ship-epic Step 6.5; Task 4's execute-plans Step 8 gate.
- Produces: `sh:pushed` = PR opened, `sh:shipped` = merge confirmed by a re-run (snippet `merge-check`); the unshipped-epic check at Step 0 of the three batch commands; the bash hook's single-simple-command auto-allow.

Each part below lists its own files, interfaces and steps; run the parts in order, A first.

- [ ] **Start: mark the W7 bead in progress**

```bash
source .beads/sgw-ids.env && bd update "$W7" --status in_progress && bd show "$W7" | head -6
```
Expected: the bead shows `IN_PROGRESS`. (If `.beads/sgw-ids.env` is missing, Task 0 has not run.)

#### Part A: surface-unshipped-epics — the two-step ship

**Files:**
- Modify: `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md` — Rule 1 also flags a closed epic at `sh:pushed` without `sh:shipped` ("PR opened on <date>, not merged"); Rule 3 is restated with the two labels and the merge check (`gh pr view` first); Rule 4's handoff names both steps; *Why not just auto-ship?* and *Generalized Lesson* match the PR-only ship.

**Interfaces:**
- Consumes: ship-epic closing the tasks and the epic at PR open with `sh:pushed` and appending the notes line `PR: <pr-url> · head: <epic-head-sha> · opened: <YYYY-MM-DD>`, and its re-run that confirms the merge (`gh pr view <url> --json state,mergedAt`, then `git merge-base --is-ancestor` against the fetched trunk) and adds `sh:shipped` (Task 7 Part B).
- Produces: Rule 1's two states and their surface messages — the wording the Step 0 checks in planning-sequence, writing-plans and execute-plans print (Task 7 Part B); Rule 4's three-line handoff, which execute-plans' final handoff states (Task 7 Part B).

All five steps replace whole sections between headings, so they apply cleanly after Task 1's
naming sweep has rewritten the old text.

- [ ] **Step 1: Rule 1 — check both unshipped states**

In `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md`, replace everything from the heading
`### 1. Check for a finished-but-unshipped epic before starting new epic work` up to (not
including) the heading `### 2. Warn before stacking onto an unmerged branch` with:

````markdown
### 1. Check for a finished-but-unshipped epic before starting new epic work

At the START of `/workflow-commands:workflow-planning-sequence`,
`/workflow-commands:workflow-writing-plans` and
`/workflow-commands:workflow-execute-plans`, read every epic with its labels
(`bd list --type=epic --all -n 0 --json`) and look for either of two states.
Surface the first one found before doing anything else:

- **Finished, never shipped** — an open epic whose children are all `ex:done`
  (`bd list --parent <id> -n 0 --json`) and which carries no `sh:*` label:
  `/workflow-commands:workflow-ship-epic` never ran.

  > ⚠️ Epic **<id> "<title>"** finished executing on <date> but was never
  > shipped — all N children are `ex:done`, the epic has no `sh:shipped`, and
  > its code is not on the trunk.
  >
  > Ship it with `/workflow-commands:workflow-ship-epic <id>` first, or tell me
  > to proceed and stack this new work on top of it.

- **PR opened, not merged** — a closed epic that carries `sh:pushed` but not
  `sh:shipped`. Ship-epic closes the tasks and the epic when it opens the PR,
  so a closed epic proves only that the PR was opened. `<date>` is the
  `opened:` date in the `PR: <pr-url> · head: <epic-head-sha> · opened: <date>`
  line ship-epic appends to the epic's notes.

  > ⚠️ Epic **<id> "<title>"** opened its PR on <date> but is not marked
  > shipped — it carries `sh:pushed` without `sh:shipped`.
  >
  > If the PR has merged, re-run `/workflow-commands:workflow-ship-epic <id>`
  > to confirm the merge and mark it shipped. If not, merge it first, or tell
  > me to proceed and stack this new work on top of it.

This is a **surface-and-ask**, not a hard stop. Stacking is sometimes the
right call — in the observed case the second epic genuinely built on the
first. What must not happen is stacking **silently**.

````

- [ ] **Step 2: Rule 3 — closed is not shipped**

In `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md`, replace everything from the heading `### 3. A pushed branch is not a shipped epic`
up to (not including) the heading `### 4. Closing an epic is what ends it — say so at the handoff`
with:

````markdown
### 3. A pushed branch, an open PR or a closed epic is not a shipped epic

Do not read `origin/<branch>` existing as evidence that an epic shipped — in
the observed failure the branch was pushed and the epic was not. This repo
ships through pull requests (`Git Best Practices/no-direct-push-to-master.md`),
and `/workflow-commands:workflow-ship-epic` records the two steps separately:

- **`sh:pushed`** — the PR is open. Ship-epic closed the epic's tasks and the
  epic when it opened the PR, so **closed is not shipped**.
- **`sh:shipped`** — a later re-run of ship-epic confirmed the merge. This is
  the only label that means shipped.

Verify the merge itself rather than trusting a label, using the `<pr-url>` and
`<epic-head-sha>` from the `PR: … · head: … · opened: …` line in the epic's
notes. Ask GitHub first, because a squash merge rewrites the commits and can
defeat ancestry checks; fall back to the trunk (`origin/master`, or
`origin/main`):

```bash
gh pr view <pr-url> --json state,mergedAt               # "MERGED" with a mergedAt time?
git fetch origin
git merge-base --is-ancestor <epic-head-sha> origin/master && echo merged
git cat-file -e origin/master:<a file the epic added>   # supporting evidence
```

An open PR is the same class of false signal as a pushed branch: "reachable
from the trunk" means **the PR was merged**, not merely opened.

````

- [ ] **Step 3: Rule 4 — the two-step handoff**

In `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md`, replace everything from the heading
`### 4. Closing an epic is what ends it — say so at the handoff` up to (not including) the
heading `## Why not just auto-ship?` with:

````markdown
### 4. Shipping ends an epic in two steps — say so at the handoff

When `/workflow-commands:workflow-execute-plans` reports an epic fully
executed, its next-command line (`/workflow-commands:workflow-ship-epic <id>`)
is the **only** thing standing between finished and shipped. Say plainly at
that handoff:

- the epic and its tasks stay OPEN until ship-epic runs;
- ship-epic opens the PR, closes the tasks and the epic, and marks the epic
  `sh:pushed`;
- the epic counts as shipped only once the PR merges and a re-run of
  `/workflow-commands:workflow-ship-epic <id>` confirms the merge and adds
  `sh:shipped`.

That way neither an unshipped epic nor a merely opened PR is mistaken for a
shipped one.

````

- [ ] **Step 4: *Why not just auto-ship?***

In `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md`, replace everything from the heading `## Why not just auto-ship?` up to (not
including) the heading `## Generalized Lesson` with:

```markdown
## Why not just auto-ship?

Because shipping pushes, opens a PR and closes beads — all outward-facing and
hard to reverse. `/workflow-commands:workflow-ship-epic`'s EXECUTION LOCK
requires explicit invocation plus a confirmation gate, it never merges, and
`critical ai agent rule.md` treats trunk integration as a protected operation.
Those are right. The failure here was not too little automation; it was
**silence**. The fix is a check, not a trigger.

```

- [ ] **Step 5: *Generalized Lesson***

In `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md`, replace everything from the heading `## Generalized Lesson` to the end of the file
with:

```markdown
## Generalized Lesson

> A pipeline that correctly refuses to take the last step must still make it
> impossible to forget that the step is outstanding.

Every stage in the epic-batch pipeline advances a label, and each stage reads
the previous stage's label to know where to resume. In the observed failure
`sh:*` was the one label with **no consumer** — nothing read it, so nothing
noticed its absence. A terminal state that nothing checks is indistinguishable
from a state nobody reached. The Step 0 checks in Rule 1 are its consumer now,
and they read both halves: the missing `sh:*` label, and the `sh:pushed` that
never became `sh:shipped`.
```

- [ ] **Step 6: Verify**

```bash
F=".claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md"
grep -n '^### \|^## ' "$F"
grep -c 'sh:pushed' "$F"
grep -n 'PR opened, not merged\|closed is not shipped\|gh pr view <pr-url> --json state,mergedAt' "$F"
grep -n -o -E '/workflow-[A-Za-z0-9._-]+[:/]?' "$F" | grep -v -E ':/workflow-commands[:/]$' || echo "OK: no bare command names"
```

Expected: the headings list ends with `### 3. A pushed branch, an open PR or a closed epic is not a shipped epic`,
`### 4. Shipping ends an epic in two steps — say so at the handoff`, `## Why not just auto-ship?` and
`## Generalized Lesson`; the count is `6`; three matching lines (Rule 1's state bullet, Rule 3's
`**closed is not shipped**`, the `gh pr view` line); and `OK: no bare command names` (Task 1 swept the
untouched sections).

#### Part B: the unshipped-epic check in planning-sequence and writing-plans

**Files:**
- Modify: `.claude/Commands/workflow-commands/workflow-planning-sequence.md` — new Step 0 runs the unshipped-epic check before anything else.
- Modify: `.claude/Commands/workflow-commands/workflow-writing-plans.md` — Step 0 runs the unshipped-epic check (0a) before the resume check (0b).

**Interfaces:**
- Consumes: `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md` Rules 1 and 2 as Task 7 restates them (a closed epic at `sh:pushed` reads "PR opened on <date>, not merged"); workflow-ship-epic's `sh:pushed` → `sh:shipped` re-run flow (Task 7, other part).
- Produces: the same three-part check (finished-never-shipped, PR-opened-not-merged, stacking) at the start of both commands; execute-plans' Step 0 (other part of Task 7) should read the same.

These steps run after Task 1, so command names in the files already read `/workflow-commands:<name>`. Every anchor below avoids the lines Task 1 rewrites, or quotes them in their post-Task-1 form; if an anchor does not match, re-read the file rather than guessing.

- [ ] **Step 1: Add Step 0 — the unshipped-epic check — to planning-sequence**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, insert directly before the heading `### 1. [main ctx] Load input (spec mode or epic mode)` (keep one blank line between the new text and that heading):

```markdown
### 0. [main ctx] Check for a finished epic that never shipped
Before loading anything, run the check in
`.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md` (Rules 1 and 2):

- **Finished but never shipped:** an epic whose children all carry `ex:done`
  while the epic itself has neither `sh:pushed` nor `sh:shipped`. Find
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
it confirms the merge and adds `sh:shipped`, or proceed and stack the new work
on top. It is a surface-and-ask, not a hard stop — what must never happen is
stacking silently. When nothing turns up, continue without comment.
```

- [ ] **Step 2: Name the unshipped-epic check in the step map**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Step Map — Segmentation at a Glance`, replace this whole line:

```text
| 0 | Resume check (idempotency) | main ctx | — |
```

with:

```markdown
| 0 | Unshipped-epic check, then resume check (idempotency) | main ctx | — |
```

- [ ] **Step 3: Run the unshipped-epic check at the start of Step 0**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, replace the passage that begins

```text
## Step 0: Resume Check (idempotency) [main ctx]
```

and ends

```text
stage** — skip steps already completed.
```

(both ends included) with:

```markdown
## Step 0: Unshipped-Epic Check, then Resume Check [main ctx]

**0a — Check for a finished epic that never shipped.** Before touching this
epic, run the check in `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md`
(Rules 1 and 2):

- **Finished but never shipped:** an epic whose children all carry `ex:done`
  while the epic itself has neither `sh:pushed` nor `sh:shipped`. Find
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
```

- [ ] **Step 4: Verify Part B of Task 7**

Run from the repo root:

```bash
d=.claude/Commands/workflow-commands
printf '%s\n' \
  "ps-step0-heading=$(grep -cxF '### 0. [main ctx] Check for a finished epic that never shipped' "$d/workflow-planning-sequence.md")" \
  "ps-rule-cite=$(grep -cF 'surface-unshipped-epics.md' "$d/workflow-planning-sequence.md")" \
  "ps-sh-pushed=$(grep -cF 'sh:pushed' "$d/workflow-planning-sequence.md")" \
  "wp-step0-heading=$(grep -cxF '## Step 0: Unshipped-Epic Check, then Resume Check [main ctx]' "$d/workflow-writing-plans.md")" \
  "wp-rule-cite=$(grep -cF 'surface-unshipped-epics.md' "$d/workflow-writing-plans.md")" \
  "wp-sh-pushed=$(grep -cF 'sh:pushed' "$d/workflow-writing-plans.md")"
```

Expected output, exactly:

```text
ps-step0-heading=1
ps-rule-cite=1
ps-sh-pushed=2
wp-step0-heading=1
wp-rule-cite=1
wp-sh-pushed=2
```

Any other number means a step above was skipped or applied to the wrong passage; re-read that file and fix it before moving on.

#### Part C: ship-epic marks an epic shipped only after its PR merges; execute-plans surfaces unshipped epics

**Files:**
- Modify: `.claude/Commands/workflow-commands/workflow-ship-epic.md` — description, intro, EXECUTION LOCK, Model & Budget, Step Map, Step 0 (re-run merge check, with the `merge-check` snippet), Steps 3–6, Step 7 run kinds, label lifecycle, CRITICAL.
- Modify: `.claude/Commands/workflow-commands/workflow-execute-plans.md` — Step Map row 0, Step 0 pre-check, Step 8 "Fully executed" bullet, CRITICAL.
- Test (outside the repo, never committed): `$CHECKS/check-ship-merge.sh`.

**Interfaces:**
- Consumes: Rule 1 (with its new `sh:pushed` case) and Rule 2 of `.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md`, rewritten earlier in this task; the trunk lookup; Task 4's ship-recommendation gate and "Fully executed" bullet; Task 6's Step 6.5.
- Produces: `sh:pushed` = PR opened (tasks and epic closed); `sh:shipped` = merge confirmed by a re-run; the epic-notes line `PR: <pr-url> · head: <epic-head-sha> · opened: <YYYY-MM-DD>`; the `merge-check` snippet and `check-ship-merge.sh` (Task 9 re-runs it). Task 8 rewrites execute-plans Step 8's closing paragraph and ship-epic Step 7's closing paragraphs.

- [ ] **Step 1: Write the failing check for the ship-epic merge check**

Create `check-ship-merge.sh` in the check directory, outside the repo — never committed. Run `CHECKS="<scratchpad>/sgw-checks"; mkdir -p "$CHECKS"`, then create `<scratchpad>/sgw-checks/check-ship-merge.sh` with the Write tool, not a shell heredoc (see Global Constraints), with exactly this content. It builds throwaway repos with a bare `origin` and exercises the git fallback that Step 0 uses when `gh` cannot say whether the PR merged: an unmerged branch, a merge commit, a squash merge, a trunk called `main`, no `origin` at all, and a head commit the clone does not have.

````bash
#!/usr/bin/env bash
# check-ship-merge.sh <repo-root>
# Exercises the `merge-check` snippet in workflow-ship-epic.md Step 0 (the git
# fallback a re-run uses when `gh` cannot say whether the epic's PR merged).
set -u
REPO="${1:?usage: check-ship-merge.sh <repo-root>}"
FILE="$REPO/.claude/Commands/workflow-commands/workflow-ship-epic.md"
HERE="$(cd "$(dirname "$0")" && pwd)"
W="$HERE/ship-merge"
fail=0
pass()  { echo "PASS: $*"; }
failm() { echo "FAIL: $*"; fail=1; }

extract_snippet() {   # extract_snippet <file> <name>
  awk -v want="# snippet: $2" '
    /^[[:space:]]*```/ { if (inb) { if (hit) exit; inb=0 } else { inb=1; first=1 }; next }
    inb && first { first=0; t=$0; sub(/^[[:space:]]+/, "", t); if (t == want) hit=1; next }
    inb && hit { print }
  ' "$1"
}

rm -rf "$W"; mkdir -p "$W"
SNIP="$W/merge-check.sh"
extract_snippet "$FILE" merge-check > "$SNIP"
if [ ! -s "$SNIP" ]; then
  failm "snippet merge-check not found in workflow-ship-epic.md"
  exit 1
fi
pass "snippet merge-check extracted ($(wc -l < "$SNIP" | tr -d ' ') lines)"

# Isolate the scratch repos from the user's git config (signing, hooks, default branch).
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=check GIT_AUTHOR_EMAIL=check@example.invalid
export GIT_COMMITTER_NAME=check GIT_COMMITTER_EMAIL=check@example.invalid

verdict() {   # verdict <clone-dir> <epic-head> -> the snippet's last "merge-check:" line
  (cd "$1" && EPIC_HEAD="$2" bash "$SNIP" 2>/dev/null) | grep '^merge-check:' | tail -1
}

setup() {   # setup <name> <trunk>: bare origin, a work clone (trunk + pushed branch feat), a merger clone
  local d="$W/$1" t="$2"
  mkdir -p "$d"
  git init -q --bare -b "$t" "$d/origin.git"
  git clone -q "$d/origin.git" "$d/work" 2>/dev/null
  ( cd "$d/work" \
    && git switch -q -c "$t" && echo a > a && git add a && git commit -qm a && git push -q -u origin "$t" \
    && git switch -q -c feat && echo b > b && git add b && git commit -qm b && git push -q -u origin feat ) >/dev/null 2>&1
  git clone -q "$d/origin.git" "$d/merger" 2>/dev/null
}

# 1. Branch pushed, PR not merged; origin/HEAD unset in the work clone (exercises set-head --auto).
setup m master
head=$(git -C "$W/m/work" rev-parse feat)
out=$(verdict "$W/m/work" "$head")
[ "$out" = "merge-check: not merged into origin/master" ] && pass "unmerged branch reads not merged ($out)" || failm "unmerged branch: got '$out'"

# 2. A real merge commit on the remote trunk.
( cd "$W/m/merger" && git merge -q --no-ff -m "merge feat" origin/feat && git push -q origin master ) >/dev/null 2>&1
out=$(verdict "$W/m/work" "$head")
[ "$out" = "merge-check: merged into origin/master" ] && pass "merge commit reads merged ($out)" || failm "merge commit: got '$out'"

# 3. A squash merge: git alone cannot see it, which is why Step 0 asks GitHub first.
setup s master
head=$(git -C "$W/s/work" rev-parse feat)
( cd "$W/s/merger" && git merge -q --squash origin/feat && git commit -qm "squash feat" && git push -q origin master ) >/dev/null 2>&1
out=$(verdict "$W/s/work" "$head")
[ "$out" = "merge-check: not merged into origin/master" ] && pass "squash merge reads not merged, as Step 0 warns ($out)" || failm "squash merge: got '$out'"

# 4. A trunk called main.
setup n main
head=$(git -C "$W/n/work" rev-parse feat)
( cd "$W/n/merger" && git merge -q --no-ff -m "merge feat" origin/feat && git push -q origin main ) >/dev/null 2>&1
out=$(verdict "$W/n/work" "$head")
[ "$out" = "merge-check: merged into origin/main" ] && pass "trunk called main is found ($out)" || failm "trunk called main: got '$out'"

# 5. No origin remote at all.
mkdir -p "$W/none"
( cd "$W/none" && git init -q -b master && echo a > a && git add a && git commit -qm a ) >/dev/null 2>&1
head=$(git -C "$W/none" rev-parse HEAD)
out=$(verdict "$W/none" "$head")
[ "$out" = "merge-check: unknown (no origin trunk found)" ] && pass "no origin reads unknown ($out)" || failm "no origin: got '$out'"

# 6. A head commit this clone does not have.
out=$(verdict "$W/m/work" 0123456789abcdef0123456789abcdef01234567)
case "$out" in
  "merge-check: unknown ("*) pass "missing head commit reads unknown ($out)" ;;
  *) failm "missing head commit: got '$out'" ;;
esac

exit $fail
````

- [ ] **Step 2: Run the check and watch it fail**

Run from the repo root:

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-ship-merge.sh" "$(git rev-parse --show-toplevel)"
```

Expected: exactly `FAIL: snippet merge-check not found in workflow-ship-epic.md`, exit status 1 — the snippet arrives with the Step 0 edit below.

- [ ] **Step 3: ship-epic — frontmatter description: shipped means merged**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, replace the passage that begins `description: Ship a fully-executed beads epic` and ends `and report unblocked work.` with:

```markdown
description: Ship a fully-executed beads epic — open one PR for the shared epic branch, close all child tasks + the epic, and mark the epic shipped once a re-run confirms the PR merged.
```

- [ ] **Step 4: ship-epic — intro: one PR, shipped only once it merges**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, section `# Workflow: Ship an Epic (Python)`, replace the passage that begins `Take a **fully-executed** beads epic and ship it:` and ends `and report what is now unblocked.` with:

```markdown
Take a **fully-executed** beads epic and ship it: **open one PR for the shared
epic branch** (commit + push + PR), **close the epic's child tasks + the epic**,
and report what is now unblocked. The epic counts as **shipped** only once that
PR has merged: the owner merges it, then re-runs this command, which confirms
the merge and marks the epic `sh:shipped`.
```

- [ ] **Step 5: ship-epic — EXECUTION LOCK: the PR is the only integration path**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, section `## 🔒 EXECUTION LOCK (read first)`, replace the passage that begins `` - **It never merges to `main` on its own.** `` and ends `branch and stop.` with:

```markdown
- **It never merges to the trunk.** Integration is always the PR: this command
  commits and pushes the epic branch, opens the PR, and stops. The owner reviews
  and merges it — merge-to-trunk is a protected action under
  `.claude/rules/critical ai agent rule.md` — and a re-run afterwards only
  confirms the merge.
```

- [ ] **Step 6: ship-epic — Model & Budget: drop the leftover integration choice**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, section `## Model & Budget`, replace the passage that begins `| This command's own work |` and ends `` (no `git add -A`). | `` with:

```markdown
| This command's own work | **Cheap** — read beads state, assemble an integration summary, drive `commit-commands:commit-push-pr`. No agent fan-out. |
| Optional | One short summarizer agent **may** draft the change summary / PR body from the per-task plans + QA ledger; not required. |
| Git | Integrates **ONE** epic branch through **one PR** (commit + push + PR). **Never merges to the trunk** — the owner merges the PR. Safe staging only (no `git add -A`). |
```

- [ ] **Step 7: ship-epic — Step Map: sh:pushed at PR open, sh:shipped on the confirming re-run**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, section `## Step Map — Segmentation at a Glance`, replace the passage that begins `| 0 | Resume check (idempotency) | — |` and ends `| 7 | Report unblocked + next epic | — |` with:

```markdown
| 0 | Resume check; on a re-run, confirm the PR merged | `sh:shipped` (re-run only, once merged) |
| 1 | Precondition: execution complete (HARD GATE) | — |
| 2 | Cross-epic closure check | — |
| 3 | Assemble integration summary | — |
| 4 | 🛑 Ship gate (explicit confirm) | — |
| 5 | Commit + push + open the PR | `sh:pushed` |
| 6 | Close tasks + epic (idempotent) | — |
| 6.5 | Publish beads (Dolt sync) | — |
| 7 | Report: PR opened, or epic shipped | — |
```

- [ ] **Step 8: ship-epic — Step 0: on a re-run, confirm the merge before marking shipped**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, replace everything from the heading `## Step 0: Resume Check (idempotency) [main ctx]` up to (not including) the heading `## Step 1: Precondition — Execution Complete (HARD GATE) [main ctx]` with:

````markdown
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
     trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null) || {
       git remote set-head origin --auto >/dev/null 2>&1
       trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
     }
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
````

- [ ] **Step 9: ship-epic — Step 3: the summary always feeds the PR body**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, section `## Step 3: Assemble Integration Summary [main ctx]`, replace the passage that begins `Build a change summary (used for the commit body and, if the user later chooses a PR,` and ends `the PR body)` with:

```markdown
Build a change summary (used for the commit body and the PR body)
```

- [ ] **Step 10: ship-epic — Step 4: explicit confirm only; the gate says when the epic counts as shipped**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, replace everything from the heading `## Step 4: 🛑 Ship Gate — Explicit Confirm + Integration Choice [main ctx]` up to (not including) the heading `## Step 5: Commit + Push (+ chosen integration) [main ctx]` with:

````markdown
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
````

- [ ] **Step 11: ship-epic — Step 5: open the PR, record it, label sh:pushed**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, replace everything from the heading `## Step 5: Commit + Push (+ chosen integration) [main ctx]` up to (not including) the heading `## Step 6: Close Tasks + Epic (idempotent) [main ctx]` with:

```markdown
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
```

- [ ] **Step 12: ship-epic — Step 6: closing is not shipping; drop the "push only" note**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, section `## Step 6: Close Tasks + Epic (idempotent) [main ctx]`, replace the passage that begins `` Advance the epic label to **`sh:shipped`**. `` and ends `close on a re-run after merge.` with:

```markdown
The epic keeps the `sh:pushed` label from Step 5 and does **not** get `sh:shipped`
here. Closing happens when the PR opens, but shipped means merged: only a re-run of
this command after the merge (Step 0) adds `sh:shipped`. Until then
`.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md` keeps flagging the
epic as "PR opened, not merged".
```

- [ ] **Step 13: ship-epic — Step 7: say which run this was**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, insert after the line `## Step 7: Report — Epic Status & Next-Steps Summary [main ctx]`, leaving one blank line between that line and the new text:

```markdown
This command runs at least twice for every epic, and the report says which run
this was:

- **First run — PR opened.** The tasks and the epic are closed and the epic is
  `sh:pushed`, but it is **not shipped yet**: give the PR URL and say that the
  owner merges it and then re-runs this command.
- **A re-run before the merge.** Report "PR open, awaiting merge: <pr-url>" and
  nothing else.
- **The confirming re-run — merged.** Step 0 found the PR merged and added
  `sh:shipped`; report the epic as shipped.
```

- [ ] **Step 14: ship-epic — label lifecycle: sh:pushed = PR opened, sh:shipped = merge confirmed**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, section `## Beads Label Lifecycle (ship-epic)`, replace the passage that begins `Epic-level labels (not per-task)` and ends `resumable (Step 0).` with:

````markdown
Epic-level labels (not per-task). `sh:pushed` is written at the end of Step 5 on
the first run; `sh:shipped` only by Step 0 on a re-run, once the PR has merged:

```
sh:pushed       (first run: PR opened; child tasks + epic closed — Steps 5–6)
   → sh:shipped (re-run: PR merged and confirmed — Step 0)
```

An epic at `sh:pushed` without `sh:shipped` is closed but **not shipped**. Use
`beads:label` / `beads:close` / `beads:show` / `beads:update` skills — never raw
`bd` in Bash. These labels make the ship resumable (Step 0).
````

- [ ] **Step 15: ship-epic — CRITICAL: shipped means merged**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, insert after the line `  never merge to the trunk — integration is via the PR.`, as the very next line (no blank line between — it continues the list):

```markdown
- **Shipped means merged:** the first run ends at `sh:pushed` (PR opened, tasks and
  epic closed); only a re-run that confirms the merge (Step 0) adds `sh:shipped`.
  Never add `sh:shipped` on the strength of a pushed branch or an open PR.
```

- [ ] **Step 16: execute-plans — Step Map row 0 names the unshipped-epic check**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, section `## Step Map — Segmentation at a Glance`, replace the passage that begins `| 0 | Scope + precondition + resume check |` and ends `| — |` with:

```markdown
| 0 | Unshipped-epic check + scope + precondition + resume check | main ctx | — |
```

- [ ] **Step 17: execute-plans — Step 0 pre-check: surface an epic that finished but never shipped**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, insert after the line `## Step 0: Scope + Precondition + Resume Check (idempotency) [main ctx]`, leaving one blank line between that line and the new text:

```markdown
### Pre-check — surface an epic that finished but never shipped

Before resolving scope, apply Rule 1 of
`.claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md`. Read every epic's
labels, and its children's, with `beads:list` / `beads:show` in this turn, and
look for another epic in either state:

- **Finished, never shipped:** every child is `ex:done`, but the epic has no
  `sh:*` label. Its tasks are still open and its code is not on the trunk.
- **PR opened, not merged:** the epic carries `sh:pushed` but not `sh:shipped`.
  `/workflow-commands:workflow-ship-epic` opened its PR and closed its tasks, but
  nobody has confirmed the merge.

If either exists, say so before anything else, for example:

> ⚠️ Epic **<id> "<title>"** finished executing on <date> but was never shipped —
> all N children are `ex:done`, the epic has no `sh:*` label, and its code is not
> on the trunk.

> ⚠️ Epic **<id> "<title>"**: PR opened on <date>, not merged — it is `sh:pushed`
> without `sh:shipped`.

> Ship or confirm it with `/workflow-commands:workflow-ship-epic <id>` first, or
> tell me to proceed and stack this work on top of it.

This is surface-and-ask, not a hard stop: stacking is sometimes right, but never
silently. Apply Rule 2 of the same file too: before executing on a branch that
already carries another epic's unmerged commits, name that epic and the commit
count, and say that shipping this branch will ship both.
```

- [ ] **Step 18: execute-plans — final handoff: open until ship-epic, shipped only once the PR merges**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, section `## Step 8: Epic Status & Next-Steps Summary [main ctx]`, replace the passage that begins `- **Fully executed**` and ends `` <epic-id>`. `` with:

```markdown
- **Fully executed** — if every task in the resolved scope (Step 0a) is
  `ex:done` and the ship-recommendation gate below finds nothing left, say so
  and name the next command: `/workflow-commands:workflow-ship-epic <epic-id>`.
  Say plainly that the epic and its tasks stay **open** until that command runs
  — `ex:done` means executed, not shipped — and that ship-epic closes them when
  it opens the PR, but the epic counts as shipped only once that PR has merged
  and a re-run of ship-epic has confirmed it (`sh:shipped`). A pushed branch or
  an open PR is not a shipped epic.
```

- [ ] **Step 19: execute-plans — CRITICAL: unshipped epics first**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, section `## CRITICAL — Honor Project Rules`, replace the passage that begins `## CRITICAL — Honor Project Rules` and ends `- **Scope + approval precondition (Steps 0a–0b):**` with:

```markdown
## CRITICAL — Honor Project Rules

- **Unshipped epics first (Step 0 pre-check):** before starting, surface any epic
  that finished executing but never shipped, or that sits at `sh:pushed` waiting
  for its PR to merge — surface and ask, never stack new work on it silently.
- **Scope + approval precondition (Steps 0a–0b):**
```

- [ ] **Step 20: Run the check and watch it pass**

Run from the repo root:

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-ship-merge.sh" "$(git rev-parse --show-toplevel)"
```

Expected, exit status 0:

```
PASS: snippet merge-check extracted (16 lines)
PASS: unmerged branch reads not merged (merge-check: not merged into origin/master)
PASS: merge commit reads merged (merge-check: merged into origin/master)
PASS: squash merge reads not merged, as Step 0 warns (merge-check: not merged into origin/master)
PASS: trunk called main is found (merge-check: merged into origin/main)
PASS: no origin reads unknown (merge-check: unknown (no origin trunk found))
PASS: missing head commit reads unknown (merge-check: unknown (0123456789abcdef0123456789abcdef01234567 is not a commit in this clone))
```

- [ ] **Step 21: Verify this part's edits landed**

Run from the repo root:

```bash
C=.claude/Commands/workflow-commands
while IFS='|' read -r want f s; do
  got=$(grep -c -F -- "$s" "$C/$f")
  if [ "$got" = "$want" ]; then echo "ok   $f: $s"; else echo "MISMATCH (got $got, want $want)  $f: $s"; fi
done <<'EOF'
1|workflow-ship-epic.md|# snippet: merge-check
0|workflow-ship-epic.md|Integration Choice
0|workflow-ship-epic.md|chosen integration
0|workflow-ship-epic.md|push only
0|workflow-ship-epic.md|later chooses a PR
0|workflow-ship-epic.md|Advance the epic label to **`sh:shipped`**.
1|workflow-ship-epic.md|PR: <pr-url> · head: <epic-head-sha>
1|workflow-ship-epic.md|**Closed without merging**
1|workflow-execute-plans.md|### Pre-check — surface an epic that finished but never shipped
1|workflow-execute-plans.md|**Unshipped epics first (Step 0 pre-check):**
1|workflow-execute-plans.md|an open PR is not a shipped epic.
EOF
```

Expected: 11 lines, every one starting with `ok`. A `MISMATCH` line names the file and phrase whose edit is missing or duplicated.

#### Part D: `validate-bash.sh` auto-allows only a single simple command

**Files:**
- Modify: `.claude/hooks/validate-bash.sh` — a 10-line insertion between the dangerous-pattern loop and the quick-allow list. The dangerous-pattern check is byte-for-byte unchanged and still runs first.
- Test (not committed): `$CHECKS/check-validate-bash.sh`

**Interfaces:**
- Consumes: nothing from earlier tasks (no task before this one edits the hook).
- Produces: the hook's decision contract — `allow` only for a single simple command matching the quick-allow list; `ask` for any dangerous pattern, compound or not; otherwise no output (Claude Code's normal permission prompt). Task 9 re-runs `check-validate-bash.sh`.

Why the character set is wider than the spec's list (`;`, `&&`, `||`, `|`, `$(`, backtick, newline): the spec's principle is "the quick-allow list applies only to a single simple command", and four more constructs hide a second action behind an allowed first word just as well — a single `&` (backgrounding: `ls & rm -rf build` is auto-allowed today), `<(` and `>(` (process substitution), and `>` (output redirection: `echo hi > notes.txt` overwrites a file with no prompt today). Checking for any `&` also covers `&&`, any `|` covers `||`, and `>` covers `>(`. A carriage return counts as a newline. Such commands only lose the auto-allow; Claude Code still prompts for them normally.

- [ ] **Step 1: Write the failing check**

Create `<scratchpad>/sgw-checks/check-validate-bash.sh` with the Write tool, not a Bash heredoc (see Global Constraints): a command-rewriting hook could otherwise alter the `rm` test strings below. The check runs the hook through its own `#!/bin/bash` shebang (bash 3.2 on macOS), exactly as Claude Code does, so it also proves the executable bit survived.

```bash
#!/usr/bin/env bash
# Behaviour check for .claude/hooks/validate-bash.sh (Task 7).
# Feeds PreToolUse hook JSON on stdin and checks the permission decision:
# allow (auto-allowed), ask (dangerous pattern), none (no opinion -> normal prompt).
# The hook runs through its own shebang, as Claude Code runs it.
# Usage: bash check-validate-bash.sh <repo-root>
set -u
HOOK="$1/.claude/hooks/validate-bash.sh"
fail=0

if [ ! -x "$HOOK" ]; then
  echo "FAIL: $HOOK is not executable"
  exit 1
fi

decide() {  # prints allow | ask | none
  local out
  out=$(jq -n --arg c "$1" '{hook_event_name: "PreToolUse", tool_name: "Bash", tool_input: {command: $c}}' | "$HOOK")
  if [ -z "$out" ]; then echo none; else printf '%s' "$out" | jq -r '.hookSpecificOutput.permissionDecision // "none"'; fi
}

expect() {  # expect <allow|ask|none> <command>
  local got
  got=$(decide "$2")
  if [ "$got" = "$1" ]; then
    echo "PASS: $1 <- $(printf '%q' "$2")"
  else
    echo "FAIL: expected $1, got $got <- $(printf '%q' "$2")"
    fail=1
  fi
}

# A single simple command on the quick-allow list is still auto-allowed.
expect allow 'ls -la'
expect allow 'cat README.md'
# Chaining, piping, substitution, backgrounding, redirection or a newline: no auto-allow.
expect none 'cd x && git reset --hard'
expect none 'echo hi; rm f'
expect none 'cat a | sh'
expect none 'ls && git push --force'
expect none 'true && git push --force'
expect none 'git commit -m "a && b"'
expect none $'ls\nrm -rf build'
expect none 'echo $(rm -rf build)'
expect none 'echo `rm -rf build`'
expect none 'ls & rm -rf build'
expect none 'echo hi > notes.txt'
# The dangerous-pattern check still runs first, compound or not.
expect ask 'rm -rf /'
expect ask 'ls; rm -rf /'

exit $fail
```

Note on `git push --force`: it is not in `DANGEROUS_PATTERNS` (the push patterns were removed from the template on purpose and stay removed — spec §8), so `true && git push --force` gets no decision both before and after this task, which means Claude Code prompts for it normally. The case that was actually auto-allowed is `ls && git push --force`, and that is what this task fixes.

- [ ] **Step 2: Run the check against the current hook and watch it fail**

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-validate-bash.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
```

Expected — 6 PASS and 9 FAIL, every FAIL being a compound command the current hook auto-allows because its first word is on the quick-allow list (the escaping of the command text comes from `printf %q` and may differ slightly between bash versions; the PASS/FAIL pattern must not):

```
PASS: allow <- ls\ -la
PASS: allow <- cat\ README.md
FAIL: expected none, got allow <- cd\ x\ \&\&\ git\ reset\ --hard
FAIL: expected none, got allow <- echo\ hi\;\ rm\ f
FAIL: expected none, got allow <- cat\ a\ \|\ sh
FAIL: expected none, got allow <- ls\ \&\&\ git\ push\ --force
PASS: none <- true\ \&\&\ git\ push\ --force
PASS: none <- git\ commit\ -m\ \"a\ \&\&\ b\"
FAIL: expected none, got allow <- $'ls\nrm -rf build'
FAIL: expected none, got allow <- echo\ \$\(rm\ -rf\ build\)
FAIL: expected none, got allow <- echo\ \`rm\ -rf\ build\`
FAIL: expected none, got allow <- ls\ \&\ rm\ -rf\ build
FAIL: expected none, got allow <- echo\ hi\ \>\ notes.txt
PASS: ask <- rm\ -rf\ /
PASS: ask <- ls\;\ rm\ -rf\ /
exit=1
```

- [ ] **Step 3: Replace the hook**

Replace the whole of `.claude/hooks/validate-bash.sh` with the content below (use the Write tool, which keeps the file's executable mode). The only change from the current file is the commented `case` block inserted after the dangerous-pattern loop.

```bash
#!/bin/bash

# Read the tool input from stdin
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Define dangerous patterns (includes both rm and trash since rm→trash conversion happens first)
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "rm -rf \$HOME"
    "rm -rf \*"
    "trash /"
    "trash ~"
    "trash \$HOME"
    "trash \*"
    "> /dev/sd"
    "mkfs"
    "dd if="
    ":(){:|:&};:"         # Fork bomb
    "chmod -R 777 /"
    "chown -R"
    "curl.*\\| bash"
    "wget.*\\| bash"
    "curl.*\\| sh"
    "wget.*\\| sh"
    "DROP TABLE"
    "DROP DATABASE"
    "DELETE FROM.*WHERE 1"
    "npm publish"
    "pip upload"
)

# Check each pattern - BLOCK dangerous commands outright
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        jq -n --arg reason "⚠️ Dangerous command detected ($pattern). Are you sure?" '{
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": $reason
            }
        }'
        exit 0
    fi
done

# The quick-allow list below applies only to a single simple command. A command
# that chains (; & && ||), pipes (|), substitutes ($( ) or backticks, <( ) >( )),
# redirects output (>), or spans lines can hide a second action behind an allowed
# first word, so it gets no auto-allow and falls through to the normal prompt.
case "$COMMAND" in
    *$'\n'*|*$'\r'*|*';'*|*'&'*|*'|'*|*'`'*|*'$('*|*'<('*|*'>'*)
        exit 0
        ;;
esac

# Explicitly allow safe commands so they bypass permission prompts
SAFE_PATTERNS=(
    "^cd "
    "^cat "
    "^echo "
    "^ls"
    "^head "
    "^tail "
    "^wc "
    "^sort "
    "^which "
    "^where "
    "^test "
    "^\\["
)

for pattern in "${SAFE_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        jq -n '{
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            }
        }'
        exit 0
    fi
done

# No opinion — fall through to normal permission checking
exit 0
```

- [ ] **Step 4: Run the check and watch it pass**

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-validate-bash.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
```

Expected: 15 lines, every one starting with `PASS:` (2 `allow`, 11 `none`, 2 `ask`), then `exit=0`.

- [ ] **Step 5: Prove the change is a pure insertion with the mode intact**

```bash
git diff --numstat -- .claude/hooks/validate-bash.sh
git diff --summary -- .claude/hooks/validate-bash.sh
bash -n .claude/hooks/validate-bash.sh && test -x .claude/hooks/validate-bash.sh && echo "syntax ok, executable"
```

Expected: `10	0	.claude/hooks/validate-bash.sh` (ten lines added, none removed — so the dangerous-pattern check and the quick-allow list are untouched); then no output from `--summary` (no mode change; the file is tracked as 100755); then `syntax ok, executable`.

- [ ] **Finish 1: Confirm this task's change set**

```bash
git status --short
```
Expected: exactly the files in this task's **Files** list above (`M` modified, `??` new, `D` deleted), and nothing else — apart from a `?? .claude/worktrees/` line if that local folder holds a worktree, which is never staged. Anything else means a step touched the wrong file: find it with `git diff <path>` before staging.

- [ ] **Finish 2: Commit W7**

```bash
git add -- \
  ".claude/rules/0_Beads x Superpowers/surface-unshipped-epics.md" \
  ".claude/Commands/workflow-commands/workflow-planning-sequence.md" \
  ".claude/Commands/workflow-commands/workflow-writing-plans.md" \
  ".claude/Commands/workflow-commands/workflow-ship-epic.md" \
  ".claude/Commands/workflow-commands/workflow-execute-plans.md" \
  ".claude/hooks/validate-bash.sh" && \
git diff --cached --stat && git commit -F- <<'EOF'
fix(workflow): an epic is shipped only after its PR merges; scope the bash hook's auto-allow

Ship-epic marks sh:pushed when it opens the PR and sh:shipped only when a
re-run confirms the merge; the three batch commands surface unshipped epics at
Step 0; validate-bash.sh auto-allows only a single simple command.

<attribution trailer>
EOF
```
Expected: the stat lists only this task's files, then the commit summary line. Replace `<attribution trailer>` with the attribution lines from your session's system reminder before running it.

- [ ] **Finish 3: Record the commit on the W7 bead**

```bash
source .beads/sgw-ids.env && bd update "$W7" --append-notes "Landed in $(git rev-parse --short HEAD): fix(workflow): an epic is shipped only after its PR merges; scope the bash hook's auto-allow" && bd show "$W7" | sed -n '1,20p'
```
Expected: the notes end with the "Landed in" line and the status is still `IN_PROGRESS` — all eight workstream beads close together when the PR opens (Task 9).

---

### Task 8: W8 — README, diagram and `/clear` steps

Spec: §6 W8; §3 decisions 5 and 7; §7 (the batch commands' Next lines include `/clear` between phases).

**Files:**
- Modify: `README.md`, `docs/workflow-process-flow.drawio`, `docs/workflow-process-flow.drawio.png` (Part A)
- Modify: `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, `.claude/Commands/workflow-commands/workflow-writing-plans.md`, `.claude/Commands/workflow-commands/workflow-execution-sequence.md` (Part B)
- Modify: `.claude/Commands/workflow-commands/workflow-execute-plans.md`, `.claude/Commands/workflow-commands/workflow-execute-spikes.md`, `.claude/Commands/workflow-commands/workflow-ship-epic.md` (Part C)

**Interfaces:**
- Consumes: every earlier task's command names and behaviour, which the README and the diagram describe.
- Produces: the README's verified setup and usage recipe; the updated diagram; Next lines with `/clear` as its own step.

Each part below lists its own files, interfaces and steps; run the parts in order, A first.

- [ ] **Start: mark the W8 bead in progress**

```bash
source .beads/sgw-ids.env && bd update "$W8" --status in_progress && bd show "$W8" | head -6
```
Expected: the bead shows `IN_PROGRESS`. (If `.beads/sgw-ids.env` is missing, Task 0 has not run.)

#### Part A: the README rewrite and the diagram update

**Files:**
- Modify: `README.md` — rewritten as a short numbered recipe: set up (8 steps), one task (6 steps), an epic (16 steps, with the diagram), one context tip, and five "what's inside" pointers. 374 lines become 109.
- Modify: `docs/workflow-process-flow.drawio` — rebuilt: writing-plans now comes before the spike decision and the spike step loops back to it; step 2 shows plan depth; step 6 shows "PR opened (sh:pushed) → sh:shipped after merge"; every command has its full name; the context note matches the README's tip.
- Modify: `docs/workflow-process-flow.drawio.png` — re-exported from the new XML with the diagram embedded.
- Test (not committed): `$CHECKS/check-readme-setup.sh`

**Interfaces:**
- Consumes: Task 0's restore of both diagram files from HEAD; the post-Task-1 command names; Task 4's `.claude/skills/` directory and the router path `.claude/rules/0_Beads x Superpowers/beads-workflow-router.md`; Task 5's order (writing-plans, then spikes, then writing-plans again for the unblocked tasks); Task 7's ship-epic behaviour (the first run opens the PR and adds `sh:pushed`; a re-run after the merge adds `sh:shipped`).
- Produces: the README's setup and usage commands, which Task 9's reference sweep checks. The README names three plugin-namespace commands the sweep must accept as external: `/beads:ready`, `/superpowers:brainstorming`, and the `/plugin …` lines.

How the README's commands were verified on 2026-10-02 (beads 1.0.4, Claude Code 2.1.287, draw.io 31.1.8), so the executor does not need to re-derive them:

- Plugin ids match what is installed here: `beads@beads-marketplace` from the `steveyegge/beads` marketplace, `superpowers@claude-plugins-official`, `commit-commands@claude-plugins-official`, and `codex@openai-codex` from `openai/codex-plugin-cc`. The syntax matches `claude plugin install <plugin>@<marketplace>` and `claude plugin marketplace add <owner/repo>`.
- `bd` here was installed with `npm install -g @beads/bd`.
- `cp -rn src/.claude/ .claude/` on macOS copies the contents without nesting, never overwrites an existing file, and exits 1 when it skips one — hence the README's note.
- `bd init` commits its own files on the current branch (and `bd dolt remote add` makes a second commit holding `config.yaml`), which is why the README starts a setup branch and ends with a PR. Plain `bd init` also writes and commits `AGENTS.md` and `CLAUDE.md` with generic beads instructions; `--skip-agents` leaves those out (the beads plugin already provides the `bd prime` session hook).
- `no-auto-import` is not a `bd config set` key, and `bd config set` leaves `config.yaml` without a trailing newline, so the README appends the key with a leading `\n`. Beads 1.0.4 itself does not read this key (the binary contains no such string, and `bd config get no-auto-import` reports "not set"); it is kept to mirror the owner's setup. What actually prevents stale-export reverts on 1.0.4 is keeping `issues.jsonl` untracked: with it untracked, the post-checkout hook re-exports from the database instead of importing the file (a closed bead stayed closed across two branch switches with a deliberately stale export on disk).
- `git worktree add ../<project>-<epic> -b feat/<epic-slug>` and `gh pr create --fill` both work as written; `git switch -c` works even in a repo with no commits yet.

- [ ] **Step 1: Write the failing check**

Create `<scratchpad>/sgw-checks/check-readme-setup.sh` with the Write tool, not a Bash heredoc (see Global Constraints). The script never deletes anything: each run uses fresh `mktemp -d` directories, and it takes the template's `.claude/` from `git archive HEAD`, which is exactly what a fresh clone of the template contains (so the local, untracked `.claude/worktrees/` never leaks in).

```bash
#!/usr/bin/env bash
# Behaviour check for the README's one-time setup (Task 8).
# Part A: every setup command appears verbatim in README.md.
# Part B: the shell commands, run in README order in a fresh repo, give the
#         expected beads config and git state.
# Each run works in a new mktemp directory, so nothing is ever deleted.
# Usage: bash check-readme-setup.sh <repo-root>
set -u
REPO="$1"
README="$REPO/README.md"
HERE="$(cd "$(dirname "$0")" && pwd)"
fail=0
pass() { echo "PASS: $1"; }
bad()  { echo "FAIL: $1"; fail=1; }

# --- Part A: the README carries each command exactly ------------------------
while IFS= read -r line; do
  [ -z "$line" ] && continue
  if grep -qF -- "$line" "$README"; then pass "README has: $line"; else bad "README lacks: $line"; fi
done <<'LINES'
brew install jq gh
gh auth login
npm install -g @beads/bd
/plugin marketplace add steveyegge/beads
/plugin install beads@beads-marketplace
/plugin install superpowers@claude-plugins-official
/plugin install commit-commands@claude-plugins-official
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
git switch -c chore/workflow-setup
cp -rn /path/to/beadspowers-python/.claude/ .claude/
chmod +x .claude/hooks/*.sh
bd init --skip-agents
bd config set export.git-add false
printf '\nno-auto-import: true\n' >> .beads/config.yaml
printf '\nissues.jsonl\n.session-state.json\n.workflow-step\n.verification-done\n' >> .beads/.gitignore
git rm --cached --ignore-unmatch .beads/issues.jsonl
bd dolt remote add origin git+https://github.com/<owner>/<repo>.git
grep -rn -e '<owner>/<repo>' -e 'src/<your_package>/' -e '<project>_test' -e '<run-command>' .claude/
git add .claude .beads/config.yaml .beads/.gitignore
git commit -m "chore: add the Beadspowers workflow"
git push -u origin HEAD
gh pr create --fill
LINES

# --- Part B: run the shell steps in README order ------------------------------
# The template source is the committed .claude/ tree, as a fresh clone has it.
SRC=$(mktemp -d "$HERE/readme-template.XXXXXX")
git -C "$REPO" archive HEAD .claude | tar -x -C "$SRC" || bad "could not export the template's .claude/"
DIR=$(mktemp -d "$HERE/readme-setup.XXXXXX")
cd "$DIR" || exit 1
git init -q -b main && echo "# demo" > README.md && git add README.md && git commit -q -m init
git switch -q -c chore/workflow-setup
cp -rn "$SRC/.claude/" .claude/ || true          # cp -n exits 1 when it skips a file
if [ -f .claude/settings.json ] && [ ! -e .claude/.claude ]; then
  pass "cp -rn copied .claude/ without nesting"
else
  bad "cp -rn did not produce .claude/settings.json cleanly"
fi
chmod +x .claude/hooks/*.sh
[ -x .claude/hooks/validate-bash.sh ] && pass "hooks are executable" || bad "hooks not executable"

bd init --skip-agents >/dev/null 2>&1 || bad "bd init --skip-agents failed"
if [ "$(git log -1 --format=%s)" = "bd init: initialize beads issue tracking" ]; then
  pass "bd init made its own commit on the setup branch"
else
  bad "bd init did not commit as expected"
fi
if [ ! -e AGENTS.md ] && [ ! -e CLAUDE.md ]; then
  pass "--skip-agents wrote no AGENTS.md or CLAUDE.md"
else
  bad "bd init wrote AGENTS.md or CLAUDE.md"
fi
bd config set export.git-add false >/dev/null
printf '\nno-auto-import: true\n' >> .beads/config.yaml
printf '\nissues.jsonl\n.session-state.json\n.workflow-step\n.verification-done\n' >> .beads/.gitignore
git rm -q --cached --ignore-unmatch .beads/issues.jsonl
bd dolt remote add origin git+https://github.com/example/example.git >/dev/null

grep -qx 'export.git-add: false' .beads/config.yaml && pass "config.yaml: export.git-add: false" || bad "export.git-add not set"
if grep -qx 'no-auto-import: true' .beads/config.yaml; then
  pass "config.yaml: no-auto-import: true on its own line"
else
  bad "no-auto-import line missing or glued to the previous line"
fi
if grep -qx 'sync.remote: "git+https://github.com/example/example.git"' .beads/config.yaml; then
  pass "config.yaml: sync.remote recorded"
else
  bad "sync.remote not recorded"
fi
cfg=$(bd config get export.git-add 2>&1)
case "$cfg" in
  *"While parsing config"*) bad "config.yaml no longer parses: $cfg" ;;
  false) pass "config.yaml parses and bd reads export.git-add=false" ;;
  *) bad "unexpected bd config get output: $cfg" ;;
esac
bd dolt remote list 2>/dev/null | grep -q '^origin ' && pass "Dolt remote origin configured" || bad "Dolt remote missing"
if [ -n "$(grep -rn -e '<owner>/<repo>' -e 'src/<your_package>/' -e '<project>_test' -e '<run-command>' .claude/)" ]; then
  pass "the placeholder grep finds the placeholders"
else
  bad "the placeholder grep found nothing"
fi

git add .claude .beads/config.yaml .beads/.gitignore
git commit -q -m "chore: add the Beadspowers workflow"
if [ -z "$(git status --short)" ]; then
  pass "the setup commit leaves a clean tree"
else
  bad "tree not clean after the setup commit: $(git status --short | tr '\n' ' ')"
fi

bd create "readme setup check" -t task --silent >/dev/null
bd export -o .beads/issues.jsonl >/dev/null
[ -s .beads/issues.jsonl ] && pass "bd export wrote .beads/issues.jsonl" || bad "export missing"
git check-ignore -q .beads/issues.jsonl && pass "issues.jsonl is ignored" || bad "issues.jsonl is not ignored"
for f in .session-state.json .workflow-step .verification-done; do
  : > ".beads/$f"
  git check-ignore -q ".beads/$f" && pass "workflow state file $f is ignored" || bad "workflow state file $f is not ignored"
done
if git ls-files --error-unmatch .beads/issues.jsonl >/dev/null 2>&1; then
  bad "issues.jsonl is tracked"
else
  pass "issues.jsonl is untracked"
fi
git diff --cached --quiet && pass "bd staged nothing" || bad "bd staged: $(git diff --cached --name-only | tr '\n' ' ')"

exit $fail
```

- [ ] **Step 2: Run the check and watch it fail**

Run it by itself (it runs `bd`, only inside its own scratch repos), from the repo root:

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-readme-setup.sh" "$(git rev-parse --show-toplevel)" > "$CHECKS/readme-red.txt" 2>/dev/null
grep -c '^FAIL' "$CHECKS/readme-red.txt"
grep '^FAIL' "$CHECKS/readme-red.txt" | head -3
```

Expected: `21`, then the first three of them:

```
FAIL: README lacks: brew install jq gh
FAIL: README lacks: npm install -g @beads/bd
FAIL: README lacks: /plugin marketplace add steveyegge/beads
```

All 21 failures are Part A (the current README lacks the commands). Part B already passes, because the check runs the commands itself; it proves the commands work, and Part A proves the README carries them.

- [ ] **Step 3: Rewrite the README**

Replace the whole of `README.md` with:

````markdown
# Beadspowers: Python

Beadspowers is a Claude Code workflow for Python projects that combines **Beads** issue tracking with the **Superpowers** plan → execute → verify lifecycle, and enforces the order. Work one task at a time with you in the loop, or hand Claude a whole epic to plan and build across parallel agents.

## Set up (once per project)

1. Install the system tools (the workflow is verified with beads 1.0.4):

   ```bash
   brew install jq gh
   gh auth login
   npm install -g @beads/bd
   ```

2. Install the plugins, inside Claude Code:

   ```
   /plugin marketplace add steveyegge/beads
   /plugin install beads@beads-marketplace
   /plugin install superpowers@claude-plugins-official
   /plugin install commit-commands@claude-plugins-official
   /plugin marketplace add openai/codex-plugin-cc
   /plugin install codex@openai-codex
   ```

   The last two lines add the Codex plugin. Only the full verification tier's adversarial review uses it, so skip them if you don't use Codex.

3. From your project root, start a setup branch and copy the workflow in. `cp -n` never overwrites your files (it exits 1 when it skips one). If you already had a `.claude/settings.json`, merge this repo's `hooks` and `enabledPlugins` into it by hand.

   ```bash
   git switch -c chore/workflow-setup
   cp -rn /path/to/beadspowers-python/.claude/ .claude/
   ```

4. Make the hooks executable:

   ```bash
   chmod +x .claude/hooks/*.sh
   ```

5. Set up beads. `bd init` makes its own commit on the current branch. Beads sync through a Dolt remote on your git host, and `.beads/issues.jsonl` stays an untracked, readable export. The workflow's own state files (`.session-state.json`, `.workflow-step`, `.verification-done`) are ignored too, so a ship never commits them. <!-- Refined: Data Flow -->

   ```bash
   bd init --skip-agents
   bd config set export.git-add false
   printf '\nno-auto-import: true\n' >> .beads/config.yaml
   printf '\nissues.jsonl\n.session-state.json\n.workflow-step\n.verification-done\n' >> .beads/.gitignore
   git rm --cached --ignore-unmatch .beads/issues.jsonl
   bd dolt remote add origin git+https://github.com/<owner>/<repo>.git
   ```

6. Find the placeholders and replace each one with your project's value:

   ```bash
   grep -rn -e '<owner>/<repo>' -e 'src/<your_package>/' -e '<project>_test' -e '<run-command>' .claude/
   ```

7. Commit the setup and open a PR. Merge it before your first task, because task branches start from the trunk.

   ```bash
   git add .claude .beads/config.yaml .beads/.gitignore
   git commit -m "chore: add the Beadspowers workflow"
   git push -u origin HEAD
   gh pr create --fill
   ```

8. Start a new Claude Code session in the project.

## One task

1. `/beads:ready`
2. `/workflow-commands:beads-start-task <task-id>` — Claude announces the lane; in Lane C it asks the refinement questions and the execution choice.
3. Verification runs automatically after execution.
4. `/workflow-commands:beads-ship-task` — opens the PR and closes the bead.
5. Merge the PR.
6. `/clear`

## An epic

![Epic-batch workflow](docs/workflow-process-flow.drawio.png)

1. `git worktree add ../<project>-<epic> -b feat/<epic-slug>`, then `cd ../<project>-<epic> && claude`
2. `/superpowers:brainstorming` — the approved spec lands in `docs/plans/`.
3. `/clear`
4. `/workflow-commands:workflow-planning-sequence --spec docs/plans/<date>-<topic>-design.md` — creates the epic; note its id.
5. `/clear`
6. `/workflow-commands:workflow-writing-plans <epic-id>`
7. `/clear`
8. Only if the epic has spike tasks: `/workflow-commands:workflow-execute-spikes <epic-id>`, then `/clear`, then `/workflow-commands:workflow-writing-plans <epic-id>` again (it plans the tasks the spikes unblocked), then `/clear`.
9. `/workflow-commands:workflow-execution-sequence <epic-id>`
10. `/clear`
11. `/workflow-commands:workflow-execute-plans <epic-id>`
12. `/clear`
13. `/workflow-commands:workflow-ship-epic <epic-id>` — opens the PR.
14. Merge the PR.
15. `/workflow-commands:workflow-ship-epic <epic-id>` again — confirms the merge and marks the epic shipped.
16. `/clear`

If tasks are left over after step 11, unplanned ones go back to step 6 and unordered ones to step 9.

**Context tip:** past roughly 30–50% of the context window in the middle of a phase, ask Claude for a handoff doc for the next session, `/clear`, and paste the doc back in.

## What's inside

- `.claude/rules/` — the router (`0_Beads x Superpowers/beads-workflow-router.md`) and the rules it enforces; start here.
- `.claude/Commands/workflow-commands/` — the single-task and epic-batch commands, plus the `python-verification-*` tiers.
- `.claude/agents/` — the review agents the full verification tier runs.
- `.claude/skills/` — troubleshooting skills, such as beads in a worktree.
- `.claude/hooks/` — the Bash and file-write safety hooks wired up in `settings.json`.
````

- [ ] **Step 4: Rewrite the diagram source**

Replace the whole of `docs/workflow-process-flow.drawio` (restored from HEAD in Task 0) with the XML below. It is rebuilt as plain cells: the old file's mermaid-import wrappers (`UserObject` with `mermaidBaseValue`) would no longer match the new labels, so they are dropped. Colours, fonts and the diagram id are kept; edges are orthogonal.

```xml
<mxfile host="Electron">
  <diagram id="r6X1ASLXcBkJzwljNGvy" name="Epic-batch workflow">
    <mxGraphModel dx="0" dy="0" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="0" page="0" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="2" value="0 · Set up&#xa;Create a worktree + branch" style="html=1;whiteSpace=wrap;strokeWidth=1;fillColor=#e8eef7;strokeColor=#4a6fa5;fontColor=#1a1a1a;fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="162" y="37" width="258" height="73" as="geometry" />
        </mxCell>
        <mxCell id="3" value="1 · Spec&#xa;/superpowers:brainstorming&#xa;→ design document" style="html=1;whiteSpace=wrap;strokeWidth=1;fillColor=#e8eef7;strokeColor=#4a6fa5;fontColor=#1a1a1a;fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="146" y="160" width="290" height="93" as="geometry" />
        </mxCell>
        <mxCell id="4" value="2 · Sequence the spec&#xa;/workflow-commands:workflow-planning-sequence&#xa;→ epic + tasks, planning waves, plan depth" style="html=1;whiteSpace=wrap;strokeWidth=1;fillColor=#dce9dc;strokeColor=#4a7a4a;fontColor=#1a1a1a;fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="71" y="303" width="440" height="93" as="geometry" />
        </mxCell>
        <mxCell id="7" value="3 · Write the plans&#xa;/workflow-commands:workflow-writing-plans&#xa;→ a plan or task card per task (wp:approved)" style="html=1;whiteSpace=wrap;strokeWidth=1;fillColor=#dce9dc;strokeColor=#4a7a4a;fontColor=#1a1a1a;fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="71" y="446" width="440" height="93" as="geometry" />
        </mxCell>
        <mxCell id="5" value="Any SPIKE-FIRST&#xa;tasks left to run?" style="rhombus;html=1;strokeWidth=1;whiteSpace=wrap;fillColor=light-dark(#ECECFF,#1f2020);strokeColor=light-dark(#9370DB,#cccccc);fontColor=light-dark(#333333,#cccccc);fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="191" y="589" width="200" height="200" as="geometry" />
        </mxCell>
        <mxCell id="6" value="3a · Run the spikes&#xa;/workflow-commands:workflow-execute-spikes&#xa;→ findings; each closed spike unblocks&#xa;its EXEC-GATED dependents" style="html=1;whiteSpace=wrap;strokeWidth=1;fillColor=#f7edd8;strokeColor=#a5883f;fontColor=#1a1a1a;fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="560" y="632" width="420" height="114" as="geometry" />
        </mxCell>
        <mxCell id="8" value="4 · Order the work&#xa;/workflow-commands:workflow-execution-sequence&#xa;→ execution waves + plan-coverage gate" style="html=1;whiteSpace=wrap;strokeWidth=1;fillColor=#dce9dc;strokeColor=#4a7a4a;fontColor=#1a1a1a;fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="71" y="839" width="440" height="93" as="geometry" />
        </mxCell>
        <mxCell id="9" value="5 · Build it&#xa;/workflow-commands:workflow-execute-plans&#xa;→ ex:done per task" style="html=1;whiteSpace=wrap;strokeWidth=1;fillColor=#dce9dc;strokeColor=#4a7a4a;fontColor=#1a1a1a;fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="71" y="982" width="440" height="93" as="geometry" />
        </mxCell>
        <mxCell id="10" value="Every task in&#xa;the epic done?" style="rhombus;html=1;strokeWidth=1;whiteSpace=wrap;fillColor=light-dark(#ECECFF,#1f2020);strokeColor=light-dark(#9370DB,#cccccc);fontColor=light-dark(#333333,#cccccc);fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="200" y="1125" width="182" height="182" as="geometry" />
        </mxCell>
        <mxCell id="11" value="6 · Ship the epic&#xa;/workflow-commands:workflow-ship-epic&#xa;→ PR opened (sh:pushed)&#xa;→ sh:shipped after merge" style="html=1;whiteSpace=wrap;strokeWidth=1;fillColor=#d8e4f0;strokeColor=#2f5c94;fontColor=#1a1a1a;fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="560" y="1160" width="380" height="112" as="geometry" />
        </mxCell>
        <mxCell id="12" value="Go back to the phase&#xa;the leftover tasks are in:&#xa;unplanned → step 3&#xa;unordered → step 4" style="html=1;whiteSpace=wrap;strokeWidth=1;fillColor=#f5dede;strokeColor=#a34a4a;fontColor=#1a1a1a;fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="172" y="1357" width="238" height="112" as="geometry" />
        </mxCell>
        <mxCell id="13" value="⚠ Context hygiene&#xa;/clear between phases.&#xa;Mid-phase, past roughly 30–50% of the&#xa;context window: ask for a handoff doc,&#xa;/clear, and paste it back." style="html=1;whiteSpace=wrap;strokeWidth=1;fillColor=#fdf6d8;strokeColor=#b09a3c;fontColor=#1a1a1a;fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="560" y="37" width="380" height="131" as="geometry" />
        </mxCell>
        <mxCell id="14" style="edgeStyle=orthogonalEdgeStyle;rounded=1;startArrow=none;endArrow=block;endSize=7;strokeColor=light-dark(#333333,#cccccc);exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="2" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="15" style="edgeStyle=orthogonalEdgeStyle;rounded=1;startArrow=none;endArrow=block;endSize=7;strokeColor=light-dark(#333333,#cccccc);exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="3" target="4">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="16" style="edgeStyle=orthogonalEdgeStyle;rounded=1;startArrow=none;endArrow=block;endSize=7;strokeColor=light-dark(#333333,#cccccc);exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="4" target="7">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="17" style="edgeStyle=orthogonalEdgeStyle;rounded=1;startArrow=none;endArrow=block;endSize=7;strokeColor=light-dark(#333333,#cccccc);exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="7" target="5">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="18" value="yes" style="edgeStyle=orthogonalEdgeStyle;rounded=1;startArrow=none;endArrow=block;endSize=7;strokeColor=light-dark(#333333,#cccccc);html=1;fontSize=16;labelBackgroundColor=light-dark(#E8E8E88D,#2a2a2a8D);fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontColor=light-dark(#333333,#cccccc);exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="5" target="6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="19" value="then re-run step 3: it plans&#xa;the tasks the spikes unblocked" style="edgeStyle=orthogonalEdgeStyle;rounded=1;startArrow=none;endArrow=block;endSize=7;strokeColor=light-dark(#333333,#cccccc);html=1;fontSize=16;labelBackgroundColor=light-dark(#E8E8E88D,#2a2a2a8D);fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontColor=light-dark(#333333,#cccccc);exitX=0.5;exitY=0;entryX=1;entryY=0.5;" edge="1" parent="1" source="6" target="7">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="770" y="492" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="20" value="no" style="edgeStyle=orthogonalEdgeStyle;rounded=1;startArrow=none;endArrow=block;endSize=7;strokeColor=light-dark(#333333,#cccccc);html=1;fontSize=16;labelBackgroundColor=light-dark(#E8E8E88D,#2a2a2a8D);fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontColor=light-dark(#333333,#cccccc);exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="5" target="8">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="21" style="edgeStyle=orthogonalEdgeStyle;rounded=1;startArrow=none;endArrow=block;endSize=7;strokeColor=light-dark(#333333,#cccccc);exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="8" target="9">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="22" style="edgeStyle=orthogonalEdgeStyle;rounded=1;startArrow=none;endArrow=block;endSize=7;strokeColor=light-dark(#333333,#cccccc);exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="9" target="10">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="23" value="no" style="edgeStyle=orthogonalEdgeStyle;rounded=1;startArrow=none;endArrow=block;endSize=7;strokeColor=light-dark(#333333,#cccccc);html=1;fontSize=16;labelBackgroundColor=light-dark(#E8E8E88D,#2a2a2a8D);fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontColor=light-dark(#333333,#cccccc);exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="10" target="12">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="24" style="edgeStyle=orthogonalEdgeStyle;rounded=1;startArrow=none;endArrow=block;endSize=7;strokeColor=light-dark(#333333,#cccccc);exitX=0;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="12" target="7">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="30" y="1413" />
              <mxPoint x="30" y="492" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="25" value="yes" style="edgeStyle=orthogonalEdgeStyle;rounded=1;startArrow=none;endArrow=block;endSize=7;strokeColor=light-dark(#333333,#cccccc);html=1;fontSize=16;labelBackgroundColor=light-dark(#E8E8E88D,#2a2a2a8D);fontFamily=Trebuchet MS,Verdana,Arial,sans-serif;fontColor=light-dark(#333333,#cccccc);exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="10" target="11">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

- [ ] **Step 5: Re-export the PNG with the diagram embedded**

```bash
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -e -s 2 -b 10 -o docs/workflow-process-flow.drawio.png docs/workflow-process-flow.drawio
sips -g pixelWidth -g pixelHeight docs/workflow-process-flow.drawio.png
```

Expected: the export prints `docs/workflow-process-flow.drawio -> docs/workflow-process-flow.drawio.png` (Electron may add log noise), and `sips` reports `pixelWidth: 1951` and `pixelHeight: 2899`. `-e` embeds the diagram, `-s 2 -b 10` matches how the original PNG was produced (it was 1709×3459 at the same scale).

- [ ] **Step 6: Prove the PNG carries the new diagram**

draw.io stores the diagram in a compressed `zTXt` chunk keyed `mxGraphModel`. Decode it and look for the new labels:

```bash
python3 - docs/workflow-process-flow.drawio.png <<'PY'
import sys, zlib, struct, urllib.parse
data = open(sys.argv[1], 'rb').read()
pos, xml = 8, ''
while pos < len(data):
    n, kind = struct.unpack('>I4s', data[pos:pos + 8])
    body = data[pos + 8:pos + 8 + n]
    pos += 12 + n
    if kind == b'zTXt' and body.split(b'\0', 1)[0] == b'mxGraphModel':
        xml = urllib.parse.unquote(zlib.decompress(body.split(b'\0', 1)[1][1:]).decode('latin-1'))
for want in ['/workflow-commands:workflow-writing-plans', 'tasks left to run?', 'PR opened (sh:pushed)', 'sh:shipped after merge', 'plan depth']:
    print(('PASS' if want in xml else 'FAIL') + ': embedded diagram has "' + want + '"')
PY
```

Expected: five `PASS:` lines. (Against the old PNG all five print `FAIL:`.)

- [ ] **Step 7: Look at the rendered diagram**

Open `docs/workflow-process-flow.drawio.png` with the Read tool and confirm, top to bottom: 0 Set up → 1 Spec (`/superpowers:brainstorming`) → 2 Sequence the spec (mentions plan depth) → 3 Write the plans → the diamond "Any SPIKE-FIRST tasks left to run?"; its "yes" arrow goes right to 3a Run the spikes, whose arrow climbs back into step 3 with the label "then re-run step 3: it plans the tasks the spikes unblocked"; its "no" arrow goes down to 4 Order the work → 5 Build it → "Every task in the epic done?"; "yes" goes right to 6 Ship the epic (PR opened (sh:pushed) → sh:shipped after merge); "no" goes down to the red "Go back" box, whose arrow runs up the left edge into step 3. The yellow context note sits top right. No label is clipped and no line crosses a box.

- [ ] **Step 8: Run the check and watch it pass**

```bash
CHECKS="<scratchpad>/sgw-checks"
bash "$CHECKS/check-readme-setup.sh" "$(git rev-parse --show-toplevel)"; echo "exit=$?"
wc -l < README.md
```

Expected: 41 lines starting with `PASS:` (23 for Part A, 18 for Part B: cp without nesting; hooks executable; bd init's own commit; no AGENTS.md or CLAUDE.md; `export.git-add: false`; `no-auto-import: true` on its own line; `sync.remote` recorded; config parses; Dolt remote `origin`; the placeholder grep finds hits; a clean tree after the setup commit; the export written; ignored; the three workflow state files ignored; untracked; nothing staged), no `FAIL:` lines, two `Exported N issues to …` lines that bd prints on stderr (one from its git hook during the setup commit, one from `bd export`), then `exit=0`, then `109`. <!-- Refined: Data Flow -->

#### Part B: `/clear` before the next phase in planning-sequence, writing-plans and execution-sequence

**Files:**
- Modify: `.claude/Commands/workflow-commands/workflow-planning-sequence.md` — Step 7's next steps: `/clear`, then writing-plans.
- Modify: `.claude/Commands/workflow-commands/workflow-writing-plans.md` — Step 7's next steps: `/clear`, then execute-spikes (and this command again) or execution-sequence; execution-sequence is always the next stage.
- Modify: `.claude/Commands/workflow-commands/workflow-execution-sequence.md` — Step 7's next steps: `/clear`, then execute-plans.

**Interfaces:**
- Consumes: the README's epic recipe order (Task 8, other part): planning-sequence → writing-plans → (execute-spikes → writing-plans again) → execution-sequence → execute-plans → ship-epic.
- Produces: Next lines that match the README step for step, each with `/clear` as its own numbered line.

These steps run after Task 1, so command names in the files already read `/workflow-commands:<name>`. Every anchor below avoids the lines Task 1 rewrites, or quotes them in their post-Task-1 form; if an anchor does not match, re-read the file rather than guessing.

- [ ] **Step 1: End planning-sequence with numbered next steps, `/clear` first**

In `.claude/Commands/workflow-commands/workflow-planning-sequence.md`, section `### 7. [main ctx] Handoff — Epic Status & Next-Steps Summary`, replace the passage that begins

```text
State the single next command plainly:
```

and ends

```text
their upstream spikes/tasks are executed.
```

(both ends included) with:

````markdown
State the next steps plainly, with `/clear` as its own step — planning starts
in a fresh context, and the sequence file and beads carry everything it needs:

```
1. /clear
2. /workflow-commands:workflow-writing-plans <epic-id-or-sequence-file-path>
```

and remind the user this first run only drafts the plannable wave(s) — later
waves reappear automatically on a future
`/workflow-commands:workflow-writing-plans` re-run once their upstream
spikes/tasks are executed.
````

- [ ] **Step 2: End writing-plans with numbered next steps, `/clear` first**

In `.claude/Commands/workflow-commands/workflow-writing-plans.md`, section `## Step 7: Epic Status & Next-Steps Summary [main ctx]`, replace the passage that begins

```text
- **Whether execution-sequence will matter**
```

and ends

```text
  until an earlier wave executes, say that plainly and name what's blocking it.
```

(both ends included) with:

````markdown
- **Whether the closure crosses epics** — if any approved task has a cross-epic
  `blocks`-predecessor with no `exec:<slug>` label yet, say that
  `/workflow-commands:workflow-execution-sequence` is required before execution:
  it labels the closure `exec:<slug>`, without which
  `/workflow-commands:workflow-execute-plans` refuses the run. For a
  self-contained epic, say that execution-sequence is still the next stage but
  only confirms plan coverage and the execution order.
- **The next steps**, as numbered lines with `/clear` as its own step before
  the next phase's command (every phase reads what it needs from beads and
  `docs/plans/`, so nothing is lost):
  - An approved spike that has not been executed yet:

    ```
    1. /clear
    2. /workflow-commands:workflow-execute-spikes <epic-id>
    ```

    and say that this command runs again after the spikes, to plan the tasks
    their findings unblock.
  - Otherwise, once the plannable tasks are approved:

    ```
    1. /clear
    2. /workflow-commands:workflow-execution-sequence <epic-id>
    ```

  - If nothing more can happen until an earlier wave executes, say that plainly
    and name what's blocking it.
````

- [ ] **Step 3: End execution-sequence with numbered next steps, `/clear` first**

In `.claude/Commands/workflow-commands/workflow-execution-sequence.md`, section `### 7. [main ctx] Label the closure (if cross-epic) + Epic Status & Next-Steps Summary`, replace the passage that begins

```text
executed. Restate the **execution-wave order**, then hand off with the single
```

and ends

````text
/workflow-commands:workflow-execute-plans <epic-id>
```
````

(both ends included) with:

````markdown
executed. Restate the **execution-wave order**, then hand off with the next
steps, `/clear` first — execution starts in a fresh context, and the plans and
labels carry everything it needs:

```
1. /clear
2. /workflow-commands:workflow-execute-plans <epic-id>
```
````

- [ ] **Step 4: Verify Part B of Task 8**

Run from the repo root:

```bash
d=.claude/Commands/workflow-commands
printf '%s\n' \
  "ps-clear-step=$(grep -cF '1. /clear' "$d/workflow-planning-sequence.md")" \
  "wp-clear-step=$(grep -cF '1. /clear' "$d/workflow-writing-plans.md")" \
  "es-clear-step=$(grep -cF '1. /clear' "$d/workflow-execution-sequence.md")" \
  "ps-single-next-left=$(grep -cF 'State the single next command' "$d/workflow-planning-sequence.md")" \
  "wp-single-next-left=$(grep -cF 'The single next command' "$d/workflow-writing-plans.md")" \
  "es-single-next-left=$(grep -cF 'hand off with the single' "$d/workflow-execution-sequence.md")"
```

Expected output, exactly:

```text
ps-clear-step=1
wp-clear-step=2
es-clear-step=1
ps-single-next-left=0
wp-single-next-left=0
es-single-next-left=0
```

Any other number means a step above was skipped or applied to the wrong passage; re-read that file and fix it before moving on.

#### Part C: `/clear` before each next phase in execute-plans, execute-spikes and ship-epic

**Files:**
- Modify: `.claude/Commands/workflow-commands/workflow-execute-plans.md` — Step 8's closing paragraph becomes a numbered **Next** list.
- Modify: `.claude/Commands/workflow-commands/workflow-execute-spikes.md` — Step 7's closing command becomes `/clear` then writing-plans.
- Modify: `.claude/Commands/workflow-commands/workflow-ship-epic.md` — Step 7's closing paragraphs become per-run numbered Next lists.

**Interfaces:**
- Consumes: Task 7's two-run ship flow; the router's *Recommending What's Next — Batch Beats Single-Task* section (Task 4); planning-sequence's `--epic <epic-id>` argument.
- Produces: the three commands' Next lists, which this task's README epic recipe mirrors.

- [ ] **Step 1: execute-plans — Step 8 Next: numbered steps, `/clear` before each next phase**

In `.claude/Commands/workflow-commands/workflow-execute-plans.md`, section `## Step 8: Epic Status & Next-Steps Summary [main ctx]`, replace the passage that begins `State the single next command plainly` and ends `possibility.` with:

```markdown
**Next.** Close the report with the next steps as a short numbered list. `/clear`
is its own step before each next-phase command, and the list holds only what
applies now — never a menu of every possibility:

- **Nothing left** (the ship-recommendation gate below passes):
  1. `/clear`
  2. `/workflow-commands:workflow-ship-epic <epic-id>` — opens the epic's PR and
     closes its tasks; it stops at its own confirmation gate first.
  3. Merge the PR.
  4. `/workflow-commands:workflow-ship-epic <epic-id>` again — confirms the merge
     and marks the epic shipped.
- **Deferred tasks this wave unblocked:**
  1. `/clear`
  2. `/workflow-commands:workflow-writing-plans <epic-id>` — plans them.
- **Refused at Step 0b:**
  1. `/clear`
  2. `/workflow-commands:workflow-writing-plans <epic-id>` — finishes planning.
- **A blocked bug, an open smoke gate, or an ops step:** the step that finishes
  it, as the gate below names it. Once it is done:
  1. `/clear`
  2. `/workflow-commands:workflow-execute-plans <epic-id>` — resumes from the
     `ex:*` labels.
```

- [ ] **Step 2: execute-spikes — Step 7 Next: `/clear`, then writing-plans again**

In `.claude/Commands/workflow-commands/workflow-execute-spikes.md`, section `## Step 7: Epic Status & Next-Steps Summary [main ctx]`, replace the passage that begins `State the single next command plainly:` and ends `and mention re-running this command instead if a further spike layer is next.` with:

````markdown
Close with the next steps as a numbered list, `/clear` as its own step before the
next phase's command. Normally:

```
1. /clear
2. /workflow-commands:workflow-writing-plans <epic-id>
```

That re-run plans every `EXEC-GATED` task these findings unblocked. When the next
layer of spikes is already approved and was only waiting on the spikes that just
closed, run this command again first instead: `/clear`, then
`/workflow-commands:workflow-execute-spikes <epic-id>`.
````

- [ ] **Step 3: ship-epic — Step 7 Next: merge, re-run, then `/clear` before the next epic**

In `.claude/Commands/workflow-commands/workflow-ship-epic.md`, section `## Step 7: Report — Epic Status & Next-Steps Summary [main ctx]`, replace the passage that begins `Show what is now unblocked, the branch / PR URL,` and ends `or nothing further if no open epics remain.` with:

```markdown
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
```

- [ ] **Step 4: Verify this part's edits landed**

Run from the repo root:

```bash
C=.claude/Commands/workflow-commands
while IFS='|' read -r want f s; do
  got=$(grep -c -F -- "$s" "$C/$f")
  if [ "$got" = "$want" ]; then echo "ok   $f: $s"; else echo "MISMATCH (got $got, want $want)  $f: $s"; fi
done <<'EOF'
0|workflow-execute-plans.md|State the single next command plainly
1|workflow-execute-plans.md|**Next.** Close the report with the next steps as a short numbered list.
0|workflow-execute-spikes.md|State the single next command plainly
1|workflow-execute-spikes.md|2. /workflow-commands:workflow-writing-plans <epic-id>
0|workflow-ship-epic.md|and state the single next command
1|workflow-ship-epic.md|Close with the next steps as a numbered list in which `/clear` is its own
EOF
```

Expected: 6 lines, every one starting with `ok`. A `MISMATCH` line names the file and phrase whose edit is missing or duplicated.

- [ ] **Finish 1: Confirm this task's change set**

```bash
git status --short
```
Expected: exactly the files in this task's **Files** list above (`M` modified, `??` new, `D` deleted), and nothing else — apart from a `?? .claude/worktrees/` line if that local folder holds a worktree, which is never staged. Anything else means a step touched the wrong file: find it with `git diff <path>` before staging.

- [ ] **Finish 2: Commit W8**

```bash
git add -- \
  "README.md" \
  "docs/workflow-process-flow.drawio" \
  "docs/workflow-process-flow.drawio.png" \
  ".claude/Commands/workflow-commands/workflow-planning-sequence.md" \
  ".claude/Commands/workflow-commands/workflow-writing-plans.md" \
  ".claude/Commands/workflow-commands/workflow-execution-sequence.md" \
  ".claude/Commands/workflow-commands/workflow-execute-plans.md" \
  ".claude/Commands/workflow-commands/workflow-execute-spikes.md" \
  ".claude/Commands/workflow-commands/workflow-ship-epic.md" && \
git diff --cached --stat && git commit -F- <<'EOF'
docs: short README recipe, updated process diagram, /clear between phases

Rewrite the README as numbered, verified commands with each /clear as its own
step; fix the spike order and the two-run ship in the diagram; end every batch
command with numbered Next steps.

<attribution trailer>
EOF
```
Expected: the stat lists only this task's files, then the commit summary line. Replace `<attribution trailer>` with the attribution lines from your session's system reminder before running it.

- [ ] **Finish 3: Record the commit on the W8 bead**

```bash
source .beads/sgw-ids.env && bd update "$W8" --append-notes "Landed in $(git rev-parse --short HEAD): docs: short README recipe, updated process diagram, /clear between phases" && bd show "$W8" | sed -n '1,20p'
```
Expected: the notes end with the "Landed in" line and the status is still `IN_PROGRESS` — all eight workstream beads close together when the PR opens (Task 9).

---

### Task 9: Final reference sweep, verification gate, and ship

Spec: §1 success criteria, §10 (ship, sync marker), §11 (reference sweep, workflow gate).

**Files:**
- Modify: none, unless a check below finds a defect; then fix it in the file that owns it, as one extra commit (Step 4).

**Interfaces:**
- Consumes: every check script written by Tasks 1–8; `.beads/sgw-ids.env`; the router's *Completion Report* section (Task 4); `/workflow-commands:beads-post-execution` with Step 2a (Task 2); `/workflow-commands:beads-ship-task` with Step 6.5 (Task 6).
- Produces: the pull request, with "Synced with the global workflow as of 2026-10-02." in its description; the eight workstream beads and the epic closed.

- [ ] **Step 1: Write the final reference check**

It checks spec §11's reference sweep on the whole tree: every `workflow-commands:<name>`, plugin skill, backticked `.md` path, agent, local skill, hook script and router-section citation mentioned under `.claude/` and in the README exists; nothing owner-specific leaked in; P04, P05 and the tiers' phase counts are gone. (Bare `/workflow-…` names are covered by Task 1's `check-w1-names.sh`, re-run in Step 2.)

Create `<scratchpad>/sgw-checks/check-references.sh` with the Write tool, not a shell heredoc (see Global Constraints), with exactly this content:
```bash
#!/usr/bin/env bash
# check-references.sh <repo-root>
# Final-tree reference sweep for the global-workflow sync (plan Task 9).
# Everything mentioned under .claude/ and in README.md must exist: workflow-commands
# skills, plugin skills, rule/command files, agents, the local skill, hook scripts and
# router sections. No owner-specific text may leak in, and the retired phases must be
# gone. Prints one PASS/FAIL line per check (with offending hits) and exits 1 on any FAIL.
set -u
REPO="${1:?usage: check-references.sh <repo-root>}"
cd "$REPO" || exit 2
CMD=.claude/Commands/workflow-commands
ROUTER=".claude/rules/0_Beads x Superpowers/beads-workflow-router.md"
PLUG="$HOME/.claude/plugins/cache"
fail=0
report() {  # report <label> <hits-text>
  if [ -z "$2" ]; then printf 'PASS: %s\n' "$1"
  else printf 'FAIL: %s\n%s\n' "$1" "$(printf '%s\n' "$2" | sed 's/^/    /')"; fail=1; fi
}
# scan <ERE> [grep flags…] → "file:line:match" across .claude/ (minus worktrees) + README.md
scan() {
  local re="$1"; shift
  { find .claude -type f \( -name '*.md' -o -name '*.sh' -o -name '*.json' \) \
      -not -path '.claude/worktrees/*' -print0; printf '%s\0' README.md; } |
    xargs -0 grep -HnoE "$@" -e "$re" 2>/dev/null
}
# scanl <ERE> [grep flags…] → "file:line:full line" (for allowlist filtering by context)
scanl() {
  local re="$1"; shift
  { find .claude -type f \( -name '*.md' -o -name '*.sh' -o -name '*.json' \) \
      -not -path '.claude/worktrees/*' -print0; printf '%s\0' README.md; } |
    xargs -0 grep -HnE "$@" -e "$re" 2>/dev/null
}

# 1. Every workflow-commands:<name> resolves to a command file.
hits=""
while IFS= read -r line; do
  tok="${line##*:workflow-commands:}"; tok="${tok%.}"
  case "$tok" in *-|debug|debug:*) continue ;; esac   # "workflow-*" patterns; illustrative sub-namespace
  [ -f "$CMD/${tok//://}.md" ] || hits+="${line%%:*}: workflow-commands:$tok"$'\n'
done < <(scan 'workflow-commands:[A-Za-z0-9_.-]+(:[A-Za-z0-9_.-]+)*(\[[A-Z]+\])?')
report "workflow-commands:<name> references resolve to command files" "$(printf '%s' "$hits" | sort -u)"

# 2. Every plugin skill reference exists in the installed plugin it names.
hits=""
while IFS= read -r line; do
  m="${line#*:}"; m="${m#*:}"; ns="${m%%:*}"; n="${m#*:}"
  ok=1
  case "$ns" in
    superpowers)     compgen -G "$PLUG/claude-plugins-official/superpowers/*/skills/$n/SKILL.md" >/dev/null || ok=0 ;;
    beads)           [ "$n" = beads ] || compgen -G "$PLUG/beads-marketplace/beads/*/skills/beads/commands/$n.md" >/dev/null || ok=0 ;;
    commit-commands) compgen -G "$PLUG/claude-plugins-official/commit-commands/*/commands/$n.md" >/dev/null || ok=0 ;;
    codex)           compgen -G "$PLUG/openai-codex/codex/*/commands/$n.md" >/dev/null \
                       || compgen -G "$PLUG/openai-codex/codex/*/skills/$n/SKILL.md" >/dev/null || ok=0 ;;
  esac
  [ "$ok" = 1 ] || hits+="${line%%:*}: $ns:$n"$'\n'
done < <(scan '\b(superpowers|beads|commit-commands|codex):[a-z0-9_-]+[a-z0-9]')
report "plugin skill references exist in the installed plugins" "$(printf '%s' "$hits" | sort -u)"

# 3. Every backticked .md path that names a real file resolves (placeholders and
#    generated-artifact names are skipped).
hits=""
while IFS= read -r line; do
  ref="${line#*:}"; ref="${ref#*:}"; ref="${ref#\`}"; ref="${ref%\`}"
  case "$ref" in
    *'<'*|*'*'*|*'...'*|*YYYY*|.md) continue ;;
  esac
  base="${ref##*/}"
  case "$base" in
    refinements.md|findings.md|cross-plan-verification.md|PROGRESS.md|SKILL.md|CLAUDE.md|AGENTS.md|README.md|MEMORY.md) continue ;;
    "Python Verification Quick.md"|"Beads Start Task.md"|2026-01-old-thing.md) continue ;;  # deliberate wrong-name examples
  esac
  if [[ "$ref" == .claude/* || "$ref" == docs/* ]]; then
    [ -f "$ref" ] || hits+="${line%%:*}: $ref"$'\n'
  else
    [ -n "$(find .claude docs -name "$base" -not -path '.claude/worktrees/*' -print -quit 2>/dev/null)" ] \
      || hits+="${line%%:*}: $ref"$'\n'
  fi
done < <(scan '`[^`]*\.md`')
report "backticked .md paths resolve" "$(printf '%s' "$hits" | sort -u)"

# 4. Router section citations ("the router's *<heading>*", even when wrapped across
#    lines) name a heading the router has; no old "Hard Stop: …" heading names remain.
hits=$(
  { find .claude -type f -name '*.md' -not -path '.claude/worktrees/*' -print0; printf '%s\0' README.md; } |
    xargs -0 perl -0777 -ne 'while (/router(?:\x27s)?\s+\*([^*]+)\*/g) { my $s = $1; $s =~ s/\n[ \t]*>[ \t]?/ /g; $s =~ s/\s+/ /g; print "$ARGV\t$s\n" }' |
    while IFS=$'\t' read -r f sec; do
      grep -qxF "## $sec" "$ROUTER" || printf '%s: router section "%s"\n' "$f" "$sec"
    done)
old=$(scanl 'Hard Stop: [A-Z][A-Za-z]' | grep -vF "$ROUTER:" | cut -c1-200)
report "router section citations resolve" "$(printf '%s\n%s' "$hits" "$old" | sed '/^$/d' | sort -u)"

# 5. Agents named by subagent_type exist; the local skill and hook scripts exist.
hits=""
while IFS= read -r line; do
  a="${line##*subagent_type: \"}"; a="${a%\"}"
  [ -f ".claude/agents/$a.md" ] || hits+="${line%%:*}: agent $a"$'\n'
done < <(scan 'subagent_type: "[a-z0-9-]+"')
for s in .claude/skills/*/; do
  [ -d "$s" ] || continue
  n=$(basename "$s")
  grep -q "^name: $n\$" "$s/SKILL.md" 2>/dev/null || hits+="$s: SKILL.md missing or its name: is not $n"$'\n'
done
if [ -n "$(scan 'beads-worktree-troubleshooting')" ] && [ ! -f .claude/skills/beads-worktree-troubleshooting/SKILL.md ]; then
  hits+="beads-worktree-troubleshooting is cited but .claude/skills/beads-worktree-troubleshooting/SKILL.md is missing"$'\n'
fi
while IFS= read -r h; do
  f="${h#\"\$CLAUDE_PROJECT_DIR\"/}"
  [ -x "$f" ] || hits+=".claude/settings.json: hook $f missing or not executable"$'\n'
done < <(jq -r '.. | .command? // empty' .claude/settings.json)
report "agents, local skills and hook scripts exist" "$(printf '%s' "$hits" | sort -u)"

# 6. No owner-specific or platform leaks (spec §11). The owner's private terms come from
#    private-terms.txt next to this script (one extended regex per line; never committed).
#    Generic "(Jira, Linear …)" tracker examples, prohibitions that quote a versioned
#    model id, and the untouched methodology file's "no Python/Flutter/repo assumptions"
#    line are allowed.
TERMS="$(cd "$(dirname "$0")" && pwd)/private-terms.txt"
PRIV=$(grep -v '^[[:space:]]*$' "$TERMS" 2>/dev/null | paste -sd'|' -)
leaks=$(
  { if [ -n "$PRIV" ]; then scanl "$PRIV" -i; else echo "private term list missing or empty: $TERMS"; fi
    scanl '127\.0\.0\.1|~/\.claude/rules'
    scanl 'Flutter|Dart' -w | grep -vF 'no Python/Flutter/repo assumptions'
    scanl 'dart '
    scanl 'Jira' | grep -vE '\(Jira, Linear'
    scanl 'Opus-4\.8|Sonnet-5|opus-4\.8|claude-(opus|sonnet|haiku)-[0-9]' | grep -vE 'never|not an enum|not enum|is not'
  } | cut -c1-200 | sort -u)
report "no owner-specific or platform leaks" "$leaks"

# 7. Retired phases are gone: no P04/P05 files or mentions and no Architecture Score
#    anywhere; no phase counts in the tiers, post-execution, the router or the README
#    (tdd-test-writer's own "8-phase" wording is untouched by design).
ret=$(
  { ls "$CMD"/P04-* "$CMD"/P05-* 2>/dev/null | sed 's/$/: file still exists/'
    scan 'P04|P05|Architecture Score'
    grep -HnoE '[0-9]+-phase\b|[0-9]+ phases' "$CMD"/python-verification-*.md \
      "$CMD"/beads-post-execution.md "$ROUTER" README.md 2>/dev/null
  } | cut -c1-200 | sort -u)
report "retired phases (P04, P05, phase counts) are gone" "$ret"

exit "$fail"
```

- [ ] **Step 2: Run every behaviour check on the final tree**

Run:
```bash
CHECKS="<scratchpad>/sgw-checks"; R="$(git rev-parse --show-toplevel)"; rc=0
for c in check-w1-names check-changed-set check-ruff-scope check-phase6-gate check-codex-companion check-router check-dolt-guard check-ship-merge check-validate-bash check-readme-setup check-references; do
  echo "=== $c"; if [ -f "$CHECKS/$c.sh" ]; then bash "$CHECKS/$c.sh" "$R" || rc=1; else echo "MISSING: $c.sh"; rc=1; fi
done; echo "overall rc=$rc"
```
Expected: no script prints a `FAIL:` or `MISSING:` line (some also echo the output of the bash they test), and the last line is `overall rc=0`. Each check that runs `bd` does so only in its own scratch repos, and the loop runs them one at a time.

If a script is `MISSING` (this is a new session, so the scratchpad changed), re-create it by re-running the step that writes it, then run this step again:
- `check-w1-names.sh` — Task 1 Step 1
- `check-changed-set.sh` — Task 2 Part A Step 1
- `check-ruff-scope.sh` — Task 2 Part A Step 2
- `check-phase6-gate.sh` — Task 3 Part B Step 1
- `check-codex-companion.sh` — Task 3 Part B Step 3
- `check-router.sh` — Task 4 Part A Step 1
- `check-dolt-guard.sh` — Task 6 Part D Step 1
- `check-ship-merge.sh` — Task 7 Part C Step 1
- `check-validate-bash.sh` — Task 7 Part D Step 1
- `check-readme-setup.sh` — Task 8 Part A Step 1
- `check-references.sh` — Task 9 Step 1
- `private-terms.txt` (read by `check-router.sh` and `check-references.sh`) — Task 0 Step 7, from the owner's private memory note

- [ ] **Step 3: Confirm the commit list and a clean tree**

Run:
```bash
git log --oneline master..HEAD && git status --short
```
Expected: exactly ten commits, newest first — W8, W7, W6, W5, W4, W3, W2, W1, the plan, the spec (eleven if Step 4 added a fix commit) — and `git status --short` prints nothing (or only `?? .claude/worktrees/`, if that local folder holds a worktree).

- [ ] **Step 4: Fix anything a check found, as one commit**

Skip this step when Step 2 ended with `overall rc=0`. Otherwise fix each failure in the file that owns it, following the owning task's text, and re-run Step 2 until it ends with `overall rc=0`. Then stage the fixed files by their quoted paths and commit once:
```bash
git diff --stat && git add <the fixed files, quoted> && git diff --cached --stat && git commit -F- <<'EOF'
chore(workflow): fix findings from the final reference sweep

<one line per finding: file, what was wrong, what changed>

<attribution trailer>
EOF
```

- [ ] **Step 5: Run the verification gate**

The router requires post-execution verification after every implementation path. Invoke `/workflow-commands:beads-post-execution`. Its Step 2a records the branch's whole changed set, which is far over 200 lines, so it selects `/workflow-commands:python-verification-full`. This template has no Python code: ruff, mypy, pytest and the Python review agents have nothing to check, and the report should say so plainly — Step 2's behaviour checks are the real evidence (spec §11, "Workflow gate"). The Codex pass still reviews the branch; weigh its findings with `superpowers:receiving-code-review`, fix the real ones the way Step 4 does, and list the rest in the PR description.

Expected: the tier completes and `.beads/.verification-done` exists:
```bash
test -f .beads/.verification-done && cat .beads/.verification-done
```

- [ ] **Step 6: Completion report, then wait for "ship it"**

Print the router's *Completion Report*: the Epic Status Table for `$EPIC`, read this turn from `source .beads/sgw-ids.env && bd list --parent "$EPIC" --all -n 0 --json`; what landed, per workstream; what is left (nothing, or the owner-review items); and the next step, `/workflow-commands:beads-ship-task`. Opening a PR is outward-facing, so wait for the owner's "ship it".

- [ ] **Step 7: Ship — one PR, then close the beads**

On "ship it", invoke `/workflow-commands:beads-ship-task` and follow it end to end. Specifics for this PR:
- Step 0 finds the marker from Step 5.
- Push the branch with `git push -u origin chore/sync-global-workflow-2026-10` and open the PR to `master` through `commit-commands:commit-push-pr`. PR description: a Summary with one short paragraph per workstream (W1–W8); Test Results listing each behaviour check from Step 2 with its PASS count, plus the verification tier's result; Beads listing `$EPIC` and `$W1`–`$W8`; and this exact line: `Synced with the global workflow as of 2026-10-02.`
- Close the beads when the PR opens (spec §3 decision 4 — the single-task lane's closure is unchanged), in one Bash call:
  ```bash
  source .beads/sgw-ids.env && PR=$(gh pr view --json url -q .url) && \
  for w in "$W1" "$W2" "$W3" "$W4" "$W5" "$W6" "$W7" "$W8"; do bd close "$w" --reason "Shipped in $PR"; done && \
  bd close "$EPIC" --reason "All eight workstreams shipped in $PR" && bd list --parent "$EPIC" --all -n 0 && bd show "$EPIC" | head -6
  ```
  Expected: all eight beads and the epic read `closed`.
- Step 6.5 runs `bd dolt push`; this stealth store has no Dolt remote, so it prints the one-line skip and continues.
- After the owner merges the PR, ship-task's Step 4 cleans up the branch.

---

## Refinement Decisions

Decisions from plan refinement Q&A on 2026-10-02. The owner chose questions 1 and 2, then accepted the recommended option for every remaining question (3–8) without seeing each one; any of them can still be changed.

| # | Category | Tier | Decision | Rationale |
|---|----------|------|----------|-----------|
| 1 | Data Flow | Critical | README setup step 5 also ignores `.session-state.json`, `.workflow-step` and `.verification-done` (alongside `issues.jsonl`); `check-readme-setup.sh` asserts all three. | "Ship it" stages `.beads/` and commits before the marker is cleared, so a committed `.verification-done` would let another clone pass the ship gate unverified; the files also made the tree look dirty to the Codex pass. Chosen by the owner. |
| 2 | Architecture | Critical | The always-loaded `verification-write-scope.md` keeps only the policy (207 → 63 lines). The two runnable blocks move to `.claude/Commands/workflow-commands/references/scoped-ruff.md` (Task 2 Part A Step 4b), which P02 and the tiers run unchanged. Phase 12 adds the test files it creates to `modified_files` instead of passing file lists. | Keeps about 150 lines of code out of every session's context while keeping one canonical copy. It also fixes a mismatch found while applying this: the full tier passed file lists to blocks that read the changed set themselves. Chosen by the owner (confidence was CLOSE). |
| 3 | Testing Strategy | Recommended | Keep the behaviour checks out of the repo, as the spec's fixed file map says. | This plan lives permanently in `docs/plans/` and carries every script verbatim, so the next sync can re-extract them; committed copies would be tied to this sync's specific edits, and the reference sweep's leak list names private projects. Accepted recommendation. |
| 4 | Scope Control | Recommended | Accept the additions beyond the spec listed below, as one batch. | Each closes a gap found while planning — a trigger with no check behind it, a real auto-allow hole, a `bd init` that commits, an untestable merge check — and none changes the spec's direction. Accepted recommendation. |
| 5 | Integration Points | Recommended | Keep the Codex plugin in the README setup (as the spec says), plus one sentence saying only the full tier's adversarial review uses it. | Full-tier Phase 8.7 needs it and `settings.json` enables it; the note tells a reader exactly what skipping it costs, which answers why it was once removed from the README. Accepted recommendation. |
| 6 | Edge Cases | Recommended | Keep `no-auto-import: true` in the setup, with `beads.md` stating that beads 1.0.4 does not read it and that the untracked export is the real protection. | It mirrors the owner's setup, costs nothing, and would protect if a later beads release honours the key; the honest note stops anyone relying on it. Accepted recommendation. |
| 7 | Edge Cases | Nice-to-have | Keep the router's `smoke:passed` rule and add that no command writes it (execute-plans moves a smoked task straight to `ex:done`; the flag appears only when someone records a smoke by hand). | The spec keeps the rule; saying who writes the flag stops a reader hunting for a command that sets it. Accepted recommendation. |
| 8 | File Organization | Nice-to-have | The global-workflow snapshot stays an ask-first step (Task 0 Step 8), now noting that no global file had changed by refinement time. | It writes outside the repo, so it waits for an explicit yes rather than a blanket acceptance; taking it soon keeps it the exact base for the next sync. Accepted recommendation. |

**Decision 4 — the additions beyond the spec, accepted as a batch:**

- P14 keeps its trigger list identical to the two tiers' Phase 14 gate and gains a `yaml.load` example and a database-authorization check, so every trigger has a check behind it; `.env` files and `src/**/http/**` are triggers in all three lists.
- The standard tier's bug scan keeps a "swallowed errors" class (standard runs no agents); the hotfix trigger reads "Bug scan (Phase 7 in full, Phase 3 in standard)".
- `validate-bash.sh` also withholds the auto-allow for `&`, `<(`, `>(` and `>`.
- The README setup starts a setup branch and ends with a PR (8 steps), and uses `bd init --skip-agents`, because a plain `bd init` commits to the current branch and writes `AGENTS.md` and `CLAUDE.md`.
- writing-plans' Next always routes through execution-sequence; its temporary apply branches are named `chore/wp-apply-<task-id>-<n>`; a re-classification replaces a task's `depth:*` label.
- Extra checks and snippets: `check-ship-merge.sh` (snippet `merge-check`) and `codex-scope`; ship-epic records the PR line in the epic's notes and handles a PR closed without merging; both Step 6.5s refresh the readable export.
- Small fixes: export-progress's duplicate step number; the router's "format" route limited to the changed set; skill-usage's non-existent `commit-push` example; the router check's length band widened to 520–600.

Also changed during refinement, with no decision needed: Task 0 Step 6 now merges into `.beads/.session-state.json` instead of overwriting it, so the refinement record written before Task 0 survives.
