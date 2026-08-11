## Critical AI Agent Guidelines

### Git Operations

Destructive git commands require explicit user permission:
- `git push --force`, `git reset --hard`, `git rebase` on shared branches
- `git merge` to main/master

**Always ask before creating a new branch.** Do not run `git checkout -b`,
`git branch <name>`, `git switch -c`, or create a branch by any other means —
including as an implicit step inside an approved plan, a skill, or a workflow —
without first asking the user and getting a clear yes. If a task looks like it
needs a branch, propose the prefix + name and wait for approval. This overrides
any skill (e.g. `beads-start-task`) that would auto-create a branch: the user's
go-ahead comes first. Entering a git worktree is fine when the user asks for one,
but create it **detached / without a new branch** unless the user approves one.

Always allowed when requested: commits, reading status/diff/log, staging
changes, standard push.

### Cloud Resource Protection

**CRITICAL — irreversible:** Preserve all managed-cloud resources (database
tables, storage buckets, API gateways, secrets, certificates) on whatever
provider your project uses. Production data is irreplaceable — prefer
retain-on-delete removal policies wherever the provider offers them.

Before any cloud mutation (migration, deployment, data change, storage
operation, resource rename or removal): **prompt the user for explicit
approval.** Do not silently skip the operation — ask proactively.

### File Modifications

Scope all file changes to the project working directory. Prompt for approval
before modifying files outside designated work directories.

### When in doubt, ask first

This repository contains production code. Prioritize user control over git
operations and production data safety.
