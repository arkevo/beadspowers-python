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
| `beads-start-task` | `workflow-commands:beads-start-task` |
| `stats` | `beads:stats` |
| `ready` | `beads:ready` |

### Common Skill Namespaces

| Namespace | Skills | Source |
|-----------|--------|--------|
| `commit-commands` | `commit`, `commit-push`, `commit-push-pr`, `clean_gone` | plugin (`commit-commands@claude-plugins-official`) |
| `superpowers` | `test-driven-development`, `systematic-debugging`, `writing-plans`, etc. | plugin (`superpowers@claude-plugins-official`) |
| `beads` | `stats`, `ready`, `list`, `show`, `create`, `update`, `close`, `sync`, etc. | plugin (`beads`) |
| `workflow-commands` | `beads-start-task`, `beads-ship-task`, `plan-refinement-qa`, `plan-summary-console`, `python-verification-quick/standard/full`, `hotfix-interrupt`, `P*-*` phase gates, etc. | local (`.claude/Commands/workflow-commands/`) |

> Only the namespaces above ship with this template. If you add your own local
> namespace, create it as a kebab-case folder under `.claude/Commands/` and list
> it here — a skill Claude cannot name is a skill Claude will not invoke.

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
| `workflow-commands` | `Workflow Commands` |
| `commit-commands` | `Commit Commands` |
| `writing` | `Writing Commands` |

Claude Code's `/` slash command parser splits on spaces. A namespace like
`Encoding Commands` causes the parser to treat `Encoding` as the skill name
and drop the rest, resulting in "Unknown skill" errors.

### Skill File Names Must Be Kebab-Case

Skill `.md` filenames inside namespace folders must also be `kebab-case`:

| Correct | Wrong |
|---------|-------|
| `beads-start-task.md` | `Beads Start Task.md` |
| `python-verification-quick.md` | `Python Verification Quick.md` |

### Sub-Namespace Folders

If a namespace ever gets sub-folders (e.g. `workflow-commands/debug/`), they
also follow kebab-case, creating nested namespaces like
`workflow-commands:debug:trace-pipeline`. This repo currently has no nested
skill namespaces — `workflow-commands` is flat, and its `references/` folder
holds shared assets, not skill sub-namespaces.

### Checklist for New Skills

Before creating a new skill:

1. Namespace folder exists and is kebab-case? If not, create it in kebab-case.
2. Skill filename is kebab-case `.md`?
3. No spaces anywhere in the path from `.claude/Commands/` to the skill file?

## Beads Plugin Enforcement

### Rule: Prefer Beads Plugin Skills

See `.claude/rules/0_Beads x Superpowers/beads-plugin-cli-only.md` — this
plugin has no MCP layer, so invoking a `beads:*` skill means running the
`bd` command it names, directly in Bash.

This is a single repo — Beads runs against the local store under `.beads/`.
There is no multi-repo hub, so **`bd repo sync` is not part of any workflow here.**

**Team sync depends on how your project is set up.** By default beads state
travels as `issues.jsonl` committed alongside your code, so a normal
`git commit` + `git push` ships both. If you configure a **Dolt remote**
instead, beads becomes a **second channel**: sync it at session/task start and
again at ship/session close (`bd dolt pull` / `bd dolt push`), in addition to
`git push`. Either way, never `--force` a beads push except a deliberate,
agreed re-baseline.

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
| Pull teammate's beads (session/task START) | `git pull` — or `bd dolt pull` on a Dolt remote |
| Publish your beads (ship / session CLOSE) | `git push` — or `bd dolt push` on a Dolt remote |

