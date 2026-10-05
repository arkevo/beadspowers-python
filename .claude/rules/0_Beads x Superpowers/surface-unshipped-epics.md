# A Finished Epic That Never Shipped Must Be Surfaced

**Section:** Task Management (guardrail — prevents an observed failure)

## The Failure This Rule Prevents

Observed in a downstream project using this workflow. An epic finished
executing and shipped **eleven days later** — and only because an unrelated
ship stumbled over it.

What went wrong, verified from the record rather than inferred:

- `/workflow-commands:workflow-ship-epic` was **never invoked**. The epic's label set was empty
  — no `sh:pushed`, no `sh:shipped`. It did not fail partway; it never ran.
- All child tasks sat at `ex:done` with their QA levels recorded, and the
  visual ones carried `ex:design` with saved parity evidence. **The work was
  finished and verified.** Nothing was wrong with it.
- The tasks and the epic therefore stayed **open**, because closure happens at
  ship. For eleven days the tracker said an epic was in progress while its
  code was done.
- The next day, a second epic was planned and built **on the same branch**.
  The first epic's commits became ancestry for the second.
- The branch *was* pushed to origin — but its tip was a commit belonging to
  the second epic. It was pushed as ongoing work, not as an integration step,
  which is exactly why the push looked like progress and hid the problem.
- By the time anyone shipped, trunk was ~90 commits behind and integrating one
  epic silently integrated two. That had to be caught and surfaced by hand,
  mid-ship.

**The pipeline behaved correctly at every step.** `/workflow-commands:workflow-execute-plans`
ends at `ex:done` and never auto-ships; `/workflow-commands:workflow-ship-epic` never auto-runs.
Both are deliberate safety properties and this rule does **not** weaken them.
The gap is that **nothing notices an epic that stops between them**, and
nothing objects when the next epic is stacked on top of it.

## The Rule

### 1. Check for a finished-but-unshipped epic before starting new epic work

At the START of `/workflow-commands:workflow-planning-sequence`,
`/workflow-commands:workflow-writing-plans` and
`/workflow-commands:workflow-execute-plans`, read every epic with its labels
(`bd list --type=epic --all -n 0 --json`) and look for either of two states.
Surface the first one found before doing anything else:

- **Finished, never shipped** — an open epic with at least one `ex:done` child,
  whose open children are all `ex:done` (`bd list --parent <id> -n 0 --json`),
  and which carries no `sh:*` label: `/workflow-commands:workflow-ship-epic`
  never ran. An epic with no children, or whose children are all closed and none
  `ex:done`, does not match.

  > ⚠️ Epic **<id> "<title>"** finished executing on <date> but was never
  > shipped — all N open children are `ex:done`, the epic has no `sh:shipped`,
  > and its code is not on the trunk.
  >
  > Ship it with `/workflow-commands:workflow-ship-epic <id>` first, or tell me
  > to proceed and stack this new work on top of it.

- **PR opened, not merged** — an epic that carries `sh:pushed` but not
  `sh:shipped`, open or closed. It is usually closed: ship-epic closes the tasks
  and the epic when it opens the PR, so a closed epic proves only that the PR
  was opened, and an open one means a ship stopped in between. `<date>` is the
  `opened:` date in the `PR: <pr-url> · head: <epic-head-sha> · opened: <date>`
  line ship-epic appends to the epic's notes.

  > ⚠️ Epic **<id> "<title>"** opened its PR on <date> but is not marked
  > shipped — it carries `sh:pushed` without `sh:shipped`.
  >
  > If the PR has merged, re-run `/workflow-commands:workflow-ship-epic <id>`
  > to confirm the merge and mark it shipped. If not, merge it first, or tell
  > me to proceed and stack this new work on top of it.

This is a **surface-and-ask**, not a hard stop. Stacking is sometimes the
right call — in the observed case the second epic genuinely built on the
first. What must not happen is stacking **silently**.

### 2. Warn before stacking onto an unmerged branch

Before planning or executing an epic on a branch that already carries commits
from a *different* epic and is unmerged to trunk, say so plainly: name the
other epic, the commit count, and that shipping this branch will ship both.
Cheap to check:

```bash
git rev-list --left-right --count origin/master...HEAD   # behind / ahead
git log --oneline origin/master..HEAD | wc -l
```

If the ahead-count is much larger than the current epic's own commits, the
branch is carrying someone else's work — find out whose before adding more.

### 3. A pushed branch, an open PR or a closed epic is not a shipped epic

Do not read `origin/<branch>` existing as evidence that an epic shipped — in
the observed failure the branch was pushed and the epic was not. This repo
ships through pull requests (`Git Best Practices/no-direct-push-to-master.md`),
and `/workflow-commands:workflow-ship-epic` records the two steps separately:

- **`sh:pushed`** — the PR is open. Ship-epic closed the epic's tasks and the
  epic when it opened the PR, so **closed is not shipped**.
- **`sh:shipped`** — a later re-run of ship-epic confirmed the merge. This is
  the only label that means shipped.

Verify the merge itself rather than trusting a label, using the `<pr-url>` and
`<epic-head-sha>` from the `PR: … · head: … · opened: …` line in the epic's
notes. Ask GitHub first, because a squash merge rewrites the commits and can
defeat ancestry checks; fall back to the trunk (`origin/master`, or
`origin/main`):

```bash
gh pr view <pr-url> --json state,mergedAt               # "MERGED" with a mergedAt time?
git fetch origin
git merge-base --is-ancestor <epic-head-sha> origin/master && echo merged
git cat-file -e origin/master:<a file the epic added>   # supporting evidence
```

An open PR is the same class of false signal as a pushed branch: "reachable
from the trunk" means **the PR was merged**, not merely opened.

### 4. Shipping ends an epic in two steps — say so at the handoff

When `/workflow-commands:workflow-execute-plans` reports an epic fully
executed, its next-command line (`/workflow-commands:workflow-ship-epic <id>`)
is the **only** thing standing between finished and shipped. Say plainly at
that handoff:

- the epic and its tasks stay OPEN until ship-epic runs;
- ship-epic opens the PR, closes the tasks and the epic, and marks the epic
  `sh:pushed`;
- the epic counts as shipped only once the PR merges and a re-run of
  `/workflow-commands:workflow-ship-epic <id>` confirms the merge and adds
  `sh:shipped`.

That way neither an unshipped epic nor a merely opened PR is mistaken for a
shipped one.

## Why not just auto-ship?

Because shipping pushes, opens a PR and closes beads — all outward-facing and
hard to reverse. `/workflow-commands:workflow-ship-epic`'s EXECUTION LOCK
requires explicit invocation plus a confirmation gate, it never merges, and
`critical ai agent rule.md` treats trunk integration as a protected operation.
Those are right. The failure here was not too little automation; it was
**silence**. The fix is a check, not a trigger.

## Generalized Lesson

> A pipeline that correctly refuses to take the last step must still make it
> impossible to forget that the step is outstanding.

Every stage in the epic-batch pipeline advances a label, and each stage reads
the previous stage's label to know where to resume. In the observed failure
`sh:*` was the one label with **no consumer** — nothing read it, so nothing
noticed its absence. A terminal state that nothing checks is indistinguishable
from a state nobody reached. The Step 0 checks in Rule 1 are its consumer now,
and they read both halves: the missing `sh:*` label, and the `sh:pushed` that
never became `sh:shipped`.
