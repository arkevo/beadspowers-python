# A Finished Epic That Never Shipped Must Be Surfaced

**Section:** Task Management (guardrail — prevents an observed failure)

## The Failure This Rule Prevents

Observed in a downstream project using this workflow. An epic finished
executing and shipped **eleven days later** — and only because an unrelated
ship stumbled over it.

What went wrong, verified from the record rather than inferred:

- `/workflow-ship-epic` was **never invoked**. The epic's label set was empty
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

**The pipeline behaved correctly at every step.** `/workflow-execute-plans`
ends at `ex:done` and never auto-ships; `/workflow-ship-epic` never auto-runs.
Both are deliberate safety properties and this rule does **not** weaken them.
The gap is that **nothing notices an epic that stops between them**, and
nothing objects when the next epic is stacked on top of it.

## The Rule

### 1. Check for a finished-but-unshipped epic before starting new epic work

At the START of `/workflow-planning-sequence`, `/workflow-writing-plans` and
`/workflow-execute-plans`, look for any epic whose children are all `ex:done`
but which lacks `sh:shipped`. If one exists, surface it before doing anything
else:

> ⚠️ Epic **<id> "<title>"** finished executing on <date> but was never
> shipped — all N children are `ex:done`, the epic has no `sh:shipped`, and
> its code is not on trunk.
>
> Ship it with `/workflow-ship-epic <id>` first, or tell me to proceed and
> stack this new work on top of it.

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

### 3. A pushed branch is not a shipped epic

Do not read `origin/<branch>` existing as evidence that an epic shipped. In
the observed failure the branch was pushed and the epic was not. **The only
signals that mean shipped are the `sh:shipped` label AND the code being
reachable from trunk** — and verify the second rather than trusting the first:

```bash
git cat-file -e origin/master:<a file the epic added>   # exists?
git log --oneline origin/master --grep="<epic-id>"      # commits present?
```

Note this repo ships through pull requests
(`Git Best Practices/no-direct-push-to-master.md`), so "reachable from trunk"
means **the PR was merged**, not merely opened. An open PR is the same class
of false signal as a pushed branch.

### 4. Closing an epic is what ends it — say so at the handoff

When `/workflow-execute-plans` reports an epic fully executed, its
next-command line (`/workflow-ship-epic <id>`) is the **only** thing standing
between finished and shipped. State that the epic and its tasks stay OPEN
until that command runs, so an unshipped epic is never mistaken for a closed
one.

## Why not just auto-ship?

Because shipping pushes, opens or merges a PR, and closes tickets — all
outward-facing and hard to reverse. `/workflow-ship-epic`'s EXECUTION LOCK
requires explicit invocation plus a confirmation gate, and
`critical ai agent rule.md` treats trunk integration as a protected
operation. Those are right. The failure here was not too little automation;
it was **silence**. The fix is a check, not a trigger.

## Generalized Lesson

> A pipeline that correctly refuses to take the last step must still make it
> impossible to forget that the step is outstanding.

Every stage in the epic-batch pipeline advances a label, and each stage reads
the previous stage's label to know where to resume. `sh:*` is the one label
with **no consumer** — nothing reads it, so nothing notices its absence. A
terminal state that nothing checks is indistinguishable from a state nobody
reached.
