#!/bin/bash

# Read the tool input from stdin
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Define dangerous patterns (includes both rm and trash since rm→trash conversion happens first)
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "rm -rf \$HOME"
    "rm -rf \*"
    "trash /"
    "trash ~"
    "trash \$HOME"
    "trash \*"
    "rm -rf ~/development"
    "rm -rf ~/development/mtalkie"
    "trash ~/development"
    "trash ~/development/mtalkie"
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
    "git push.*--force"
    "git push.*-f"
    "git push.*\bmaster\b"
    "git push.*\bmain\b"
    "DROP TABLE"
    "DROP DATABASE"
    "DELETE FROM.*WHERE 1"
    "npm publish"
    "pip upload"
)

# Check each pattern - BLOCK dangerous commands outright
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
