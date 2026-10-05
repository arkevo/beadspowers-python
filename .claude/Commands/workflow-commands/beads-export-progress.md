---
description: Regenerate .beads/PROGRESS.md from issues.jsonl by running .beads/generate_progress.py
---

# Beads Export Progress

Regenerates the human-readable progress report at `.beads/PROGRESS.md` from a fresh export of the beads database. Groups issues by phase, shows completion stats, progress bar, blockers, and close dates.

`.beads/issues.jsonl` is a readable export, not a sync channel: it is untracked, beads sync over the Dolt remote, and the file is only as current as its last export. So this command always refreshes it before reading.

## Steps

1. Refresh the export from the live beads database:
   ```bash
   bd export -o .beads/issues.jsonl
   ```
   If this fails, say so and ask before reporting from the existing export, which may be stale.

2. Run the generator:
   ```bash
   python3 .beads/generate_progress.py
   ```

3. Confirm the output was written and report line count:
   ```bash
   wc -l .beads/PROGRESS.md
   ```

4. Show the user the top of the generated file (stats + first phase) so they can see the result.

## Notes

- Script location: `.beads/generate_progress.py`
- Input: `.beads/issues.jsonl`, refreshed in Step 1
- Output: `.beads/PROGRESS.md` (overwritten each run)
- Pure local script — reads JSONL, writes Markdown. No network, no DB writes.
