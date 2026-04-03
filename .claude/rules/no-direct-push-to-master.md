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
