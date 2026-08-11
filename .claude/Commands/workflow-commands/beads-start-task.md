---
description: Start a Beads task - mark in_progress, create branch, initialize session state
---

# Start Beads Task

When the user starts a task, execute these steps in order:

## Step 0: Pull Latest Beads (team sync)
Before anything else, sync the beads store so you start from the team's latest state:
```bash
git pull            # default setup: beads travels as issues.jsonl in git
# bd dolt pull      # Dolt-remote setup: beads is a separate channel
```
If a beads pull is rejected as diverged, do **not** `--force` — coordinate or re-pull.

## Step 1: Mark Task In Progress
- Run `bd update <id> --status=in_progress` (use `beads:update` skill)

## Step 2: Initialize Session State
Create/reset `.beads/.session-state.json` (include `task_id` so the verification
marker can record which task it covers):
```json
{
  "task_id": "<id>",
  "task_requirements": "",
  "plan_created": false,
  "plan_file": "",
  "modified_files": [],
  "total_lines_changed": 0
}
```

Also clear any stale verification marker from a previous task so it cannot pass
the ship gate (router *Hard Stop: Verification Before Ship / "Done"*):
```bash
rm -f .beads/.verification-done
```

## Step 3: External Tracker Key (optional)

**Skip this step unless your project mirrors Beads to an external tracker**
(Jira, Linear, etc.). Beads is always the source of truth; a tracker key is only
used to make the branch name greppable from that tracker.

If you do mirror: resolve the task's tracker key from whatever mapping your
mirror maintains, and carry it into the branch name in Step 4. If no key
resolves, create the branch without one and say so — never block on it.

## Step 4: Create or Switch to Feature Branch

Before creating anything, **scan existing branches for a match**. Resumable
tasks (paused multi-phase work, hotfix-interrupted work, tasks where Phase
1 already merged but the branch is parked awaiting downstream deps) often
already have a branch — checking it out is correct; creating a duplicate
silently splits the work in two and is destructive.

### Step 4a — Scan for an existing branch

Run:
```bash
git branch --list 'feat/*' 'fix/*' 'refactor/*' 'exp/*' 'hotfix/*' 'chore/*'
```

Match against the current task using these signals (in priority order):
1. **Tracker key match:** branch name contains the key resolved in Step 3
   (e.g. key `AB-17` → matches `feat/AB-17-...`).
2. **Beads ID match:** branch name contains the task ID slug — both the full
   form (`<prefix>-m8d9`) and the short form (`m8d9`, the suffix after the
   project prefix). A task `<prefix>-m8d9.4` matches an unrelated-looking
   branch name ONLY if the task notes / `bd show` output reference that branch;
   otherwise check signal 3.
3. **Title slug match:** branch slug contains **3+ consecutive kebab-case
   tokens** from the task title (after normalizing to lowercase). Example:
   task title "Response cache TTL expiry sweep" → tokens
   `response cache ttl expiry sweep` → matches `feat/response-cache-ttl`.
4. **Notes-recorded branch:** run `bd show <id>` and grep the output for
   branch-prefix strings (`ui/`, `fix/`, `backend/`, `stt/`, …). Multi-phase
   tasks (especially ones where Phase 1 already shipped) often record the
   branch name in notes.

**Action on match:**

- **Exactly one match** → checkout that branch and skip directly to
  Step 5:
  ```bash
  git checkout <existing-branch>
  ```
  Confirm to the user:
  > 🔁 Resuming task on existing branch: `<existing-branch>`

- **Multiple matches** → list them and ask the user which to use. Do NOT
  pick one silently.

- **No match** → proceed to Step 4b.

### Step 4b — Branch-state safety check (when no match found)

If you are **not on the trunk** (`master` / `main`) AND no existing branch
matched in Step 4a, **stop and ask the user before doing anything**:

> ⚠️ Current branch `<current-branch>` does not match task
> `<task-id>`. I found no existing branch for this task.
>
> Options:
> 1. Checkout the trunk and create a new feature branch for this task.
> 2. Stay on `<current-branch>` and piggyback this task's commits onto
>    that branch (only correct if the work genuinely belongs together —
>    uncommon).
> 3. Cancel — let me sort out the branch state manually first.

Do NOT silently leave the user on a mismatched branch and start writing
code there.

### Step 4c — Create a new branch

If on the trunk and no existing branch matched, use a `Git Best Practices/Git Best Practices.md`
prefix:

| Task area / type | Branch prefix |
|---|---|
| New behavior | `feat/` |
| `bug` | `fix/` |
| Internal restructuring, no behavior change | `refactor/` |
| Spike / throwaway prototype | `exp/` |
| Emergency fix | `hotfix/` |
| Tooling, CI, `.claude/` rules, docs | `chore/` |

Branch name = `<prefix>/[tracker-key-]kebab-case-description`.
Examples: `feat/response-cache-ttl`, `fix/null-guard-on-empty-payload`,
`chore/workflow-router-refresh`.

## Step 5: Update Workflow Step
```bash
echo "Starting Work" > .beads/.workflow-step
```

## Step 6: Confirm

With a tracker key:
> ✅ Marked **bd-xxxx "[Task Title]"** as in_progress.
> 🌿 Branch: `feat/AB-17-task-title-kebab`
> 🔗 Tracker: AB-17

Without a tracker key:
> ✅ Marked **bd-xxxx "[Task Title]"** as in_progress.
> 🌿 Branch: `feat/task-title-kebab`

## Step 7: Check for Plan
- Search `docs/plans/` for an existing plan matching the task (by task ID, title keywords, or related epic)
- If found → offer:
  > Found existing plan: `docs/plans/[filename]`
  > 1. **Use existing plan** — review and execute this plan
  > 2. **Write new plan** — create a fresh plan with `superpowers:writing-plans`
- If not found → ask for additional requirements, then start planning

**IMPORTANT:** When writing a new plan, invoke `superpowers:writing-plans` DIRECTLY.
Do NOT invoke `superpowers:brainstorming` first — brainstorming is not needed here
because the Beads task already defines the scope. Skip brainstorming and go straight
to plan writing. Save the plan under `docs/plans/` (per `protect_plans_and_commit_all.md`).

---

## "What's Ready?" Scoping Logic

When the user asks "What's ready?" or "What should I work on?":
1. Run `bd list --status=in_progress --type=epic` to find the active epic
2. Run `bd list --status=open --parent=<epic-id>` for tasks within that epic
3. Only fall back to `bd ready` if NO epic is in_progress — tell the user: "No epic is in progress — showing all unblocked tasks."
