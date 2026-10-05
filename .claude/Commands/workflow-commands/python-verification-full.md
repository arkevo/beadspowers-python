---
name: python-verification-full
description: Full verification with parallel review agents and a Codex adversarial pass. Use for 200+ line changes or new modules.
---

# Python Full Verification Workflow

**Section:** Code Quality

When running verification before completion in this Python project, use the
combined methodologies from P02-lint-issues-fix, P03-code-review-checks (rules
compliance and historical intent only), P06-type-design-analysis (only when the
change adds a type), P07-silent-failure-hunt (which now carries the bug scan),
P08-comment-analysis, the Codex adversarial review, P12-test-coverage-analysis,
and P14-security-review (only when sensitive files changed). This ensures
thorough quality checks before claiming work is complete.

**Retired: the architecture-validation and code-simplification phases** (once
Phases 4 and 5, which is why the numbering jumps from 3 to 6). In a downstream
project that ran this workflow, neither produced a finding in any recorded run,
at full or standard level, so both were removed from this tier and from
`workflow-commands:python-verification-standard`, and their command files were
deleted. Do not re-add them. An architecture review that a task genuinely needs
is its own task, with its own bead.

---

## Integration with Superpowers Verification

**IMPORTANT:** When running `/superpowers:verification-before-completion` in
**this Python project**, follow this comprehensive workflow that integrates
the project's verification methodologies. This workflow is specific to this
project and should be used whenever verifying completed work before committing
or creating PRs in this codebase.

---

## Phase 1: Gather Context

Before reviewing any code:

### Step 1: Identify Changed Files
- Read `modified_files` from `.beads/.session-state.json`. That list is the
  task's changed set, recorded by `workflow-commands:beads-post-execution` in
  its Step 2a: uncommitted edits to tracked files (deletions excluded),
  untracked files, and the files this branch changed since it left the trunk.
- If the file is missing or unreadable, or `modified_files` is empty, set
  `CHANGED_SET = UNKNOWN`. You may ask which files to look at, to steer the
  review phases, but the answer only decides what gets read, never what gets
  written: Phase 2 Step 3, Phase 8.5 step 6 and Phase 12.5 step 1 skip their
  writes in this state and say so in the report, and nothing ever widens to
  the project root. A file list the user volunteers without being asked is a
  valid changed set: echo it back, then use it. Write it into `modified_files`
  first, as `.claude/rules/verification-write-scope.md`
  describes, so the write blocks see it.
- Note which directories/layers were affected
- **Scope all subsequent phases to ONLY these files**, for reading and writing
  alike (see Scope Control)

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
Run `ruff check --no-fix <changed .py/.pyi files>` and `mypy <changed .py/.pyi files>`
via Bash on the changed files only (not entire codebase). `<changed .py/.pyi files>`
stands for the changed set's `.py`/`.pyi` files only — ruff and mypy fail on
anything else, such as a `README.md` — and when it has none, skip every command
that takes it and say so in the report. Analysis only reads, so when
`CHANGED_SET = UNKNOWN`, run the same two commands on `src/ tests/` instead.

### Step 2: Categorize Issues
Group discovered issues by severity:

| Severity | Action |
|----------|--------|
| **Errors** | Must fix - code has critical issues or type violations |
| **Warnings** | Should fix - potential bugs or problematic patterns |
| **Info/Hints** | Consider fixing - style suggestions (fix if quick) |

### Step 3: Auto-Fix — scoped to the changed set, or skipped

The binding rule is `.claude/rules/verification-write-scope.md`, which is
always loaded; follow it exactly. Run the `scoped-ruff-fix` block from
`.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged: it reads the changed
set itself, drops deleted files and the paths the rule never auto-fixes, and
skips without calling ruff when nothing is left. In short:

1. Snapshot `git status --short`.
2. Preview with `ruff check --diff --force-exclude <files>`, which writes
   nothing.
3. Fix with `ruff check --fix --force-exclude <files>`.
4. Compare `git status --short` with the snapshot. Any file outside the changed
   set that moved is reported and never reverted (it may be someone else's edit
   made during the run), and the block exits 1 so it is inspected; an untracked
   file that appeared is never deleted without approval.

`--force-exclude` is required because ruff ignores its own `exclude` settings
for files named on the command line. Never run ruff with an empty file list: a
bare `ruff check --fix` rewrites the whole project. If no Python file is left
after filtering, or `CHANGED_SET = UNKNOWN`, skip this step and say so in the
report.

Typically resolves: unused imports, import sorting, and simple style fixes.

### Step 4: Manual Fixes (if needed)
Address remaining errors and warnings:
1. Fix errors first (blocking issues)
2. Address warnings that could cause runtime problems
3. Apply quick style fixes for consistency
4. Skip info-level hints unless specifically requested

### Step 5: Verify Fixes
Run `ruff check --no-fix <changed .py/.pyi files>` and `mypy <changed .py/.pyi files>`
again on changed files to confirm issues resolved.

**Important:** Do not introduce new warnings while fixing existing ones.

---

## Phase 3: Code Review Checks (from P03-code-review-checks)

Review ONLY the changed files identified in Phase 1. This phase keeps the two
checks nothing else covers. The rest of the old P03 checklist moved: the bug
scan runs in Phase 7 (inside the `verification-silent-failure` agent, with an
in-context fallback in the Phase 7 section), comment compliance is Phase 8, and
the test-presence check is part of Phase 11.

### Check #1: Rules Compliance
Audit the changes against `.claude/rules/`:
- Code structure and organization rules
- Naming conventions
- Documentation requirements
- Testing requirements
- Python best practices defined in rules

### Check #2: Historical Context
Review context of modified files:
- Check Beads task description for original intent
- Review `.beads/.session-state.json` for task requirements
- Verify changes align with the task's stated goals
- Respect any TODO/FIXME or "don't modify" guidance in the touched code

**Report only what reaches 80% confidence.** In the runs measured in a
downstream project, this phase never surfaced a defect that Phase 7 did not
also report, so a clean pass here is one line in the report, not a paragraph.

---

## Phase 6: Type Design Analysis (from P06-type-design-analysis)

> **USE AGENT:** Launch `verification-type-analyzer` agent via Task tool.
> See [Agent Orchestration](#agent-orchestration) for parallel execution details.

**Parallel Group A** - Can run simultaneously with Phases 7-8 and Codex Adversarial Review.

**Scope:** New or modified classes/types in changed files only.

### Step 0: Gate — launch only when the change adds a type

In the runs measured in a downstream project, this agent mostly returned
low-severity encapsulation notes, and the one real bug it found was also found
by Phase 7 in the same run. It earns its cost only on new types, so check the
changed set before launching it. Run this from the repository root:

```bash
# snippet: phase6-gate
# Prints PHASE6_GATE=launch or PHASE6_GATE=skip, with the reason.
changed="$(python3 -c '
import json
try:
    d = json.load(open(".beads/.session-state.json"))
except Exception:
    d = {}
for p in d.get("modified_files") or []:
    print(p["path"] if isinstance(p, dict) else p)
' 2>/dev/null)"
trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
if [ -z "$trunk" ] || ! git rev-parse -q --verify "$trunk^{commit}" >/dev/null 2>&1; then
  git remote set-head origin --auto >/dev/null 2>&1   # unset, or dangling after the remote renamed its default branch
  trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
  git rev-parse -q --verify "$trunk^{commit}" >/dev/null 2>&1 || trunk=""
fi
if [ -z "$changed" ]; then
  echo "PHASE6_GATE=launch (changed set unknown)"
elif [ -z "$trunk" ]; then
  echo "PHASE6_GATE=launch (no origin/HEAD, so committed changes cannot be checked)"
elif ! git merge-base "$trunk" HEAD >/dev/null 2>&1; then
  echo "PHASE6_GATE=launch (no merge base with $trunk, as in a shallow clone, so committed changes cannot be checked)"
else
  src_files=()
  while IFS= read -r f; do
    case "$f" in src/*.py) ;; *) continue ;; esac
    case "/$f" in */tests/*|*/test_*.py|*_test.py|*/conftest.py) continue ;; esac
    src_files+=("$f")
  done <<< "$changed"
  count=0
  if [ "${#src_files[@]}" -gt 0 ]; then
    count=$(
      {
        git diff --unified=0 "$trunk"...HEAD -- "${src_files[@]}"
        git diff --unified=0 HEAD -- "${src_files[@]}"
        git ls-files --others --exclude-standard -z -- "${src_files[@]}" |
          while IFS= read -r -d '' f; do git diff --unified=0 --no-index /dev/null "$f"; done
      } 2>/dev/null |
        grep -E '^\+[^+]' |
        grep -vE '^\+[[:space:]]*#' |
        grep -vE '^\+[[:space:]]*class[[:space:]]+Test' |
        grep -cE '^\+[[:space:]]*class[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*([(:]|\[)|^\+[[:space:]]*type[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*(\[[^]]*\])?[[:space:]]*=|:[[:space:]]*([A-Za-z_][A-Za-z0-9_]*\.)?TypeAlias[[:space:]]*=|=[[:space:]]*([A-Za-z_][A-Za-z0-9_]*\.)?(NewType|TypedDict|NamedTuple)[[:space:]]*\('
    )
  fi
  if [ "${count:-0}" -gt 0 ]; then
    echo "PHASE6_GATE=launch ($count added type definition(s) under src/)"
  else
    echo "PHASE6_GATE=skip (no new types)"
  fi
fi
```

- `PHASE6_GATE=skip` → do not launch the type-design agent. Report
  `Type design: Skipped (no new types)` and launch only the Phase 7 and
  Phase 8 agents, plus Codex.
- `PHASE6_GATE=launch` → launch it with the others (Agent Orchestration).

The gate counts added lines under `src/` that define a type: a `class`, a
`TypeAlias` annotation, a `type X = …` statement, or a `NewType`, `TypedDict`
or `NamedTuple` call. It reads every tree state: commits on this branch
(`<trunk>...HEAD`), staged and unstaged edits (against `HEAD`), and untracked
files. Comments, import lines and test classes (`class Test…`, and anything
under `tests/` or named `test_*.py`, `*_test.py` or `conftest.py`) don't count.
When the changed set is unknown, or there is no `origin/HEAD` (or no merge base
with it, as in a shallow clone) to diff committed work against, it launches the
agent anyway, because it cannot rule out a new type.

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

**Scope:** Error handling code in changed files only, plus the bug scan in Step 4.

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

### Step 4: Bug Scan
The `verification-silent-failure` agent runs this scan as its Step 1.5. When the
agent fails and this phase falls back to in-context analysis (see Fallback
Behavior), run it here instead, so the bug scan is never lost. Report real
paths, not theoretical ones, and skip anything ruff or mypy already reports
under the project's configuration:

- **None handling:** attribute access, indexing or calls on a value that can be
  `None` on a real path; `cast()` or `# type: ignore` hiding it; `assert` as
  the only runtime guard; attributes first assigned outside `__init__`; falsy
  values treated as missing.
- **Async misuse:** coroutines never awaited; `create_task()` results not kept;
  blocking calls inside `async def`; `CancelledError` swallowed; resources used
  after their `with` block closed them.
- **Resource lifecycle:** files, sockets, connections, sessions, HTTP clients,
  `subprocess.Popen`, executors or pools opened without `with`/`finally`; locks
  without a release in `finally`; threads never joined.
- **Shared mutable state:** mutable default arguments and class attributes;
  unlocked state shared across threads or tasks; a collection mutated while
  iterating it; late-binding closures in loops.
- **Silent wrong results:** a generator consumed twice; naive and aware
  datetimes mixed.

### Step 5: Report Issues
Format for each issue:
```
Location: file:line
Severity: CRITICAL/HIGH/MEDIUM
Pattern: [what was found; for a bug-scan finding, "bug scan: <class>"]
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

## Phase 8.7: Codex Adversarial Review

> **EXTERNAL AGENT:** Runs via the Codex CLI in parallel with Phases 6-8.
> See [Agent Orchestration](#agent-orchestration) for execution details.

**Parallel Group A** - Launches alongside the Claude verification agents.

**Purpose:** An independent adversarial review from a different AI model: the
model configured in your Codex config, run through the Codex CLI. Codex defaults
to skepticism and targets failure modes that static analysis and Claude's
agents may miss: auth boundaries, data corruption, race conditions, rollback
safety, stale state, and observability gaps.

### Execution

**1. Find the companion script.** The Codex plugin installs it in a versioned
directory, so never hard-code the path; take the newest installed version:

```bash
# snippet: codex-companion
COMPANION="$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)"
if [ -f "$COMPANION" ]; then
  echo "Codex companion: $COMPANION"
else
  COMPANION=""
  echo "Codex companion: not found (is the codex plugin installed?)"
fi
```

If it is not found, Codex is unavailable: note it (Codex Availability Handling,
in Agent Orchestration) and continue without this phase.

**2. Pick the review scope from the tree state.** Never rely on the companion's
own `auto` scope. Verification usually runs before the ship commit, so a review
that looks only at commits can approve a diff that leaves out the uncommitted
implementation; and on a clean tree, `auto` diffs against the local default
branch, which can lag or lead the trunk. This block defines `codex_scopes`,
which prints one line of scope arguments per review pass:

```bash
# snippet: codex-scope
codex_scopes() {
  local trunk dirty ahead=0
  trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
  if [ -z "$trunk" ] || ! git rev-parse -q --verify "$trunk^{commit}" >/dev/null 2>&1; then
    git remote set-head origin --auto >/dev/null 2>&1   # unset, or dangling after the remote renamed its default branch
    trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
    git rev-parse -q --verify "$trunk^{commit}" >/dev/null 2>&1 || trunk=""
  fi
  dirty=$(git status --porcelain)
  if [ -n "$trunk" ]; then
    ahead=$(git rev-list --count "$trunk..HEAD" 2>/dev/null || echo 0)
  fi
  if [ -n "$dirty" ]; then
    echo "--scope working-tree"
  fi
  if [ -n "$trunk" ]; then
    if [ -z "$dirty" ] || [ "$ahead" -gt 0 ]; then
      echo "--scope branch --base $trunk"
    fi
  elif [ -z "$dirty" ]; then
    echo "--scope branch"
  else
    echo "codex-scope: no origin/HEAD, so commits already on this branch are not reviewed" >&2
  fi
}
```

- **Dirty tree** (staged, unstaged or untracked changes): one pass with
  `--scope working-tree`.
- **Clean tree:** one pass with `--scope branch --base <trunk>`.
- **Mixed state** (uncommitted edits on top of commits this branch already
  made): both passes. Merge their findings before Phase 9.
- **No `origin/HEAD`:** a clean tree gets `--scope branch`, which diffs against
  the local default branch; a dirty tree gets only the working-tree pass, and
  the commits already on the branch go unreviewed. Say so in the report.
- **Never pass `--base` together with `--scope working-tree`.** `--base` forces
  a branch review and silently drops the uncommitted work.

**3. Launch** one background pass per scope line, in the same Bash call as
steps 1 and 2:

```bash
[ -n "$COMPANION" ] && codex_scopes | while IFS= read -r scope; do
  printf '%s\n' "$scope" | xargs node "$COMPANION" adversarial-review --background
done
```

Each launch prints `… started in the background as <jobId>. …`. Keep every
job id: results are collected by id.

### Collecting Results

After the Phase 6-8 agents return, collect each pass by its job id, one call
per pass, with the `codex-companion` block run first in the same Bash call so
that `$COMPANION` is set. Never call `result` without an id: it returns the
newest *finished* job, so while a second pass is still running it hands back
the first pass's verdict again and the other scope goes unreviewed.

```bash
node "$COMPANION" result <jobId> --json | jq '{status: .storedJob.status, scope: .storedJob.result.target.label, verdict: .storedJob.result.result.verdict, findings: ((.storedJob.result.result.findings // []) | length), parseError: .storedJob.result.parseError}'
```

1. If the command says the job "is still running", proceed with Phase 8.5 and
   collect it again before Phase 9.
2. Check that `scope` matches the pass you launched (`working tree diff` for
   `--scope working-tree`, `branch diff against <trunk>` for a branch pass)
   before merging its findings. A mismatch means you collected the wrong job.
3. A non-null `parseError` means Codex answered with prose instead of the JSON
   it was asked for. Treat that pass as a failed run.
4. Record each pass's scope next to its verdict in the Phase 13 report, one
   line per pass.
5. If Codex timed out or failed, follow Codex Availability Handling in Agent
   Orchestration.

### Runtime Rules

- **Run `codex --version` before blaming the plugin.** The companion runs
  whichever `codex` binary is first on `PATH`, and that binary reads your Codex
  config (`~/.codex/config.toml`). A CLI older than its config fails at
  startup, which looks like a broken plugin.
- **A config or effort rejection:** fix what `codex --version` or the error
  shows, then relaunch once. Do not loop.
- **A usage-limit message:** do not retry. Note the reset time the message
  gives in the report.
- **No `bd` writes while a pass is in flight.** The review runs inside the
  repository with its agent instructions, may run `bd` commands of its own, and
  two `bd` processes at once can overwrite each other's writes.
- **A reply that is not JSON is a failed run**, even when the job reports
  `completed`.
- **Effort comes from your Codex config.** The review command takes no effort
  flag. For a deliberately deeper pass (an auth, migration or payment diff),
  raise `model_reasoning_effort` in the Codex config for that run, put it back
  afterwards, and name the effort in the report.

### Codex Finding Format

The review sits at `.storedJob.result.result` in the `result --json` reply:
- `verdict`: `approve` or `needs-attention`
- `summary`: a short overall assessment
- `findings`: array of issues with `severity` (`critical`, `high`, `medium` or
  `low`), `title`, `body`, `file`, `line_start`, `line_end`, `confidence`
  (0-1) and `recommendation`
- `next_steps`: array of suggested follow-ups

### Merging Codex Findings

Map Codex findings into the unified findings list:
- `confidence` 0-1 → multiply by 100 for the 0-100 scale
- `needs-attention` verdict → treat findings as HIGH severity minimum
- Apply the same Phase 10 false-positive filtering to Codex findings
- Deduplicate against Claude agent findings (same file + overlapping lines)
- When two passes ran, merge both result sets before Phase 9

---

## Phase 9: Confidence Scoring

For each issue found (from Phases 3, 6-8 and Codex 8.7), assign a confidence score:

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
1. `ruff check --no-fix <changed .py/.pyi files>` via Bash - Confirm no lint errors remain
2. `ruff format --check <changed .py/.pyi files>` via Bash - Ensure consistent formatting
3. `pytest -v` via Bash - Execute all tests

**All must pass before claiming completion.**

**Test presence (moved here from Phase 3).** For each changed module under
`src/`, confirm that a corresponding test file exists under `tests/` (mirror
structure: `tests/test_billing.py` for `src/<your_package>/billing.py`) and
that step 3 ran it. A changed module with no test file is reported here;
Phase 12 rates the gap and may propose the missing tests.

---

## Phase 11.5: Build Validation (from P11.5-build-validation)

**Prerequisite:** Phase 11 must pass (tests must run successfully).

**Purpose:** Verify the Python package actually builds and the environment is
healthy. Code can pass `ruff check` and `pytest` but fail to install or build
due to missing dependencies, broken entry points, or packaging configuration
errors.

### Step 1: Invoke Build Validator Skill

Invoke `workflow-commands:P11.5-build-validation-[F]` to perform comprehensive build checks:
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
3. First add every test file Phase 12 created to `modified_files` in
   `.beads/.session-state.json` (read the file, extend that one list, write it
   back): the rule lets Phase 12 create mirrored tests, and from then on they
   are part of the task's changes. Then run the `scoped-ruff-format` block from
   `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged — it formats the
   changed set (now including those tests) and re-checks it, with the leak check.

### Step 2: Analyze New Test Files

Run `ruff check --no-fix <modified_test_files>` via Bash on the test files that were
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

**Gated: Steps 2 and 3 run only when Step 1 matches.**
`workflow-commands:python-verification-standard` uses the same gate. Run
unconditionally, this phase produced no findings in the runs measured in a
downstream project, so the gate keeps it as a backstop for the files where it
can matter. Its triggers cover everything Steps 2 and 3 look for, so a change
that only adds a `pickle.loads` call, or only edits a migration, still
triggers it.

### Step 1: Gate on Sensitive Files

Check every file in the Phase 1 changed set against these patterns.

**Path patterns:**
- `src/**/auth/**`, `src/**/api/**`, `src/**/service*/**`
- `src/**/repository/**`, `src/**/network/**`, `src/**/http/**`
- `**/migrations/**`, `alembic/versions/**`, `**/*.sql`
- Settings modules: `**/settings.py`, `**/settings/**`
- Environment files: `.env`, `.env.*`

**Content patterns** (anywhere in a changed file):
- Secrets: `api_key`, `apiKey`, `secret`, `token`, `password`, `credential` (any case)
- Network: `http`, `requests`, `httpx`
- Risky calls: `eval(`, `exec(`, `pickle`, `yaml.load`, `subprocess`,
  `shell=True`, `verify=False`, `DEBUG`, `random.`
- Database authorization: `GRANT`, `REVOKE`, `CREATE POLICY`,
  `ROW LEVEL SECURITY`, `SECURITY DEFINER`

Run this from the repository root. It prints each matching file once — or only
`CHANGED_SET=UNKNOWN` when the session state is missing or unreadable, or
`modified_files` is missing or empty:

```bash
files=$(python3 -c 'import json; [print(p) for p in json.load(open(".beads/.session-state.json")).get("modified_files") or []]' 2>/dev/null)
if [ -z "$files" ]; then
  echo "CHANGED_SET=UNKNOWN"
else
  printf '%s\n' "$files" | while IFS= read -r f; do
    if printf '%s\n' "$f" | grep -qE '(^|/)src/(.*/)?(auth|api|service[^/]*|repository|network|http)/|(^|/)migrations/|(^|/)alembic/versions/|\.sql$|(^|/)settings(\.py$|/)|(^|/)\.env(\..+)?$'; then
      printf '%s\n' "$f"
    elif [ -f "$f" ] && { grep -qiE 'api_?key|secret|token|password|credential' -- "$f" ||
        grep -qE 'http|requests|httpx|eval\(|exec\(|pickle|yaml\.load|subprocess|shell=True|verify=False|DEBUG|random\.|GRANT|REVOKE|CREATE POLICY|ROW LEVEL SECURITY|SECURITY DEFINER' -- "$f"; }; then
      printf '%s\n' "$f"
    fi
  done
fi
```

- **`CHANGED_SET=UNKNOWN` printed** → run Steps 2 and 3 on the files the review
  phases covered, and report `Security review: Triggered (changed set unknown)`.
- **No file printed** → skip Steps 2 and 3. Report
  `Security review: Skipped (no sensitive files)` and continue.
- **Files printed** → run Steps 2 and 3 on them, and report
  `Security review: Triggered (<matching files>)`.

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
| Database authorization | `GRANT`, `REVOKE`, row-level-security policies or `SECURITY DEFINER` in a migration or `.sql` file: no grant or policy wider than the change needs, policy predicates that name the requesting user, and the application-side check the policy backs still in place |

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

### Summary
Found [N] issues before completion.

---

### Lint Fixes Applied (P02-lint-issues-fix)
- Auto-fixed: [N] issues across [M] changed files
  *(or:* `SKIPPED (changed set unknown)` *or* `SKIPPED (no Python files in the changed set)` *or* `FAILED (<ruff call> exited <code>)`, a failed lint phase *)*
- Scope check: no files outside the changed set changed
  *(or:* **LEAK: [list]** *— each reported, none reverted; inspect them before continuing)*
- Manual fixes needed: [N] issues
  - `file:line` - [description]

---

### Code Review Issues (P03-code-review-checks)

#### Issue 1: [Brief description]
**Confidence:** [score]%
**Source:** [rules compliance / historical intent]
**File:** `path/to/file.py:line`
**Suggested fix:** [how to resolve]

---

### Type Design Issues (P06-type-design-analysis)

| Type | File | Encap | Invariant | Issue |
|------|------|-------|-----------|-------|
| ClassName | path:line | 5/10 | 4/10 | Description |

*Or: No type design issues found / Skipped (no new types) / Skipped (already run)*

---

### Silent Failure and Bug-Scan Issues (P07-silent-failure-hunt)

| Severity | Location | Issue | Recommendation |
|----------|----------|-------|----------------|
| CRITICAL | path:line | Bare except: pass | Add logging.exception() |

*Or: No silent failures or bugs found / Skipped (already run)*

---

### Comment Issues (P08-comment-analysis)

| Location | Issue Type | Current | Suggestion |
|----------|------------|---------|------------|
| path:line | Inaccurate | "Returns None" | "Raises ValueError" |

*Or: No comment issues found / Skipped (already run)*

---

### Codex Adversarial Review (P8.7)

**Verdict:** [approve / needs-attention / unavailable] · **Scope:** [working tree diff / branch diff against <trunk>; one line per pass] · **Effort:** [optional: the effort your Codex config ran at]

| Confidence | File | Lines | Issue | Recommendation |
|------------|------|-------|-------|----------------|
| 0.85 | path/to/file.py | 42-58 | Race condition in... | Add mutex or... |

*Or: No adversarial findings / Codex review: unavailable — [reason]*

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

**Status:** [Triggered (<matching files>) | Skipped (no sensitive files)]

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

### Checks Completed:
- Lint issues (analyzed; auto-fixed inside the changed set only)
- Rules compliance (.claude/rules/)
- Historical context (Beads context)
- Type design analysis (run / skipped: no new types)
- Silent failure hunt, including the bug scan
- Comment accuracy
- Codex adversarial review (independent second model; scope and effort noted)
- Build validation (environment and package build checked)
- Test presence and test coverage quality
- Security review (triggered / skipped: no sensitive files)

**Ready for:** commit / PR creation
```

---

## Hotfix Discovered During Verification

When verification discovers a **CRITICAL** issue that needs immediate attention,
Claude should offer options for handling the hotfix.


### When to Trigger

Offer hotfix options when ANY of these occur:
- Phase 7 bug scan (moved there from Phase 3): CRITICAL severity issue found
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
- `/workflow-commands:python-verification-quick` (< 50 lines): lint + tests only
- `/workflow-commands:python-verification-standard` (50-200 lines): analysis without agents

**Automatic hotfix prompt triggers:**

When any phase discovers a CRITICAL/P0 issue during verification, automatically
show the hotfix options prompt (see "Hotfix Discovered During Verification"
section above) before continuing with the report.

**Note:** This workflow is tailored to this Python project's
architecture and rules. Other projects may have different verification
workflows.

---

## Quick Reference: The Phases

| Phase | Source | Description | Execution |
|-------|--------|-------------|-----------|
| 1 | - | Gather context (changed set, rules, summary) | Main context |
| 2 | P02-lint-issues-fix | ruff check + mypy, auto-fix (**changed files only**), manual fix lint issues | Main context |
| 3 | P03-code-review-checks | Rules compliance + historical intent (bug scan moved to Phase 7) | Main context |
| 6 | `verification-type-analyzer` | Type design quality — only when the change adds a type | **AGENT (parallel, gated)** |
| 7 | `verification-silent-failure` | Error handling audit (silent failures) + bug scan | **AGENT (parallel)** |
| 8 | `verification-comment-analyzer` | Documentation accuracy verification | **AGENT (parallel)** |
| 8.7 | Codex adversarial-review | Independent adversarial review by a second model | **CODEX (parallel)** |
| 8.5 | - | Apply agent edits, collect Codex results, scoped format | Main context |
| 9 | P03-code-review-checks | Confidence scoring (0-100 scale) | Main context |
| 10 | P03-code-review-checks | False positive filtering (>=80 only) | Main context |
| 11 | - | Final Verification: ruff check + ruff format --check + pytest + test presence | Main context |
| 11.5 | P11.5-build-validation | Python build validation (environment + package) | Main context |
| 12 | `verification-test-coverage` | Test coverage quality analysis | **AGENT (sequential)** |
| 13 | Combined | Comprehensive verification report | Main context |
| 14 | P14-security-review | Security audit — only when sensitive files changed | Main context (gated) |

**Parallel Agents (6-8):** Launch in a SINGLE Task tool call with 2-3 invocations (Phase 6 only when its gate passes).
**Codex (8.7):** Launch via Bash `--background` in the SAME message as agents.
**Sequential Agent (12):** Launch after Phase 11 passes.

---

## Integrated Methodologies

| Methodology | Focus Area |
|-------------|------------|
| **P02-lint-issues-fix** | Static analysis, scoped auto-fix, manual lint fixes |
| **P03-code-review-checks** | Rules compliance, historical context, confidence scoring |
| **P06-type-design-analysis** | Type encapsulation, invariants, type hints, Python patterns (gated on new types) |
| **P07-silent-failure-hunt** | Error handling audit, silent failures, fallback behavior, bug scan |
| **P08-comment-analysis** | Documentation accuracy, docstring compliance, comment rot |
| **Codex adversarial-review** | Independent adversarial review by a second model: auth, data safety, races, rollback |
| **P12-test-coverage-analysis** | Test coverage quality, gap analysis, edge case coverage |
| **P14-security-review** | Security audit (gated): secrets, HTTPS, dynamic code execution, deserialization, database authorization |

---

## Scope Control

**Critical:** All phases operate ONLY on the changed set identified in Phase 1,
for reading AND for writing. The binding rule is
`.claude/rules/verification-write-scope.md`: read wide, write narrow.

### Read scope

- **Never scan the entire codebase for findings.** A phase may read other files
  for context, but it reports findings only for the changed set.
- Lint analysis: changed files only
- Code review: changed files only
- Type design analysis: new/modified types in changed files only
- Silent failure hunt: error handling in changed files only
- Comment analysis: comments in changed files only
- Test coverage: tests corresponding to changed source files in `src/` only

### Write scope

Anything that writes touches only files inside the changed set. That covers
`ruff check --fix`, `ruff format`, and every edit an agent proposes in Phases
6-8, 8.7 and 12:

- Phase 2 Step 3, Phase 8.5 step 6 and Phase 12.5 step 1 run the
  `scoped-ruff-fix` and `scoped-ruff-format` blocks from
  `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged: always with
  `--force-exclude`, never with an empty file list.
- An agent edit proposed for a file outside the changed set is reported, not
  applied.
- One exception: Phase 12 may create new test files under `tests/` that mirror
  a changed module, and adds each one to `modified_files` so the write blocks
  cover it.
- Never auto-fixed, even inside the changed set: `.venv/`, `vendor/`,
  `third_party/`, generated code such as `*_pb2.py`, and `migrations/` (a
  protected path). Notebooks (`.ipynb`) are linted and reported only.
- `CHANGED_SET = UNKNOWN` skips every write, and the report says so. Never
  widen to the project root, and never ask for a file list just to justify a
  fix.
- A whole-project cleanup is its own task, with its own bead and review.

**After every step that writes,** compare `git status --short` with the
snapshot taken before it. A file outside the changed set that moved is a leak:
list it in the report and inspect it as `.claude/rules/verification-write-scope.md`
describes, but never revert it — it may be someone else's edit made during the
run (the owner's editor, another agent or session). An untracked file outside the
set is reported, never deleted without approval.

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
| Codex adversarial-review | 8.7 | Codex CLI (your configured model) | Adversarial review: auth, data safety, races, rollback |
| `verification-test-coverage` | 12 | Claude | Test coverage quality, gap analysis |

### Phases 6-8 + 8.7: Parallel Agent + Codex Execution

Launch the Claude agents (two, or three when the Phase 6 gate passed) AND the
Codex adversarial review concurrently.

**Claude agents** — single Task tool call with multiple invocations:

```
Task(subagent_type: "verification-type-analyzer", model: "opus", prompt: "...")   # only when the Phase 6 gate passed
Task(subagent_type: "verification-silent-failure", model: "opus", prompt: "...")
Task(subagent_type: "verification-comment-analyzer", model: "opus", prompt: "...")
```

**Codex adversarial review** — in the SAME message as the Task calls above,
one Bash call with `run_in_background: true` that runs, in order, the
`codex-companion` block, the `codex-scope` block and the launch loop from
Phase 8.7. Keep every job id it prints.

**CRITICAL:** Use a single message with multiple tool calls (2-3x Task + 1x Bash)
to ensure parallel execution. Do NOT call them sequentially.

### Codex Availability Handling

Codex is a **best-effort enhancement**, not a gate. If Codex is unavailable
(plugin not installed, not authenticated, CLI missing, network error), the
verification continues without it:

| Codex Status | Action |
|--------------|--------|
| Completed with findings | Merge findings into Phase 9 |
| Completed with `approve` | Note "Codex: no issues" in report |
| Still running at Phase 9 | Wait up to 60s, then proceed without |
| Companion not found | Note "Codex review: unavailable — plugin not installed" |
| Failed with a config or effort rejection | Run `codex --version`, fix what it shows, relaunch once; report the effort used |
| Failed with a usage-limit message | Note "Codex review: unavailable (usage limit, resets <time from the message>)"; do not retry before then |
| Reply was not JSON (`parseError` set) | Treat as failed: note "Codex review: unavailable — reply was not JSON" |
| Failed or unavailable for any other reason | Run `codex --version` first (Phase 8.7); note "Codex review: unavailable — <reason>" |

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
2. **Collect Codex results** by job id, one call per pass, with the
   `codex-companion` block from Phase 8.7 run first in the same Bash call:
   ```bash
   node "$COMPANION" result <jobId> --json
   ```
   - If a pass completed: check its scope (`target.label`), then parse
     `verdict` and `findings` and merge them into the unified list
   - If a pass is still running: proceed with edits, collect again before Phase 9
   - If a pass failed or Codex was unavailable: note it in the report and
     continue without it
3. **Group by file** to detect potential conflicts (multiple edits to same file)
4. **Detect conflicts** - if two agents propose edits to overlapping code:
   - Present both edits to user
   - Ask which to apply (or both if non-overlapping)
5. **Apply non-conflicting edits** using the Edit tool, to files inside the
   changed set only. An edit proposed for any other file is listed in the
   report, not applied (Scope Control, Write scope).
6. **Format inside the changed set only**: run the `scoped-ruff-format` block
   from `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged. It formats the
   changed set's Python files — which include every file step 5 may edit — and
   re-checks them with the leak check. Never a bare `ruff format`, which
   rewrites every file in the project. If step 5 edited no Python file, skip
   this.
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
2. Run `ruff check --no-fix` on modified test files
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
| - Get modified_files (changed set)  |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phases 2-3: Sequential Analysis     |
| - Lint fixes (changed set only)     |
| - Rules + intent review (main ctx)  |
| - Phase 6 gate: new types? (grep)   |
+-------------------------------------+
        |
        v
+---------------------------------------------+
| Phases 6-8 + 8.7: PARALLEL AGENTS + CODEX   |
|                                             |
|  +-------------+ +-------------+            |
|  |verification-| |verification-|            |
|  |type-analyzer| |silent-      |            |
|  | (Claude,    | |failure +    |            |
|  |  gated)     | |bug scan     |            |
|  +-------------+ |(Claude)     |            |
|         +-------------+  +-------------+    |
|         |verification-|  |   CODEX     |    |
|         |comment-     |  | adversarial |    |
|         |analyzer     |  |  review     |    |
|         |(Claude)     |  |(2nd model)  |    |
|         +-------------+  +-------------+    |
|                                             |
|  Claude: Single Task call, 2-3 invocations  |
|  Codex:  Bash --background (concurrent)     |
|  Returns: findings + proposed_edits         |
+---------------------------------------------+
        |
        v
+-------------------------------------+
| Phase 8.5: APPLY AGENT EDITS        |
| - Collect proposed_edits from all   |
| - Group by file, detect conflicts   |
| - Apply edits inside changed set    |
| - Prompt user for conflicts         |
| - Scoped ruff format + leak check   |
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
| - test presence (from Phase 3)      |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 11.5: Build Validation        |
| - Invoke /workflow-commands:        |
|   P11.5-build-validation-[F]        |
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
| - Scoped ruff format, ruff check    |
| - pytest -v (all old + new)         |
| - Fix up to 3x, then revert         |
| (Skip if no edits were applied)     |
+-------------------------------------+
        |
        v
+-------------------------------------+
| Phase 14: Security Review (gated)   |
| - Only when sensitive files changed |
| - Hardcoded secrets scan            |
| - HTTPS/auth/storage checks         |
| - Python-specific security checks:  |
|   dynamic code, deserialization,    |
|   shell, SQL, database grants       |
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
passed (and no blocking finding remains) — write the marker the router's *Verification Before Ship / "Done"* and `workflow-commands:beads-ship-task` gate on:

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
2. Fall back to sequential in-context analysis for that phase (for Phase 7,
   that includes its Step 4 bug scan)
3. Continue with remaining phases
4. Note the fallback in the verification report
