# Protect Plans & Commit All Changed Files

**Section:** Git Workflow

## Rule 1: Save Every Plan Under `docs/plans/`

**OVERRIDE:** Any skill or plugin that specifies a different plan output path
(e.g. `docs/superpowers/plans/`) MUST be ignored. The canonical plan location
for this project is `docs/plans/` — no exceptions.

Any time Codex/Claude creates a plan for this repository, it must save that
plan as a Markdown file under `docs/plans/`. Do not leave plans only in chat,
scratch notes, session state, or temporary output.

This applies to all planning flows:
- Built-in planning mode
- `/superpowers:writing-plans` (ignore the skill's default `docs/superpowers/plans/` path)
- Ad hoc implementation plans written during normal task work
- Refactor, migration, investigation, and execution plans

### Plan file requirements

- Save the plan before treating it as the active plan for execution or handoff
- Use the filename format `YYYY-MM-DD-kebab-case-topic.md`
- Prefer updating an existing matching plan when continuing the same work
- When presenting a plan to the user, reference the saved `docs/plans/...` path

## Rule 2: Never Delete Plan Files

Files under `docs/plans/` must **NEVER** be deleted, moved, or included in
cleanup commits. Plans are permanent architectural documentation — they remain
valuable as historical context even after execution is complete.

This applies to all contexts:
- Chore commits and cleanup tasks
- Branch merges and rebases
- Any automated or manual file operations

If a plan is outdated, leave it in place. Future sessions benefit from seeing
past architectural decisions.

## Rule 3: Commit All Changed Files When Shipping

When the user says "ship it", "send it", or "commit and push", stage **ALL**
changed files — not just files touched during the current task.

The user may have modified files in another session, manually, or via a
different tool. Those changes should not be silently left behind.

### Safe Staging Protocol

**Never use `git add -A`.** It blindly stages deletions and can commit missing
files you didn't intend to remove. Instead:

1. **Stage explicitly:** add files by name, directory, or pattern
   ```bash
   git add lib/ test/ .claude/ pipeline/  # known change directories
   git add <specific-new-files>           # untracked files
   ```
2. **Review before committing:**
   ```bash
   git status                # verify staged vs unstaged
   git diff --cached --stat  # what WILL be committed
   ```
3. **Flag unexpected deletions:** if `git status` shows deleted files you
   didn't deliberately remove, **stop and ask the user** before staging them.
4. **Catch leftovers:** after staging, check `git diff --stat` for unstaged
   changes that should be included. Ask the user if unsure.

### What to stage

- All modified tracked files related to the task
- All new files created during the session
- Config/rule changes (`.claude/`, `.beads/`)
- Still warn about sensitive files (`.env`, credentials) per existing rules
- Still respect `.gitignore`

### What NOT to stage without confirmation

- File deletions (could be accidental — missing from disk != intentional delete)
- Files outside the project working directories
- Large binary files or build artifacts
