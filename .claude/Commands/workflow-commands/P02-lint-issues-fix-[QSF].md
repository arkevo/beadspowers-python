Please analyze and fix lint issues here: $ARGUMENTS.

## Analysis Workflow

### Step 1: Run Static Analysis
Use `ruff check src/ tests/` to identify all lint issues in the specified path. If no path is provided, analyze the entire project. Also run `mypy src/` for type checking.

```bash
# Lint errors and warnings
ruff check src/ tests/

# Type checking
mypy src/
```

### Step 2: Run Dead Code Analysis
Use `vulture` to find unused code, and `ruff` for unused imports:

```bash
# Find unused code (functions, methods, classes, variables)
vulture src/

# Find unused imports specifically
ruff check --select F401 src/
```

**Note:** Vulture may report false positives for:
- Entry points (`main()`, CLI entry functions)
- Exported public APIs (`__all__`)
- Code used via dynamic dispatch or dependency injection
- `__dunder__` methods (excluded by convention)

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

### Step 4: Auto-Fix Where Possible
Before manual fixes, run `ruff check --fix` to automatically resolve common issues like:
- Unused imports removal
- Missing whitespace and formatting
- Simple style fixes
- Import organization

```bash
ruff check --fix src/ tests/
```

### Step 5: Manual Fixes
Address remaining issues one by one:
1. Mark the current issue as in-progress
2. Read the relevant code section using the Read tool
3. Apply the fix following project lint rules in `.claude/rules/lint_rules/` and `pyproject.toml [tool.ruff]`
4. Verify the fix by re-running `ruff check <file>` on that file
5. Check off the completed item before moving to the next

**For vulture unused code:**
- Verify the code is truly unused (not an entry point or public API)
- Check `__all__` exports and dynamic usage before removing
- If confirmed unused, remove the code
- If it's a false positive, note it and skip

### Step 6: Format and Verify
1. Run `ruff format src/ tests/` on modified files
2. Run final `ruff check src/ tests/` to confirm all lint issues are resolved
3. Re-run `mypy src/` to confirm type errors are resolved
4. Optionally re-run `vulture src/` to confirm unused code is removed
5. Report summary of fixes applied

```bash
ruff format src/ tests/
ruff check src/ tests/
mypy src/
```

## Priority Guidelines
1. Fix ruff errors first (E-codes and F-codes — blocking or critical issues)
2. Address mypy type errors that could cause runtime problems
3. Fix ruff warnings (W-codes — potential bugs and bad patterns)
4. Remove confirmed unused code/imports (vulture + F401 findings)
5. Apply style fixes for consistency
6. Skip info-level hints unless specifically requested

## Tools to Use
- Bash: `ruff check src/ tests/` — run Python lint analysis
- Bash: `ruff check --fix src/ tests/` — apply automatic fixes
- Bash: `ruff format src/ tests/` — format code consistently
- Bash: `mypy src/` — run type checking
- Bash: `vulture src/` — detect unused code
- Bash: `ruff check --select F401 src/` — detect unused imports
- Grep/Glob — for targeted code search and pattern matching
- Read/Edit — for targeted code modifications

## Important Notes
- Follow the project's `pyproject.toml [tool.ruff]` configuration
- Respect existing code patterns when fixing style issues
- Do not introduce new warnings while fixing existing ones
- Test that fixes don't break functionality (run `pytest` after significant changes)
- Vulture findings require manual review — not all "unused" code is safe to remove
- Entry points, public APIs, and dynamically-dispatched code may appear as unused
