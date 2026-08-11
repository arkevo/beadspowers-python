---
description: Handle critical bug discovered mid-task - stash/worktree/in-place hotfix options
---

# Hotfix Interruption Handler

When a critical bug is discovered while a task is in_progress, offer three approaches.

## Triggers
- User reports critical/P0 bug while task is in_progress
- User says "This is critical" or "This needs a hotfix"
- Verification discovers CRITICAL issue:
  - Phase 3 Bug Scan: CRITICAL severity found
  - Phase 7 Silent Failure Hunt: CRITICAL severity with confidence >= 80%
  - Phase 11: Tests fail due to newly discovered bug (not a test bug)

## Step 1: Create Bug in Beads
- Invoke `beads:create` with type=bug, priority=0, title matching the bug description

## Step 2: Show Options

```
Created: **bd-xxxx "[Bug description]"** (P0, bug)

⚠️ **Hotfix needed!** Your current task **[current-task]** is still in_progress.

How would you like to handle this?

**1. Stash and switch** (quick fix, ~30 seconds overhead)
**2. Use a worktree** (longer fix, keeps your WIP untouched)
**3. Fix it here** (no context switch, handle in current branch)
```

---

## Option 1: Stash and Switch
Best for: Quick fixes (< 30 min)

```bash
git stash push -m "WIP: [task-id] [task-name]"
git checkout main
git checkout -b hotfix/[description]
```

**Return:**
```bash
git checkout [original-branch] && git stash pop
```

---

## Option 2: Worktree
Best for: Longer fixes, complex debugging

```bash
git worktree add ../<repo>-hotfix -b hotfix/[description]
# Work using absolute paths in the worktree: /Users/.../<repo>-hotfix/src/...
```

**Return:**
```bash
git worktree remove ../<repo>-hotfix
# Continue in original directory
```

---

## Option 3: Fix It Here
Best for: Minor issues, same-branch fixes. No git operations needed. Continue in current context.

---

## Natural Language Commands

| User Says | Action |
|-----------|--------|
| "Stash and switch" | Run stash → checkout main → create hotfix branch |
| "Use a worktree" | Create sibling worktree for isolated hotfix |
| "Fix it here" | Continue in current branch |
| "I'm back" / "Back to my task" | Return per approach (checkout + pop stash, or remove worktree) |
| "Pop my stash" | `git stash pop` |
| "Remove the worktree" | `git worktree remove ../<repo>-hotfix` |

---

## After Hotfix Ships
1. Close hotfix bug task via `beads:close`
2. Return to original task:
   - Stash approach: `git checkout [branch] && git stash pop`
   - Worktree approach: `git worktree remove ../<repo>-hotfix`
   - In-place: already there
3. If interrupted during verification → say "Continue verification" to resume from where you left off

---

## Verification Interruption Note

When a CRITICAL issue is found during verification, the automatic prompt is:

```
⚠️ **CRITICAL issue found during verification!**

**Issue:** [Brief description]
**Location:** `path/to/file.dart:line`
**Impact:** [User impact]

1. **Stash and switch**
2. **Use a worktree**
3. **Fix it here**
```

After hotfix: say "Continue verification" to resume the interrupted verification phase.
