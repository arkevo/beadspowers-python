---
name: python-verification-standard
description: Standard verification - analysis phases without parallel agents. Use for 50-200 line changes.
---

# Python Standard Verification

For medium changes (50-200 lines), run analysis phases without spawning parallel
agents. This provides thorough code review without the overhead of agent
orchestration.

---

## When to Use

- Changes affect 50-200 lines of code
- Single feature additions or bug fixes
- Moderate complexity changes
- User explicitly requests "standard verify" or "verify without agents"
- Default choice when change size is medium

---

## Phase 1: Gather Context

Before reviewing any code:

### Step 1: Identify Changed Files

- Read `modified_files` from `.beads/.session-state.json`
- If session state unavailable, ask user for file list
- Note which directories/layers were affected
- **Scope all subsequent phases to ONLY these files**

### Step 2: Gather Relevant Rules

- Read `.claude/rules/` files in affected directories
- Read root-level rules applicable to the changes
- Note specific requirements for the modified code

### Step 3: Understand the Change

- Summarize what was changed and why
- Identify scope: new feature, bug fix, refactor, etc.

---

## Phase 2: Lint Issues Fix

**Run this early to clean up code before deeper analysis.**

### Step 1: Run Static Analysis

Run ruff and mypy on changed files only:

```bash
ruff check <changed_files>
mypy <changed_files>
```

### Step 2: Categorize Issues

| Severity | Action |
|----------|--------|
| **Errors** | Must fix - code won't run or has critical issues |
| **Warnings** | Should fix - potential bugs |
| **Info/Hints** | Consider fixing if quick |

### Step 3: Auto-Fix

Run `ruff check --fix` to automatically resolve:
- Unused imports
- Import sorting
- Simple style issues
- Trailing whitespace

### Step 4: Manual Fixes (if needed)

Address remaining errors and warnings:
1. Fix errors first (blocking)
2. Address warnings that could cause runtime issues
3. Apply quick style fixes

### Step 5: Verify Fixes

Run `ruff check` again to confirm resolution.

---

## Phase 3: Code Review Checks

Review ONLY the changed files identified in Phase 1.

### Check #1: Rules Compliance

Audit changes against `.claude/rules/`:
- Code structure and organization
- Naming conventions
- Documentation requirements
- Testing requirements
- Python best practices

### Check #2: Bug Scan

Shallow scan for obvious bugs:
- Type annotation issues
- Missing error handling
- Incorrect async/await usage
- Resource management (unclosed files, connections)
- Thread safety / async issues
- Resource leaks (unclosed files, database connections)

**Focus on:** Large bugs, not nitpicks. Ignore what linter catches.

### Check #3: Historical Context

Review context of modified files:
- Check Beads task description for original intent
- Review `.beads/.session-state.json` for task requirements
- Verify changes align with task's stated goals

### Check #4: Code Comments Compliance

Read comments in modified files:
- Ensure changes comply with TODO/FIXME guidance
- Check existing documentation accuracy
- Verify "don't modify" warnings are respected

### Check #5: Test Coverage

Verify tests exist and pass:
- Check for corresponding test files
- Run tests on affected files
- Note if edge cases are covered

---

## Phase 4: Architecture Validation

Validate architecture for changed files and immediate dependencies.

### Layer Compliance Check

| Layer | Purpose | Allowed Dependencies |
|-------|---------|---------------------|
| **API/CLI** | Routes, CLI commands, entry points | Services, Core |
| **Services** | Business logic, orchestration | Domain, Data, Core |
| **Domain** | Core business rules, entities | Core only |
| **Data** | Repositories, database access | Core only |
| **Core** | Shared utilities, config | None (leaf layer) |

**Detect:**
- API/CLI layer importing Data directly
- Data layer containing business logic
- Circular dependencies between layers

### SOLID Principles Check

| Principle | Verify |
|-----------|--------|
| **S**ingle Responsibility | Each class/module has ONE reason to change |
| **O**pen/Closed | Extend via composition, not modification |
| **L**iskov Substitution | Subclasses are substitutable |
| **I**nterface Segregation | Small, focused ABCs/Protocols |
| **D**ependency Inversion | Depend on abstractions |

### Class Design Check

- Small, focused classes with single responsibility
- Composition over inheritance
- `@dataclass(frozen=True)` for value types
- No business logic in `__init__`
- No side effects in properties

### Code Quality Standards

- Functions: < 20 lines, single purpose
- Line length: <= 88 characters (ruff default)
- Naming: PascalCase (classes), snake_case (everything else)
- Error handling: try-except with specific exceptions
- Type hints on all public functions
- Logging: Use `logging` module (NOT print)

---

## Phase 5: Code Simplification Review

Focus on recently modified code and evaluate:

### Clarity Enhancements

- [ ] Reduced unnecessary complexity?
- [ ] Large functions (>20 lines) broken into smaller functions?
- [ ] Generators or itertools for large sequences?
- [ ] No expensive operations in properties?
- [ ] Clear variable and function names?
- [ ] Structural pattern matching where it simplifies code?

### Python Standards

- [ ] Frozen dataclasses for value types?
- [ ] Composition over class inheritance?
- [ ] Type hints on public APIs?
- [ ] Google-style docstrings for public APIs?
- [ ] List comprehensions where clearer than loops?
- [ ] Context managers for resource management?
- [ ] F-strings for string formatting?

### Balance Check (Avoid Over-Simplification)

- [ ] Not removing helpful abstractions?
- [ ] Not combining too many concerns?
- [ ] Proper separation of concerns maintained?
- [ ] Code remains debuggable and extensible?

---

## Phase 9: Confidence Scoring

For each issue found (Phases 3-5), assign a confidence score:

| Score | Meaning |
|-------|---------|
| 0 | False positive |
| 25 | Might be real, could be false positive |
| 50 | Real but minor/nitpick |
| 75 | Verified real, important |
| 100 | Definitely real, will happen frequently |

**Only report issues with score >= 80**

---

## Phase 10: False Positive Filtering

Exclude from final report:
- Pre-existing issues (not introduced by current changes)
- Issues already fixed by Phase 2
- Pedantic nitpicks a senior engineer wouldn't flag
- General quality issues unless in `.claude/rules/`
- Issues silenced by noqa comments
- Intentional changes related to the task
- Issues on lines not modified

---

## Phase 11: Final Verification

Run final verification sequence:

1. `ruff check <changed_files>` via Bash - Confirm no lint errors
2. `ruff format --check <changed_files>` via Bash - Ensure consistent formatting
3. `pytest -v` via Bash - Execute all tests

**All must pass before claiming completion.**

---

## Phase 14: Security Review (Auto-Triggered)

**This phase auto-triggers when changed files match sensitive patterns.**

### Auto-Trigger Detection

Check if any changed files match:

**Path patterns:**
- `src/**/auth/**`
- `src/**/api/**`
- `src/**/service*/**`
- `src/**/repository/**`
- `src/**/network/**`

**Content patterns (file contains):**
- `apiKey`, `api_key`, `secret`, `token`, `password`
- `requests`, `httpx`, `http`

### If Triggered: Run Security Checks

1. **Hardcoded secrets scan** - Check for API keys, tokens in code
2. **HTTPS enforcement** - Verify no HTTP URLs (except localhost)
3. **Environment variables** - Sensitive data uses env vars or python-dotenv, not hardcoded
4. **SQL injection** - No raw SQL queries with user input
5. **Dangerous functions** - No `eval()`, `exec()`, `pickle.loads()` on untrusted data
6. **Subprocess safety** - No `shell=True` with user input
7. **SSL verification** - No `verify=False` in requests/httpx
8. **Debug mode** - No `DEBUG=True` in production config
9. **Error exposure** - Errors don't leak internal details to users

### If NOT Triggered

Skip this phase - no sensitive files modified.

---

## Standard Verification Report

```markdown
## Standard Verification Report

### Architecture Score: X/10

### Summary
Ran standard verification on [N] files ([M] lines).
Found [X] issues. [Y] auto-fixed. [Z] require attention.

---

### Lint Results (Phase 2)
**Auto-fixed:** [N] issues
**Manual fixes needed:**
- `file:line` - [description]

---

### Code Review Issues (Phase 3)

#### Issue 1: [Brief description]
**Confidence:** [score]%
**Source:** [rules compliance / bug scan / etc.]
**File:** `path/to/file.py:line`
**Suggested fix:** [how to resolve]

---

### Architecture Violations (Phase 4)

| Layer | Status | Issue |
|-------|--------|-------|
| API/CLI | OK/WARN | Description |
| Services | OK/WARN | Description |
| Domain | OK/WARN | Description |
| Data | OK/WARN | Description |
| Core | OK/WARN | Description |

---

### Simplification Opportunities (Phase 5)

1. **[File/Class]:** [Opportunity]
   - Before: [description]
   - After: [suggestion]

---

### Test Results (Phase 11)
**Status:** [PASS / FAIL]
**Tests:** [N] tests in [M] files

---

### Recommendation
**Ready for:** commit / PR creation
*Or:* Address [N] issues before completion.

---

**Note:** Standard verification does not include:
- Type design analysis (agent)
- Silent failure hunt (agent)
- Comment analysis (agent)
- Test coverage analysis (agent)
- Package build validation

Use **Full verification** for comprehensive checks.
```

---

## Triggers

Invoke this skill when:

- User says "standard verify" or "verify without agents"
- User says "verify" with 50-200 lines changed
- Workflow integration detects medium change size
- User chooses Standard from post-execution options

---

## What Standard Verification Does NOT Include

| Phase | Description | Why Excluded |
|-------|-------------|--------------|
| 6 | Type Design Analysis | Requires agent |
| 7 | Silent Failure Hunt | Requires agent |
| 8 | Comment Analysis | Requires agent |
| 11.5 | Package Build Validation | Time-intensive |
| 12 | Test Coverage Analysis | Requires agent |

For comprehensive verification, use `/python-verification-full`.
