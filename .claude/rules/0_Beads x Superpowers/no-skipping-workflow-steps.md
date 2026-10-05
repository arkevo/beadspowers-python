# Perform Every Mandated Step

**Section:** Interaction Guidelines

If a rule, skill, agent, command or CLAUDE.md directive says to perform a step, perform
it — every checklist item, every auto-invoke, every numbered instruction.

There are only two legitimate pauses:

1. **A destructive or locked action the skill does not explicitly authorize** — a
   force-push, a hard reset, dropping tables, a force-merge. If the skill authorizes it
   (for example, `workflow-commands:beads-ship-task` authorizes pushing the feature
   branch and opening its PR), proceed without asking. The hard locks in
   `critical ai agent rule.md` — creating a branch, a managed-cloud mutation, a merge to
   the trunk — always pause for the owner, even when a skill names the action.
2. **Genuinely conflicting instructions** that reading the files cannot resolve. Quote
   both verbatim and ask which wins. Don't invent ambiguity to create an opt-out.

Skip authority comes only from explicit words this turn: "skip refinement", "skip
verification", "skip summary", "skip debugging skill", "just plan it", "just execute",
"let's just execute", "don't close the task", "I'm confident". These are NOT skip
phrases: "ship it", "execute the plan", "quick verify", "done", "looks good" — they run
the full workflow.

**One standing exception: the Sizing Gate** (the router's
*Sizing Gate — Claude picks the lane* section). Choosing Lane A (TDD-direct) or Lane B
(plan-lite) is a sanctioned decision, not a skip: the owner delegates that judgement so
that small fixes stop attracting full planning.

The same exception covers its batch mirror: `workflow-commands:workflow-planning-sequence`
assigning a task `PLAN-LITE` or `TDD-DIRECT` as its plan depth, and
`workflow-commands:workflow-writing-plans` therefore skipping the refinement round for
that task. That is the assigned depth taking effect, not a skipped step — and the owner
has already seen and approved the depth at two gates (the planning-sequence review and
the writing-plans budget preview).

The exception is bounded. The lane is announced in one line, with its reason, before
work starts; ties go to Lane C; and a mid-flight discovery that the work is bigger
means stop and switch lanes. It grants no authority to skip anything else —
verification, the ship steps, `workflow-commands:beads-post-execution` and the
Completion Report still run in every lane.

If Claude disagrees with a step, it runs the step anyway, raises the concern in the
final summary, and proposes a rule change in a follow-up turn.
