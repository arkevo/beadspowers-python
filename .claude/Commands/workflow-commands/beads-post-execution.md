---
description: Post-execution options after plan execution completes - verification level detection, build validator, smoke test
---

# Post-Execution Options

After **any** implementation path completes — `execute-plans` /
`subagent-driven-development`, the **bug path** (`systematic-debugging → TDD`), or
any **direct TDD** fix — determine verification level and offer options. This is
mandatory before ship/"done" (see the router's *Hard Stop: Verification Before
Ship / "Done"*); it is NOT limited to plan-execution. The chosen
`python-verification-{level}` skill writes the `.beads/.verification-done` marker
that `workflow-commands:beads-ship-task` gates on.

## Step 1: Update Workflow Step
```bash
echo "Post-Execution" > .beads/.workflow-step
```

## Step 2: Record the Changed Set, Then Pick the Level

### Step 2a: Record the changed set first (never skip this)

Nothing else in the workflow writes `modified_files`.
`workflow-commands:beads-start-task` creates `.beads/.session-state.json` with an
empty list, and every verification skill only reads it. Left empty, every task
would route to Quick (because `total_lines_changed` stays 0) and every scoped
auto-fix would be skipped. So derive the changed set here, once. It is:

- tracked files with uncommitted edits, staged or not (deleted files are left out);
- untracked files (nested repositories and worktrees are left out);
- files the branch changed since it left the trunk, that is since
  `git merge-base <trunk> HEAD`.

Workflow state under `.beads/` is not task work, so it is left out too, and a
renamed file is recorded under its new path. `total_lines_changed` covers the same
range (lines added plus lines removed) plus the full length of every untracked
file. The trunk is whatever `origin/HEAD` points at, normally `origin/main` or
`origin/master`; when that is unset, the block asks git to set it once. When the
repository has no `origin` at all, the branch's own commits cannot be measured,
so the block records the uncommitted and untracked files and says the branch
range was skipped.

Run the block from anywhere inside the repository. It rewrites only
`modified_files` (a plain list of path strings) and `total_lines_changed`, and
keeps every other key in the file (`task_id`, `plan_file`, `verification`, …):

```bash
# snippet: changed-set
cd "$(git rev-parse --show-toplevel)" || exit 1
trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null) || {
  git remote set-head origin --auto >/dev/null 2>&1
  trunk=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
}
base=""
[ -n "$trunk" ] && base=$(git merge-base "$trunk" HEAD 2>/dev/null)
if [ -z "$base" ]; then
  echo "Changed set: branch range skipped (no trunk to compare with) - uncommitted and untracked files only."
  base=$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)
fi
BASE="$base" python3 - <<'PY'
import json, os, subprocess
from pathlib import Path

def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout.decode()

def keep(path):
    return bool(path) and not path.endswith("/") and not path.startswith(".beads/")

base = os.environ["BASE"]
tracked = {p for p in git("diff", "--name-only", "-z", "--diff-filter=d", base).split("\0") if keep(p)}
untracked = {p for p in git("ls-files", "--others", "--exclude-standard", "-z").split("\0") if keep(p)}
added = {p for p in git("diff", "--name-only", "-z", "--diff-filter=A", base).split("\0") if keep(p)}

lines, parts, i = 0, git("diff", "--numstat", "-z", base).split("\0"), 0
while i < len(parts) and parts[i]:
    plus, minus, path = parts[i].split("\t", 2)
    if path:
        i += 1
    else:  # a rename or copy: the old path, then the new path, follow
        path, i = parts[i + 2], i + 3
    if keep(path) and plus != "-":  # "-" marks a binary file
        lines += int(plus) + int(minus)
for path in untracked:
    try:
        data = Path(path).read_bytes()
    except OSError:
        continue
    if b"\0" not in data[:8000]:  # skip binary files
        lines += data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)

files = sorted(tracked | untracked)
new_modules = sorted(p for p in added | untracked if p.startswith("src/") and p.endswith(".py"))

state_path = Path(".beads/.session-state.json")
try:
    state = json.loads(state_path.read_text())
except (OSError, ValueError):
    state = {}
if not isinstance(state, dict):
    state = {}
state["modified_files"] = files
state["total_lines_changed"] = lines
state_path.parent.mkdir(exist_ok=True)
tmp = state_path.with_name(state_path.name + ".tmp")
tmp.write_text(json.dumps(state, indent=2) + "\n")
tmp.replace(state_path)

print(f"Changed set: {len(files)} file(s), {lines} line(s) changed")
for path in files:
    print(f"  {path}")
print("New modules under src/: " + (", ".join(new_modules) if new_modules else "none"))
PY
```

The block reads a possibly-dirty tree, so it can pick up unrelated
work-in-progress. That is accepted here, and only here: it runs once, at the point
where this task is what dirtied the tree, and it prints the list so you can see
what it caught. A verification skill never re-derives the set; when the set is
unknown it skips its auto-fix instead (`.claude/rules/verification-write-scope.md`).

### Step 2b: Pick the level

Read `modified_files` and `total_lines_changed` back from
`.beads/.session-state.json`, then:

- **Under 50 lines:** Quick (lint + tests)
- **50–200 lines:** Standard (analysis phases, no agents)
- **Over 200 lines, or a new module under `src/`:** Full (review agents + Codex
  adversarial pass). Step 2a prints the new modules it found. A new test file on
  its own does not force Full.

If `modified_files` is still empty after Step 2a (outside a git repository, or a
genuinely clean tree), ask:
> What files did you change? (Or say "quick", "standard", or "full" to select level)

This question only picks the level. Never ask it in order to justify running an
auto-fix. If the answer names files, that list becomes the changed set: write it
into `modified_files` (read the file, change that one key, write it back) and echo
it back in the invoked skill's report, as the router's *Named Scope Is
Authorization* section allows. If the answer names only a level, the changed set
stays **unknown**, and the invoked skill skips its auto-fix rather than widening
it to the project root.

## Step 3: Build Validator Check

| Change Type | Recommend | Reason |
|-------------|-----------|--------|
| New C extension or native dependency | **Yes** | Native compilation may fail silently |
| pyproject.toml changes (build-system, dependencies) | **Yes** | Build-breaking misconfigs |
| New dependency with native components | **Yes** | Native compilation may fail |
| Pure Python logic, services, utilities | No | Tests import the code |
| Test-only changes | No | No build impact |
| Config/tooling changes (.claude/, .beads/) | No | No build impact |

## Step 4: Smoke Test Check

| Change Type | Recommend | Why |
|-------------|-----------|-----|
| CLI/API endpoint changes | **Yes** | Manual verification confirms expected behavior |
| Template/rendering changes | **Yes** | Visual correctness needs human eyes |
| New native extension integration | **Yes** | Native failures surface at runtime |
| Pure data layer (repositories, models, services) | **Skip** | No user-facing output |
| Test-only / config changes | **Skip** | No app behavior change |

## Step 5: Show Prompt

```
✅ Execution complete for **bd-xxxx "[Task Title]"**

Changes: [N] lines across [M] files (recorded in Step 2a)

**Verification options:**
1. **Quick verify** — lint + tests only (~30 sec)
2. **Standard verify** — analysis phases, no agents (~2 min)
3. **Full verify** — review agents + Codex adversarial pass (~5+ min)
4. **Ship it** — skip verification, commit

Recommended: **[Level based on change size]**
[⚙️ Build validation recommended — say "build check" anytime]  ← include if applicable
[🔥 Smoke test recommended after verification]  ← include if applicable

Say "quick", "standard", "full", or "ship it" to continue.
```

## Natural Language Commands

| User Says | Action |
|-----------|--------|
| "Quick verify" / "just lint and test" | Invoke `workflow-commands:python-verification-quick` |
| "Standard verify" / "verify without agents" | Invoke `workflow-commands:python-verification-standard` |
| "Full verify" / "complete verification" | Invoke `workflow-commands:python-verification-full` |
| "Ship it" / "Send it" | Invoke `workflow-commands:beads-ship-task` |
| "I'm confident" / "Skip verification" | Invoke `workflow-commands:beads-ship-task` |
| "Build check" / "run build validator" | Invoke `workflow-commands:P11.5-build-validation-[F]` |
| "Smoke test" / "run the app" | Run app manually, guide visual check |
| "actually do full verify" | Override level, invoke full verification |

---

## Post-Verification Smoke Test

After verification passes and before ship, show:

```
✅ Verification passed.

🔥 **Smoke test?** (optional)
Run the app locally to confirm changes work.

1. **Run locally** — Quick launch via terminal
2. **Skip** — Ship based on tests alone

Recommended: **[Run / Skip]** — [reason based on change type]
```

During smoke test:
```bash
echo "Smoke Test" > .beads/.workflow-step
```

When user confirms app works → stop app → proceed to `workflow-commands:beads-ship-task`.

If user finds an issue → stop app → fix → re-run verification (at least quick) → offer smoke test again.

---

## CRITICAL — Project Override

Do NOT invoke `finishing-a-development-branch` after execution completes. This project uses `workflow-commands:beads-ship-task` and commit-commands skills instead.
