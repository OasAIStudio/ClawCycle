#!/bin/bash
set -e

# Execute Claude CLI in isolated workspace
# Usage: ./execute_isolated.sh "your prompt here"

PROMPT="$1"
TASK_ID="task-$(date +%s)"
WORKSPACE="/tmp/openclaw-workspaces/${TASK_ID}"

if [ -z "$PROMPT" ]; then
    echo "Usage: $0 \"your prompt\"" >&2
    exit 1
fi

echo "Creating isolated workspace: ${WORKSPACE}" >&2

# 1. Create isolated workspace
mkdir -p "${WORKSPACE}"
cd "${WORKSPACE}"

# 2. Initialize git (required by Claude CLI)
git init
git config user.name "OpenClaw"
git config user.email "openclaw@example.com"
echo "# OpenClaw Task ${TASK_ID}" > README.md
git add README.md
git commit -m "Initial commit"

# 3. Load user configuration for Claude CLI
CONFIG_FILE="${HOME}/.config/openclaw/claude-config.json"

if [ -f "${CONFIG_FILE}" ]; then
    echo "Loading Claude CLI configuration from ${CONFIG_FILE}" >&2

    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        echo "Warning: jq not found, using default 'claude' command" >&2
        COMMAND="claude"
        ENV_VARS=""
    else
        # Parse configuration
        ENV_VARS=$(jq -r '.env // {} | to_entries | map("\(.key)=\(.value)") | join(" ")' "${CONFIG_FILE}")
        COMMAND=$(jq -r '.command // "claude"' "${CONFIG_FILE}")
    fi
else
    echo "No configuration found, using default 'claude' command" >&2
    COMMAND="claude"
    ENV_VARS=""
fi

echo "Executing: ${ENV_VARS} ${COMMAND} \"${PROMPT}\"" >&2

# 4. Execute task
eval "${ENV_VARS} ${COMMAND} \"${PROMPT}\""

EXIT_CODE=$?

# 5. Output results
echo "" >&2
echo "=== Task Completed ===" >&2
echo "Workspace: ${WORKSPACE}" >&2
echo "Exit code: ${EXIT_CODE}" >&2
echo "" >&2
echo "Generated files:" >&2
ls -lah

# 6. Optional: Clean up (commented out for debugging)
# echo "Cleaning up workspace..." >&2
# cd / && rm -rf "${WORKSPACE}"

exit ${EXIT_CODE}
