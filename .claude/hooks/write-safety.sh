#!/bin/bash

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Protected paths
PROTECTED_PATTERNS=(
    "^/etc/"
    "^/usr/"
    "^/bin/"
    "^/sbin/"
    "^\\.env$"
    "^\\.env\\."
    "^.*\\.pem$"
    "^.*\\.key$"
    "^.*_rsa$"
)

for pattern in "${PROTECTED_PATTERNS[@]}"; do
    if echo "$FILE_PATH" | grep -qE "$pattern"; then
        echo '{"decision": "ask", "reason": "Protected file: '"$FILE_PATH"'"}'
        exit 0
    fi
done

exit 0
