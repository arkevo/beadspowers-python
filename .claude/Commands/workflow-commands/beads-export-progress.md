---
description: Regenerate .beads/PROGRESS.md from issues.jsonl by running .beads/generate_progress.py
---

# Beads Export Progress

Regenerates the human-readable progress report at `.beads/PROGRESS.md` from the current `.beads/issues.jsonl` export. Groups issues by phase, shows completion stats, progress bar, blockers, and close dates.

## Steps

1. Re-export issues from the live Dolt DB so the JSONL is fresh:
   ```bash
   bd export > .beads/issues.jsonl
   ```

2. Run the generator:
   ```bash
   python3 .beads/generate_progress.py
   ```

2. Confirm the output was written and report line count:
   ```bash
   wc -l .beads/PROGRESS.md
   ```

3. Show the user the top of the generated file (stats + first phase) so they can see the result.

## Notes

- Script location: `.beads/generate_progress.py`
- Input: `.beads/issues.jsonl`
- Output: `.beads/PROGRESS.md` (overwritten each run)
- Pure local script — reads JSONL, writes Markdown. No network, no DB writes.
- If `issues.jsonl` is stale relative to the live Dolt DB, the report will also be stale. Regenerate `issues.jsonl` first (via `bd export`) if the live DB is accessible.
