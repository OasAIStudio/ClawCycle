# Cookie Extraction Strategy

The ClawPiggy skill uses a three-tier fallback strategy to obtain Claude.ai authentication cookies.

## Method 1: Environment Variable (Highest Priority)

**Use case:** CI/CD environments, automated scripts, headless servers

**Setup:**
```bash
export CLAUDE_SESSION_KEY="sk-ant-xxxxx"
```

**Advantages:**
- No browser automation needed
- Works in headless environments
- Fast and reliable

**Limitations:**
- Requires manual cookie extraction
- Cookie expires periodically (need manual refresh)

## Method 2: Local Cache with Validation

**Use case:** Repeated usage after initial browser login

**Location:** `~/.config/openclaw/claude-session.json`

**Format:**
```json
[
  {
    "name": "sessionKey",
    "value": "sk-ant-xxxxx",
    "domain": ".claude.ai",
    "path": "/",
    "expires": 1234567890,
    "httpOnly": true,
    "secure": true
  }
]
```

**Validation:**
- Cached cookies are validated before use by calling `GET /api/organizations`
- If validation fails (401/403), fallback to Method 3

## Method 3: Browser-Based Login (Fallback)

**Use case:** First-time setup or expired cookies

**Process:**
1. Launch Chromium browser (headful mode)
2. Navigate to https://claude.ai
3. Wait for user to complete login (max 2 minutes)
4. Detect successful login by checking URL path contains `/chat` or `/settings`
5. Extract all cookies from browser context
6. Save to `~/.config/openclaw/claude-session.json`

**User Experience:**
```
$ python scripts/get_claude_cookie.py
Starting browser for authentication...
Please log in to Claude.ai in the browser window
Login detected, extracting cookies...
Cookies saved to /Users/username/.config/openclaw/claude-session.json
```

## Technical Implementation

### Cookie Validation Function

```python
def validate_cookie(cookies):
    """Test if cookie is valid by calling Claude API"""
    cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    headers = {
        "Cookie": cookie_header,
        "User-Agent": "Mozilla/5.0...",
    }
    response = requests.get("https://claude.ai/api/organizations", headers=headers)
    return response.status_code == 200
```

### Browser Automation

Uses Playwright for reliable browser automation:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://claude.ai")

    # Wait for login completion
    page.wait_for_function(
        "window.location.pathname.includes('/chat')",
        timeout=120000
    )

    cookies = context.cookies()
    browser.close()
```

## Security Considerations

1. **Cookie Storage:**
   - Stored in `~/.config/openclaw/` with restricted permissions
   - Not committed to git
   - Should be treated as sensitive credentials

2. **Cookie Lifetime:**
   - Claude sessionKey cookies typically valid for 30 days
   - Automatic re-validation on each use
   - User prompted to re-login only when necessary

3. **Environment Variables:**
   - `CLAUDE_SESSION_KEY` should be kept secure
   - Never logged or printed to stdout
   - Only use in trusted environments

## Troubleshooting

### "Login timeout" Error

**Cause:** User didn't complete login within 2 minutes

**Solution:**
- Run script again
- Complete login faster
- Check internet connection

### "Cookie validation failed" Error

**Cause:** Expired or invalid cookie

**Solution:**
- Script will automatically fallback to browser login
- For environment variable method, export a fresh cookie

### Browser Not Launching

**Cause:** Playwright not installed properly

**Solution:**
```bash
pip install playwright
playwright install chromium
```

## Integration with OpenClaw

OpenClaw uses this cookie extraction in two scenarios:

1. **Usage Monitoring:** Extract cookie → Call usage API
2. **Isolated Execution:** Use cookie to authenticate Claude CLI in isolated workspace

Example workflow:
```bash
# Get cookie
python scripts/get_claude_cookie.py > /tmp/cookies.json

# Get usage
python scripts/get_usage.py /tmp/cookies.json

# Use in isolated execution (cookie passed via config)
bash scripts/execute_isolated.sh "Your task"
```
