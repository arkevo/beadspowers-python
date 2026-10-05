---
name: python-verification-standard
description: Standard verification - analysis phases without parallel agents. Use for 50-200 line changes.
---

# Python Standard Verification

For medium changes (50-200 lines), run analysis phases without spawning parallel
agents. This provides thorough code review without the overhead of agent
orchestration.

**Retired: Phase 4 (architecture validation) and Phase 5 (code simplification).**
Across every recorded verification run in the downstream project this workflow
comes from, neither phase produced a single finding, at standard or full level,
so both tiers dropped them and their standalone skill files were deleted. Do not
re-add them here. An architecture review that a task genuinely needs is its own
task, with its own bead.

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
- If the file is missing or unreadable, **or** `modified_files` is empty, the
  changed set is **UNKNOWN**. You may ask the user for a file list to guide the
  review phases, but Phase 2's auto-fix is skipped in this state — never widened
  to the project root (`.claude/rules/verification-write-scope.md`). A list the
  user volunteers is a valid changed set; echo it back in the report. Write it
  into `modified_files` first, as `.claude/rules/verification-write-scope.md`
  describes, so the write blocks see it.
- Note which directories/layers were affected
- **Scope all subsequent phases to ONLY these files**: the review phases report
  only on them, and nothing outside them is ever written

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

Run ruff and mypy on the changed set's Python files. `<changed .py/.pyi files>`
stands for the changed set's `.py`/`.pyi` files only — ruff and mypy fail on
anything else, such as a `README.md` — and when it has none, skip every command
that takes it and say so in the report. Analysis only reads, so when the changed
set is UNKNOWN, run the same two commands on `src/ tests/` instead:

```bash
ruff check --no-fix <changed .py/.pyi files>
mypy <changed .py/.pyi files>
```

### Step 2: Categorize Issues

| Severity | Action |
|----------|--------|
| **Errors** | Must fix - code won't run or has critical issues |
| **Warnings** | Should fix - potential bugs |
| **Info/Hints** | Consider fixing if quick |

### Step 3: Auto-Fix — scoped to the changed set, or skipped

Never auto-fix outside the task's changed set. Run the `scoped-ruff-fix` block
from `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged (policy:
`.claude/rules/verification-write-scope.md`) — never a bare `ruff check --fix`, which rewrites every file it can
reach. In short, the block reads the changed set; skips every write when
the set is UNKNOWN or holds no Python files (a changed notebook is still linted,
read-only); previews with `ruff check --diff`;
applies `ruff check --fix --force-exclude` to the changed Python files only; and
compares `git status` with its snapshot, reporting any file outside the set that
changed — never reverting it — and exiting 1 so it is inspected.

It typically resolves unused imports, import sorting, simple style issues and
trailing whitespace. Record the block's `Auto-fixed:` and `Scope check:` lines in
the report.

### Step 4: Manual Fixes (if needed)

Address the remaining errors and warnings in the changed files (an issue in a
file outside the changed set is reported, not fixed):
1. Fix errors first (blocking)
2. Address warnings that could cause runtime issues
3. Apply quick style fixes

### Step 5: Verify Fixes

Run `ruff check --no-fix` again to confirm resolution.

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

Standard runs no review agents, so this shallow scan is its only bug pass. It
looks for the same classes the full tier's silent-failure agent scans for:

- **None handling:** attribute access, indexing or calls on a value that can be
  `None` on a real path; `cast()` or `# type: ignore` hiding it; `assert` as the
  only runtime guard; attributes first assigned outside `__init__`; falsy values
  treated as missing
- **Async misuse:** coroutines never awaited; `create_task()` results not kept;
  blocking calls inside `async def`; `CancelledError` swallowed; resources used
  after their `with` block closed them
- **Resource lifecycle:** files, sockets, connections, sessions, HTTP clients,
  `subprocess.Popen`, executors or pools opened without `with`/`finally`; locks
  without a release in `finally`; threads never joined
- **Shared mutable state:** mutable default arguments and class attributes;
  unlocked state shared across threads or tasks; a collection mutated while
  iterating it; late-binding closures in loops
- **Silent wrong results:** a generator consumed twice; naive and aware datetimes
  mixed
- **Swallowed errors:** bare `except:`, `except Exception: pass`, errors reported
  with `print()` (the full tier hands this to its silent-failure agent; standard
  checks it here)

**Focus on:** large bugs a senior engineer would stop the merge for, not nitpicks.
Ignore anything ruff or mypy already reports under the project's configuration.

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

## Phase 9: Confidence Scoring

For each issue found (Phase 3), assign a confidence score:

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

1. `ruff check --no-fix <changed .py/.pyi files>` via Bash - Confirm no lint errors
2. `ruff format --check <changed .py/.pyi files>` via Bash - Ensure consistent formatting
3. `pytest -v` via Bash - Execute all tests

**All must pass before claiming completion.**

---

## Phase 14: Security Review (Auto-Triggered)

**This phase runs only when the gate below matches.**

### Gate: Sensitive File Patterns

Check whether any file in the changed set matches. An UNKNOWN changed set counts
as a match.

**Path patterns:**
- `src/**/auth/**`, `src/**/api/**`, `src/**/service*/**`, `src/**/repository/**`,
  `src/**/network/**`, `src/**/http/**`
- `**/migrations/**`, `alembic/versions/**`, `**/*.sql`
- settings modules (`**/settings.py`, `**/settings/**`)
- environment files (`.env`, `.env.*`)

**Content patterns (the changed file contains):**
- `apiKey`, `api_key`, `secret`, `token`, `password`, `credential` (any case)
- `requests`, `httpx`, `http`
- `eval(`, `exec(`, `pickle`, `yaml.load`, `subprocess`, `shell=True`,
  `verify=False`, `DEBUG`, `random.`
- `GRANT`, `REVOKE`, `CREATE POLICY`, `ROW LEVEL SECURITY`, `SECURITY DEFINER`

**No match →** skip the checks and record `Security review: Skipped (no sensitive files)`.
**Match →** run the checks below and record `Security review: Triggered (<matching files>)`.

### If Triggered: Run Security Checks

1. **Hardcoded secrets scan** - Check for API keys, tokens in code
2. **HTTPS enforcement** - Verify no HTTP URLs (except localhost)
3. **Environment variables** - Sensitive data uses env vars or python-dotenv, not hardcoded
4. **SQL injection** - No raw SQL queries with user input
5. **Dangerous functions** - No `eval()`, `exec()`, `pickle.loads()`, or `yaml.load()` without a safe loader, on untrusted data
6. **Subprocess safety** - No `shell=True` with user input
7. **SSL verification** - No `verify=False` in requests/httpx
8. **Debug mode** - No `DEBUG=True` in production config
9. **Weak randomness** - No `random` module for tokens, passwords or IDs (use `secrets`)
10. **Database authorization** - Grants, revokes, row-level security policies and `SECURITY DEFINER` functions read for cross-user access: each policy names the requesting user, and the application-side check it backs still exists
11. **Committed secrets** - No `.env` file is tracked in git (`git ls-files | grep '\.env'`)
12. **Error exposure** - Errors don't leak internal details to users

### Report Format

```markdown
### Security Review (Phase 14)
**Status:** [Triggered (<matching files>) / Skipped (no sensitive files)]
**Findings:**
- [ ] `file:line` - [issue description] (CRITICAL/HIGH/MEDIUM)
```

---

## Phase 13: Write Verification Marker (ONLY on PASS)

The router's *Verification Before Ship / "Done"* and `workflow-commands:beads-ship-task`
gate on this marker. Write it ONLY after Phase 11's tests pass — never on failure:

```bash
TASK=$(python3 -c "import json;print(json.load(open('.beads/.session-state.json')).get('task_id',''))" 2>/dev/null)
printf '{"level":"standard","task":"%s","passed":true,"at":"%s"}\n' "$TASK" "$(date -u +%FT%TZ)" > .beads/.verification-done
```

If any phase FAILED, do NOT write the marker, and delete any prior one
(`rm -f .beads/.verification-done`): a marker left by an earlier passing run would
keep the ship gate open.

---

## Standard Verification Report

```markdown
## Standard Verification Report

### Summary
Ran standard verification on [N] files ([M] lines).
Found [X] issues. [Y] auto-fixed. [Z] require attention.

---

### Lint Results (Phase 2)
**Auto-fixed:** [N] issues across [M] changed files
*(or:* `SKIPPED (changed set unknown)` *or* `SKIPPED (no Python files in the changed set)` *or* `FAILED (<ruff call> exited <code>)`, a failed lint phase *)*
**Scope check:** no files outside the changed set / **LEAK: [list]** / not run (the block skipped, or failed on notebooks before any write)
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

For comprehensive verification, use `/workflow-commands:python-verification-full`.
