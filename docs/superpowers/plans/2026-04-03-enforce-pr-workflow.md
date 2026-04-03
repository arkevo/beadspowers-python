# Enforce PR Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make PRs mandatory when shipping tasks and block all direct pushes to master, so every change goes through code review.

**Architecture:** Four files are modified to enforce this at every layer: the shipping skill (workflow), the bash validation hook (runtime), the settings deny list (permission), and a new Claude rule (instruction). The workflow router is updated to remove the no-PR path.

**Tech Stack:** Markdown (skills/rules), Bash (hook), JSON (settings)

---

### Task 1: Block direct pushes to master in the bash validation hook

**Files:**
- Modify: `.claude/hooks/validate-bash.sh:8-38`

- [ ] **Step 1: Add master/main push patterns to DANGEROUS_PATTERNS**

Add these two patterns to the `DANGEROUS_PATTERNS` array in `validate-bash.sh`, after the existing `git push.*-f` entry (line 32):

```bash
    "git push.*(origin|upstream)?\s*(master|main)\b"
    "git push\b(?!.*-u).*(?!feat/|fix/|hotfix/|release/)" 
```

Wait — the second pattern is too complex for grep -E and could false-positive. Keep it simple with just the explicit master/main block:

```bash
    "git push.*\bmaster\b"
    "git push.*\bmain\b"
```

These go inside the `DANGEROUS_PATTERNS=( ... )` array, right after line 32 (`"git push.*-f"`). The full addition:

Open `.claude/hooks/validate-bash.sh` and add after line 32:

```bash
    "git push.*\bmaster\b"
    "git push.*\bmain\b"
```

- [ ] **Step 2: Verify the hook catches master pushes**

Run:
```bash
echo '{"tool_input":{"command":"git push origin master"}}' | bash ".claude/hooks/validate-bash.sh"
```

Expected output (JSON with `permissionDecision: "ask"` and reason mentioning dangerous command).

- [ ] **Step 3: Verify the hook still allows feature branch pushes**

Run:
```bash
echo '{"tool_input":{"command":"git push -u origin feat/my-feature"}}' | bash ".claude/hooks/validate-bash.sh"
```

Expected: No output (exit 0, falls through to normal permission checking — no opinion).

- [ ] **Step 4: Commit**

```bash
git add .claude/hooks/validate-bash.sh
git commit -m "fix(hooks): block direct pushes to master/main in bash validation"
```

---

### Task 2: Add master/main push to settings.json deny list

**Files:**
- Modify: `.claude/settings.json:5-9`

- [ ] **Step 1: Add deny patterns for direct master pushes**

Add two new entries to the `deny` array in `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
    ],
    "deny": [
      "Bash(rm -rf /)*",
      "Bash(git push --force *)",
      "Bash(git reset --hard *)",
      "Bash(git push * master)*",
      "Bash(git push * main)*"
    ]
  }
}
```

The two new lines are:
```
"Bash(git push * master)*",
"Bash(git push * main)*"
```

- [ ] **Step 2: Validate JSON syntax**

Run:
```bash
python3 -c "import json; json.load(open('.claude/settings.json'))" && echo "Valid JSON"
```

Expected: `Valid JSON`

- [ ] **Step 3: Commit**

```bash
git add .claude/settings.json
git commit -m "fix(settings): deny direct pushes to master/main branches"
```

---

### Task 3: Create a Claude rule enforcing PR-only workflow

**Files:**
- Create: `.claude/rules/no-direct-push-to-master.md`

- [ ] **Step 1: Create the rule file**

Create `.claude/rules/no-direct-push-to-master.md` with this content:

```markdown
# No Direct Push to Master

**Section:** Git Workflow

## Hard Rule: Never Push Directly to Master or Main

Claude MUST NEVER push commits directly to `master` or `main`. All changes must go through a pull request.

### What This Means

- **Always create a feature branch** before making changes (handled by `beads-start-task`)
- **Always create a PR** when shipping (handled by `beads-ship-task` using `commit-commands:commit-push-pr`)
- **Never run** `git push origin master` or `git push origin main`
- **Never run** `git push` while on the `master` or `main` branch

### Applies To

- All shipping workflows (`beads-ship-task`, manual commits)
- Hotfix workflows (must still branch and PR)
- Any ad-hoc push commands

### No Exceptions

There are no exceptions to this rule. If the user asks to push directly to master, explain why this is blocked and offer to create a PR instead.
```

- [ ] **Step 2: Verify the rule is picked up**

Run:
```bash
ls -la ".claude/rules/no-direct-push-to-master.md"
```

Expected: File exists.

- [ ] **Step 3: Commit**

```bash
git add .claude/rules/no-direct-push-to-master.md
git commit -m "docs(rules): add no-direct-push-to-master rule"
```

---

### Task 4: Make beads-ship-task always create a PR

**Files:**
- Modify: `.claude/Commands/workflow-commands/beads-ship-task.md:12-14`

- [ ] **Step 1: Replace Step 2 to always use PR**

In `.claude/Commands/workflow-commands/beads-ship-task.md`, replace lines 12-14:

```markdown
## Step 2: Commit and Push
- No PR requested → Invoke `commit-commands:commit-push`
- PR requested → Invoke `commit-commands:commit-push-pr`
```

With:

```markdown
## Step 2: Commit and Create PR
- Always invoke `commit-commands:commit-push-pr`
- Direct pushes to master are not allowed — all changes must go through a PR
```

- [ ] **Step 2: Verify the file reads correctly**

Run:
```bash
grep -n "commit-push-pr" ".claude/Commands/workflow-commands/beads-ship-task.md"
```

Expected: Shows the updated line referencing `commit-push-pr` only — no `commit-push` without `-pr`.

- [ ] **Step 3: Commit**

```bash
git add .claude/Commands/workflow-commands/beads-ship-task.md
git commit -m "feat(ship): always create PR when shipping, remove direct-push option"
```

---

### Task 5: Update workflow router to remove no-PR path

**Files:**
- Modify: `.claude/rules/0_Beads x Superpowers/beads-workflow-router.md:32-33`

- [ ] **Step 1: Update routing table entries**

In `.claude/rules/0_Beads x Superpowers/beads-workflow-router.md`, replace lines 32-33:

```markdown
| "Ship it" / "Send it" / "Commit and push" | `workflow-commands:beads-ship-task` |
| "Create a PR" / "PR this" / "I'm ready to create a PR" | `workflow-commands:beads-ship-task` (with PR flag) |
```

With:

```markdown
| "Ship it" / "Send it" / "Commit and push" / "Create a PR" / "PR this" | `workflow-commands:beads-ship-task` (always creates PR) |
```

Both trigger phrases now route to the same behavior — shipping always creates a PR.

- [ ] **Step 2: Verify no stale references remain**

Run:
```bash
grep -rn "with PR flag" ".claude/rules/0_Beads x Superpowers/beads-workflow-router.md"
```

Expected: No output (the "with PR flag" distinction is removed).

- [ ] **Step 3: Commit**

```bash
git add ".claude/rules/0_Beads x Superpowers/beads-workflow-router.md"
git commit -m "feat(router): unify ship routing, all paths create PRs"
```

---

### Task 6: Update README with PR workflow and push policy

**Files:**
- Modify: `README.md:6,36-37,48,95,248-249`

- [ ] **Step 1: Update the workflow diagram**

In `README.md`, replace line 6:

```
Start Task -> Plan -> Refine Plan -> Execute -> Verify -> Ship
```

With:

```
Start Task -> Plan -> Refine Plan -> Execute -> Verify -> Ship (PR)
```

- [ ] **Step 2: Update the Ship step description**

In `README.md`, replace line 37:

```markdown
6. **Ship** — `beads-ship-task` commits, pushes, closes the beads issue
```

With:

```markdown
6. **Ship** — `beads-ship-task` commits, pushes, creates a PR, closes the beads issue
```

- [ ] **Step 3: Update the "Ship it" trigger description**

In `README.md`, replace line 48:

```markdown
| "Ship it" | `beads-ship-task` |
```

With:

```markdown
| "Ship it" | `beads-ship-task` (always creates PR) |
```

- [ ] **Step 4: Add the new rule file to the directory tree**

In `README.md`, after the line listing `skill-usage.md` (line 204), add the new rule file to the tree:

```markdown
│   ├── 0_Beads x Superpowers/
│   │   └── beads-workflow-router.md     # Natural language -> skill router
│   ├── no-direct-push-to-master.md      # Blocks direct pushes to master/main
│   └── skill-usage.md                   # Naming conventions + enforcement
```

- [ ] **Step 5: Update the settings.json deny list documentation**

In `README.md`, replace lines 248-249:

```markdown
- `permissions.deny` — Safety rails preventing `rm -rf /`, `git push --force`, and `git reset --hard`
```

With:

```markdown
- `permissions.deny` — Safety rails preventing `rm -rf /`, `git push --force`, `git reset --hard`, and direct pushes to `master`/`main`
```

- [ ] **Step 6: Commit**

```bash
git add README.md
git commit -m "docs(readme): document PR-only workflow and no-push-to-master policy"
```

---

### Task 7: Final verification

**Files:**
- None (verification only, no commits)

- [ ] **Step 1: Verify bash hook blocks master push**

Run:
```bash
echo '{"tool_input":{"command":"git push origin master"}}' | bash ".claude/hooks/validate-bash.sh"
```

Expected: JSON with `permissionDecision: "ask"`.

- [ ] **Step 2: Verify bash hook allows feature branch push**

Run:
```bash
echo '{"tool_input":{"command":"git push -u origin feat/enforce-pr-workflow"}}' | bash ".claude/hooks/validate-bash.sh"
```

Expected: No output (falls through).

- [ ] **Step 3: Verify settings.json is valid**

Run:
```bash
python3 -c "import json; json.load(open('.claude/settings.json'))" && echo "Valid JSON"
```

Expected: `Valid JSON`

- [ ] **Step 4: Verify all rules files exist**

Run:
```bash
ls -la .claude/rules/no-direct-push-to-master.md .claude/rules/0_Beads\ x\ Superpowers/beads-workflow-router.md .claude/Commands/workflow-commands/beads-ship-task.md .claude/hooks/validate-bash.sh .claude/settings.json
```

Expected: All five files listed.

- [ ] **Step 5: Verify no remaining references to push-without-PR**

Run:
```bash
grep -rn "commit-push\b" .claude/Commands/workflow-commands/beads-ship-task.md
```

Expected: Only `commit-push-pr` matches, no bare `commit-push`.
