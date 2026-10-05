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
  (`git ls-files --cached --others --exclude-standard -- <dir>`). Write each path
  relative to the repository root, the way `git status` prints it (no leading `./`,
  never absolute): the blocks match paths against `git status` exactly, so
  `./src/a.py` makes them report their own fix of `src/a.py` as a LEAK. An answer to
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
4. compares `git status` with the snapshot. Any file outside the changed set that
   changed during the run is reported and never reverted — it may be someone
   else's edit made while the block ran (the owner's editor, another agent or
   session) — and the block exits 1 so the leak is inspected before anything else
   happens. That covers a tracked file that was clean before, an untracked file
   that appeared, and a file that already had uncommitted edits and changed again.
   The check skips only the Python files the block rewrites, so a changed-set file
   it leaves alone, such as a `README.md` or a notebook, is reported the same way.

Report what they print in the verification report:

- `Auto-fixed: N across M changed files` (on success the block itself prints
  `Auto-fix ran on M changed file(s).`; take N from ruff's own summary above it), or
  `Auto-fixed: SKIPPED (changed set unknown)`, or
  `Auto-fixed: SKIPPED (no Python files in the changed set)`, or
  `Auto-fixed: FAILED (<ruff call> exited <code>)` when ruff itself failed, which
  the report carries as a failed lint phase, never as a pass;
- `Scope check: no files outside the changed set`, or `Scope check: LEAK: [list]`,
  which stops the step until each listed file is inspected; nothing on the list was
  reverted. A run that writes nothing — a skipped run, or one that failed on a
  notebook before any write — prints no `Scope check:` line.

To inspect a leak, read `git diff HEAD -- <path>` (or the new file) for each listed
path, leave the file as it is, and name it in the report with what changed. A LEAK
on its own is not a failed phase and does not withhold the verification marker,
but the owner must see it before shipping: "ship it" stages every changed file
(`Git Best Practices/protect_plans_and_commit_all.md` Rule 3), so the file ships
with the task unless the owner stashes it first. Committing it separately only gives
it its own commit message: it stays on the branch, so it still goes out in the
task's PR.
