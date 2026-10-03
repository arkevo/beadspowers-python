# Verification Writes Only What the Task Changed

**Section:** Verification (always loaded)

## Read Wide, Write Narrow

Verification may **read** anything. Analysis, search and review can look at the
whole project. Anything that **writes** — `ruff check --fix`, `ruff format`, an
edit a review agent proposes — touches only the task's **changed set**: the paths
in `modified_files` in `.beads/.session-state.json`, which
`workflow-commands:beads-post-execution` Step 2a records.
Analysis calls are always `ruff check --no-fix …`: a project may set `fix = true`
in `[tool.ruff]`, and a bare `ruff check` then rewrites files.

- **Changed set unknown → no auto-fix.** When the session state is missing or
  unreadable, or `modified_files` is empty, skip every automatic fix and say so in
  the report: `Auto-fixed: SKIPPED (changed set unknown)`. Never widen to the
  project root, and never ask the user for a file list just to justify a fix. A
  list the user volunteers is a valid changed set; echo it back in the report. So
  is a path a command takes as its argument (P02's, for example). Before any write
  block runs, write such a list into `modified_files` — read the file, change that
  one key, write it back, as `workflow-commands:beads-post-execution` Step 2b does
  — with a named directory standing for the files under it
  (`git ls-files --cached --others --exclude-standard -- <dir>`). An answer to
  "which files should I look at?" only steers reading; it never becomes the
  changed set.
- **Never auto-fixed, even inside the changed set:** anything under `.venv/`,
  `vendor/` or `third_party/`; generated code (for example `*_pb2.py`); and
  `migrations/`, which is a protected path in this workflow. Notebooks (`.ipynb`)
  are linted and reported, never rewritten.
- **One exception for tests:** Phase 12 may create new test files under `tests/`
  that mirror a module in the changed set. It adds each one to `modified_files`,
  so the write blocks cover it — never pass a file list to a block instead.
- **A whole-project cleanup is its own task**, with its own bead and its own
  review — never a side effect of verifying something else.

## Why

Observed in a downstream project: an unscoped auto-fix during verification
rewrote 17 files, including read-only exports and a dependency manifest. Because
"ship it" stages every changed file (`Git Best Practices/protect_plans_and_commit_all.md`
Rule 3), a fix like that rides into an unrelated commit under a message about
something else.

## The Write Sequence

Every step that rewrites files runs one of two blocks, unchanged: `scoped-ruff-fix`
for lint fixes, `scoped-ruff-format` for formatting. Both live in
`.claude/Commands/workflow-commands/references/scoped-ruff.md`, which loads only when a step
needs it: open it and run the block exactly as written — never retype or
paraphrase it. Each block reads the changed set itself, keeps only the files that
are safe to rewrite, and never calls ruff with an empty file list
(`ruff check --fix` with no paths rewrites the whole project). Then it:

1. snapshots `git status`;
2. previews the lint fixes with `ruff check --diff`, which writes nothing (lint
   block only);
3. writes, with `--force-exclude`, because ruff ignores the project's own
   `exclude` settings for files named on the command line unless that flag is set;
4. compares `git status` with the snapshot. A tracked file outside the changed set
   that changed was clean before, so it is restored with
   `git checkout HEAD -- <path>` (nothing is lost) and reported. An untracked file
   that appeared is reported and left for the user to decide about. A file outside
   the set that already had uncommitted edits and changed again is reported, never
   reverted.

Report what they print in the verification report:

- `Auto-fixed: N across M changed files` (N from ruff's own summary), or
  `Auto-fixed: SKIPPED (changed set unknown)`, or
  `Auto-fixed: SKIPPED (no Python files in the changed set)`;
- `Scope check: no files outside the changed set`, or `Scope check: LEAK: [list]`.
