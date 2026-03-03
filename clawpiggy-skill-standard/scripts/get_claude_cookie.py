#!/usr/bin/env python3
"""
Extract Claude sessionKey cookie using Playwright.
Falls back to browser login if cached cookie is invalid.
"""

from playwright.sync_api import sync_playwright
import json
import os
import sys
import requests

COOKIE_PATH = os.path.expanduser("~/.config/openclaw/claude-session.json")

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
    """Extract Claude sessionKey cookie"""

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

    # 3. Launch browser for user login
    print("Starting browser for authentication...", file=sys.stderr)
    with sync_playwright() as p:
        # Launch browser with arguments to avoid detection
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',  # Hide automation
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )
        page = context.new_page()

        # Remove webdriver flag
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # Navigate to Claude
        print("Please log in to Claude.ai in the browser window", file=sys.stderr)
        page.goto("https://claude.ai")

        # Wait for user to complete login
        print("Waiting for login completion (max 2 minutes)...", file=sys.stderr)
        print("Please log in and navigate to any page (chat, settings, projects)", file=sys.stderr)

        login_detected = False
        try:
            # Method 1: Try to detect URL change
            page.wait_for_url(
                lambda url: '/chat' in url.path or '/settings' in url.path or '/projects' in url.path,
                timeout=120000  # 2 minutes
            )
            login_detected = True
            print("Login detected via URL change", file=sys.stderr)
        except Exception as e:
            # Method 2: Fallback - check if sessionKey cookie exists
            print("URL detection failed, checking for sessionKey cookie...", file=sys.stderr)
            import time
            start_time = time.time()
            while time.time() - start_time < 120:  # 2 minutes timeout
                cookies = context.cookies()
                if any(c['name'] == 'sessionKey' for c in cookies):
                    login_detected = True
                    print("Login detected via sessionKey cookie", file=sys.stderr)
                    break
                time.sleep(2)  # Check every 2 seconds

        if not login_detected:
            print("Login timeout: Could not detect successful login", file=sys.stderr)
            print("Please ensure you complete the login process", file=sys.stderr)
            browser.close()
            sys.exit(1)

        # Extract cookies
        cookies = context.cookies()
        browser.close()

        # Save to cache
        os.makedirs(os.path.dirname(COOKIE_PATH), exist_ok=True)
        with open(COOKIE_PATH, 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f"Cookies saved to {COOKIE_PATH}", file=sys.stderr)

        return cookies

if __name__ == "__main__":
    try:
        cookies = get_claude_cookie()
        print(json.dumps(cookies, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
