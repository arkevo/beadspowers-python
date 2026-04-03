---
description: Ship completed task - commit, push, close Beads task, check epic completion, sync Jira
---

# Ship Beads Task

## Step 1: Update Workflow Step
```bash
echo "Committing" > .beads/.workflow-step
```

## Step 2: Commit and Push
- No PR requested → Invoke `commit-commands:commit-push`
- PR requested → Invoke `commit-commands:commit-push-pr`

## Step 3: Close Beads Task
After successful push:
- Close task with meaningful reason: `bd close <task-id> --reason="[description of what was done]"`
- Use `beads:close` skill

## Step 4: Epic Auto-Completion
After closing the task, check if parent epic is fully complete:

1. Run `bd show <parent-epic-id>` (use `beads:show` skill) to list all child tasks
2. If **every child** has status `closed` → proceed to close the epic:
   - `bd close <epic-id> --reason="All child tasks completed"`
3. Determine next epic using priority ordering (P0 → P1 → P2 → P4) among open epics.

4. Promote next epic: `bd update <next-epic-id> --status=in_progress`
   - Only if next epic exists and is currently `open`

## Step 5: Sync Jira
If Jira sync is configured:
- Invoke `one-off-commands:jira-quick-sync` for closed task + immediate dependents

## Step 6: Show Unblocked Tasks
Show what's now unblocked. If an epic is active, scope to that epic's tasks.

## Step 7: Update Workflow Step
```bash
echo "Complete" > .beads/.workflow-step
```

## Step 8: Clean Up Session State
- Delete `.beads/.session-state.json`

## Step 9: Suggest /clear

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
