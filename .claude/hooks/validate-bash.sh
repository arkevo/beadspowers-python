#!/bin/bash

# Read the tool input from stdin
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Define dangerous patterns. The trash forms cover setups that rewrite rm into
# trash; this repo ships no such rewrite.
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    'rm -rf \$HOME'
    "rm -rf \*"
    "trash /"
    "trash ~"
    'trash \$HOME'
    "trash \*"
    "> /dev/sd"
    "mkfs"
    "dd if="
    ":(){:|:&};:"         # Fork bomb
    "chmod -R 777 /"
    "chown -R"
    "curl.*\\| bash"
    "wget.*\\| bash"
    "curl.*\\| sh"
    "wget.*\\| sh"
    "DROP TABLE"
    "DROP DATABASE"
    "DELETE FROM.*WHERE 1"
    "npm publish"
    "pip upload"
)

# Check each pattern. A match returns an "ask" decision: the command is not
# blocked, but the user must confirm it before it runs.
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        jq -n --arg reason "⚠️ Dangerous command detected ($pattern). Are you sure?" '{
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": $reason
            }
        }'
        exit 0
    fi
done

# The quick-allow list below applies only to a single simple command. A command
# that chains (; & && ||), pipes (|), substitutes ($( ) or backticks, <( ) >( )),
# redirects output (>), or spans lines can hide a second action behind an allowed
# first word, so it gets no auto-allow and falls through to the normal prompt.
# Any "(" also disqualifies it: the Bash tool runs the user's shell (zsh on
# macOS), where =(cmd) and glob qualifiers such as *(e:'cmd':) or *(+fn) run
# code without any of the characters above.
case "$COMMAND" in
    *$'\n'*|*$'\r'*|*';'*|*'&'*|*'|'*|*'`'*|*'('*|*'>'*)
        exit 0
        ;;
esac

# Explicitly allow safe commands so they bypass permission prompts
SAFE_PATTERNS=(
    "^cd "
    "^cat "
    "^echo "
    "^ls"
    "^head "
    "^tail "
    "^wc "
    "^sort "
    "^which "
    "^where "
    "^test "
    "^\\["
)

for pattern in "${SAFE_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        jq -n '{
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            }
        }'
        exit 0
    fi
done

# No opinion — fall through to normal permission checking
exit 0
