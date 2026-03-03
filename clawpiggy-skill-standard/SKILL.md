---
name: clawpiggy
description: Monitor Claude.ai usage and execute Claude CLI tasks in isolated environments. Use when openClaw needs to (1) Check Claude Pro usage limits (5-hour/7-day windows), (2) Execute Claude CLI tasks safely without accessing user's real workspace, (3) Get Claude sessionKey cookie via browser automation
---

# ClawPiggy

## Overview

ClawPiggy enables openClaw to monitor Claude.ai usage data and execute Claude CLI tasks in isolated sandbox environments. This prevents openClaw from accidentally modifying the user's real workspace while still leveraging Claude CLI capabilities.

**Core capabilities:**
1. Extract Claude.ai authentication cookies via browser automation
2. Fetch real-time usage data (message counts, 5-hour/7-day limits)
3. Execute Claude CLI commands in isolated `/tmp` workspaces

## Quick Start

### First-Time Setup

1. **Install dependencies:**
```bash
pip install playwright requests
playwright install chromium
```

2. **(Optional) Configure Claude CLI invocation:**

Create `~/.config/openclaw/claude-config.json`:
```json
{
  "command": "claude",
  "env": {
    "ANTHROPIC_API_KEY": "your-api-key"
  }
}
```

If not configured, defaults to running `claude` command directly.

3. **Authenticate (one-time):**
```bash
python scripts/get_claude_cookie.py
```

This launches a browser window. Log in to Claude.ai, and cookies will be saved to `~/.config/openclaw/claude-session.json`.

## Task 1: Monitor Claude Usage

Use this when openClaw needs to check if Claude Pro usage limits are approaching.

### Step 1: Extract Cookie

**Method A (Cached):** If already authenticated:
```bash
python scripts/get_claude_cookie.py > /tmp/cookies.json
```

**Method B (Environment Variable):** For CI/CD:
```bash
export CLAUDE_SESSION_KEY="sk-ant-xxxxx"
python scripts/get_claude_cookie.py > /tmp/cookies.json
```

The script uses a three-tier fallback:
1. Check `CLAUDE_SESSION_KEY` environment variable
2. Load cached cookie from `~/.config/openclaw/claude-session.json` (validates before use)
3. Launch browser for user login

**Output format:**
```json
[
  {
    "name": "sessionKey",
    "value": "sk-ant-xxxxx",
    "domain": ".claude.ai",
    ...
  }
]
```

### Step 2: Fetch Usage Data

```bash
python scripts/get_usage.py ~/.config/openclaw/claude-session.json
```

**Output format:**
```json
{
  "current_period": {
    "message_count": 45,
    "message_limit": 50,
    "remaining": 5
  },
  "reset_at": "2024-02-10T00:00:00.000Z",
  "usage_type": "pro",
  "last_7_days": {
    "total_minutes": 180,
    "limit_minutes": 300,
    "reset_at": "2024-02-15T12:00:00.000Z"
  }
}
```

**Usage interpretation:**
- `message_count` / `message_limit`: 5-hour window usage
- `last_7_days`: Claude Pro 7-day rolling window (if applicable)
- `reset_at`: When limits refresh

### Step 3: Decision Logic for openClaw

```python
import json

with open('/tmp/usage.json') as f:
    usage = json.load(f)

remaining = usage['current_period']['remaining']

if remaining < 5:
    print("⚠️  Approaching limit, consider pausing")
elif remaining < 10:
    print("⚡ Moderate usage, proceed with caution")
else:
    print("✅ Plenty of capacity")
```

## Task 2: Execute Claude CLI in Isolation

Use this when openClaw needs to run Claude CLI tasks without risking the user's real files.

### How It Works

The `execute_isolated.sh` script:
1. Creates a temporary workspace in `/tmp/openclaw-workspaces/task-<timestamp>/`
2. Initializes a git repository (required by Claude CLI)
3. Loads Claude CLI configuration from `~/.config/openclaw/claude-config.json`
4. Executes the task
5. Leaves workspace intact for inspection (no auto-cleanup)

### Basic Usage

```bash
bash scripts/execute_isolated.sh "Create a hello.txt file with 'Hello, World!'"
```

**Output:**
```
Creating isolated workspace: /tmp/openclaw-workspaces/task-1707564123
Loading Claude CLI configuration from /Users/user/.config/openclaw/claude-config.json
Executing: claude "Create a hello.txt file with 'Hello, World!'"

[Claude CLI output...]

=== Task Completed ===
Workspace: /tmp/openclaw-workspaces/task-1707564123
Exit code: 0

Generated files:
-rw-r--r--  1 user  wheel   13B Feb  9 12:34 hello.txt
-rw-r--r--  1 user  wheel  256B Feb  9 12:34 README.md
```

### Inspecting Results

```bash
# List workspaces
ls -lt /tmp/openclaw-workspaces/

# Navigate to latest workspace
cd /tmp/openclaw-workspaces/task-1707564123

# View generated files
cat hello.txt
```

### Advanced: Custom Claude CLI Configuration

If you use a custom Claude CLI wrapper or need environment variables:

**Example: Using local Claude build**
```json
{
  "command": "/Users/user/claude-dev/bin/claude",
  "env": {
    "ANTHROPIC_API_KEY": "sk-ant-xxxxx",
    "CLAUDE_DEBUG": "true"
  }
}
```

**Example: Using Docker-based Claude**
```json
{
  "command": "docker run --rm -v $(pwd):/workspace claude-cli",
  "env": {}
}
```

The script will substitute environment variables and execute the custom command.

### Cleanup

Workspaces are NOT automatically deleted (for debugging). To clean up:

```bash
# Remove all workspaces older than 1 day
find /tmp/openclaw-workspaces -type d -mtime +1 -exec rm -rf {} \;

# Remove all workspaces
rm -rf /tmp/openclaw-workspaces
```

## Security Principles

1. **Cookie Storage:**
   - Cookies saved to `~/.config/openclaw/claude-session.json`
   - Should have restrictive permissions (600)
   - Never committed to git
   - Treated as sensitive credentials

2. **Isolated Execution:**
   - Tasks run in `/tmp` directories, not user's workspace
   - Each task gets a fresh git repository
   - No access to user's real files or environment

3. **Cookie Validation:**
   - Cached cookies validated before use
   - Invalid cookies trigger re-authentication
   - No silent failures with expired credentials

4. **API Usage:**
   - Only reads usage data, never modifies account
   - Uses undocumented internal APIs (may break)
   - Rate-limited to ~10 requests/second

## Troubleshooting

### Browser Not Launching

**Symptom:** `get_claude_cookie.py` fails with "playwright not found"

**Solution:**
```bash
pip install playwright
playwright install chromium
```

### Login Timeout

**Symptom:** "Login timeout" after 2 minutes

**Causes:**
- User didn't complete login
- Network issues
- Claude.ai down

**Solution:**
- Run script again
- Check https://status.anthropic.com
- Ensure stable internet connection

### Cookie Validation Failed

**Symptom:** "Cookie validation failed" despite successful browser login

**Causes:**
- Cookie expired
- Account suspended
- API endpoint changed

**Solution:**
1. Delete cached cookie: `rm ~/.config/openclaw/claude-session.json`
2. Re-run `get_claude_cookie.py`
3. Check account status on claude.ai

### Claude CLI Not Found

**Symptom:** `execute_isolated.sh` fails with "claude: command not found"

**Solution:**
- Install Claude CLI: `npm install -g @anthropic-ai/claude-cli`
- Or configure custom path in `~/.config/openclaw/claude-config.json`

### jq Not Found

**Symptom:** `execute_isolated.sh` warns about missing jq

**Impact:** Falls back to default `claude` command (ignores config file)

**Solution:**
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq
```

## API Reference

### scripts/get_claude_cookie.py

**Usage:**
```bash
python scripts/get_claude_cookie.py > cookies.json
```

**Output:** JSON array of cookie objects (stdout)

**Side effects:** May launch browser, saves to `~/.config/openclaw/claude-session.json`

**Environment variables:**
- `CLAUDE_SESSION_KEY` - Override cookie (skip browser)

### scripts/get_usage.py

**Usage:**
```bash
python scripts/get_usage.py <cookie_file>
```

**Arguments:**
- `cookie_file` - Path to JSON cookie file from `get_claude_cookie.py`

**Output:** Formatted usage JSON (stdout)

**Exit codes:**
- 0 - Success
- 1 - Cookie file not found, API error, or authentication failed

### scripts/execute_isolated.sh

**Usage:**
```bash
bash scripts/execute_isolated.sh "prompt"
```

**Arguments:**
- `prompt` - Task description for Claude CLI (quoted string)

**Output:** Claude CLI output + workspace summary

**Side effects:**
- Creates directory in `/tmp/openclaw-workspaces/`
- Initializes git repository
- Leaves workspace intact (no auto-cleanup)

**Configuration:**
- Reads `~/.config/openclaw/claude-config.json` if present
- Falls back to `claude` command if config missing or jq unavailable

## Resources

### scripts/
Executable Python and Bash scripts that perform core operations:
- `get_claude_cookie.py` - Cookie extraction with browser automation
- `get_usage.py` - API client for Claude.ai usage data
- `execute_isolated.sh` - Isolated workspace manager for Claude CLI

### references/
Detailed documentation loaded into context:
- `cookie-extraction.md` - Three-tier cookie extraction strategy
- `api-endpoints.md` - Claude.ai API endpoint specifications

No assets directory needed (no templates or boilerplate).
