# Beads

**Section:** Task Management

How to run `bd` safely in this workflow. The `beads:*` plugin skills run these same
commands — the plugin has no MCP layer (`beads-plugin-cli-only.md`).

## Two channels: code and beads

- Git carries code; `bd dolt` carries beads. Pull first, push last: at session or task
  start run `git pull` and `bd dolt pull`; at ship or session close run `git push` and
  `bd dolt push`. Never `--force` a beads push except a deliberate, agreed re-baseline.
- The Dolt remote lives on the project's own git remote:
  `bd dolt remote add origin git+https://github.com/<owner>/<repo>.git`.
- A project with no Dolt remote yet keeps working. `bd dolt push` skips on its own
  ("No remote is configured — skipping."), but `bd dolt pull` fails ("no remote"), so
  every step that pulls guards it and says so in one line:

  ```bash
  if bd dolt remote list 2>/dev/null | grep -q 'No remotes configured'; then
    echo "Beads: no Dolt remote configured — skipping bd dolt pull."
  else
    bd dolt pull
  fi
  ```

- A brand-new Dolt remote is empty, and `bd dolt pull` fails on it
  ("no branches found in remote"). Seed it once with `bd dolt push`
  right after `bd dolt remote add` — the setup below does — and
  pull first, push last works from then on.

## Setting up a new project

After `/beads:init` (or instead of it), finish the setup from the project root, on a
setup branch because `bd init` commits to the current branch, then open a PR for it:

```bash
git switch -c chore/workflow-setup
bd init --skip-agents
bd config set export.git-add false
printf '\nno-auto-import: true\n' >> .beads/config.yaml
printf '\nissues.jsonl\n.session-state.json\n.workflow-step\n.verification-done\n' >> .beads/.gitignore
git rm --cached --ignore-unmatch .beads/issues.jsonl
bd dolt remote add origin git+https://github.com/<owner>/<repo>.git
bd dolt push
```

Skip `bd init` if `/beads:init` already ran it. The ignored state files keep a ship
from committing the workflow's own state. The final `bd dolt push` seeds the new
remote; it publishes the beads on the project's git remote, so on a public
repository the bead text is public.

## The JSONL export is a readable artifact, nothing else

- `.beads/issues.jsonl` is for reading — diffs, grep, progress reports. It is not a
  sync channel. Keep it untracked and gitignored, and never re-track it.
- After mutating `bd` commands — and always after a burst of concurrent writes, such as
  a parallel agent fan-out — refresh it with `bd export -o .beads/issues.jsonl`
  (`bd export` without `-o` writes to stdout).
- Keep the export unstaged and untracked: `.beads/config.yaml` carries
  `export.git-add: false`, and `.beads/.gitignore` lists `issues.jsonl`. The config also
  carries `no-auto-import: true`, which mirrors the setup the fix below was made on.
  Beads 1.0.4 does not read that key — the binary has no such setting, and its checkout
  hook re-exports from the database rather than importing the file — so it costs nothing
  but protects nothing on 1.0.4 either; the untracked export is what holds. `bd config
  set` rejects the key, so it is appended directly, with a leading newline, because
  `bd config set` leaves the file without a trailing one and a plain append corrupts the
  YAML:

  ```bash
  bd config set export.git-add false
  printf '\nno-auto-import: true\n' >> .beads/config.yaml
  ```

- **Why — observed in a downstream project.** Finished beads kept reverting on their
  own. `issues.jsonl` was tracked in git AND was an auto-import source. `bd import`
  upserts every row in the file over the live store; auto-import fired whenever the file
  was newer than the database; and any checkout, merge or worktree switch that rewrote
  the file armed it. A stale snapshot then silently restored old `status` and old
  `updated_at` values over rows that had moved on — more than a dozen at a time, once
  including a shipped epic and all its children. Untracking the export and stopping it
  from being auto-staged fixed it (the `no-auto-import` line was added at the same time).
  Undo neither.

## Read back what you write

- Read back every mutating command with `bd show <id>`, and never report a bead state
  you have not read back. This matters most for the batch lane's `wp:*` and `ex:*`
  labels: they are its only durable progress record, and a lost label silently un-does
  a finished wave, so a resumed run redoes it.
- Know the limit. A read-back would not have caught the reverts above: those writes did
  land and read back correctly at the time, and were undone later by an unrelated
  command, usually in another session. So if a bead looks wrong and you already
  verified the write, do not simply re-apply it. Compare its `updated_at` with when you
  wrote it: a value OLDER than your own write means something restored a snapshot, and
  the fix is upstream, not another retry.

## Never run two `bd` commands at the same time

Every worktree and session shares one embedded Dolt store, and a `bd` process that
commits a stale working set overwrites rows another process committed moments before.
Put every `bd` command of a step in one `&&` chain — reads included, since they can
create commits too — never in separate parallel tool calls. A parallel agent fan-out
has the same exposure, so read its labels back after it returns.

Observed in a downstream project: a `bd close` landed and read back closed; a
`bd create` issued as a parallel tool call in the same response committed seconds
later, and its only change was that status going from closed back to open.

To diagnose a revert, run `bd history <id> --json` (keys `CommitHash`, `CommitDate`,
`Committer`, `Issue`), then `bd diff <full-hash> <full-hash>`. Short hashes fail with
"branch not found", and the diff shows issue fields only, not dependencies. If the
reverting commit's time matches another `bd` process you ran, it is this race: re-apply
the write serially and read it back.

## Worktrees and store health

- **No bootstrap after `EnterWorktree`.** In beads' embedded mode (check yours with
  `bd dolt status`) a fresh worktree sees the full parent store automatically, through
  git-common-dir detection. There is no setup step to invent.
- **Never stop the store from inside a worktree.** In server mode, `bd dolt stop`
  targets the shared parent store and takes beads down for every concurrent agent.
  Start or stop it only from the main repo root, and only when something is actually
  wrong.
- **`bd doctor` proves nothing in embedded mode** — it exits cleanly whatever state the
  store is in, so never use it as a readiness gate. Verify a store with
  `bd list -n 0 | wc -l` against a known count (plain `bd list` stops at 50 rows), plus
  non-zero `manifest` and `journal.idx` files, which live under
  `.beads/embeddeddolt/<db>/.dolt/noms/`:
  `find .beads/embeddeddolt \( -name manifest -o -name journal.idx \) -size +0 -print`
  must print both.
- If `bd` in a worktree returns `[]`, errors, or reports "database is locked", load the
  `beads-worktree-troubleshooting` skill.

## Cross-session memory

`bd remember "insight"` persists knowledge across sessions; search it with
`bd memories <keyword>`.
