# Beadspowers: Python

A structured AI-assisted development workflow for Claude Code that combines
**Beads** (git-backed issue tracking) with **Superpowers** (plan-execute-verify lifecycle) into an enforced sequence.

```
Start Task -> Plan -> Refine Plan -> Execute -> Verify -> Ship (PR)
```

## Features

### Verification

Python-specific multi-phase verification with three tiers. After execution completes, the workflow recommends the appropriate tier based on change size.

| Tier | Phases | When to Use |
|------|--------|-------------|
| **Quick** | Lint + tests | Small changes (< 50 lines), hotfixes |
| **Standard** | Lint + code review + architecture + simplification + tests | Normal tasks (50-200 lines) |
| **Full** | All 13 phases with parallel agents (lint through security) | Major features (200+ lines), pre-release |

**Tooling:** ruff (lint/format), mypy (type checking), pytest (tests), python -m build (packaging).

### Plan Refinement

After Superpowers planning completes, Claude analyzes the plan and asks you 10 questions — a mix of Critical, Recommended, and Nice-to-Have — to refine the plan before execution. Each question includes 3 options with reasoning and a recommendation. Skip at any stage by typing "skip."

### Enforced Workflow Sequence

The router (`beads-workflow-router.md`) enforces this mandatory sequence:

1. **Start** — `beads-start-task` marks the issue `in_progress`, creates a feature branch
2. **Plan** — `superpowers:writing-plans` writes a plan to `docs/plans/`
3. **Refine** — `plan-refinement-qa` runs Q&A to stress-test the plan
4. **Execute** — User chooses sequential (`superpowers:executing-plans`) or parallel (`superpowers:subagent-driven-development`)
5. **Verify** — `beads-post-execution` auto-invokes, presents verification tier options
6. **Ship** — `beads-ship-task` commits, pushes, creates a PR (with structured description), deletes the branch, closes the beads issue

### Natural Language Triggers

| Say This | Invokes |
|----------|---------|
| "What's ready?" | `beads:ready` (scoped to active epic) |
| "I'm starting [task]" | `beads-start-task` |
| "Plan this" | `superpowers:writing-plans` |
| "Refine the plan" | `plan-refinement-qa` |
| "Execute the plan" | Execution gate (sequential vs parallel) |
| "Quick verify" | `python-verification-quick` |
| "Standard verify" | `python-verification-standard` |
| "Full verify" | `python-verification-full` |
| "Ship it" | `beads-ship-task` (always creates PR) |

## Prerequisites

### Claude Code

Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI, desktop app, or IDE extension).

### Required Plugins

Install these Claude Code plugins in order. Run each command inside Claude Code (not your shell).

#### 1. Beads (git-backed issue tracker)

```
/install-plugin beads from steveyegge/beads
```

- **What it provides:** `beads:*` skills (create, list, show, ready, close, sync, etc.) and the `bd` CLI for git-backed issue tracking
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

- **What it provides:** `superpowers:*` skills (writing-plans, executing-plans, subagent-driven-development, brainstorming, systematic-debugging, test-driven-development, verification-before-completion, etc.)
- **Scope:** project
- **Repo:** [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)

#### 3. Commit Commands

```
/install-plugin commit-commands from anthropics/claude-plugins-official
```

- **What it provides:** `commit-commands:*` skills (commit, commit-push, commit-push-pr, clean_gone)
- **Scope:** project


### System Dependencies

The hooks in `.claude/hooks/` require:

| Tool | Purpose | Install |
|------|---------|---------|
| `jq` | JSON parsing in hook scripts | `brew install jq` (macOS) |
| `gh` | GitHub CLI for PR creation and code review | `brew install gh` then `gh auth login` |

## Installation

### 1. Copy the `.claude/` folder

Merge the contents of this repo's `.claude/` directory into your target project's `.claude/` directory:

```bash
# From your target project root:
cp -rn /path/to/this-repo/.claude/ .claude/
```

> **Note:** Use `cp -rn` (no-clobber) to avoid overwriting existing files. If you already have a `.claude/settings.json`, merge the `hooks` section manually.

### 2. Merge settings.json

If your project already has `.claude/settings.json`, merge these sections from the exported `settings.json`:

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

### 4. Initialize Beads

> **Skip this step** if you already have a `.beads/` directory or have previously installed Beads in your project.

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
│       ├── beads-ship-task.md           # Commit, PR (structured desc), branch cleanup, close task
│       ├── beads-start-task.md          # Start task + create branch
│       ├── python-verification-*.md     # Quick/Standard/Full tiers
│       ├── hotfix-interrupt.md          # Emergency hotfix flow
│       ├── P02–P14 phases              # Individual verification phases
│       ├── plan-refinement-qa.md        # Plan Q&A before execution
│       ├── Planning-context-*.md        # Context injected during planning
│       └── tdd-test-writer.md           # TDD test scaffolding
├── hooks/                               # Shell automation scripts
│   ├── validate-bash.sh                 # Pre-validate bash commands
│   └── write-safety.sh                  # Prevent writes to protected paths
├── rules/
│   ├── 0_Beads x Superpowers/
│   │   └── beads-workflow-router.md     # Natural language -> skill router
│   └── (add project-specific rules here)
└── settings.json                        # Hook wiring + plugin enables
```

### Verification Phases (Full)

| Phase | Skill | Tier |
|-------|-------|------|
| P02 | Lint Issues Fix (ruff + mypy) | Quick, Standard, Full |
| P03 | Code Review Checks | Standard, Full |
| P04 | Architecture Validation (5-layer) | Standard, Full |
| P05 | Code Simplification Review | Standard, Full |
| P06 | Type Design Analysis | Full (agent) |
| P07 | Silent Failure Hunt | Full (agent) |
| P08 | Comment/Docstring Analysis | Full (agent) |
| P09 | Confidence Scoring | Standard, Full |
| P10 | False Positive Filtering | Standard, Full |
| P11 | Final Verification (ruff + pytest) | Quick, Standard, Full |
| P11.5 | Build Validation (python -m build) | Full |
| P12 | Test Coverage Analysis | Full (agent) |
| P14 | Security Review (auto-triggered) | Standard, Full |

### Architecture Layers

The verification phases validate against a 5-layer Python architecture:

| Layer | Purpose | Allowed Dependencies |
|-------|---------|---------------------|
| **API/CLI** | Routes, CLI commands, entry points | Services, Core |
| **Services** | Business logic, orchestration | Domain, Data, Core |
| **Domain** | Core business rules, entities | Core only |
| **Data** | Repositories, database access | Core only |
| **Core** | Shared utilities, config | None (leaf layer) |

## Customization

### Verification Phases

The P02–P14 phase commands and verification agents are Python-focused, using **ruff** for linting/formatting, **mypy** for type checking, and **pytest** for testing. To adapt for other languages, modify the phase files and agents in `.claude/Commands/workflow-commands/` and `.claude/agents/`.

### settings.json

The exported `settings.json` includes permissions and plugin enables. Review and adjust:

- `permissions.allow` — Empty by default; add tool-specific permissions as needed
- `permissions.deny` — Add safety rails as needed (e.g., prevent destructive commands)
- `enabledPlugins` — Keep superpowers, codex, and commit-commands; remove any you don't use
