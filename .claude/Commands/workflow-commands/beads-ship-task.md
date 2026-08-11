---
description: Ship a completed task - commit, push the feature branch, close the Beads task, check epic completion
---

# Ship Beads Task

Single-repo workflow. There is no multi-repo hub (no `bd repo sync`). Every
change reaches the trunk (`master` / `main`) through a **PR** — see
`Git Best Practices/no-direct-push-to-master.md`. If you mirror Beads to an
external tracker, wire it as a post-`bd close` hook rather than a step here;
Beads stays the source of truth.

## Step 0: Verification Gate (HARD STOP)

**Refuse to ship until verification has run this session** — see the router's
*Hard Stop: Verification Before Ship / "Done"*. Check for the marker a
`python-verification-{level}` skill writes on pass:

```bash
test -f .beads/.verification-done && cat .beads/.verification-done || echo "NO VERIFICATION MARKER"
```

- **Marker present** → proceed to Step 1.
- **Marker absent** → STOP. Do not commit. Tell the user verification has not run
  and invoke `workflow-commands:beads-post-execution` first (it detects the level
  and runs the matching `python-verification-{quick,standard,full}` skill, which
  writes the marker). Ad-hoc `pytest`/smoke does NOT satisfy this — only the named
  skill writes the marker.
- **Explicit bypass only:** proceed without the marker ONLY if the user gave a
  real-time instruction naming the skip ("skip verification", "I'm confident, ship
  it"). Record the bypass in the commit/PR body. Claude's own "it's a tiny change"
  is NOT a valid bypass.

> Fan-out (epic-batch) lane: the equivalent gate is the per-task `ex:qa:<level>`
> label enforced by `workflow-execute-plans` — this Step 0 is the single-task lane's
> analog.

## Step 1: Update Workflow Step
```bash
echo "Committing" > .beads/.workflow-step
```

## Step 2: Commit and Push the Feature Branch
- **Never commit or push directly to `master` / `main`** — see
  `Git Best Practices/no-direct-push-to-master.md`. Commit on the feature branch.
- Stage explicitly (never `git add -A`) per `Git Best Practices/protect_plans_and_commit_all.md`, then commit and push the branch.
  - Use TDD commit labels when applicable: `RED:` / `GREEN:`.
- Ship = commit + `git push -u origin <branch>`, then open the PR in Step 3.

## Step 3: Open the PR
Per `Git Best Practices/no-direct-push-to-master.md`, **all changes reach the
trunk through a PR** — there is no local-merge option. Invoke
`commit-commands:commit-push-pr`, using the PR body format below.

### PR Description Format

Gather this before creating the PR:

**Summary:** A thorough technical summary of the changes. Group by component/layer if the change spans multiple areas. Explain the *what* and *why*, not just file names.

**Test Results:** Test counts (passed/failed), pre-existing failures noted separately, number of new tests added, and any manual verification performed. Note the `RED:`/`GREEN:` commits where TDD applied.

**Beads:** The epic ID and all task IDs in this PR. Use `beads:show` on the current task to get the epic and task IDs.

Example PR body:

```markdown
## Summary
Add a per-entry TTL to the response cache so stale entries expire instead of
being served indefinitely.

**Cache layer:** `src/<your_package>/cache.py` — added `ttl_seconds` to `put()`,
an expiry check in `get()`, and a metrics counter for TTL evictions.

**Config:** `src/<your_package>/config.py` — new `cache_ttl_seconds` setting
(default 3600).

## Test Results
- 642 passed (2 pre-existing failures), 9 new tests
- RED/GREEN commits present for the cache change
- Manual verification: HIT/MISS behavior confirmed against a local run

## Beads
- Epic: `<epic-id>`
- Tasks: `<task-id>` (TTL), `<task-id>` (config)
```

## Step 4: Branch Cleanup (after the PR is merged)
1. `gh pr view <number> --json headRefName -q .headRefName` then `git push origin --delete <branch>`
   - If the PR was merged with `gh pr merge --delete-branch`, the remote is already gone — skip this.
2. `git checkout <trunk> && git pull`
3. `git branch -d <branch>`

> **Tip:** When merging via `gh pr merge`, pass `--delete-branch` to handle remote cleanup automatically.

## Step 5: Close Beads Task
After a successful push:
- Close the task with a meaningful reason: `bd close <task-id> --reason="[description of what was done]"`
- Use the `beads:close` skill.

## Step 6: Epic Auto-Completion
After closing the task, check if the parent epic is fully complete:

1. Run `bd show <parent-epic-id>` (use `beads:show` skill) to list all child tasks.
2. If **every child** has status `closed` → close the epic: `bd close <epic-id> --reason="All child tasks completed"`.
3. Determine the next epic by priority ordering (P0 → P1 → P2 → P3 → P4) among open epics.
4. Promote the next epic: `bd update <next-epic-id> --status=in_progress` (only if it exists and is currently `open`).

## Step 6.5: Publish Beads (team sync)
After all beads mutations (task closed, epic close/promote done), publish so
teammates get them.

**Default setup (`issues.jsonl` in git):** the beads changes are files in your
repo — stage and commit them with the work in Step 2. Nothing extra to do here.

**Dolt-remote setup:** beads is a **second channel** and Step 2's `git push`
did not ship it:
```bash
bd dolt pull        # fast-forward first
bd dolt push        # publish YOUR beads changes
```
If the push is rejected as diverged, `bd dolt pull` and retry — never `--force`
(only for a deliberate, agreed re-baseline).

## Step 7: Show Unblocked Tasks
Show what's now unblocked. If an epic is active, scope to that epic's tasks.

## Step 8: Update Workflow Step
```bash
echo "Complete" > .beads/.workflow-step
```

## Step 9: Clean Up Session State
- Delete `.beads/.session-state.json`
- Delete `.beads/.verification-done` — the marker is per-task; clearing it here
  (and at task start) prevents a stale marker from passing Step 0's gate for the
  next task: `rm -f .beads/.verification-done`

## Step 10: Suggest /clear

---

## Response Formats

**Epic NOT fully complete (other tasks remain):**
```
✅ Shipped and closed: bd-xxxx "Task Title"

Now unblocked:
- bd-yyyy "Next Task" (P1)

Recommend: `/clear` before starting next task.
```

**Epic IS fully complete (all children closed):**
```
✅ Shipped and closed: bd-xxxx "Task Title"

🏁 **Epic completed:** bd-yyyy "Phase N: Epic Name" — all tasks done!
🚀 **Next phase started:** bd-zzzz "Phase N+1: Epic Name" → in_progress

Now unblocked:
- bd-aaaa "Next Task" (P1)

Recommend: `/clear` before starting next task.
```

**Final epic (project complete):**
```
✅ Shipped and closed: bd-xxxx "Task Title"

🏁 **Epic completed:** bd-yyyy "GTM: Launch" — all tasks done!
🎉 **All project phases complete!**

Recommend: `/clear` to start a new session.
```
