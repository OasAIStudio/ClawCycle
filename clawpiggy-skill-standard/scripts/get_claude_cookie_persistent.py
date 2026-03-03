#!/usr/bin/env python3
"""
Persistent context version: Uses real browser profile to maintain login state.
This opens a normal (non-incognito) browser window with existing login data.
"""

from playwright.sync_api import sync_playwright
import json
import os
import sys
import requests

COOKIE_PATH = os.path.expanduser("~/.config/openclaw/claude-session.json")
# Use a dedicated profile directory for Claude authentication
BROWSER_DATA_DIR = os.path.expanduser("~/.config/openclaw/browser-data")

def validate_cookie(cookies):
    """Validate cookie by testing a simple API call"""
    try:
        cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        headers = {
            "Cookie": cookie_header,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        }
        response = requests.get("https://claude.ai/api/organizations", headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Cookie validation failed: {e}", file=sys.stderr)
        return False

def get_claude_cookie():
    """Extract Claude sessionKey cookie using persistent browser context"""

    # 1. Check environment variable first
    env_cookie = os.environ.get("CLAUDE_SESSION_KEY")
    if env_cookie:
        print("Using CLAUDE_SESSION_KEY from environment", file=sys.stderr)
        cookies = [{"name": "sessionKey", "value": env_cookie, "domain": ".claude.ai"}]
        if validate_cookie(cookies):
            return cookies
        else:
            print("Environment cookie invalid, proceeding to other methods", file=sys.stderr)

    # 2. Try loading from cache
    if os.path.exists(COOKIE_PATH):
        print(f"Loading cached cookie from {COOKIE_PATH}", file=sys.stderr)
        with open(COOKIE_PATH) as f:
            cookies = json.load(f)
            if validate_cookie(cookies):
                print("Cached cookie is valid", file=sys.stderr)
                return cookies
            else:
                print("Cached cookie expired, need re-authentication", file=sys.stderr)

    # 3. Launch browser with persistent context
    print("\n" + "="*60, file=sys.stderr)
    print("🌐 Opening browser with persistent profile", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print(f"\nBrowser data directory: {BROWSER_DATA_DIR}", file=sys.stderr)
    print("\nAdvantages of persistent mode:", file=sys.stderr)
    print("✓ Uses real browser profile (not incognito)", file=sys.stderr)
    print("✓ Preserves login state between runs", file=sys.stderr)
    print("✓ May already be logged in from previous session", file=sys.stderr)
    print("\nInstructions:", file=sys.stderr)
    print("1. Browser window will open", file=sys.stderr)
    print("2. Log in to Claude.ai (if not already logged in)", file=sys.stderr)
    print("3. Navigate to any page (chat/settings/projects)", file=sys.stderr)
    print("4. Return to this terminal and press ENTER", file=sys.stderr)
    print("\n" + "="*60 + "\n", file=sys.stderr)

    # Create browser data directory
    os.makedirs(BROWSER_DATA_DIR, exist_ok=True)

    with sync_playwright() as p:
        # Launch with persistent context (uses real profile)
        context = p.chromium.launch_persistent_context(
            user_data_dir=BROWSER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Arguments to avoid detection
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ],
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )

        # Get or create a page
        if len(context.pages) > 0:
            page = context.pages[0]
        else:
            page = context.new_page()

        # Navigate to Claude
        page.goto("https://claude.ai")

        # Wait for user confirmation
        try:
            input("Press ENTER after you have logged in and see the Claude interface... ")
        except KeyboardInterrupt:
            print("\n\nLogin cancelled by user", file=sys.stderr)
            context.close()
            sys.exit(1)

        # Extract cookies
        print("\nExtracting cookies...", file=sys.stderr)
        cookies = context.cookies()

        # Verify we got the sessionKey
        has_session_key = any(c['name'] == 'sessionKey' for c in cookies)
        if not has_session_key:
            print("❌ Error: sessionKey not found in cookies", file=sys.stderr)
            print("   Please ensure you completed the login process", file=sys.stderr)
            context.close()
            sys.exit(1)

        print(f"✅ Found {len(cookies)} cookies including sessionKey", file=sys.stderr)

        # Validate before saving
        print("Validating cookies...", file=sys.stderr)
        if not validate_cookie(cookies):
            print("❌ Error: Cookies are not valid", file=sys.stderr)
            print("   Please try logging in again", file=sys.stderr)
            context.close()
            sys.exit(1)

        print("✅ Cookies validated successfully", file=sys.stderr)

        context.close()

        # Save to cache
        os.makedirs(os.path.dirname(COOKIE_PATH), exist_ok=True)
        with open(COOKIE_PATH, 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f"✅ Cookies saved to {COOKIE_PATH}", file=sys.stderr)
        print(f"✅ Browser profile saved to {BROWSER_DATA_DIR}", file=sys.stderr)
        print("\n💡 Next time you run this script, you may already be logged in!", file=sys.stderr)

        return cookies

if __name__ == "__main__":
    try:
        cookies = get_claude_cookie()
        print(json.dumps(cookies, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
