---
allowed-tools: Bash(gh issue view:*), Bash(gh search:*), Bash(gh issue list:*), Bash(gh pr comment:*), Bash(gh pr diff:*), Bash(gh pr view:*), Bash(gh pr list:*), Bash(git diff:*), Bash(git log:*), Bash(git status:*)
description: Code review a pull request or local changes
disable-model-invocation: false
---

Provide a code review for the given pull request OR local changes.

## Mode Detection

**Determine the review mode based on input:**

- **PR Mode**: If a pull request number/URL is provided, review that PR
- **Local Mode**: If no PR is provided, review local files

**Do NOT ask for a PR if one is not provided. Automatically use Local Mode.**

### Local Mode Input Options

| Input | What Gets Reviewed |
|-------|-------------------|
| No arguments | Only git diff changes (staged + unstaged) |
| Specific file paths | Only those exact files |
| From verification context | Files modified during the task |

**Examples:**
```
/python-code-review                              → reviews git diff only
/python-code-review src/auth/login.py          → reviews only login.py
/python-code-review src/auth/ src/core/utils.py → reviews auth dir + utils.py
```

**Never scan the entire codebase. Always limit scope to specified or changed files.**

---

## PR Mode Workflow

If a pull request is provided, follow these steps:

1. Use a Haiku agent to check if the pull request (a) is closed, (b) is a draft, (c) does not need a code review (eg. because it is an automated pull request, or is very simple and obviously ok), or (d) already has a code review from you from earlier. If so, do not proceed.
2. Use another Haiku agent to give you a list of file paths to (but not the contents of) any relevant .claude/rules files from the codebase: the root .claude/rules file (if one exists), as well as any .claude/rules files in the directories whose files the pull request modified
3. Use a Haiku agent to view the pull request, and ask the agent to return a summary of the change
4. Then, launch 5 parallel Opus agents to independently code review the change. The agents should do the following, then return a list of issues and the reason each issue was flagged (eg. .claude/rules adherence, bug, historical git context, etc.):
   a. Agent #1: Audit the changes to make sure they comply with the .claude/rules. Note that .claude/rules is guidance for Claude as it writes code, so not all instructions will be applicable during code review.
   b. Agent #2: Read the file changes in the pull request, then do a shallow scan for obvious bugs. Avoid reading extra context beyond the changes, focusing just on the changes themselves. Focus on large bugs, and avoid small issues and nitpicks. Ignore likely false positives.
   c. Agent #3: Read the git blame and history of the code modified, to identify any bugs in light of that historical context
   d. Agent #4: Read previous pull requests that touched these files, and check for any comments on those pull requests that may also apply to the current pull request.
   e. Agent #5: Read code comments in the modified files, and make sure the changes in the pull request comply with any guidance in the comments.
5. For each issue found in #4, launch a parallel Haiku agent that takes the PR, issue description, and list of .claude/rules files (from step 2), and returns a score to indicate the agent's level of confidence for whether the issue is real or false positive (see Confidence Scoring below).
6. Filter out any issues with a score less than 80. If there are no issues that meet this criteria, do not proceed.
7. Use a Haiku agent to repeat the eligibility check from #1, to make sure that the pull request is still eligible for code review.
8. Finally, use the gh bash command to comment back on the pull request with the result (see Output Format below).

---

## Local Mode Workflow

If no pull request is provided, review local changes. **Never scan the whole codebase.**

### Step 1: Determine Files to Review

**Priority order for identifying files:**

1. **Specific files provided**: If user provides file paths, review ONLY those files
   - Example: `/python-code-review src/features/auth/login.py`

2. **Verification context**: If invoked from `superpowers:verification-before-completion`, review the files that were modified during the current task (from git diff)

3. **Git changes (default)**: If no files specified, review uncommitted changes only:
   - Run `git diff --name-only` for unstaged changes
   - Run `git diff --staged --name-only` for staged changes
   - Review ONLY these changed files, not the entire codebase

### Step 2: Validate Scope

- **If no files to review**: Report "No changes to review" and stop
- **Maximum scope**: Only review the identified files, never expand to other files
- **Focus on changes**: Within each file, focus on the changed lines (use `git diff` output)

### Step 3: Gather Relevant Rules

Use an agent to find .claude/rules files ONLY in:
- The root .claude/rules directory
- Directories containing the files being reviewed

### Step 4: Summarize Scope

Report what will be reviewed:
- Number of files
- File paths
- General nature of changes

### Step 5: Parallel Review (5 Agents)

Launch 5 parallel Opus agents to review ONLY the identified files:

a. **Agent #1 (Rules)**: Audit changes against .claude/rules
b. **Agent #2 (Bugs)**: Shallow scan for obvious bugs in the changes. Focus on large bugs, avoid nitpicks.
c. **Agent #3 (History)**: Read git blame/history of the modified files for context
d. **Agent #4 (Patterns)**: Read previous commits on these specific files for patterns
e. **Agent #5 (Comments)**: Check code comments in the modified files

**Important**: Agents should ONLY read the files being reviewed, not explore other files.

### Step 6: Confidence Scoring

For each issue found, launch a parallel Haiku agent to score confidence (see Confidence Scoring below).

### Step 7: Filter Results

Filter out any issues with a score less than 80.

### Step 8: Output

Output the review directly to the user (see Local Output Format below).

---

## Confidence Scoring

Score each issue on a scale from 0-100:

| Score | Meaning |
|-------|---------|
| 0 | Not confident at all. False positive that doesn't stand up to light scrutiny, or is a pre-existing issue. |
| 25 | Somewhat confident. Might be real, but may be a false positive. If stylistic, not explicitly in .claude/rules. |
| 50 | Moderately confident. Verified real issue, but might be a nitpick or rare in practice. Not very important. |
| 75 | Highly confident. Double-checked, very likely real and will be hit in practice. Important, impacts functionality, or directly mentioned in .claude/rules. |
| 100 | Absolutely certain. Confirmed real issue that will happen frequently. Evidence directly confirms this. |

---

## False Positives to Exclude

- Pre-existing issues (not introduced by current changes)
- Something that looks like a bug but is not actually a bug
- Pedantic nitpicks that a senior engineer wouldn't call out
- Issues that a linter, typechecker, or compiler would catch (imports, type errors, formatting)
- General code quality issues unless explicitly required in .claude/rules
- Issues silenced in code (lint ignore comments)
- Intentional functionality changes related to the broader change
- Real issues on lines that were not modified

---

## Output Formats

### PR Mode Output

Comment on the PR using `gh pr comment`:

```markdown
### Code review

Found [N] issues:

1. <brief description of bug> (.claude/rules says "<...>")

<link to file and line with full sha1 + line range>

2. <brief description of bug> (bug due to <file and code snippet>)

<link to file and line with full sha1 + line range>

Generated with [Claude Code](https://claude.ai/code)

<sub>If this code review was useful, please react with 👍. Otherwise, react with 👎.</sub>
```

Or if no issues:

```markdown
### Code review

No issues found. Checked for bugs and .claude/rules compliance.

Generated with [Claude Code](https://claude.ai/code)
```

### Local Mode Output

Output directly to the user:

```markdown
## Code Review: Local Changes

### Summary
Reviewed [N] files with [description of changes].

### Issues Found: [N]

#### Issue 1: [Brief description]
**Confidence:** [score]%
**Source:** [.claude/rules / bug scan / historical context / etc.]
**File:** `path/to/file.py:line`
**Details:** [explanation]
**Suggested fix:** [how to resolve]

---

### No Issues Found
(If applicable)
Checked for bugs and .claude/rules compliance. Ready to commit.
```

---

## Notes

- Do not check build signal or attempt to build or typecheck the app
- For PR mode, use `gh` to interact with Github
- Make a todo list first
- Cite and link each bug with file paths and line numbers
- For PR links, use full SHA: `https://github.com/owner/repo/blob/[full-sha]/path/file.py#L10-L15`
  - Requires full git sha (not variables like `$(git rev-parse HEAD)`)
  - Line range format: `L[start]-L[end]`
  - Provide at least 1 line of context before and after
