---
name: clawpiggy-skill
version: 1.0.0
description: ClawPiggy skill for monitoring Claude usage and executing Claude CLI tasks in isolated environments
---

# ClawPiggy Skill

A skill for AI agents to monitor Claude.ai usage and execute Claude CLI tasks safely.

## Skill Files

| File | Description |
|------|-------------|
| **SKILL.md** (this file) | Main entry point and setup guide |
| **clawpiggy-claudecode-usage.md** | Instructions for fetching Claude.ai usage data |
| **clawpiggy-use-claudecode.md** | Instructions for executing Claude CLI in isolated workspace |

**Install locally:**
```bash
mkdir -p ~/.openclaw/skills/clawpiggy-skill
# Copy these files to the directory above
```

---

## Overview

This skill provides two main capabilities:

1. **Monitor Claude Usage** - Fetch usage data from claude.ai (5-hour and 7-day limits)
2. **Execute Claude CLI** - Run Claude CLI tasks in isolated workspaces (prevents access to user's real files)

---

## Setup (First Time)

### Step 1: Configure Claude CLI Invocation

Before using the execution feature, you need to know how to invoke Claude CLI in the user's environment.

**Ask the user:**
"How should I invoke Claude CLI in your environment? Do you need any environment variables (like proxy settings) or custom command?"

**Common configurations:**
- Simple: `claude "prompt"`
- With proxy: `HTTP_PROXY=http://proxy:8080 HTTPS_PROXY=http://proxy:8080 claude "prompt"`
- Custom wrapper: `/path/to/my-wrapper "prompt"`

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

### Step 3: Test Configuration

Verify the configuration works:

```bash
# Load config and test
claude "echo 'test'"
```

---

## Using the Skill

### Monitor Claude Usage

When you need to check Claude.ai usage limits:

1. Read [clawpiggy-claudecode-usage.md](clawpiggy-claudecode-usage.md) for detailed instructions
2. Navigate to `https://claude.ai/settings/usage`
3. Intercept the API response or scrape the page
4. Return usage data in JSON format

**Quick example:**
```json
{
  "five_hour": { "utilization": 0.0, "resets_at": null },
  "seven_day": { "utilization": 23.0, "resets_at": "2026-02-09T12:00:00+00:00" }
}
```

### Execute Claude CLI Tasks

When you need to run Claude CLI for a task:

1. Read [clawpiggy-use-claudecode.md](clawpiggy-use-claudecode.md) for detailed instructions
2. Create isolated workspace in `/tmp/openclaw-workspaces/{taskId}/`
3. Initialize git repository
4. Execute Claude CLI with configured command
5. Collect results and cleanup

**Quick example:**
```bash
# Create workspace
WORKSPACE="/tmp/openclaw-workspaces/task-$(date +%s)"
mkdir -p "${WORKSPACE}" && cd "${WORKSPACE}"

# Initialize git
git init && git config user.name "OpenClaw" && git config user.email "openclaw@example.com"

# Execute task
claude "Create a hello.txt file"

# Read results
cat hello.txt

# Cleanup
cd / && rm -rf "${WORKSPACE}"
```

---

## Security Principles

### ⚠️ CRITICAL: For Claude CLI Execution

**NEVER access the user's real workspace files.**

All operations MUST happen in isolated directories under `/tmp/openclaw-workspaces/`

### For Usage Monitoring

- Handle user's session cookies securely
- Don't log or expose session tokens
- Only send requests to `claude.ai` domain

---

## Quick Reference

| Task | File to Read | Key Points |
|------|-------------|------------|
| Check usage limits | [clawpiggy-claudecode-usage.md](clawpiggy-claudecode-usage.md) | Intercept API or scrape DOM |
| Run Claude CLI task | [clawpiggy-use-claudecode.md](clawpiggy-use-claudecode.md) | Use isolated workspace |
| First-time setup | This file | Configure CLI invocation |

---

## Troubleshooting

### "Configuration not found"
Run the setup process above to create `~/.config/openclaw/claude-config.json`

### "Claude CLI not found"
User needs to install Claude CLI first: `which claude`

### "Permission denied" on /tmp
Check `/tmp` permissions: `chmod 1777 /tmp`

---

**Last updated**: 2026-02-09
**Version**: 1.0.0
