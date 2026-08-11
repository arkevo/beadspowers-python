---
name: python-verification-full
description: Full 13-phase verification with parallel agents. Use for 200+ line changes or new modules.
---

# Python Full Verification Workflow

**Section:** Code Quality

When running verification before completion in this Python project, use the
combined methodologies from P02-lint-issues-fix, P03-code-review-checks,
P04-architecture-validation, P05-code-simplification, P06-type-design-analysis,
P07-silent-failure-hunt, P08-comment-analysis, P12-test-coverage-analysis, and
P14-security-review. This ensures thorough quality checks before claiming
work is complete.

---

## Integration with Superpowers Verification

**IMPORTANT:** When running `/superpowers:verification-before-completion` in
**this Python project**, follow this comprehensive workflow that integrates
eight Python quality methodologies. This workflow is specific to this project
and should be used whenever verifying completed work before committing or
creating PRs in this codebase.

---

## Phase 1: Gather Context

Before reviewing any code:

### Step 1: Identify Changed Files
- Read `modified_files` from `.beads/.session-state.json` (tracks files changed during execution)
- If session state is empty or missing, ask user: "What files did you change?"
- Note which directories/layers were affected
- **Scope all subsequent phases to ONLY these files**

### Step 2: Gather Relevant Rules
- Read `.claude/rules/` files in affected directories
- Read root-level `.claude/rules/` applicable to the changes
- Note specific requirements that apply to the modified code

### Step 3: Understand the Change
- Summarize what was changed and why
- Identify the scope: new feature, bug fix, refactor, etc.

---

## Phase 2: Lint Issues Fix (from P02-lint-issues-fix)

**Run this early to clean up code before deeper analysis.**

### Step 1: Run Static Analysis
Run `ruff check <changed_files>` and `mypy <changed_files>` via Bash on the
changed files only (not entire codebase).

### Step 2: Categorize Issues
Group discovered issues by severity:

| Severity | Action |
|----------|--------|
| **Errors** | Must fix - code has critical issues or type violations |
| **Warnings** | Should fix - potential bugs or problematic patterns |
| **Info/Hints** | Consider fixing - style suggestions (fix if quick) |

### Step 3: Auto-Fix
Run `ruff check --fix <changed_files>` via Bash to automatically resolve:
- Unused imports
- Import sorting
- Style fixes
- Whitespace and formatting issues

### Step 4: Manual Fixes (if needed)
Address remaining errors and warnings:
1. Fix errors first (blocking issues)
2. Address warnings that could cause runtime problems
3. Apply quick style fixes for consistency
4. Skip info-level hints unless specifically requested

### Step 5: Verify Fixes
Run `ruff check <changed_files>` and `mypy <changed_files>` again on changed
files to confirm issues resolved.

**Important:** Do not introduce new warnings while fixing existing ones.

---

## Phase 3: Code Review Checks (from P03-code-review-checks)

Review ONLY the changed files identified in Phase 1.

### Check #1: Rules Compliance
Audit the changes against `.claude/rules/`:
- Code structure and organization rules
- Naming conventions
- Documentation requirements
- Testing requirements
- Python best practices defined in rules

### Check #2: Bug Scan
Shallow scan for obvious bugs:
- Type annotation issues
- Missing error handling
- Incorrect async/await usage
- Resource management (unclosed files, connections)
- Thread safety / async issues
- Resource leaks (unclosed files, database connections)

**Focus on:** Large bugs, not nitpicks. Ignore what linter/analyzer catches.

### Check #3: Historical Context
Review context of modified files:
- Check Beads task description for original intent
- Review `.beads/.session-state.json` for task requirements
- Verify changes align with the task's stated goals

### Check #4: Code Comments Compliance
Read code comments in modified files:
- Ensure changes comply with any TODO/FIXME guidance
- Check that existing documentation is still accurate
- Verify any "don't modify" or warning comments are respected

### Check #5: Test Coverage
Verify tests exist and pass:
- Check for corresponding test files
- Run `pytest <affected_test_files> -v` via Bash
- Verify edge cases are covered

---

## Phase 4: Architecture Validation (from P04-architecture-validation)

Validate architecture ONLY for changed files and their immediate dependencies.

### Layer Compliance Check
Validate 5-layer architecture:

| Layer | Purpose | Allowed Dependencies |
|-------|---------|---------------------|
| **API/CLI** | Routes, CLI commands, entry points | Services, Core |
| **Services** | Business logic, orchestration | Domain, Data, Core |
| **Domain** | Core business rules, entities | Core only |
| **Data** | Repositories, database access | Core only |
| **Core** | Shared utilities, config | None (leaf layer) |

**Violations to detect:**
- API/CLI layer importing Data layer directly
- Data layer containing business logic
- Circular dependencies between layers

### SOLID Principles Check

| Principle | What to Verify |
|-----------|----------------|
| **S**ingle Responsibility | Each module/class has ONE reason to change |
| **O**pen/Closed | Extend via composition, not modification |
| **L**iskov Substitution | Subclasses are substitutable |
| **I**nterface Segregation | Small, focused abstract classes/protocols |
| **D**ependency Inversion | Depend on abstractions, not concretions |

### Code Quality Standards
- Functions: **< 20 lines**, single purpose
- Line length: **<= 88 characters** (ruff default)
- Naming: snake_case (functions, variables, modules), PascalCase (classes), UPPER_CASE (constants)
- Error handling: try-except with specific exception types
- Type hints: Required on all public functions
- Logging: Use `logging` module (NOT print)

---

## Phase 5: Code Simplification Review (from P05-code-simplification)

Focus on recently modified code and evaluate:

### Clarity Enhancements
- [ ] Reduced unnecessary complexity and deep nesting?
- [ ] Large functions broken into smaller focused functions?
- [ ] Using generators or list comprehensions where appropriate?
- [ ] No expensive operations in hot paths?
- [ ] Clear variable and function names?
- [ ] Pattern matching used where it simplifies code?
- [ ] Explicit code preferred over overly compact solutions?

### Python Standards
- [ ] Frozen dataclasses used for immutable value types?
- [ ] Composition preferred over class inheritance?
- [ ] Proper type hints on all public APIs?
- [ ] Google-style docstrings for public APIs?
- [ ] f-strings used instead of string concatenation?
- [ ] Context managers used for resource management?

### Balance Check (Avoid Over-Simplification)
- [ ] Not removing helpful abstractions?
- [ ] Not combining too many concerns?
- [ ] Proper separation of business logic and I/O maintained?
- [ ] Code remains easy to debug and extend?

---

## Phase 6: Type Design Analysis (from P06-type-design-analysis)

> **USE AGENT:** Launch `verification-type-analyzer` agent via Task tool.
> See [Agent Orchestration](#agent-orchestration) for parallel execution details.

**Parallel Group A** - Can run simultaneously with Phases 7-8 and Codex Adversarial Review.

**Scope:** New or modified classes/types in changed files only.

### Step 1: Identify Types to Analyze
From Phase 1 changed files, identify:
- New class definitions
- Modified class definitions
- New TypeAlias / type alias definitions
- New enums with complex logic

### Step 2: Run Type Analysis
For each identified type, evaluate on a 1-10 scale:

| Criterion | What to Check |
|-----------|---------------|
| **Encapsulation** | Are fields private? Is internal state hidden? |
| **Invariant Expression** | Does the type express its constraints clearly? |
| **Invariant Usefulness** | Are the constraints meaningful and helpful? |
| **Invariant Enforcement** | Are constraints enforced at construction/mutation? |

### Step 3: Python-Specific Checks
- Type hint completeness (no missing annotations)
- Frozen dataclasses where applicable
- Proper `__post_init__` validation for types with invariants
- Factory classmethods for complex construction
- Mutable default arguments (classic Python footgun)
- Missing `frozen=True` on dataclasses that should be immutable

### Step 4: Flag Issues
Only report types with:
- Any rating below 6/10
- Critical anti-patterns:
  - Mutable default arguments
  - Missing `frozen=True` on value-type dataclasses
  - Public mutable state without protection
  - Unvalidated constructors for types with invariants

---

## Phase 7: Silent Failure Hunt (from P07-silent-failure-hunt)

> **USE AGENT:** Launch `verification-silent-failure` agent via Task tool.
> See [Agent Orchestration](#agent-orchestration) for parallel execution details.

**Parallel Group A** - Can run simultaneously with Phases 6, 8, and Codex Adversarial Review.

**Scope:** Error handling code in changed files only.

### Step 1: Identify Error Handling Code
In changed files, locate:
- `try-except` blocks
- Null coalescing with fallbacks (`or`, `if x is None`)
- `Result` type pattern usage
- Bare `except: pass` blocks
- `except Exception: pass` blocks

### Step 2: Audit Each Handler

| Pattern | Severity | Check |
|---------|----------|-------|
| Bare `except: pass` | **CRITICAL** | Must log or handle meaningfully |
| `except Exception: pass` | **CRITICAL** | Must log or handle meaningfully |
| Catching broad `Exception` | **HIGH** | Should catch specific types |
| Missing `logging` usage | **MEDIUM** | Should use project's logging module |
| Silent fallbacks | **HIGH** | User should know something failed |
| Async without error handling | **HIGH** | Unhandled coroutine errors |

### Step 3: Check Fallback Behavior
For each fallback value found:
- Is the fallback appropriate?
- Does the user get feedback about the failure?
- Could the failure cascade to worse problems?

### Step 4: Report Issues
Format for each issue:
```
Location: file:line
Severity: CRITICAL/HIGH/MEDIUM
Pattern: [what was found]
Hidden Errors: [what gets silently dropped]
User Impact: [how user is affected]
Recommendation: [how to fix]
```

---

## Phase 8: Comment Analysis (from P08-comment-analysis)

> **USE AGENT:** Launch `verification-comment-analyzer` agent via Task tool.
> See [Agent Orchestration](#agent-orchestration) for parallel execution details.

**Parallel Group A** - Can run simultaneously with Phases 6-7 and Codex Adversarial Review.

**Scope:** Documentation comments in changed files only.

### Step 1: Identify Comments to Analyze
In changed files, locate:
- Google-style docstrings on new/modified public APIs
- Inline comments (`#`) near changed code
- Module-level documentation
- TODO/FIXME comments

### Step 2: Verify Accuracy
For each comment, cross-reference against actual code:

| Check | What to Verify |
|-------|----------------|
| Parameter docs | Do they match actual parameters? |
| Return type docs | Does it match the actual return? |
| Exception docs | Are raised exceptions documented? |
| Behavior claims | Does code actually do what comment says? |

### Step 3: Check Docstring Compliance
- Single-sentence summary as first line
- Blank line before detailed description
- Args section documents all parameters
- Returns section documents return value
- Raises section documents exceptions
- No redundant information

### Step 4: Report Issues

| Issue Type | Severity | Example |
|------------|----------|---------|
| Factually incorrect | **CRITICAL** | Comment says "returns None" but raises |
| Missing required docs | **HIGH** | Public API without documentation |
| Outdated after refactor | **HIGH** | Parameter renamed but not in docs |
| Redundant/obvious | **LOW** | `# The name` for `self.name = name` |
| Style violation | **LOW** | Missing period at end of summary line |

---

## Phase 8.7: Codex Adversarial Review (GPT-5.4)

> **EXTERNAL AGENT:** Runs via Codex CLI in parallel with Phases 6-8.
> See [Agent Orchestration](#agent-orchestration) for execution details.

**Parallel Group A** - Launches alongside the Claude verification agents.

**Purpose:** Independent adversarial review from a different AI model (GPT-5.4).
Codex defaults to skepticism and targets failure modes that static analysis and
Claude's agents may miss: auth boundaries, data corruption, race conditions,
rollback safety, stale state, and observability gaps.

### Execution

Launch Codex adversarial review in background via Bash (runs in parallel with
Claude agents — does NOT block them):

```bash
node "/Users/arkevo/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs" adversarial-review --background
```

**Note:** Use `--background` so it runs concurrently. Check results later with:

```bash
node "/Users/arkevo/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs" result --json
```

### Collecting Results

After Phases 6-8 agents return, check if Codex has completed:

1. Run the `result` command above
2. Parse the JSON response for `verdict` and `findings`
3. If Codex is still running, proceed with Phase 8.5 (apply agent edits) and
   check Codex again before Phase 9
4. If Codex timed out or failed, note in report as "Codex review: unavailable"

### Codex Finding Format

Codex returns structured JSON with:
- `verdict`: `approve` or `needs-attention`
- `findings`: array of issues with `file`, `line_start`, `line_end`,
  `confidence` (0-1), `body`, and `recommendation`

### Merging Codex Findings

Map Codex findings into the unified findings list:
- `confidence` 0-1 → multiply by 100 for the 0-100 scale
- `needs-attention` verdict → treat findings as HIGH severity minimum
- Apply the same Phase 10 false-positive filtering to Codex findings
- Deduplicate against Claude agent findings (same file + overlapping lines)

---

## Phase 9: Confidence Scoring

For each issue found (from Phases 3-8 and Codex 8.7), assign a confidence score:

| Score | Meaning |
|-------|---------|
| 0 | False positive - doesn't hold up to scrutiny |
| 25 | Might be real, but could be false positive |
| 50 | Real issue, but minor/nitpick |
| 75 | Verified real issue, important, will impact functionality |
| 100 | Definitely real, will happen frequently |

**Only report issues with score >= 80**

---

## Phase 10: False Positive Filtering

Exclude these from the final report:

- Pre-existing issues (not introduced by current changes)
- Issues already fixed by Phase 2 (lint fixes)
- Pedantic nitpicks a senior engineer wouldn't flag
- General quality issues unless explicitly in `.claude/rules/`
- Issues silenced by `noqa` comments
- Intentional changes related to the broader task
- Issues on lines not modified in current work

---

## Phase 11: Final Verification

Run final verification sequence:
1. `ruff check <changed_files>` via Bash - Confirm no lint errors remain
2. `ruff format --check <changed_files>` via Bash - Ensure consistent formatting
3. `pytest -v` via Bash - Execute all tests

**All must pass before claiming completion.**

---

## Phase 11.5: Build Validation (from P11.5-build-validation)

**Prerequisite:** Phase 11 must pass (tests must run successfully).

**Purpose:** Verify the Python package actually builds and the environment is
healthy. Code can pass `ruff check` and `pytest` but fail to install or build
due to missing dependencies, broken entry points, or packaging configuration
errors.

### Step 1: Invoke Build Validator Skill

Invoke `/P11.5-build-validation` to perform comprehensive build checks:
- Build environment validation (Python version, virtual environment, CLI tools)
- Dependency validation (`pip install -e ".[dev]"`, `pip check`)
- Static analysis (`ruff check`, `mypy`)
- Package build (`python -m build`)

### Step 2: Report Build Status

| Status | Meaning | Action |
|--------|---------|--------|
| **PASS** | Environment and package build successfully | Continue to Phase 12 |
| **WARN** | Build succeeds but has warnings | Note warnings, continue |
| **FAIL** | Build or environment check fails | Report error, stop verification |

**Build Validation Report Section:**
```markdown
### Build Validation (P11.5-build-validation)
**Status:** [PASS | WARN | FAIL]

| Check | Status | Notes |
|-------|--------|-------|
| Python version | PASS / FAIL | e.g. 3.11.x |
| Virtual environment | PASS / FAIL | venv active |
| pip install -e ".[dev]" | PASS / FAIL | |
| pip check | PASS / WARN | Dependency conflicts |
| ruff check | PASS / FAIL | |
| mypy | PASS / FAIL | |
| python -m build | PASS / FAIL | |

**Errors:** [List any errors, or "None"]
**Warnings:** [List any warnings, or "None"]
```

### Build Failure Handling

If the build fails:
1. Report the exact error message from the build output
2. Identify the likely cause (dependency issue, code error, configuration)
3. **DO NOT** continue to Phase 12 - build must pass first
4. If it's a critical issue requiring hotfix, offer the three hotfix options

---

## Phase 12: Test Coverage Analysis (from P12-test-coverage-analysis)

> **USE AGENT:** Launch `verification-test-coverage` agent via Task tool.
> This runs sequentially AFTER Phase 11.5 completes. See [Agent Orchestration](#agent-orchestration).

**Prerequisite:** Phase 11 must pass (tests must run successfully). Phase 11.5
must complete (either build passes OR a WARN was noted).

**Scope:** Test files corresponding to changed source files.

### Step 1: Map Source to Tests
For each changed file in `src/`:
- Find corresponding test file in `tests/` (mirror structure)
- Note if test file exists but wasn't updated
- Note if test file is missing entirely

### Step 2: Identify Coverage Gaps
For each changed source file with a test file:

| Check | Question |
|-------|----------|
| New methods | Are new public methods tested? |
| Modified methods | Are behavior changes tested? |
| Edge cases | Are boundary conditions covered? |
| Error states | Are error paths tested? |

### Step 3: Rate Coverage Quality

| Rating | Meaning | Action |
|--------|---------|--------|
| 8-10 | **Critical gap** | Must add tests before completion |
| 5-7 | **Important** | Should add tests |
| 3-4 | **Nice-to-have** | Can defer to follow-up |
| 1-2 | **Minor** | Note for future improvement |

### Step 4: Specific Gap Analysis
For each gap found:
```
Source File: path/to/source.py
Test File: path/to/test_source.py (or MISSING)
Gap Type: [untested method / missing edge case / no error tests]
Rating: X/10
Recommendation: [specific test to add]
```

**IMPORTANT:** After Phase 12 returns proposed edits, proceed to Phase 12.5 to
apply the edits and run the new tests. Do NOT skip to Phase 13 without verifying
the new tests pass.

---

## Phase 12.5: Run New Tests

**Prerequisite:** Phase 12 returned `proposed_edits` and at least one edit was applied.

**Skip condition:** If Phase 12 found no critical gaps (no `auto_fixable: true`
findings) or no edits were applied, skip directly to Phase 14.

### Step 1: Apply Phase 12 Edits

Collect all `proposed_edits` from the Phase 12 agent response:
1. Group by file to detect conflicts with existing code
2. Apply edits using the Edit tool
3. Run `ruff format <test_files>` via Bash to normalize formatting

### Step 2: Analyze New Test Files

Run `ruff check <modified_test_files>` via Bash on the test files that were
modified/created by Phase 12 edits. If lint errors exist:
1. Fix compilation errors in the generated tests
2. Re-run analysis until clean

### Step 3: Run Tests

Run `pytest -v` via Bash to execute ALL tests (existing + newly created).

| Result | Action |
|--------|--------|
| All pass | Proceed to Phase 14 |
| New tests fail | Fix the failing tests (adjust assertions, setup, or fakes). Re-run until green. Max 3 fix attempts — if still failing after 3 attempts, revert the new tests, note in Phase 13 report as "proposed but could not be auto-fixed", and proceed. |
| Existing tests fail | This indicates Phase 12 edits broke something. Revert the edits, report in Phase 13, and proceed. |

---

## Phase 14: Security Review (from P14-security-review)

**Auto-triggers for sensitive files.** Always runs in Full verification.

### Step 1: Check for Sensitive File Patterns

Scan changed files for security-relevant patterns:

**Path patterns:**
- `src/**/auth/**`, `src/**/api/**`, `src/**/service/**`
- `src/**/repository/**`, `src/**/network/**`

**Content patterns:**
- `apiKey`, `secret`, `token`, `password`, `credential`
- `http`, `requests`, `httpx`

### Step 2: Python-Specific Security Checks

Scan for these dangerous patterns in changed files:

| Check | What to Look For |
|-------|------------------|
| Hardcoded secrets | API keys, tokens, passwords in code |
| HTTPS enforcement | HTTP URLs (except localhost) |
| Sensitive logging | Tokens, passwords in log statements |
| Dynamic code execution | `eval()` or `exec()` with untrusted input |
| Unsafe deserialization | `pickle.loads` from untrusted sources |
| Shell injection | `subprocess` calls with `shell=True` |
| Committed secrets | `.env` file accidentally tracked in git |
| Disabled TLS | `verify=False` in HTTP client calls |
| Debug mode leaks | `DEBUG=True` in production configuration |
| SQL injection | String-formatted queries instead of parameterized |
| Weak randomness | `random` module used for security-sensitive values (use `secrets` instead) |

### Step 3: Error Exposure Check

**Distinct from Phase 7:** Phase 7 checks if errors are *handled*.
Phase 14 checks if errors *leak sensitive information*.

```python
# BAD: Exposes internal details
raise Exception(f'DB failed: {connection_string}')

# GOOD: Generic user message
raise ServiceUnavailableError('Service temporarily unavailable')
```

### Severity Classification

| Severity | Definition |
|----------|------------|
| CRITICAL | Immediate security risk, data exposure |
| HIGH | Significant vulnerability |
| MEDIUM | Best practice violation |
| LOW | Minor improvement |

---

## Phase 13: Comprehensive Verification Report

After all reviews, provide a structured report:

### If Issues Found:

```markdown
## Verification Report

### Architecture Score: X/10

### Summary
Found [N] issues before completion.

---

### Lint Fixes Applied (P02-lint-issues-fix)
- Auto-fixed: [N] issues with ruff check --fix
- Manual fixes needed: [N] issues
  - `file:line` - [description]

---

### Code Review Issues (P03-code-review-checks)

#### Issue 1: [Brief description]
**Confidence:** [score]%
**Source:** [rules compliance / bug scan / historical / etc.]
**File:** `path/to/file.py:line`
**Suggested fix:** [how to resolve]

---

### Architecture Violations (P04-architecture-validation)

| Layer | Status | Issue |
|-------|--------|-------|
| API/CLI | OK/WARN | Description |
| Services | OK/WARN | Description |
| Domain | OK/WARN | Description |
| Data | OK/WARN | Description |
| Core | OK/WARN | Description |

#### Critical Violation: [type] in `file:line`
[Description and suggested fix]

---

### Simplification Opportunities (P05-code-simplification)

1. **[File/Function]:** [Opportunity description]
   - Before: [brief description]
   - After: [suggested improvement]

---

### Type Design Issues (P06-type-design-analysis)

| Type | File | Encap | Invariant | Issue |
|------|------|-------|-----------|-------|
| ClassName | path:line | 5/10 | 4/10 | Description |

*Or: No type design issues found / Skipped (already run)*

---

### Silent Failure Issues (P07-silent-failure-hunt)

| Severity | Location | Issue | Recommendation |
|----------|----------|-------|----------------|
| CRITICAL | path:line | Bare except: pass | Add logging.exception() |

*Or: No silent failures found / Skipped (already run)*

---

### Comment Issues (P08-comment-analysis)

| Location | Issue Type | Current | Suggestion |
|----------|------------|---------|------------|
| path:line | Inaccurate | "Returns None" | "Raises ValueError" |

*Or: No comment issues found / Skipped (already run)*

---

### Codex Adversarial Review (P8.7 — GPT-5.4)

**Verdict:** [approve / needs-attention / unavailable]

| Confidence | File | Lines | Issue | Recommendation |
|------------|------|-------|-------|----------------|
| 0.85 | path/to/file.py | 42-58 | Race condition in... | Add mutex or... |

*Or: No adversarial findings / Codex review: unavailable*

---

### Test Coverage Gaps (P12-test-coverage-analysis)

| Source File | Test File | Gap | Rating |
|-------------|-----------|-----|--------|
| auth_service.py | test_auth_service.py | Missing error case tests | 8/10 |

*Or: Adequate test coverage / Skipped (already run)*

---

### Build Validation (P11.5-build-validation)

**Status:** [PASS | WARN | FAIL]
**Errors:** [List any build errors, or "None"]
**Warnings:** [List any build warnings, or "None"]

---

### Security Review (P14-security-review)

**Status:** [Triggered (sensitive files found) | Skipped (no sensitive files)]

| Severity | Location | Issue | Recommendation |
|----------|----------|-------|----------------|
| CRITICAL | path:line | Hardcoded API key | Use environment variable |

*Or: No security issues found / Skipped (no sensitive files)*

---

**Recommendation:** Address issues before marking complete.
```

### If No Issues:

```markdown
## Verification Report

All checks passed.

### Architecture Score: X/10

### Checks Completed:
- Lint issues (analyzed and auto-fixed)
- Rules compliance (.claude/rules/)
- Bug scan (type hints, async, resource management)
- Historical context (Beads context)
- Code comments compliance
- Test coverage verification
- Layer separation (API/CLI/Services/Domain/Data/Core)
- SOLID principles
- Code simplification review
- Type design analysis
- Silent failure hunt
- Comment accuracy
- Codex adversarial review (GPT-5.4 independent review)
- Build validation (environment and package build checked)
- Test coverage quality
- Security review (sensitive files checked)

**Ready for:** commit / PR creation
```

---

## Hotfix Discovered During Verification

When verification discovers a **CRITICAL** issue that needs immediate attention,
Claude should offer options for handling the hotfix.


### When to Trigger

Offer hotfix options when ANY of these occur:
- Phase 3 Bug Scan: CRITICAL severity issue found
- Phase 7 Silent Failure Hunt: CRITICAL severity with confidence >= 80%
- Phase 11: Tests fail due to a newly discovered bug (not a test bug)
- Any phase discovers a P0/P1 production issue

### Hotfix Options Prompt

When a critical issue is found, create a Beads bug task and show:

```
CRITICAL issue found during verification!

**Issue:** [Brief description from finding]
**Location:** `path/to/file.py:line`
**Impact:** [User-facing impact description]
**Beads:** Creating **bd-xxxx "[Issue description]"** (P0, bug)

This looks like it needs a hotfix. How would you like to handle it?

**1. Stash and switch** (quick fix, ~30 seconds overhead)
   git stash push -m "WIP: bd-xxxx [current-task]"
   git checkout main
   git checkout -b hotfix/[description]

**2. Use a worktree** (longer fix, keeps your WIP untouched)
   git worktree add ../project-hotfix -b hotfix/[description]
   # Claude works in worktree using absolute paths

**3. Fix it here** (no context switch, handle in current branch)
   Continue working on the fix without switching branches.
```

### Natural Language Commands

| You Say | Claude Does | Git Command |
|---------|-------------|-------------|
| "Stash and switch" / "stash it" | Stashes WIP, switches branch | `git stash push -m "WIP: [task]" && git checkout main && git checkout -b hotfix/[name]` |
| "Use a worktree" / "worktree" | Creates sibling worktree | `git worktree add ../project-hotfix -b hotfix/[name]` |
| "Fix it here" / "stay here" | Continues in current context | (none - continues verification) |
| "Back to verification" / "Continue verification" | Returns to verification | Depends on approach used |
| "Pop my stash" | Restores stashed work | `git stash pop` |
| "Remove the worktree" | Cleans up worktree | `git worktree remove ../project-hotfix` |

### After Hotfix Completion

Once the hotfix is fixed, shipped, and merged:

1. **If stash was used:**
   ```bash
   git checkout [original-branch]
   git stash pop
   ```
   Then say "Continue verification" to resume.

2. **If worktree was used:**
   ```bash
   git worktree remove ../project-hotfix
   ```
   Claude continues in original directory. Say "Continue verification".

3. **If fixed in place:**
   Say "Continue verification" to resume from where you left off.

### Verification Report with Critical Hotfix

When CRITICAL issues are found, the Phase 13 report should start with:

```markdown
## Verification Report

### CRITICAL ISSUE REQUIRES HOTFIX

Found [N] issues. **[1] CRITICAL issue needs immediate attention.**

---

### Critical Issue Requiring Hotfix

**Issue:** [Description]
**Location:** `path/to/file.py:line`
**Confidence:** [score]%
**Impact:** [User-facing impact]
**Beads:** Created **bd-xxxx "[Issue description]"** (P0, bug)

**Hotfix Options:**
1. "Stash and switch" → git stash push -m "..." && git checkout main && git checkout -b hotfix/[name]
2. "Use a worktree" → git worktree add ../project-hotfix -b hotfix/[name]
3. "Fix it here" → Continue in current context

---

### Other Issues
[Remaining non-critical issues...]
```

---

## Triggers

**This FULL verification skill should be invoked when:**

- User says "full verify" or "complete verification"
- User says "verify" with 200+ lines changed
- New modules or significant architectural changes
- Workflow integration detects large change size
- User explicitly chooses Full from post-execution options
- `/superpowers:verification-before-completion` for major changes

**For smaller changes, use:**
- `/python-verification-quick` (< 50 lines): lint + tests only
- `/python-verification-standard` (50-200 lines): analysis without agents

**Automatic hotfix prompt triggers:**

When any phase discovers a CRITICAL/P0 issue during verification, automatically
show the hotfix options prompt (see "Hotfix Discovered During Verification"
section above) before continuing with the report.

**Note:** This 13-phase workflow is tailored to this Python project's
architecture and rules. Other projects may have different verification
workflows.

---

## Quick Reference: The 14 Phases

| Phase | Source | Description | Execution |
|-------|--------|-------------|-----------|
| 1 | - | Gather context (changed files, rules, summary) | Main context |
| 2 | P02-lint-issues-fix | ruff check + mypy, auto-fix, manual fix lint issues | Main context |
| 3 | P03-code-review-checks | 5 review checks (rules, bugs, history, comments, tests) | Main context |
| 4 | P04-architecture-validation | Layer/SOLID/architecture validation | Main context |
| 5 | P05-code-simplification | Clarity, Python standards, balance review | Main context |
| 6 | `verification-type-analyzer` | Type design quality (encapsulation, invariants) | **AGENT (parallel)** |
| 7 | `verification-silent-failure` | Error handling audit (silent failures) | **AGENT (parallel)** |
| 8 | `verification-comment-analyzer` | Documentation accuracy verification | **AGENT (parallel)** |
| 8.7 | Codex adversarial-review | Independent adversarial review (GPT-5.4) | **CODEX (parallel)** |
| 8.5 | - | Apply agent edits, collect Codex results, format | Main context |
| 9 | P03-code-review-checks | Confidence scoring (0-100 scale) | Main context |
| 10 | P03-code-review-checks | False positive filtering (>=80 only) | Main context |
| 11 | - | Final Verification: ruff check + ruff format + pytest | Main context |
| 11.5 | P11.5-build-validation | Python build validation (environment + package) | Main context |
| 12 | `verification-test-coverage` | Test coverage quality analysis | **AGENT (sequential)** |
| 13 | Combined | Comprehensive verification report | Main context |
| 14 | P14-security-review | Security audit (auto-triggers for sensitive files) | Main context |

**Parallel Agents (6-8):** Launch in a SINGLE Task tool call with 3 invocations.
**Codex (8.7):** Launch via Bash `--background` in the SAME message as agents.
**Sequential Agent (12):** Launch after Phase 11 passes.

---

## The 9 Integrated Methodologies

| Methodology | Focus Area |
|-------------|------------|
| **P02-lint-issues-fix** | Static analysis, auto-fix, manual lint fixes |
| **P03-code-review-checks** | Bug detection, rules compliance, historical context, confidence scoring |
| **P04-architecture-validation** | Layer separation, SOLID, architecture patterns |
| **P05-code-simplification** | Clarity, Python standards, avoiding over-simplification |
| **P06-type-design-analysis** | Type encapsulation, invariants, type hints, Python patterns |
| **P07-silent-failure-hunt** | Error handling audit, silent failures, fallback behavior |
| **P08-comment-analysis** | Documentation accuracy, docstring compliance, comment rot |
| **Codex adversarial-review** | Independent GPT-5.4 adversarial review: auth, data safety, races, rollback |
| **P12-test-coverage-analysis** | Test coverage quality, gap analysis, edge case coverage |
| **P14-security-review** | Security audit, secrets, HTTPS, dynamic code execution, deserialization security |

---

## Scope Control

**Critical:** All phases operate ONLY on changed files identified in Phase 1.

- **Never scan the entire codebase**
- Lint analysis: changed files only
- Code review: changed files only
- Architecture validation: changed files + immediate dependencies
- Simplification review: changed files only
- Type design analysis: new/modified types in changed files only
- Silent failure hunt: error handling in changed files only
- Comment analysis: comments in changed files only
- Test coverage: tests corresponding to changed source files in `src/` only

---

## Auto-Skip Logic (Session State Based)

**Pre-check before Phases 6-8 and 12:**

Before running parallel agents (Phases 6-8) or test coverage (Phase 12):

1. Read `.beads/.session-state.json`
2. Check if `verification.phases_completed` includes the phase names AND
   `verification.files_being_verified` matches current `modified_files`
3. **If match:** Auto-skip without asking
   - Log in report: "Phases 6-8 skipped (already run this session)"
4. **If no match or no state exists:** Execute normally

**Phase name mapping for state checking:**

| Phase | Name in `phases_completed` |
|-------|---------------------------|
| 6 | `Type Design Analysis` |
| 7 | `Silent Failure Hunt` |
| 8 | `Comment Analysis` |
| 8.7 | `Codex Adversarial Review` |
| 12 | `Test Coverage Analysis` |

This prevents redundant analysis automatically while preserving state across
`/clear` operations.

---

## Guidelines

- **Evidence before assertions** - Run verification, don't assume
- **Fix lint issues first** - Clean code before deeper analysis
- **High confidence only** - Report issues with >=80% confidence
- **Actionable feedback** - Provide suggested fixes, not just problems
- **Respect existing decisions** - Check git history before flagging
- **Preserve functionality** - Simplification suggestions must not change behavior
- **Balance** - Avoid over-engineering and over-simplification
- **Scope to changes** - Never expand beyond the changed files
- **Parallel when possible** - Run Phases 6-8 concurrently to save time
- **Ask before skipping** - Let user decide on redundant analysis

---

## Agent Orchestration

This project uses dedicated verification agents for parallel execution of
Phases 6-8 and Phase 12. Agents analyze in parallel (fast), return findings AND
proposed edits, and the main context applies edits sequentially (safe, no
conflicts).

### Available Verification Agents

| Agent | Phase | Engine | Focus |
|-------|-------|--------|-------|
| `verification-type-analyzer` | 6 | Claude | Type design quality, encapsulation, invariants |
| `verification-silent-failure` | 7 | Claude | Silent failures, error handling, fallbacks |
| `verification-comment-analyzer` | 8 | Claude | Comment accuracy, docstring compliance |
| Codex adversarial-review | 8.7 | GPT-5.4 | Adversarial review: auth, data safety, races, rollback |
| `verification-test-coverage` | 12 | Claude | Test coverage quality, gap analysis |

### Phases 6-8 + 8.7: Parallel Agent + Codex Execution

Launch all three Claude agents AND Codex adversarial review concurrently.

**Claude agents** — single Task tool call with multiple invocations:

```
Task(subagent_type: "verification-type-analyzer", model: "opus", prompt: "...")
Task(subagent_type: "verification-silent-failure", model: "opus", prompt: "...")
Task(subagent_type: "verification-comment-analyzer", model: "opus", prompt: "...")
```

**Codex adversarial review** — launch via Bash in the SAME message as the Task
calls above (this makes it truly parallel):

```bash
Bash(command: 'node "/Users/arkevo/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs" adversarial-review --background', run_in_background: true)
```

**CRITICAL:** Use a single message with multiple tool calls (3x Task + 1x Bash)
to ensure parallel execution. Do NOT call them sequentially.

### Codex Availability Handling

Codex is a **best-effort enhancement**, not a gate. If Codex is unavailable
(not authenticated, CLI missing, network error), the verification continues
without it:

| Codex Status | Action |
|--------------|--------|
| Completed with findings | Merge findings into Phase 9 |
| Completed with `approve` | Note "Codex: no issues" in report |
| Still running at Phase 9 | Wait up to 60s, then proceed without |
| Failed or unavailable | Note "Codex review: unavailable" in report |

### Agent Input Format

Each agent receives a prompt containing:

```markdown
## Verification Phase [N]: [Phase Name]

### Changed Files
[List of files from Phase 1 session state]

### Project Rules
[Relevant rules from .claude/rules/ that apply to this analysis]

### Scope
- Analyze ONLY the changed files listed above
- Return findings with confidence >= 80% only
- Include proposed_edits for auto-fixable issues

Return your analysis as structured JSON.
```

### Agent Output Format

Each agent returns structured JSON with findings AND proposed edits:

```json
{
  "phase": "6|7|8|12",
  "phase_name": "Type Design Analysis|Silent Failure Hunt|Comment Analysis|Test Coverage",
  "issues_found": 3,
  "findings": [
    {
      "location": "file:line",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "confidence": 85,
      "description": "What the issue is",
      "recommendation": "How to fix it",
      "auto_fixable": true
    }
  ],
  "proposed_edits": [
    {
      "file": "src/path/to/file.py",
      "description": "What this edit does",
      "edit": {
        "old_string": "exact string to find",
        "new_string": "replacement string"
      }
    }
  ]
}
```

### Phase 8.5: Apply Agent Edits + Collect Codex Results

After all parallel agents complete, the main context applies edits and collects
Codex results:

1. **Collect** all `proposed_edits` from Claude agent responses
2. **Collect Codex results** — run:
   ```bash
   node "/Users/arkevo/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs" result --json
   ```
   - If Codex completed: parse `verdict` and `findings`, merge into unified list
   - If Codex still running: proceed with edits, check again before Phase 9
   - If Codex failed/unavailable: note in report, continue without it
3. **Group by file** to detect potential conflicts (multiple edits to same file)
4. **Detect conflicts** - if two agents propose edits to overlapping code:
   - Present both edits to user
   - Ask which to apply (or both if non-overlapping)
5. **Apply non-conflicting edits** using the Edit tool
6. **Run `ruff format`** to normalize formatting after edits
7. **Note applied edits** in the verification report

**Conflict Detection Rules:**
- Same file with overlapping `old_string` = CONFLICT
- Same file with different `old_string` = OK (apply both)
- Different files = OK (always safe)

### Phase 12: Sequential Agent Execution

After Phase 11 (tests pass), launch the test coverage agent:

```
Task(subagent_type: "verification-test-coverage", model: "opus", prompt: "...")
```

This agent runs sequentially because:
- It depends on Phase 11 passing (tests must work)
- Test edits may conflict with other changes

After Phase 12 agent returns:
1. Apply `proposed_edits` to test files (same process as Phase 8.5)
2. Run `ruff check` on modified test files
3. Run `pytest -v` — all tests (old + new) must pass
4. If new tests fail: fix up to 3 times, then revert and note in report
5. Proceed to Phase 14 (Security Review), then Phase 13 (Report)

### Result Synthesis (Phases 9-10)

Main context combines all agent findings:

1. **Merge findings** from all parallel agents into unified list
2. **Apply confidence scoring** (Phase 9) - keep only >= 80%
3. **Filter false positives** (Phase 10) - remove:
   - Pre-existing issues
   - Issues fixed by Phase 2 lint
   - Pedantic nitpicks
4. **Separate** auto-fixed issues from remaining issues
5. **Generate unified report** (Phase 13)

## Updated Execution Flow

```
Verification Triggered
        |
        v
+-------------------------------------+
| Phase 1: Gather Context             |
| - Read .beads/.session-state.json   |
| - Get modified_files list           |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phases 2-5: Sequential Analysis     |
| - Lint fixes (main context)         |
| - Code review (main context)        |
| - Architecture (main context)       |
| - Simplification (main context)     |
+-------------------------------------+
        |
        v
+---------------------------------------------+
| Phases 6-8 + 8.7: PARALLEL AGENTS + CODEX  |
|                                             |
|  +-------------+ +-------------+            |
|  |verification-| |verification-|            |
|  |type-analyzer| |silent-      |            |
|  |  (Claude)   | |failure      |            |
|  +-------------+ |(Claude)     |            |
|         +-------------+  +-------------+    |
|         |verification-|  |   CODEX     |    |
|         |comment-     |  | adversarial |    |
|         |analyzer     |  |  review     |    |
|         |(Claude)     |  |  (GPT-5.4)  |    |
|         +-------------+  +-------------+    |
|                                             |
|  Claude: Single Task call, 3 invocations    |
|  Codex:  Bash --background (concurrent)     |
|  Returns: findings + proposed_edits         |
+---------------------------------------------+
        |
        v
+-------------------------------------+
| Phase 8.5: APPLY AGENT EDITS        |
| - Collect proposed_edits from all   |
| - Group by file, detect conflicts   |
| - Apply non-conflicting edits       |
| - Prompt user for conflicts         |
| - Run ruff format to normalize      |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phases 9-10: Combine & Filter       |
| - Merge agent findings              |
| - Apply confidence scoring          |
| - Filter false positives            |
| - Note which were auto-fixed        |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 11: Final Verification        |
| - ruff check (verify edits OK)      |
| - ruff format --check               |
| - pytest -v                         |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 11.5: Build Validation        |
| - Invoke /P11.5-build-validation    |
| - Python env + package build check  |
| - PASS / WARN / FAIL result         |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 12: TEST COVERAGE AGENT       |
| (After build/warn completes)        |
| Returns: gaps + proposed test edits |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 12.5: RUN NEW TESTS           |
| - Apply Phase 12 proposed_edits     |
| - ruff check on new test files      |
| - pytest -v (all old + new)         |
| - Fix up to 3x, then revert         |
| (Skip if no edits were applied)     |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 14: Security Review           |
| - Auto-trigger for sensitive files  |
| - Hardcoded secrets scan            |
| - HTTPS/auth/storage checks         |
| - Python-specific security checks:  |
|   dynamic code, deserialization,    |
|   shell injection, SQL injection    |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 13: Generate Report           |
| - Combine all findings              |
| - List auto-applied fixes           |
| - List remaining issues             |
| - Format verification report        |
+-------------------------------------+
```

---

## Write Verification Marker (ONLY on PASS)

Immediately before generating the Phase 13 report — and ONLY if Phase 11's tests
passed (and no blocking finding remains) — write the marker the router's *Hard
Stop: Verification Before Ship / "Done"* and `beads-ship-task` gate on:

```bash
TASK=$(python3 -c "import json;print(json.load(open('.beads/.session-state.json')).get('task_id',''))" 2>/dev/null)
printf '{"level":"full","task":"%s","passed":true,"at":"%s"}\n' "$TASK" "$(date -u +%FT%TZ)" > .beads/.verification-done
```

If tests failed or a blocking issue stands, do NOT write the marker (the gate stays closed).

---

## Updated Report Format

The Phase 13 report now includes auto-fixed issues:

```markdown
## Verification Report

### Architecture Score: X/10

### Summary
Found [N] issues. Auto-fixed [M] issues. [K] issues require attention.

---

### Auto-Fixed Issues

These issues were automatically fixed by verification agents:

| Phase | Location | Issue | Fix Applied |
|-------|----------|-------|-------------|
| 6 | src/models/user.py:15 | Missing frozen=True | Added @dataclass(frozen=True) |
| 7 | src/services/api.py:45 | Bare except: pass | Added logging.exception() |
| 8 | src/utils/helpers.py:10 | Outdated docstring | Updated docs |

---

### Remaining Issues

These issues require manual attention:

#### [Issue Category]
...
```

---

## Benefits of Parallel Agents

| Benefit | Impact |
|---------|--------|
| **~3x faster** for Phases 6-8 | Parallel analysis execution |
| **Auto-fixes applied** | Agents propose edits, main context applies |
| **Conflict-safe** | Sequential edit application prevents overwrites |
| **Cleaner context** | Each agent focused on one concern |
| **Better token efficiency** | Agents don't inherit full conversation |
| **Isolated failures** | One agent failing doesn't corrupt others |
| **Structured output** | Easy to merge findings and coordinate edits |

---

## Fallback Behavior

If agent execution fails:
1. Log the failure
2. Fall back to sequential in-context analysis for that phase
3. Continue with remaining phases
4. Note the fallback in the verification report
