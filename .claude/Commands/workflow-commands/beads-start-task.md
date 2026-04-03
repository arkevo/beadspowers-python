---
description: Start a Beads task - mark in_progress, create branch, initialize session state
---

# Start Beads Task

When the user starts a task, execute these steps in order:

## Step 1: Mark Task In Progress
- Run `bd update <id> --status=in_progress` (use beads:update skill)

## Step 2: Initialize Session State
Create/reset `.beads/.session-state.json`:
```json
{
  "task_requirements": "",
  "plan_created": false,
  "plan_file": "",
  "modified_files": [],
  "total_lines_changed": 0
}
```

## Step 3: Jira Key Lookup
Before creating the branch, look up linked Jira issue:

**Step 3a — Local cache:**
- Read `.sync/jira-gid-mapping.json` (if exists)
- Find entry where `beads_id` matches → extract `jira_key`
- If found → proceed to Step 4

**Step 3b — Atlassian MCP (fallback):**
- Load `.sync/jira-config.json` for project key (e.g., `FC`)
- Use the **Atlassian MCP** tool: `mcp__plugin_atlassian__searchJiraIssuesUsingJql`
  - JQL: `project = FC AND cf[10157] = "[beads_id]" ORDER BY created DESC`
  - **NEVER use Asana MCP for Jira lookups** — Asana is not used in this project
- If found → cache result in `.sync/jira-gid-mapping.json` → proceed to Step 4
- If Atlassian MCP is unavailable or returns no results → proceed to Step 3c

**Step 3c — No match:**
- Create branch without Jira prefix
- Inform user: "No Jira issue found for this task."

## Step 4: Create Feature Branch
If still on main/master:
- `feature`/`epic`/`task` → `feat/[jira-key-]kebab-case-description`
- `bug` → `fix/[jira-key-]kebab-case-description`

Examples: `feat/FC-17-task-title-kebab`, `fix/task-title-kebab`

## Step 5: Update Workflow Step
```bash
echo "Starting Work" > .beads/.workflow-step
```

## Step 6: Confirm

With Jira key:
> ✅ Marked **bd-xxxx "[Task Title]"** as in_progress.
> 🌿 Branch: `feat/FC-17-task-title-kebab`
> 🔗 Jira: FC-17

Without Jira key:
> ✅ Marked **bd-xxxx "[Task Title]"** as in_progress.
> 🌿 Branch: `feat/task-title-kebab`
> ℹ️ No Jira issue found for this task.

## Step 7: Check for Plan
- Search `docs/plans/` for existing plan matching task (by task ID, title keywords, or related epic)
- If found → offer:
  > Found existing plan: `docs/plans/[filename]`
  > 1. **Use existing plan** — review and execute this plan
  > 2. **Write new plan** — create a fresh plan with `superpowers:writing-plans`
- If not found → ask for additional requirements, then start planning

**IMPORTANT:** When writing a new plan, invoke `superpowers:writing-plans` DIRECTLY.
Do NOT invoke `superpowers:brainstorming` first — brainstorming is not needed here
because the Beads task already defines the scope. Skip brainstorming and go straight
to plan writing.

---

## "What's Ready?" Scoping Logic

When user asks "What's ready?" or "What should I work on?":
1. Run `bd list --status=in_progress --type=epic` to find active epic
2. Run `bd list --status=open --parent=<epic-id>` for tasks within that epic
3. Only fall back to `bd ready` if NO epic is in_progress — tell user: "No epic is in progress — showing all unblocked tasks."
