---
name: beads-worktree-troubleshooting
description: Use when bd in a worktree returns [] or errors, when verifying the embedded Dolt store's integrity, after a concurrent bd write burst, or on "database is locked by another dolt process".
---

# Beads Worktree Troubleshooting (embedded mode)

## Worktree sees no data (`[]` or errors)

1. Confirm it is a real worktree of the embedded-mode repo:
   `git rev-parse --git-common-dir` from the worktree should resolve to the main repo's
   `.git`.
2. Confirm the parent's `.beads/metadata.json` shows `"dolt_mode": "embedded"`.
3. Inspect the store in the MAIN repo: `manifest` and `journal.idx` live under
   `.beads/embeddeddolt/<db>/.dolt/noms/` and must exist with non-zero size. From the
   main repo root,
   `find .beads/embeddeddolt \( -name manifest -o -name journal.idx \) -size +0 -print`
   must print both. Zero-byte or missing is a real corruption signal — a
   data-safety event: stop and follow `.claude/rules/critical ai agent rule.md` before
   any further mutation.

There is no `.beads/redirect` file to author, no port to discover, and no
`bd dolt start` / `stop` dance in embedded mode.

## Verifying store integrity

`bd doctor` in embedded mode always exits 0 with a static "not yet supported" note — it
never varies with the store's state, so never treat it as a gate. Instead compare an
unbounded read-back count against a known baseline (`bd list -n 0 | wc -l` — the default
`bd list` caps at 50 rows and silently truncates) plus the `manifest` / `journal.idx`
size check above.

## Lock contention ("database is locked by another dolt process")

A real storage-layer lock exists (`.beads/embeddeddolt/.lock`). Observed with beads
1.0.4 in a downstream project: at a realistic concurrency of about 2–8 parallel
writers, contention was 0%; it appeared only in an artificial stress test with about 50
cross-worktree writers (22–40% of writes), and every failure was loud — a non-zero exit
or an explicit error — with no silent loss ever observed. Re-validate these numbers
after a beads upgrade.

If it occurs, retry with a bound: 3–5 attempts, about 200–500 ms initial backoff capped
at about 5–10 s, retrying on the lock error or "context canceled". BEFORE each retry,
check whether the write already landed (`bd list` / `bd show` keyed on the title being
submitted): in that stress test roughly a quarter of the loud failures had actually
succeeded, so a blind resubmit creates a duplicate issue.

## JSONL staleness after a killed write

A killed `bd` process can land its Dolt write while its own JSONL auto-export is
cancelled mid-flight. A later write's full re-export usually heals this — but if the
killed write was the LAST in a concurrent burst, nothing triggers the heal. Flush by
hand: `bd export -o .beads/issues.jsonl`.

## Gitignore

`.beads/.gitignore` must contain `embeddeddolt/` — confirm
`git check-ignore .beads/embeddeddolt` succeeds before any broad `git add` in the main
checkout.
