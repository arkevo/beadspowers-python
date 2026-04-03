# Python 

A structured AI-assisted development workflow for Claude Code that combines
**Beads** (git-backed issue tracking) with **Superpowers** (plan-execute-verify lifecycle) into an enforced sequence.

```
Start Task -> Plan -> Refine Plan -> Execute -> Verify -> Ship
```

## Additional Features: 

### Verification
 Includes a Python specific 13 verification process with ability to launch a quick and  and 3 verification options at the end with a recommandation of which option you should do. Quick, Standard, and Full (13 phase):

 | Tier | Phases | When to Use |
|------|--------|-------------|
| **Quick** | Lint + build | Small changes, hotfixes |
| **Standard** | Lint + code review + architecture + build + tests | Normal tasks |
| **Full** | All 13 phases (lint through security) | Major features, pre-release |


### Plan Refinement
After Superpowers Planning is done, Claude will analyze the plan and as you 10 questions with a mix of Critical, Recommended, and nice to haves in order to engage you on refining the plan. Each question will include 3 options with reasoning and Claude will give their recommendation. You can skip this at any stage by typing skip. 






## Prerequisites

### Claude Code

Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI,
desktop app, or IDE extension).

### Required Plugins

Install these Claude Code plugins in order. Run each command inside Claude Code
(not your shell).

#### 1. Beads (git-backed issue tracker)

```
/install-plugin beads from steveyegge/beads
```

- **What it provides:** `beads:*` skills (create, list, show, ready, close,
  sync, etc.) and the `bd` CLI for git-backed issue tracking
- **Scope:** user (available across all projects)
- **Repo:** [steveyegge/beads](https://github.com/steveyegge/beads)

After installing, initialize beads in your project:

```bash
bd init
```

#### 2. Superpowers

```
/install-plugin superpowers from anthropics/claude-plugins-official
```

- **What it provides:** `superpowers:*` skills (writing-plans, executing-plans,
  subagent-driven-development, brainstorming, systematic-debugging,
  test-driven-development, verification-before-completion, etc.)
- **Scope:** project
- **Repo:** [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)

#### 3. Commit Commands

```
/install-plugin commit-commands from anthropics/claude-plugins-official
```

- **What it provides:** `commit-commands:*` skills (commit, commit-push,
  commit-push-pr, clean_gone)
- **Scope:** project

#### 4. Codex (optional but enabled)

```
/install-plugin codex from openai-codex
```

- **What it provides:** `codex:*` skills — delegate tasks to OpenAI Codex CLI
- **Scope:** project

### System Dependencies

The hooks in `.claude/hooks/` require:

| Tool | Purpose | Install |
|------|---------|---------|
| `jq` | JSON parsing in hook scripts | `brew install jq` (macOS) |

## Installation

### 1. Copy the `.claude/` folder

Merge the contents of this export's `.claude/` directory into your target
project's `.claude/` directory:

```bash
# From your target project root:
cp -rn /path/to/beads-x-superpowers-workflow/.claude/ .claude/
```

> **Note:** Use `cp -rn` (no-clobber) to avoid overwriting existing files. If
> you already have a `.claude/settings.json`, merge the `hooks` section manually.

### 2. Merge settings.json

If your project already has `.claude/settings.json`, you need to merge these
sections from the exported `settings.json`:

**Hooks** (required for automation):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validate-bash.sh" }]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/write-safety.sh" }]
      }
    ]
  }
}
```

**Enabled plugins** (add to your existing list):

```json
{
  "enabledPlugins": {
    "commit-commands@claude-plugins-official": true,
    "superpowers@claude-plugins-official": true,
    "codex@openai-codex": true
  }
}
```

### 3. Make hooks executable

```bash
chmod +x .claude/hooks/*.sh
```

### 4. Initialize Beads (if not already done)

```bash
bd init
```

This creates the `.beads/` directory for issue tracking.

## What's Included

```
.claude/
├── agents/                              # Parallel verification subagents
│   ├── verification-comment-analyzer.md # Docstring + comment quality
│   ├── verification-silent-failure.md   # Error handling gaps
│   ├── verification-test-coverage.md    # Test coverage analysis
│   └── verification-type-analyzer.md    # Type design quality
├── Commands/
│   └── workflow-commands/               # Custom workflow skills
│       ├── beads-import-prd.md          # Import PRD into beads issues
│       ├── beads-post-execution.md      # Post-execution verification
│       ├── beads-ship-task.md           # Commit, push, close task
│       ├── beads-start-task.md          # Start task + create branch
│       ├── python-verification-*.md    # Quick/Standard/Full tiers
│       ├── hotfix-interrupt.md          # Emergency hotfix flow
│       ├── P02–P14 phases              # Individual verification phases
│       ├── plan-refinement-qa.md        # Plan Q&A before execution
│       ├── Planning-context-*.md        # Context injected during planning
│       └── tdd-test-writer.md           # TDD test scaffolding
├── hooks/                               # Shell automation scripts
│   ├── format-changed-file.sh           # Auto-format on save
│   ├── session-summary.sh              # Log session activity
│   ├── validate-bash.sh                # Pre-validate bash commands
│   └── write-safety.sh                 # Prevent writes to protected paths
├── rules/
│   ├── 0_Beads x Superpowers/
│   │   └── beads-workflow-router.md     # Natural language -> skill router
│   └── skill-usage.md                   # Naming conventions + enforcement
└── settings.json                        # Hook wiring + plugin enables
```

## Workflow Overview

### The Enforced Sequence

The router (`beads-workflow-router.md`) enforces this mandatory sequence:

1. **Start** — `beads-start-task` marks the issue `in_progress`, creates a
   feature branch
2. **Plan** — `superpowers:writing-plans` writes a plan to `docs/plans/`
3. **Refine** — `plan-refinement-qa` runs Q&A to stress-test the plan
4. **Execute** — User chooses sequential (`superpowers:executing-plans`) or
   parallel (`superpowers:subagent-driven-development`)
5. **Verify** — `beads-post-execution` auto-invokes, presents verification
   tier options (quick/standard/full)
6. **Ship** — `beads-ship-task` commits, pushes, closes the beads issue

### Natural Language Triggers

| Say This | Invokes |
|----------|---------|
| "What's ready?" | `beads:ready` (scoped to active epic) |
| "I'm starting [task]" | `beads-start-task` |
| "Plan this" | `superpowers:writing-plans` |
| "Refine the plan" | `plan-refinement-qa` |
| "Execute the plan" | Execution gate (sequential vs parallel) |
| "Ship it" | `beads-ship-task` |
| "Quick verify" | `python-verification-quick` |
| "Full verify" | `python-verification-full` |



## Customization


### Verification Phases

The P02–P14 phase commands and verification agents are Python focused, using ruff for linting, mypy for type checking, and pytest for testing.

### settings.json

The exported `settings.json` includes permissions and plugin enables from the
source project. Review and adjust:

- `permissions.allow` — Empty by default; add tool-specific permissions for
  your project as needed (Claude Code will prompt for approval otherwise)
- `permissions.deny` — Safety rails preventing `rm -rf /`, `git push --force`,
  and `git reset --hard`
- `enabledPlugins` — Keep superpowers, codex, and commit-commands;