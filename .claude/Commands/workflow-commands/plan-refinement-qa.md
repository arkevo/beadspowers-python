---
description: Plan Refinement Q&A — analyze plan for improvements, ask targeted questions one at a time with difficulty tiers, update plan with user decisions
---

# Plan Refinement Q&A

## Triggers

- **Auto-trigger** after `superpowers:writing-plans` completes (always, no prompt)
- **Auto-trigger** when user selects "Use existing plan" — but ONLY if the plan file does NOT contain a `## Refinement Decisions` section (already refined → skip)
- **Manual:** "refine the plan", "review the plan", "plan Q&A", "improve the plan", "question the plan"

## Workflow Step

```bash
echo "Plan Refinement" > .beads/.workflow-step
```

## Plan Analysis

1. Read the plan file from `docs/plans/` (path from session state `plan_file`)
2. If Planning Context skill ran earlier in the session, inherit its flagged risks — use those to weight category relevance (don't re-discover the same risks)
3. Analyze against 10 categories, dynamically ranked by rework cost for THIS specific plan:

| Category | Scores High When... |
|----------|-------------------|
| Scope Control | Plan includes work that should be separate tasks, or is too narrow |
| Architecture | Pattern choices (inheritance vs composition, constructor design) |
| Error Handling | Missing try-catch, unclear failure modes, silent errors |
| Testing Strategy | TDD gaps, missing edge case coverage, wrong test types |
| Data Flow | State management choices, API contracts, unnecessary rebuilds |
| Integration Points | Breaks existing callers, unclear interfaces |
| Performance | Unbounded lists, missing caching, expensive build() operations |
| Edge Cases | Null inputs, empty states, concurrent operations, race conditions |
| Dependencies | New packages when existing utilities exist, unmaintained deps |
| File Organization | Files in wrong feature directory, naming inconsistencies |

4. Score each category: **High** (plan has a gap), **Medium** (plan has explicit choice worth validating), **Skip** (irrelevant to this plan)
5. Select top 5 by score, rank by rework cost

## Difficulty Tier Assignment

Assign each of the 5 selected questions a tier:
- **Critical** — Wrong decision here causes rework during execution. Architecture, error handling, testing choices that affect multiple files.
- **Recommended** — Improves quality but isn't load-bearing. Performance optimizations, better naming, additional edge case coverage.
- **Nice-to-have** — Polish. File organization, documentation approach, minor pattern preferences.

Order questions: Critical first → Recommended → Nice-to-have.

## Q&A Loop

For each question, use this format:
```
**Question [N] of [total]** — [Category Name] `[TIER]`

[Quote or reference the specific plan section being questioned]
[Why this matters — what could go wrong, the tradeoff]

**Options:**
1. **[Name]** — [Description, 1-2 sentences]
   *Tradeoff: [what you gain vs what you lose]*

2. **[Name]** — [Description, 1-2 sentences]
   *Tradeoff: [what you gain vs what you lose]*

3. **[Name]** *(optional)* — [Description]
   *Tradeoff: [gain vs lose]*

**Recommended: Option [X]** — [1-sentence reasoning]

Say "1", "2", "3", or explain your preference.
```

**Tier-skip trigger:** When Claude reaches the first `[RECOMMENDED]` or `[NICE-TO-HAVE]` tier question (after all Critical questions are answered), add this note:

```
💡 Remaining questions are Recommended/Nice-to-have tier.
Say "skip to done" to finish with just the Critical decisions,
or continue for deeper refinement.
```

After the user answers, Claude:
1. Acknowledges the choice (1 line)
2. Records the decision (for plan update + session state)
3. Immediately asks the next question

## Continuation Gate (after Q5)

```
5 questions complete. Refinements recorded:
- [Category] `[TIER]`: [Choice summary]
- [Category] `[TIER]`: [Choice summary]
- ...

**Continue refining?**
1. **Ask 5 more** — deeper analysis on remaining categories
2. **Done** — update the plan and proceed to execution
```

If "more": Generate up to 5 more from remaining categories or deeper dives into already-covered ones.

**After question 10 (soft cap):**
```
All 10 categories covered. Refinements recorded:
- [all 10 summaries]

Plan update ready. Have a specific question about the plan?
Or say "done" to proceed to execution.
```

User can ask ad-hoc questions at this point. When they say "done", proceed to plan update.

## Bypass / Early Exit

When user says "skip refinement" / "looks good" / "done" / "skip" mid-Q&A:

1. Show remaining unanswered question titles (category names + tier only):
   ```
   Remaining questions (not yet asked):
   - Architecture `[CRITICAL]`
   - Edge Cases `[RECOMMENDED]`
   - File Organization `[NICE-TO-HAVE]`

   Cherry-pick any to answer? (say category name, or "done" to skip all)
   ```
2. User can pick specific categories by name → Claude asks those questions
3. When user says "done" → proceed to plan update with only answered questions

**Hard rule:** Claude MUST present at least the first question before the user can bypass. "Skip refinement" is the user's opt-out, never Claude's auto-skip.

## Plan File Update

After Q&A completes:

1. Read current plan file
2. **Append** Refinement Decisions section (before any "What's NOT in This Plan" section):

```markdown
---

## Refinement Decisions

Decisions from plan refinement Q&A on [YYYY-MM-DD]:

| # | Category | Tier | Decision | Rationale |
|---|----------|------|----------|-----------|
| 1 | [Cat] | Critical | [Choice] | [Why] |
| 2 | [Cat] | Recommended | [Choice] | [Why] |
```

3. **Inline-edit** affected plan steps — if a decision changes the implementation approach (e.g., adding error handling, changing a constructor pattern), modify those steps directly in the plan body. Mark inline changes with `<!-- Refined: [category] -->` comments for traceability.

4. Update session state:
   - Set `plan_refinement.completed` timestamp
   - Set `plan_refinement.questions_asked` and `plan_refinement.questions_answered`
   - Populate `plan_refinement.decisions` array with full detail per decision

## Transition to Execution Gate

After plan update:
```
Plan updated: `docs/plans/[filename]`
[N] refinements applied ([X] critical, [Y] recommended, [Z] nice-to-have).

Ready to execute.
```

Then immediately present the execution gate prompt (from execution-option-gate.md):
```
How would you like to execute this plan?

1. **Subagent-Driven (this session)** — Fresh subagent per task, review between tasks, fast iteration. Uses `/superpowers:subagent-driven-development`.
2. **Sequential Execution (this session)** — Execute tasks in batches of 3, pause for review between batches. Uses `/superpowers:executing-plans`.
```

## Natural Language Commands

| User Says | Action |
|-----------|--------|
| "1" / "2" / "3" / "4" | Select corresponding option |
| "more" / "ask more" / "keep going" | Continue with additional questions |
| "done" / "looks good" / "proceed" | Exit Q&A → cherry-pick prompt → plan update |
| "skip refinement" / "skip" | Same as "done" |
| "skip to done" | Skip remaining non-Critical questions → plan update |
| "explain option [N]" | Elaborate on a specific option before choosing |
| "what about [topic]?" | Claude adds that topic as an ad-hoc question |
| "go back" / "change my answer to [N]" | Revise a previous answer |

## Session State Schema

During refinement, update `.beads/.session-state.json` with:

```json
{
  "plan_refinement": {
    "started": "2026-01-24T09:15:00Z",
    "completed": "2026-01-24T09:25:00Z",
    "questions_asked": 5,
    "questions_answered": 5,
    "skipped": false,
    "decisions": [
      {
        "category": "Error Handling",
        "tier": "Critical",
        "question_summary": "Add try-catch to repository fetch?",
        "chosen_option": "Fail-open with ErrorLogger",
        "option_number": 2,
        "was_recommended": false
      }
    ]
  }
}
```

**Write timing:**
- On refinement start: Set `plan_refinement.started`, reset `decisions` to []
- After each answered question: Append to `plan_refinement.decisions` with full detail
- On refinement complete: Set `plan_refinement.completed`, `questions_asked`, `questions_answered`
- On skip: Set `plan_refinement.skipped: true`, `plan_refinement.completed`
