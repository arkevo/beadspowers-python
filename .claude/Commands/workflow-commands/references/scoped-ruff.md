# Scoped Ruff Blocks

**This is a reference, not a slash command.** It holds the two runnable blocks that
`.claude/rules/verification-write-scope.md` requires every auto-fix and format step
to use: P02, and the verification tiers' Phase 2 (plus, in the full tier, Phases 8.5
and 12.5). Run a block exactly as written, from anywhere inside the repository.
Each block reads the changed set (`modified_files` in `.beads/.session-state.json`)
itself; to cover a file the task added later, such as a test Phase 12 created, add
it to `modified_files` first — never pass a file list. The two blocks differ only in
their `SCOPED_RUFF_MODE=` line; keep them identical otherwise.

## Lint auto-fix

```bash
# snippet: scoped-ruff-fix
cd "$(git rev-parse --show-toplevel)" || exit 1
SCOPED_RUFF_MODE=fix python3 - <<'PY'
import hashlib, json, os, subprocess, sys
from pathlib import Path

MODE = os.environ["SCOPED_RUFF_MODE"]
NEVER = ("/.venv/", "/vendor/", "/third_party/", "/migrations/")
GENERATED = ("_pb2.py", "_pb2_grpc.py", "_pb2.pyi")

def status():
    raw = subprocess.run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                         capture_output=True, check=True).stdout.decode().split("\0")
    entries, i = {}, 0
    while i < len(raw) and raw[i]:
        entries[raw[i][3:]] = raw[i][:2]
        i += 2 if raw[i][0] in "RC" else 1  # a rename is followed by its old path
    return entries

def digest(path):
    try:
        return hashlib.sha1(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None

try:
    changed = json.loads(Path(".beads/.session-state.json").read_text()).get("modified_files") or []
except (OSError, ValueError, AttributeError):
    changed = []
if not changed:
    print("Auto-fixed: SKIPPED (changed set unknown)")
    sys.exit(0)
files = [p for p in changed
         if p.endswith((".py", ".pyi")) and not p.endswith(GENERATED)
         and not any(d in "/" + p for d in NEVER) and Path(p).is_file()]
notebooks = [p for p in changed if p.endswith(".ipynb") and Path(p).is_file()]

before = status()
hashes = {p: digest(p) for p in before if p not in files}
if notebooks:  # report only: lint or check, never write
    check = ["check", "--no-fix"] if MODE == "fix" else ["format", "--check"]
    subprocess.run(["ruff", *check, "--force-exclude", "--", *notebooks])
if not files:
    print("Auto-fixed: SKIPPED (no Python files in the changed set)")
    sys.exit(0)
runs = [["check", "--diff"], ["check", "--fix"]] if MODE == "fix" else [["format"], ["format", "--check"]]
failed = []
for args in runs:
    rc = subprocess.run(["ruff", *args, "--force-exclude", "--", *files]).returncode
    if rc >= 2:  # 1 means findings remain or files would change; 2 means ruff itself failed
        failed.append(f"ruff {' '.join(args)} exited {rc}")

leaks = []
for path, xy in status().items():
    if path in files:
        continue
    if path not in before:
        if xy == "??":
            leaks.append(f"{path} (untracked, left in place)")
        else:  # may be someone else's edit made during the run: never revert it
            leaks.append(f"{path} (changed during the run; NOT reverted, inspect it)")
    elif digest(path) != hashes.get(path):
        leaks.append(f"{path} (had uncommitted edits before; NOT reverted, review it)")
if failed:
    print("Auto-fixed: FAILED (" + "; ".join(failed) + ") - read ruff's error above; the fix did not complete")
else:
    print(f"Auto-fix ran on {len(files)} changed file(s).")
print("Scope check: no files outside the changed set" if not leaks
      else "Scope check: LEAK: " + "; ".join(leaks))
sys.exit(1 if failed or leaks else 0)
PY
```

## Formatting

The same block in format mode: it writes with `ruff format`, then re-checks with
`ruff format --check`.

```bash
# snippet: scoped-ruff-format
cd "$(git rev-parse --show-toplevel)" || exit 1
SCOPED_RUFF_MODE=format python3 - <<'PY'
import hashlib, json, os, subprocess, sys
from pathlib import Path

MODE = os.environ["SCOPED_RUFF_MODE"]
NEVER = ("/.venv/", "/vendor/", "/third_party/", "/migrations/")
GENERATED = ("_pb2.py", "_pb2_grpc.py", "_pb2.pyi")

def status():
    raw = subprocess.run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                         capture_output=True, check=True).stdout.decode().split("\0")
    entries, i = {}, 0
    while i < len(raw) and raw[i]:
        entries[raw[i][3:]] = raw[i][:2]
        i += 2 if raw[i][0] in "RC" else 1  # a rename is followed by its old path
    return entries

def digest(path):
    try:
        return hashlib.sha1(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None

try:
    changed = json.loads(Path(".beads/.session-state.json").read_text()).get("modified_files") or []
except (OSError, ValueError, AttributeError):
    changed = []
if not changed:
    print("Auto-fixed: SKIPPED (changed set unknown)")
    sys.exit(0)
files = [p for p in changed
         if p.endswith((".py", ".pyi")) and not p.endswith(GENERATED)
         and not any(d in "/" + p for d in NEVER) and Path(p).is_file()]
notebooks = [p for p in changed if p.endswith(".ipynb") and Path(p).is_file()]

before = status()
hashes = {p: digest(p) for p in before if p not in files}
if notebooks:  # report only: lint or check, never write
    check = ["check", "--no-fix"] if MODE == "fix" else ["format", "--check"]
    subprocess.run(["ruff", *check, "--force-exclude", "--", *notebooks])
if not files:
    print("Auto-fixed: SKIPPED (no Python files in the changed set)")
    sys.exit(0)
runs = [["check", "--diff"], ["check", "--fix"]] if MODE == "fix" else [["format"], ["format", "--check"]]
failed = []
for args in runs:
    rc = subprocess.run(["ruff", *args, "--force-exclude", "--", *files]).returncode
    if rc >= 2:  # 1 means findings remain or files would change; 2 means ruff itself failed
        failed.append(f"ruff {' '.join(args)} exited {rc}")

leaks = []
for path, xy in status().items():
    if path in files:
        continue
    if path not in before:
        if xy == "??":
            leaks.append(f"{path} (untracked, left in place)")
        else:  # may be someone else's edit made during the run: never revert it
            leaks.append(f"{path} (changed during the run; NOT reverted, inspect it)")
    elif digest(path) != hashes.get(path):
        leaks.append(f"{path} (had uncommitted edits before; NOT reverted, review it)")
if failed:
    print("Auto-fixed: FAILED (" + "; ".join(failed) + ") - read ruff's error above; the fix did not complete")
else:
    print(f"Auto-fix ran on {len(files)} changed file(s).")
print("Scope check: no files outside the changed set" if not leaks
      else "Scope check: LEAK: " + "; ".join(leaks))
sys.exit(1 if failed or leaks else 0)
PY
```
