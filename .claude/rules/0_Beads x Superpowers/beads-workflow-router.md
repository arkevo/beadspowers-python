# Beads Workflow Router

**Section:** Task Management

## CRITICAL: Router Overrides Skill Handoffs

Skills loaded via the Skill tool often end with "next step" or "handoff" instructions (e.g., "offer execution choice"). **These skill-internal handoffs are ALWAYS subordinate to this router.** After ANY skill completes, check this router's mandatory sequence before following the skill's own handoff. The skill was loaded later in context — that does NOT give it priority. This router defines the canonical workflow order:

**Mandatory sequence:** start task → branch → plan → **refine plan** → execute → verify

If you are about to offer execution options and have not yet run plan refinement, STOP — you are violating the sequence.

---

## Hard Stop: No Direct Coding After Task Start

When a Beads task is started (marked `in_progress`), Claude MUST NOT write code directly. Mandatory sequence: mark in_progress → create branch → check for plan → plan → refine plan → execute → verify. Never skip execution or verification steps, even for "simple" tasks.

## Hard Stop: Systematic Debugging for Bug Tasks

When starting a Beads task whose type is `bug`, ALWAYS invoke `superpowers:systematic-debugging` immediately after marking the task `in_progress` and creating the branch — before writing any plan or code. This applies to any trigger phrase ("I'm starting [task]", "Let's work on [task]", "Let's do [task]") when the resolved task has `type: bug`.

The only way to skip this is if the user explicitly says "skip debugging skill" or "just plan it."

## Hard Stop: Scope Ready Tasks to Current Epic

When showing ready tasks, ALWAYS check `bd list --status=in_progress` for an active epic first. If one exists, show only tasks under that epic. Only show cross-epic tasks if no epic is in progress or the current epic has no ready children.

---

## Natural Language → Skill Routing

| User Says | Skill to Invoke |
|-----------|----------------|
| "What's ready?" / "What should I work on?" | Scope to current epic first, then `bd list --status=in_progress` |
| "I'm starting [task]" / "Let's work on [task]" / "Let's do [task]" | `workflow-commands:beads-start-task` |
| "Plan this task" / "Write a plan" / "Start planning" | Load Beads context → `superpowers:writing-plans` |
| "Refine the plan" / "Review the plan" / "Plan Q&A" | `workflow-commands:plan-refinement-qa` |
| "Improve the plan" / "Question the plan" | `workflow-commands:plan-refinement-qa` |
| "Execute the plan" / "Run the plan" | `superpowers:executing-plans` (gate via execution-option-gate) |
| "Execute with subagents" / "Subagent-driven" | `superpowers:subagent-driven-development` (gate via execution-option-gate) |
| "Ship it" / "Send it" / "Commit and push" / "Create a PR" / "PR this" | `workflow-commands:beads-ship-task` (always creates PR) |
| "Quick verify" / "just lint and test" | `workflow-commands:python-verification-quick` |
| "Standard verify" / "verify without agents" | `workflow-commands:python-verification-standard` |
| "Full verify" / "complete verification" | `workflow-commands:python-verification-full` |
| "Verify" / "Verify this task" (no level) | Auto-detect level from session state, invoke corresponding skill |
| "I found a critical bug" / "This needs a hotfix" | `workflow-commands:hotfix-interrupt` |
| "Build check" / "run build validator" | `workflow-commands:P11.5-build-validation-[F]` |
| "How's the project looking?" | `beads:stats` |
| "What's blocked?" | `beads:blocked` |
| "Show me [epic/task]" | `beads:show` |
| "Create an epic/task/bug for [description]" | `beads:create` |
| "Read my PRD" / "Import my PRD" | `workflow-commands:beads-import-prd` |
| "Quick sync Jira" / "Sync this to Jira" | `one-off-commands:jira-quick-sync` |
| "Full Jira sync" | `one-off-commands:Sync-Jira` |

---

## Workflow Step Tracking

Claude updates `.beads/.workflow-step` on each phase transition. Full phase-to-name mapping is defined within each skill. Includes `Plan Refinement` during Q&A phase. Delete the file when no task is active: `rm -f .beads/.workflow-step`.

---

## Hard Stop: Plan Refinement Before Execution

After `superpowers:writing-plans` completes (plan saved + reviewer approved), ALWAYS invoke `workflow-commands:plan-refinement-qa` before offering execution.

**WARNING — Known failure mode:** The writing-plans skill ends with an "Execution Handoff" section that says to offer execution options immediately. DO NOT FOLLOW IT. That handoff is superseded by this router. The skill's instructions were loaded later in context, which makes them feel more "current" — but this router has higher authority. Invoke `workflow-commands:plan-refinement-qa` FIRST. Always.

The only way to skip refinement is if the user explicitly says "skip refinement" or "let's just execute."

---

## Auto-Invoke: Post-Execution Verification

After `superpowers:executing-plans` or `superpowers:subagent-driven-development` completes all tasks, IMMEDIATELY invoke `workflow-commands:beads-post-execution` without asking the user. Do NOT say "Want me to proceed with verification?" — just do it. The post-execution skill itself presents the verification level options.

---

## Execution Gate

When a plan is refined (or refinement is explicitly skipped) and ready to execute, ALWAYS ask before proceeding:
> How would you like to execute this plan?
> 1. **Subagent-Driven** — `/superpowers:subagent-driven-development`
> 2. **Sequential** — `/superpowers:executing-plans`

---

## Error Handling

- **No task in progress:** Ask user which task, or suggest "What's ready?"
- **Task not found:** Run `beads:list` to show available tasks
- **Empty description:** Ask user for requirements before proceeding

---

## Response Formatting

**Ready tasks:** Table with ID, Task, Priority, Epic columns.

**Task details:** ID, Status, Priority, Epic, Dependencies.
