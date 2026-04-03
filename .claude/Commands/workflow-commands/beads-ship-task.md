---
description: Ship completed task - commit, push, close Beads task, check epic completion, sync Jira
---

# Ship Beads Task

## Step 1: Update Workflow Step
```bash
echo "Committing" > .beads/.workflow-step
```

## Step 2: Commit and Create PR
- Always invoke `commit-commands:commit-push-pr`
- Direct pushes to master are not allowed — all changes must go through a PR

### PR Description Format

The PR body MUST include these sections. Gather the information before creating the PR:

**Summary:** Write a thorough technical summary of the changes. Group by logical layers or components if the change spans multiple areas. Explain the *what* and *why*, not just file names.

**Test Results:** Include test counts (passed/failed), note pre-existing failures separately, count new tests added, and mention any manual verification performed (e.g., smoke tests, cross-repo checks).

**Beads:** List the epic ID and all task IDs involved in this PR. Use `beads:show` on the current task to get the epic and task IDs.

**Companion PR:** If this PR depends on or is paired with a PR in another repo, link it here. If none, omit this section entirely.

Example PR body:

```markdown
## Summary
Seller-side fix for CPM hallucination. Two layers:

**Layer 1 (pricing_type enum):** Added PricingType enum (fixed/floor/on_request) to ProductDefinition, Package, QuotePricing, and Pricing models. Made pricing fields Optional when on_request. Defaults to fixed for backward compatibility.

**Layer 4 (quote validation):** Added QuoteHistoryStore that records quotes when issued and cross-references buyer-submitted CPMs against quote history. Proposals with unverified pricing are flagged (pricing_verified=false), not blocked. 1% tolerance for price matching.

## Test Results
- Layer 1: 638 passed (2 pre-existing failures), 18 new tests
- Layer 4: 648 passed (2 pre-existing failures), 10 new tests
- Both layers Quinn VERIFIED independently
- Cross-repo smoke test: 6/6 scenarios PASS

## Beads
- Epic: `ar-rrgw`
- Tasks: `ar-7rgy` (Layer 1), `ar-hm9l` (Layer 4)

## Companion PR
Buyer-side fix (remove fallbacks, pricing provenance, LLM guardrails) in separate PR on `ad_buyer_system`.
```

## Step 3: Delete Merged Branch
After the PR is merged, clean up the branch both remotely and locally:

1. Delete remote branch: `gh pr view <number> --json headRefName -q .headRefName` then `git push origin --delete <branch>`
   - If the PR was merged with `gh pr merge --delete-branch`, the remote is already gone — skip this
2. Switch to master: `git checkout master && git pull`
3. Delete local branch: `git branch -d <branch>`

> **Tip:** When merging via `gh pr merge`, always pass `--delete-branch` to handle remote cleanup automatically.

## Step 4: Close Beads Task
After successful push:
- Close task with meaningful reason: `bd close <task-id> --reason="[description of what was done]"`
- Use `beads:close` skill

## Step 5: Epic Auto-Completion
After closing the task, check if parent epic is fully complete:

1. Run `bd show <parent-epic-id>` (use `beads:show` skill) to list all child tasks
2. If **every child** has status `closed` → proceed to close the epic:
   - `bd close <epic-id> --reason="All child tasks completed"`
3. Determine next epic using priority ordering (P0 → P1 → P2 → P4) among open epics.

4. Promote next epic: `bd update <next-epic-id> --status=in_progress`
   - Only if next epic exists and is currently `open`

## Step 6: Sync Jira
If Jira sync is configured:
- Invoke `one-off-commands:jira-quick-sync` for closed task + immediate dependents

## Step 7: Show Unblocked Tasks
Show what's now unblocked. If an epic is active, scope to that epic's tasks.

## Step 8: Update Workflow Step
```bash
echo "Complete" > .beads/.workflow-step
```

## Step 9: Clean Up Session State
- Delete `.beads/.session-state.json`

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
