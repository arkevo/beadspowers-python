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
2. Calculate `total_lines_changed` from session state
3. If session state unavailable, ask user for file list

---

## Phase 2: Lint Issues Fix

### Step 1: Run Static Analysis

Run ruff and mypy on changed files only:

```bash
ruff check <changed_files>
mypy <changed_files>
```

### Step 2: Auto-Fix

Run ruff auto-fix to resolve common issues:

```bash
ruff check --fix <changed_files>
```

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

## Quick Verification Report

```markdown
## Quick Verification Report

### Summary
Ran lint + tests on [N] changed files ([M] lines total).

### Lint Results
**Auto-fixed:** [N] issues with ruff --fix
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
| Lint analysis | `ruff check <files>` via Bash |
| Type checking | `mypy <files>` via Bash |
| Auto-fix | `ruff check --fix <files>` via Bash |
| Run tests | `pytest <files> -v` via Bash |
| Track files | `.beads/.session-state.json` |

---

## Notes

- Quick verification is **NOT** comprehensive
- Use Standard or Full for complex changes
- Does not run architecture validation, type analysis, or coverage agents
- Suitable for confident, small changes
