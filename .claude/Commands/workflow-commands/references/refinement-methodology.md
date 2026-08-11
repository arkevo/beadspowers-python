# Refinement Methodology (shared engine)

**This is a reference, not a slash command.** It is the single source of truth for
**how** to refine an implementation plan. Two adapters deliver it in two modes:

- **`plan-refinement-qa`** — the **interactive** adapter (live Q&A in main context).
- **`workflow-writing-plans` Step 4** — the **autonomous** adapter (auto-select inside
  a detached `Workflow`).

Neither adapter re-specifies the methodology below; they cite it and add only their
mode-specific delivery. Keep this file portable — refinement is stack-agnostic, so it
travels with the portable command set (no Python/Flutter/repo assumptions here).

---

## Decision Discovery

Read the plan and analyze it against **10 categories**, **dynamically ranked by rework
cost for THIS specific plan**. If a Planning-Context pass ran earlier in the session,
inherit its flagged risks to weight relevance (don't re-discover the same risks).

| Category | Scores High When… |
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

Score each category **High** (plan has a gap), **Medium** (plan has an explicit choice
worth validating), or **Skip** (irrelevant to this plan). Rank the High/Medium hits by
**rework cost** — the cost of getting the decision wrong and discovering it during
execution.

---

## Tier Taxonomy

Assign every surfaced decision a tier:

- **Critical** — A wrong decision causes rework during execution. Architecture, error
  handling, and testing choices that affect multiple files.
- **Recommended** — Improves quality but isn't load-bearing. Performance, naming,
  additional edge-case coverage.
- **Nice-to-have** — Polish. File organization, documentation approach, minor pattern
  preferences.

Order decisions **Critical → Recommended → Nice-to-have**.

---

## Per-Decision Anatomy

Every refinement decision — whether asked live or auto-selected — carries the same
fields:

- **Category** + **Tier** (from the sections above).
- **Quoted plan section** the decision questions (reference the specific text).
- **Why it matters** — the tradeoff / what could go wrong.
- **Options** — **at least two**, each with explicit **pros & cons** (gain vs. lose).
- **Recommended option** + a one-line **reasoning**.
- **Confidence flag** — `HIGH` (recommended option clearly better) or `CLOSE` (it barely
  edged the runner-up). `CLOSE` is a signal that the human should look harder.

---

## Recommendation Logic

Choose the recommended option by lowest rework cost + best fit to the plan's stated
goals and constraints (and, for a dependent plan, its upstream's pinned decisions).
Mark the confidence **`CLOSE`** whenever the top two options are within a hair of each
other — the recommendation is then a tie-break, not a verdict, and the human review
should weight it lightly.

---

## Mode Contract

Refinement runs in exactly one of two modes. **The caller passes the mode** — there is
nothing to detect, because the caller's execution context *is* the mode:

| Mode | Delivery | Selection | Caller |
|------|----------|-----------|--------|
| **`interactive`** | Present **one decision at a time**; wait for the user; iterate. | **The user** picks each option. | Main-context single-task path (`plan-refinement-qa`). |
| **`autonomous`** | Produce the **full batch at once** (no waiting). | **Auto-select** the recommended option per decision. | The detached `Workflow` fan-out (`workflow-writing-plans` Step 4). |

**Why the split is irreducible:** a detached `Workflow` **cannot pause for input**, so
`autonomous` mode *must* auto-select and defer every human decision to a single review
gate at the end. `interactive` mode can ask live. This delivery mechanism is the **only**
thing the two adapters may diverge on — discovery, tiers, anatomy, and recommendation
logic above are identical across both.

**Question budget** (the one knob each adapter owns — it follows from the mode, and the
two modes use deliberately different policies):

- **`interactive` — honest, anti-quota.** Build a prioritized queue (up to 10) ranked by
  genuine rework cost; ask the top ~5 this round, hold the rest for the continuation gate
  (soft cap 10). **No forced Critical** — assign each question its honest tier by real
  consequence, never to fill a slot or hit a count; when genuine Critical gaps run out,
  fall through to Recommended → Nice-to-have. **Don't pad** the queue with low-value
  questions — a small, sharp plan may yield fewer than 5 (or 10). The live human can
  always ask for more, so under-asking is safe.
- **`autonomous` — fixed quota.** 5 critical + 5 recommended per plan, auto-selected; no
  continuation gate (a detached Workflow can't iterate with the user). The fixed budget is
  deliberate: a single batched pass with no human in the loop must cover enough ground,
  so it does not under-ask.

---

## Output Contract

Each mode persists its decisions differently:

- **`interactive`** → append a `## Refinement Decisions` table to the plan file, inline-
  edit affected steps (mark `<!-- Refined: <category> -->`), and update the
  `plan_refinement` block in `.beads/.session-state.json`.
- **`autonomous`** → write every decision **verbatim** (question, all options w/
  pros&cons, reasoning, recommended/auto-selected, confidence) to
  `docs/plans/<epic-slug>/refinements.md`; a later Apply pass folds the (possibly
  user-overridden) decisions into each per-task plan file.

In both modes the human gets the final say — `interactive` live, `autonomous` at the
one end gate over `refinements.md`.
