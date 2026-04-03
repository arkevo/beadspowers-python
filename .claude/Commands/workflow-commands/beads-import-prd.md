---
description: Import PRD (Product Requirements Document) into Beads - creates epics, tasks, and dependencies with deduplication
---

# Import PRD to Beads

Triggered by: "Read my PRD", "Import my PRD", "Create tasks from my PRD", etc.

## Workflow

### Step 1: Get File Location
If no path provided, ask:
> What's the path to your PRD file?

### Step 2: Analyze Existing Beads
Run `bd list` to get all existing epics and tasks. Check for duplicates before creating.

### Step 3: Read and Parse PRD
Identify: major features → Epics, sub-features → Tasks, order → Dependencies, priority indicators → P0-P4.

### Step 4: Deduplicate
- **Epic match:** identical/similar name or same feature area → add tasks to existing epic
- **Task match:** identical/similar name under same epic → skip
- **Uncertain:** ask user (skip / create new / add as subtask)

### Step 5: Create Issues
1. New epics first
2. Tasks under appropriate epics
3. Dependencies: `bd dep add`

### Step 6: Report Summary
```
## PRD Import Summary
### Added to Existing Epics
### New Epics Created
### New Tasks Created (table: ID, Task, Parent, Priority)
### Dependencies Created
### Skipped (duplicates)
```

## Dependency Detection
| PRD Language | Action |
|---|---|
| "after [X]" / "requires [X]" / "depends on [X]" | X blocks new task |
| "before [Y]" / "prerequisite for [Y]" | New task blocks Y |
| Sequential numbering | Each blocks next |

## Priority Detection
| Language | Priority |
|---|---|
| "critical", "must have" | P0 |
| "high priority", "important" | P1 |
| "medium", "normal" | P2 |
| "low priority", "nice to have" | P3 |
| "backlog", "future" | P4 |
| Default | P2 |
