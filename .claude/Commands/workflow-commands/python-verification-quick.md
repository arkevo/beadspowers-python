---
name: python-verification-quick
description: Quick verification - lint and tests only. Use for changes < 50 lines.
---

# Python Quick Verification

For small changes (< 50 lines), run only essential checks: lint + tests.

---

## When to Use

- Changes affect < 50 lines of code
- Documentation-only changes
- Single-line fixes or trivial changes
- High confidence in the change
- User explicitly requests "quick verify" or "lint and test only"

---

## Phase 1: Gather Context (Minimal)

### Identify Changed Files

1. Read `modified_files` from `.beads/.session-state.json`
2. Read `total_lines_changed` from the same file
3. If the file is missing or unreadable, **or** `modified_files` is an empty list,
   the changed set is **UNKNOWN**. Do not ask the user for a file list in order to
   auto-fix, and do not fall back to the project root: Phase 2 Step 2 skips
   instead (`.claude/rules/verification-write-scope.md`). A list the user
   volunteers unprompted is a valid changed set; echo it back in the report.
   Write it into `modified_files` first, as `.claude/rules/verification-write-scope.md`
   describes, so the write blocks see it.

---

## Phase 2: Lint Issues Fix

### Step 1: Run Static Analysis

Run ruff and mypy on the changed files. Analysis only reads, so when the changed
set is UNKNOWN, run the same two commands on `src/ tests/` instead:

```bash
ruff check --no-fix <changed_files>
mypy <changed_files>
```

### Step 2: Auto-Fix — scoped to the changed set, or skipped

Never auto-fix outside the task's changed set. Run the `scoped-ruff-fix` block
from `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged (policy:
`.claude/rules/verification-write-scope.md`). In short, it reads the changed set; skips without calling ruff when the
set is UNKNOWN or holds no Python files; previews with `ruff check --diff`, a dry
run that writes nothing; applies `ruff check --fix --force-exclude` to the changed
Python files only (`--force-exclude` keeps ruff's own exclude list in force for
files named on the command line); and then compares `git status` with its
snapshot, restoring and reporting any file outside the set that changed.

Record its `Auto-fixed:` and `Scope check:` lines in the report.

### Step 3: Report Remaining Issues

If issues remain after auto-fix:
- List each issue with file:line
- Categorize as Error/Warning
- Quick verification should NOT fix manual issues - report and continue

---

## Phase 11: Run Tests

### Step 1: Identify Affected Tests

For each changed file in `src/`:
- Find corresponding test in `tests/` (mirror structure)
- Example: `src/features/auth/service.py` → `tests/features/auth/test_service.py`

### Step 2: Execute Tests

Run affected tests:

```bash
pytest <affected_test_files> -v
```

If no specific test files found, run all tests:

```bash
pytest -v
```

### Step 3: Report Results

- If tests **PASS**: Verification complete
- If tests **FAIL**: Report failures and stop

---

## Phase 12: Write Verification Marker (ONLY on PASS)

The router's *Hard Stop: Verification Before Ship / "Done"* and `workflow-commands:beads-ship-task`
gate on this marker. Write it ONLY after tests pass — never on failure:

```bash
TASK=$(python3 -c "import json;print(json.load(open('.beads/.session-state.json')).get('task_id',''))" 2>/dev/null)
printf '{"level":"quick","task":"%s","passed":true,"at":"%s"}\n' "$TASK" "$(date -u +%FT%TZ)" > .beads/.verification-done
```

If tests FAILED, do NOT write the marker (leave any prior one; the gate stays closed).

---

## Quick Verification Report

```markdown
## Quick Verification Report

### Summary
Ran lint + tests on [N] changed files ([M] lines total).

### Lint Results
**Auto-fixed:** [N] issues across [M] changed files
*(or:* `SKIPPED (changed set unknown)` *or* `SKIPPED (no Python files in the changed set)` *)*
**Scope check:** no files outside the changed set / **LEAK: [list]**
**Remaining:** [N] issues
- `file:line` - [issue description]

### Test Results
**Status:** [PASS / FAIL]
**Tests run:** [N] tests in [M] files
**Failures:** [list if any]

### Recommendation
**Ready for:** commit / PR creation
*Or:* Address [N] remaining issues before completion.
```

---

## Triggers

Invoke this skill when:

- User says "quick verify" or "lint and test only"
- User says "just run the tests"
- Workflow integration detects < 50 lines changed
- User explicitly chooses Quick level from post-execution options

---

## Quick Reference

| What | How |
|------|-----|
| Lint analysis | `ruff check --no-fix <files>` via Bash |
| Type checking | `mypy <files>` via Bash |
| Auto-fix | the `scoped-ruff-fix` block from `.claude/Commands/workflow-commands/references/scoped-ruff.md` — changed set only, never unscoped |
| Run tests | `pytest <files> -v` via Bash |
| Track files | `.beads/.session-state.json` (`modified_files`) |
| Changed set unknown | Skip auto-fix. Never widen to the project root. |

---

## Notes

- Quick verification is **NOT** comprehensive
- Use Standard or Full for complex changes
- Does not run architecture validation, type analysis, or coverage agents
- Suitable for confident, small changes
