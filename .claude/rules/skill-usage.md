# Skill Usage Rules

## Fully Qualified Names Required

When invoking skills with the `Skill` tool, **always use the fully qualified name** including the namespace prefix.

### Correct Format

```
namespace:skill-name
```

### Examples

| Wrong | Correct |
|-------|---------|
| `commit-push` | `commit-commands:commit-push` |
| `commit-push-pr` | `commit-commands:commit-push-pr` |
| `commit` | `commit-commands:commit` |
| `getIssues` | `sentry:getIssues` |
| `stats` | `beads:stats` |
| `ready` | `beads:ready` |

### Common Skill Namespaces

| Namespace | Skills |
|-----------|--------|
| `commit-commands` | `commit`, `commit-push`, `commit-push-pr`, `clean_gone` |
| `beads` | `stats`, `ready`, `list`, `show`, `create`, `update`, `close`, `sync`, etc. |
| `sentry` | `seer`, `getIssues`, `sentry-code-review`, etc. |
| `superpowers` | `test-driven-development`, `systematic-debugging`, `writing-plans`, etc. |
| `workflow-commands` | `python-verification-quick`, `python-verification-standard`, etc. |
| `one-off-commands` | `status`, etc. |
| `encoding-commands` | `encode-single-test`, `batch-encode-register` |

### Why This Matters

The `Skill` tool requires the full namespace:skill-name format. Using just the skill name without the namespace causes an "Unknown skill" error and wastes a tool call.

### Quick Reference

Before calling `Skill`, check the skill list in the system prompt. Skills are listed as:
```
- namespace:skill-name: Description...
```

Copy the full `namespace:skill-name` portion.

## Naming Convention

### Namespace Folder Names Must Be Kebab-Case

All skill namespace folders under `.claude/Commands/` **MUST** use `kebab-case`
(lowercase with hyphens). No spaces, no Title Case, no underscores.

| Correct | Wrong |
|---------|-------|
| `encoding-commands` | `Encoding Commands` |
| `one-off-commands` | `One off commands` |
| `workflow-commands` | `Workflow Commands` |
| `commit-commands` | `Commit Commands` |

Claude Code's `/` slash command parser splits on spaces. A namespace like
`Encoding Commands` causes the parser to treat `Encoding` as the skill name
and drop the rest, resulting in "Unknown skill" errors.

### Skill File Names Must Be Kebab-Case

Skill `.md` filenames inside namespace folders must also be `kebab-case`:

| Correct | Wrong |
|---------|-------|
| `encode-single-test.md` | `Encode Single Test.md` |
| `python-build-fix.md` | `Python Build Fix.md` |

### Sub-Namespace Folders

Sub-folders within a namespace (e.g., `one-off-commands/debug/`) also follow
kebab-case. This creates nested namespaces like
`one-off-commands:debug:sentry-output`.

### Checklist for New Skills

Before creating a new skill:

1. Namespace folder exists and is kebab-case? If not, create it in kebab-case.
2. Skill filename is kebab-case `.md`?
3. No spaces anywhere in the path from `.claude/Commands/` to the skill file?

## Beads Plugin Enforcement

### Rule: Always Use Beads Plugin Skills, Never the `bd` CLI

When performing any Beads operation, **always invoke the corresponding plugin
skill** via the `Skill` tool. Never run `bd` commands directly in Bash.

### Skill Mapping

| Operation | Skill to Invoke |
|-----------|----------------|
| List ready/unblocked tasks | `beads:ready` |
| List blocked tasks | `beads:blocked` |
| Show issue details | `beads:show` |
| Project stats | `beads:stats` |
| Search issues | `beads:search` |
| View/manage comments | `beads:comments` |
| Epic management | `beads:epic` |
| Export issues | `beads:export` |
| Import issues | `beads:import` |
| Initialize beads | `beads:init` |
| Rename prefix | `beads:rename-prefix` |
| Restore issue history | `beads:restore` |
| Check version | `beads:version` |
| Show workflow guide | `beads:workflow` |
| Audit interactions | `beads:audit` |

### No CLI Exceptions

At beads v0.63.3+, all beads operations are handled through the plugin
skills. The `bd sync --flush-only` exception from v0.49.4 no longer
applies — JSONL persistence has been removed and the pre-commit hook
uses Dolt-native operations automatically.

### Why

The `bd` CLI binary may not be in PATH on all machines. The beads plugin
skills are always available through Claude Code's Skill tool and provide
reliable, consistent access to the beads database regardless of environment.
