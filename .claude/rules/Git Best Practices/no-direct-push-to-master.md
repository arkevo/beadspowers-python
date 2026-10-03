# No Direct Push to Master

**Section:** Git Workflow

## Hard Rule: Never Push Directly to Master or Main

Claude MUST NEVER push commits directly to `master` or `main`. All changes must go through a pull request.

### What This Means

- **Always create a feature branch** before making changes (handled by `workflow-commands:beads-start-task`)
- **Always create a PR** when shipping (handled by `workflow-commands:beads-ship-task` using `commit-commands:commit-push-pr`)
- **Never run** `git push origin master` or `git push origin main`
- **Never run** `git push` while on the `master` or `main` branch

### Applies To

- All shipping workflows (`workflow-commands:beads-ship-task`, manual commits)
- Hotfix workflows (must still branch and PR)
- Any ad-hoc push commands

### No Exceptions

There are no exceptions to this rule. If the user asks to push directly to master, explain why this is blocked and offer to create a PR instead.

## Ship Is Atomic (PR form)

"Ship it", "send it", "commit and push" and "create a PR" all run the whole ship
sequence end to end — `workflow-commands:beads-ship-task` for one task,
`/workflow-commands:workflow-ship-epic` for an epic: stage every changed file explicitly
(`protect_plans_and_commit_all.md` Rule 3), commit, push the feature branch
(`git push -u origin HEAD`), and open the PR. Never run a partial subset, and never
narrow the scope with a leading "push the branch only?" question — the phrase already
chose the whole sequence (`no-skipping-workflow-steps.md` lists "ship it" as NOT a skip
phrase).

One legitimate pause, decided up front: a long-lived branch — an epic or foundation
branch — whose work should not be proposed for the trunk yet. Then ask before any ship
step and name the consequence: "Shipping `<branch>` opens a PR proposing all of its
current commits to the trunk. Open the PR now, or push the branch only?" Do exactly what
the user picks, in full. If you are unsure whether a branch is long-lived, ask; normal
`feat/`, `fix/` and `chore/` branches ship without asking.

If a push is rejected, the remote has commits you don't: fetch, merge the remote branch
(or the trunk) into yours, re-verify, and push again. Never force-push past a rejected
push — it throws away someone else's commits. And never run `git checkout HEAD -- .` to
"fix" a ship: it silently overwrites every uncommitted change in the tree.
