---
description: Post-execution options after plan execution completes - verification level detection, build validator, smoke test
---

# Post-Execution Options

After **any** implementation path completes — `execute-plans` /
`subagent-driven-development`, the **bug path** (`systematic-debugging → TDD`), or
any **direct TDD** fix — determine verification level and offer options. This is
mandatory before ship/"done" (see the router's *Hard Stop: Verification Before
Ship / "Done"*); it is NOT limited to plan-execution. The chosen
`python-verification-{level}` skill writes the `.beads/.verification-done` marker
that `beads-ship-task` gates on.

## Step 1: Update Workflow Step
```bash
echo "Post-Execution" > .beads/.workflow-step
```

## Step 2: Level Detection

Read `.beads/.session-state.json`:
1. Check `modified_files` array and `total_lines_changed`
2. Determine level:
   - **< 50 lines:** Quick (lint + tests)
   - **50-200 lines:** Standard (analysis, no agents)
   - **200+ lines or new files:** Full (all 14 phases)

If `modified_files` is empty or missing, ask:
> What files did you change? (Or say "quick", "standard", or "full" to select level)

## Step 3: Build Validator Check

| Change Type | Recommend | Reason |
|-------------|-----------|--------|
| New C extension or native dependency | **Yes** | Native compilation may fail silently |
| pyproject.toml changes (build-system, dependencies) | **Yes** | Build-breaking misconfigs |
| New dependency with native components | **Yes** | Native compilation may fail |
| Pure Python logic, services, utilities | No | Tests import the code |
| Test-only changes | No | No build impact |
| Config/tooling changes (.claude/, .beads/) | No | No build impact |

## Step 4: Smoke Test Check

| Change Type | Recommend | Why |
|-------------|-----------|-----|
| CLI/API endpoint changes | **Yes** | Manual verification confirms expected behavior |
| Template/rendering changes | **Yes** | Visual correctness needs human eyes |
| New native extension integration | **Yes** | Native failures surface at runtime |
| Pure data layer (repositories, models, services) | **Skip** | No user-facing output |
| Test-only / config changes | **Skip** | No app behavior change |

## Step 5: Show Prompt

```
✅ Execution complete for **bd-xxxx "[Task Title]"**

Changes: [N] lines across [M] files (tracked during execution)

**Verification options:**
1. **Quick verify** — lint + tests only (~30 sec)
2. **Standard verify** — analysis phases, no agents (~2 min)
3. **Full verify** — all 14 phases with agents (~5+ min)
4. **Ship it** — skip verification, commit

Recommended: **[Level based on change size]**
[⚙️ Build validation recommended — say "build check" anytime]  ← include if applicable
[🔥 Smoke test recommended after verification]  ← include if applicable

Say "quick", "standard", "full", or "ship it" to continue.
```

## Natural Language Commands

| User Says | Action |
|-----------|--------|
| "Quick verify" / "just lint and test" | Invoke `workflow-commands:python-verification-quick` |
| "Standard verify" / "verify without agents" | Invoke `workflow-commands:python-verification-standard` |
| "Full verify" / "complete verification" | Invoke `workflow-commands:python-verification-full` |
| "Ship it" / "Send it" | Invoke `workflow-commands:beads-ship-task` |
| "I'm confident" / "Skip verification" | Invoke `workflow-commands:beads-ship-task` |
| "Build check" / "run build validator" | Invoke `workflow-commands:P11.5-build-validation-[F]` |
| "Smoke test" / "run the app" | Run app manually, guide visual check |
| "actually do full verify" | Override level, invoke full verification |

---

## Post-Verification Smoke Test

After verification passes and before ship, show:

```
✅ Verification passed.

🔥 **Smoke test?** (optional)
Run the app locally to confirm changes work.

1. **Run locally** — Quick launch via terminal
2. **Skip** — Ship based on tests alone

Recommended: **[Run / Skip]** — [reason based on change type]
```

During smoke test:
```bash
echo "Smoke Test" > .beads/.workflow-step
```

When user confirms app works → stop app → proceed to `workflow-commands:beads-ship-task`.

If user finds an issue → stop app → fix → re-run verification (at least quick) → offer smoke test again.

---

## CRITICAL — Project Override

Do NOT invoke `finishing-a-development-branch` after execution completes. This project uses `workflow-commands:beads-ship-task` and commit-commands skills instead.
