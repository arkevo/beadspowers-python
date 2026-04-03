

# Beads Task Context Loading

When planning a Beads task, Claude auto-loads context before invoking `/superpowers:writing-plans`:

1. Check for current in_progress task (ask if none)
2. Fetch task details: `bd show <id>`
3. Display context:
   ```
   ## Task Context (from Beads)
   **Task:** bd-xxxx "[Task Title]"
   **Epic:** bd-yyyy "[Epic Title]"
   **Priority:** P[X]
   **Blocks:** [tasks waiting on this]
   **Description:** [Task description]
   ```
4. Search `docs/plans/` for existing plan matching task
5. If found → offer: use existing plan vs write new plan
6. If not found → ask for additional requirements → start planning

Update `.beads/.workflow-step` to `Planning` when entering planning phase.

---

## Integration with Beads

When planning Beads tasks:
- Reference task ID and description from `bd show <id>`
- Note any blocking/blocked dependencies
- Ensure plan addresses the full task scope
- Flag if task should be split into smaller tasks
