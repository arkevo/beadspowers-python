

Branch naming: Use type/scope-kebab-case. Types: feat/ for new behavior, fix/ for bugs, refactor/ for internal changes, exp/ for spikes, hotfix/ for emergencies, chore/ for tooling/CI. Examples: feat/upload-retry, fix/feed-null-guard, refactor/auth-service.

Releases & rollback: Tag every release (git tag -a vX.Y.Z -m "desc" then git push --tags). Prefer revert PRs over history rewrites (git revert <merge_commit_sha> → new PR). Keep release tags so you can redeploy a known-good build fast.