# ClawPiggy Skill

An Anthropic-compliant skill for monitoring Claude.ai usage and executing Claude CLI tasks in isolated environments.

## Quick Links

- **Main Documentation:** [SKILL.md](./SKILL.md)
- **Packaged Skill:** [clawpiggy.skill](./clawpiggy.skill) (15KB)

## Installation

### As a Skill (for openClaw)

```bash
# Copy to Claude skills directory
cp clawpiggy.skill ~/.claude/skills/

# Or use directly
claude --skill clawpiggy.skill
```

### Standalone Usage

```bash
# Install dependencies
pip install playwright requests
playwright install chromium

# Run scripts directly (choose one cookie extraction method)

# Method 1: Interactive (recommended for first time)
python scripts/get_claude_cookie_interactive.py

# Method 2: Automatic detection
python scripts/get_claude_cookie.py

# Then use the cookie
python scripts/get_usage.py ~/.config/openclaw/claude-session.json
bash scripts/execute_isolated.sh "Your task"
```

## What's Inside

```
clawpiggy/
├── SKILL.md                              # Main skill documentation
├── README.md                             # This file
├── TESTING.md                            # Testing guide
├── TROUBLESHOOTING.md                    # CSP error & solutions
├── scripts/
│   ├── get_claude_cookie.py              # Auto-detect cookie extraction
│   ├── get_claude_cookie_interactive.py  # Interactive (recommended)
│   ├── get_usage.py                      # Usage API client
│   ├── execute_isolated.sh               # Isolated execution
│   ├── quick_test.sh                     # Quick validation
│   └── test_cookie.py                    # Full test suite
├── references/
│   ├── cookie-extraction.md              # Cookie strategy docs
│   └── api-endpoints.md                  # Claude.ai API reference
└── clawpiggy.skill                      # Packaged skill (zip)
```

## Core Features

1. **Usage Monitoring**
   - Extract Claude.ai sessionKey via browser automation
   - Fetch real-time usage data (5-hour/7-day limits)
   - Three-tier cookie fallback (env var → cache → browser)

2. **Isolated Execution**
   - Run Claude CLI tasks in `/tmp` workspaces
   - No access to user's real files
   - Configurable Claude CLI command

3. **Security First**
   - Cookie validation before use
   - Isolated git repositories
   - No auto-cleanup (for debugging)

## Development

### Validation

```bash
python /path/to/skill-creator/scripts/package_skill.py .
```

### Testing

```bash
# Test cookie extraction (requires browser)
python scripts/get_claude_cookie.py > /tmp/test-cookies.json

# Test usage fetching (requires valid cookie)
python scripts/get_usage.py /tmp/test-cookies.json

# Test isolated execution (requires Claude CLI)
bash scripts/execute_isolated.sh "echo 'Hello, World!' > test.txt"
```

## Dependencies

### Python
- `playwright` - Browser automation
- `requests` - HTTP client

### System
- `chromium` - Playwright browser
- `jq` - JSON parsing (optional, for execute_isolated.sh)
- Claude CLI - For isolated execution

## Migration from Old Skill

This skill replaces the old `clawpiggy-skill` directory with:
- ✅ Executable scripts (no context loading needed)
- ✅ Anthropic skill-creator compliance
- ✅ Proper frontmatter and structure
- ✅ Reference documentation
- ✅ Packaged .skill file

Old skill location: `~/Personal/hackathon/clawpiggy-skill/` (can be deleted)

## License

MIT

## References

- [Anthropic Skill Creator](https://github.com/anthropics/skill-creator)
- [RapidRaptor Cookie Implementation](https://github.com/example/rapidraptor)
- [Claude.ai API Endpoints](./references/api-endpoints.md) (reverse-engineered)
