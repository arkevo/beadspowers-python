

Branch naming: Use type/scope-kebab-case. Types: feat/ for new behavior, fix/ for bugs, refactor/ for internal changes, exp/ for spikes, hotfix/ for emergencies, chore/ for tooling/CI. Examples: feat/upload-retry, fix/feed-null-guard, refactor/auth-service.

Releases & rollback: Tag every release (git tag -a vX.Y.Z -m "desc" then git push --tags). Prefer revert PRs over history rewrites (git revert <merge_commit_sha> → new PR). Keep release tags so you can redeploy a known-good build fast.

State checks: `git branch -vv` and `git status` compare against the cached copy of origin, so run `git fetch origin` in the same response before claiming a branch is ahead of or behind its remote.

Worktrees: a bare "create a worktree" request (no task attached) ends once the worktree exists — no `pip install` or `uv sync`, no `pytest`, `ruff` or `mypy`, no `python -m build` until real work starts there or the user asks. Create it detached unless the user approves a branch (`critical ai agent rule.md`).
