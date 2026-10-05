# Beadspowers: Python

Beadspowers is a Claude Code workflow for Python projects that combines **Beads** issue tracking with the **Superpowers** plan → execute → verify lifecycle, and enforces the order. Work one task at a time with you in the loop, or hand Claude a whole epic to plan and build across parallel agents.

## One task

1. `/beads:ready`
2. `/workflow-commands:beads-start-task <task-id>` — Claude announces the lane; in Lane C it asks the refinement questions and the execution choice.
3. Verification runs automatically after execution.
4. `/workflow-commands:beads-ship-task` — opens the PR and closes the bead.
5. Merge the PR, then update your local trunk: `git switch main && git pull` (use `master` if that is your trunk).
6. `/clear`

## An epic

The epic workflow is for work too big to drive one task at a time: a spec that turns into many tasks, some depending on others and some with open questions. Run one by one, that keeps you in the loop for every step and wastes the parallelism; run all at once with no structure, the agents collide on the same files and the decisions behind them get lost. So the pipeline turns a brainstormed spec (Superpowers) into a Beads epic whose tasks are sequenced into waves and given a plan depth — a full plan, a lite plan or a test-first task card — and answers the open questions with throwaway spikes before planning what depends on them. It then executes the approved plans as parallel Claude Code agents, each in its own git worktree (tasks that need you, such as smoke tests, run one at a time in the main session). Each task is built test-first and verified at a tier sized to its diff: ruff, mypy and pytest always, with review agents and a Codex adversarial pass added at the full tier. Beads labels record every task's progress, so an interrupted run resumes where it stopped; a budget gate shows the cost before each fan-out; and shipping opens one PR for the whole epic, which counts as shipped only after the merge is confirmed.

![Epic-batch workflow](assets/workflow-process-flow.drawio.png)

1. From the main checkout, after `git switch main && git pull`: `git worktree add ../<project>-<epic> -b feat/<epic-slug>`, then `cd ../<project>-<epic> && claude`
2. `/superpowers:brainstorming` — the approved spec lands in `docs/plans/`. When it asks you to review the written spec, review it, then go to step 3 instead of approving there: approving makes brainstorming start writing an implementation plan, and the epic's plans come from steps 4–6.
3. `/clear`
4. `/workflow-commands:workflow-planning-sequence --spec docs/plans/<date>-<topic>-design.md` — creates the epic; note its id.
5. `/clear`
6. `/workflow-commands:workflow-writing-plans <epic-id>`
7. `/clear`
8. Only if the epic has spike tasks:
   1. `/workflow-commands:workflow-execute-spikes <epic-id>`
   2. `/clear`
   3. `/workflow-commands:workflow-writing-plans <epic-id>` again — it plans the tasks the spikes unblocked.
   4. `/clear`
9. `/workflow-commands:workflow-execution-sequence <epic-id>`
10. `/clear`
11. `/workflow-commands:workflow-execute-plans <epic-id>`
12. `/clear`
13. `/workflow-commands:workflow-ship-epic <epic-id>` — opens the PR.
14. Merge the PR, then, in the main checkout, update your local trunk: `git switch main && git pull` (use `master` if that is your trunk).
15. `/workflow-commands:workflow-ship-epic <epic-id>` again — confirms the merge and marks the epic shipped.
16. `/clear`

If tasks are left over after step 11, unplanned ones go back to step 6 and unordered ones to step 9.

**Context tip:** past roughly 30–50% of the context window in the middle of a phase, ask Claude for a handoff doc for the next session, `/clear`, and paste the doc back in.

## What's inside

- `.claude/rules/` — the router (`0_Beads x Superpowers/beads-workflow-router.md`) and the rules it enforces; start here.
- `.claude/Commands/workflow-commands/` — the single-task and epic-batch commands, plus the `python-verification-*` tiers.
- `.claude/agents/` — the review agents the full verification tier runs.
- `.claude/skills/` — troubleshooting skills, such as beads in a worktree.

## Set up

1. Install the system tools (the workflow is verified with beads 1.0.4):

   ```bash
   brew install jq gh
   gh auth login
   npm install -g @beads/bd
   ```

2. Install the plugins, inside Claude Code:

   ```
   /plugin marketplace add steveyegge/beads
   /plugin install beads@beads-marketplace
   /plugin install superpowers@claude-plugins-official
   /plugin install commit-commands@claude-plugins-official
   /plugin marketplace add openai/codex-plugin-cc
   /plugin install codex@openai-codex
   ```

   The last two lines add the Codex plugin, which only the full verification tier's adversarial review uses; skip them if you don't use Codex.

3. Copy the workflow in. It works at either level, so pick one:

   - **User level (recommended)** — once, and it works in every project:

     ```bash
     cp -Rn /path/to/beadspowers-python/.claude/. ~/.claude/
     ```

   - **Project level** — only for one project, from its root:

     ```bash
     cp -Rn /path/to/beadspowers-python/.claude/. .claude/
     ```

   `cp -n` never overwrites a file you already have: it skips it silently and exits 1, so a same-named file already there keeps running, and re-copying never updates it. Avoid installing at both levels: a command that exists in both loads the user-level copy. Paths in the rules such as `.claude/Commands/...` mean `~/.claude/Commands/...` after a user-level install.

4. In each new project, run `/beads:init` before you start the workflow, then ask Claude to finish the beads setup. It follows the "Setting up a new project" steps in the workflow's `beads.md` rule (untracked export, ignored state files, a seeded Dolt remote) and fills in project values such as `src/<your_package>/` as it works.
