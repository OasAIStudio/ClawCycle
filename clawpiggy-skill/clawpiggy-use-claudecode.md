---
name: clawpiggy-use-claudecode
version: 1.0.0
description: Instructions for executing Claude CLI in isolated workspace
parent: clawpiggy-skill
---

# Claude CLI Execution (Isolated Mode)

**Part of [ClawPiggy Skill](SKILL.md)**

## Overview

This document tells you how to safely execute Claude CLI without accessing the user's real workspace.

## ⚠️ CRITICAL SECURITY PRINCIPLE

**YOU MUST NOT ACCESS THE USER'S ACTUAL PROJECT FILES**

All operations happen in a temporary isolated directory:
```
/tmp/openclaw-workspaces/{taskId}/
```

**Why?**
- Protects user's work-in-progress code
- Prevents accidental data leaks
- Ensures reproducible task execution
- Allows safe cleanup without affecting user files

---

## Setup (First Time Only)

### Step 1: Ask User for Configuration

Before using this skill for the first time, ask the user:

**"How should I invoke Claude CLI in your environment? Do you need any environment variables (like proxy settings) or custom command?"**

Common examples:
- Simple: `claude "prompt"`
- With proxy: `HTTP_PROXY=http://proxy:8080 HTTPS_PROXY=http://proxy:8080 claude "prompt"`
- Custom wrapper: `/path/to/my-claude-wrapper "prompt"`

### Step 2: Save Configuration

Save the configuration to `~/.config/openclaw/claude-config.json`:

```bash
mkdir -p ~/.config/openclaw
cat > ~/.config/openclaw/claude-config.json << 'EOF'
{
  "command": "claude",
  "env": {
    "HTTP_PROXY": "http://your-proxy:8080",
    "HTTPS_PROXY": "http://your-proxy:8080"
  }
}
EOF
```

You can also save it to your memory or wherever you store configuration.

---

## Prerequisites

Claude CLI must be installed:

```bash
# Check if installed
which claude

# If not found, tell user to install Claude CLI
```

---

## Step-by-Step Instructions

### Step 1: Create Isolated Workspace

```bash
TASK_ID="task-$(date +%s)"
WORKSPACE="/tmp/openclaw-workspaces/${TASK_ID}"
mkdir -p "${WORKSPACE}"
```

### Step 2: Initialize Git

Claude CLI requires a git repository:

```bash
cd "${WORKSPACE}"
git init
git config user.name "OpenClaw"
git config user.email "openclaw@example.com"
```

### Step 3: Prepare Input Files (Optional)

If the task needs specific input files:

```bash
echo "your content here" > input.txt
```

### Step 4: Execute Claude CLI

Load your saved configuration and run:

```bash
cd "${WORKSPACE}"

# Simple invocation
claude "Write a function to calculate fibonacci numbers"

# With environment variables (from config)
HTTP_PROXY=http://proxy:8080 claude "Write a function to calculate fibonacci numbers"
```

### Step 5: Collect Results

Read the generated files:

```bash
# List files
ls -la "${WORKSPACE}"

# Read specific file
cat "${WORKSPACE}/fibonacci.js"
```

### Step 6: Cleanup

```bash
rm -rf "${WORKSPACE}"
```

---

## Complete Example

```bash
# 1. Create workspace
TASK_ID="task-$(date +%s)"
WORKSPACE="/tmp/openclaw-workspaces/${TASK_ID}"
mkdir -p "${WORKSPACE}"

# 2. Initialize git
cd "${WORKSPACE}"
git init
git config user.name "OpenClaw"
git config user.email "openclaw@example.com"

# 3. Execute task (use your configured command)
claude "Create a hello.txt file with content: Hello from OpenClaw!"

# 4. Read results
cat hello.txt

# 5. Cleanup
cd /
rm -rf "${WORKSPACE}"
```

---

## Return Data Format

Return results in this structure:

```json
{
  "success": true,
  "task_id": "task-1707456789",
  "output": "Task completed successfully",
  "files": {
    "hello.txt": "Hello from OpenClaw!"
  }
}
```

Or on error:

```json
{
  "success": false,
  "error": "claude: command not found",
  "hint": "User needs to install Claude CLI"
}
```

---

## Security Checklist

### ✅ DO:
- Always use isolated workspace under `/tmp/openclaw-workspaces/`
- Clean up after completion
- Validate task prompts

### ❌ DON'T:
- Access user's real project files
- Use `../` to escape workspace
- Execute: `rm -rf /`, `sudo`, `chmod 777`
- Read system files: `/etc/passwd`
- Keep workspaces indefinitely

---

## Error Handling

### "claude: command not found"
```json
{
  "error": "claude CLI not installed",
  "hint": "User needs to install Claude CLI first"
}
```

### "Permission denied" on /tmp
```json
{
  "error": "Cannot create workspace",
  "hint": "Check /tmp permissions"
}
```

### "Git not initialized"
```json
{
  "error": "Claude CLI requires git repository",
  "hint": "Run 'git init' in workspace first"
}
```

---

## Workspace Cleanup

For long-running systems, periodically clean old workspaces:

```bash
# Remove workspaces older than 1 hour
find /tmp/openclaw-workspaces -type d -mmin +60 -exec rm -rf {} +
```

---

**Last updated**: 2026-02-09
**Version**: 1.0.0
