Please analyze and fix lint issues here: $ARGUMENTS.

## Analysis Workflow

### Step 1: Run Static Analysis
Analysis only reads, so it may look wide; what it may *write* is decided in
Step 4. Choose the files to analyse in this order:

1. the path given as the argument above, if there is one. It becomes the changed
   set: write it into `modified_files` as `.claude/rules/verification-write-scope.md`
   describes, so Step 4 fixes exactly those files;
2. otherwise the task's changed set, `modified_files` in
   `.beads/.session-state.json`;
3. otherwise, as a last resort, the whole project (`src/ tests/`).

Reading the whole project never widens the write scope. Step 4's auto-fix is
still limited to the changed set, and is skipped entirely when the changed set is
unknown (`.claude/rules/verification-write-scope.md`).

`<changed .py/.pyi files>` stands for only the `.py`/`.pyi` files among the files
chosen above (a directory, such as the `src/ tests/` fallback, goes in as it is)
— ruff and mypy fail on other files, such as a `README.md` — and when none is
left, skip this step and say so in the report.

```bash
# Lint errors and warnings (read-only)
ruff check --no-fix <changed .py/.pyi files>

# Type checking (read-only)
mypy <changed .py/.pyi files>
```

### Step 2: Run Dead Code Analysis
Use `vulture` to find unused code, and `ruff` for unused imports:

```bash
# Find unused code (functions, methods, classes, variables)
vulture src/

# Find unused imports specifically
ruff check --no-fix --select F401 src/
```

**Note:** Vulture may report false positives for:
- Entry points (`main()`, CLI entry functions)
- Exported public APIs (`__all__`)
- Code used via dynamic dispatch or dependency injection
- `__dunder__` methods (excluded by convention)

Dead-code findings in files outside the changed set are reported, never fixed:
record them, and if one matters, open a bead for it.

### Step 3: Categorize All Issues
Combine issues from ruff, mypy, and vulture into a Markdown checklist:

**Ruff Issues:**
1. **Errors** (must fix) - Code with critical problems (E-codes, F-codes)
2. **Warnings** (should fix) - Potential bugs or problematic patterns (W-codes)

**Mypy Issues:**
3. **Type Errors** (should fix) - Type annotation violations, missing types, incompatible assignments

**Vulture Issues:**
4. **Unused Code** (review) - Functions, methods, classes not referenced
5. **Unused Imports** (fix) - Imports not referenced anywhere

Format each item as:
```markdown
- [ ] `file_path:line_number` - Issue description (source: ruff/mypy/vulture)
```

### Step 4: Auto-Fix — scoped to the changed set, or skipped
Never auto-fix outside the task's changed set. Run the `scoped-ruff-fix` block
from `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged (the policy it
implements is `.claude/rules/verification-write-scope.md`). In short, it:

- reads the changed set and keeps only the Python files that are safe to rewrite
  (nothing under `.venv/`, `vendor/`, `third_party/` or `migrations/`, no
  generated `*_pb2.py`; notebooks are linted but never rewritten);
- skips entirely, without calling ruff, when the changed set is unknown or holds
  no Python files — it never widens to the project root;
- previews with `ruff check --diff`, applies `ruff check --fix --force-exclude` to
  those files only, then compares `git status` with its snapshot and restores and
  reports any file outside the set that changed.

It typically resolves unused imports, import sorting and simple style issues.

A whole-project cleanup is legitimate, but as its own task with its own bead and
its own review — never as a side effect of fixing something else.

### Step 5: Manual Fixes
Address the remaining issues in the changed set one by one (an issue in a file
outside the changed set is reported, not fixed):
1. Mark the current issue as in-progress
2. Read the relevant code section using the Read tool
3. Apply the fix following the project's `[tool.ruff]` settings in `pyproject.toml`
4. Verify the fix by re-running `ruff check --no-fix <file>` on that file
5. Check off the completed item before moving to the next

**For vulture unused code:**
- Only remove code in files inside the changed set; a finding anywhere else is
  recorded in the report (and, if it matters, filed as its own bead), never fixed
  here
- Verify the code is truly unused (not an entry point or public API)
- Check `__all__` exports and dynamic usage before removing
- If confirmed unused, remove the code
- If it's a false positive, note it and skip

### Step 6: Format and Verify
1. Format with the `scoped-ruff-format` block from
   `.claude/Commands/workflow-commands/references/scoped-ruff.md`, unchanged. It formats only the changed set's
   Python files with `ruff format --force-exclude`, re-checks them with
   `ruff format --check`, and reports anything that changed outside the set.
2. Run a final `ruff check --no-fix --force-exclude` on the `<changed .py/.pyi files>`
   from Step 1 to confirm the lint issues are resolved.
3. Re-run `mypy` on the same files to confirm the type errors are resolved.
4. Optionally re-run `vulture src/` (read-only) to confirm the unused code is gone.
5. Report a summary of the fixes applied, including the blocks' `Auto-fixed:` and
   `Scope check:` lines.

## Priority Guidelines
1. Fix ruff errors first (E-codes and F-codes — blocking or critical issues)
2. Address mypy type errors that could cause runtime problems
3. Fix ruff warnings (W-codes — potential bugs and bad patterns)
4. Remove confirmed unused code/imports (vulture + F401 findings)
5. Apply style fixes for consistency
6. Skip info-level hints unless specifically requested

## Tools to Use
- Bash: `ruff check --no-fix <files>` — Python lint analysis (read-only, may run wide)
- Bash: the `scoped-ruff-fix` block from `.claude/Commands/workflow-commands/references/scoped-ruff.md` — automatic fixes, changed set only
- Bash: the `scoped-ruff-format` block from the same file — formatting, changed set only
- Bash: `mypy <files>` — type checking (read-only)
- Bash: `vulture src/` — detect unused code (read-only)
- Bash: `ruff check --no-fix --select F401 src/` — detect unused imports (read-only)
- Grep/Glob — for targeted code search and pattern matching
- Read/Edit — for targeted code modifications inside the changed set

## Important Notes
- Follow the project's `pyproject.toml [tool.ruff]` configuration
- Respect existing code patterns when fixing style issues
- Do not introduce new warnings while fixing existing ones
- Test that fixes don't break functionality (run `pytest` after significant changes)
- Vulture findings require manual review — not all "unused" code is safe to remove
- Entry points, public APIs, and dynamically-dispatched code may appear as unused
