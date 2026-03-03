#!/usr/bin/env python3
"""
Get Claude.ai usage data via API.
Requires cookie file from get_claude_cookie.py
"""

import requests
import json
import sys
import os

def get_usage(cookies):
    """Fetch Claude.ai usage data"""

    # Format cookies for HTTP header
    cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

    headers = {
        "Cookie": cookie_header,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }

    # Step 1: Get organizations
    try:
        response = requests.get("https://claude.ai/api/organizations", headers=headers, timeout=10)
        response.raise_for_status()
        orgs = response.json()

        if not orgs or len(orgs) == 0:
            raise ValueError("No organizations found")

        org_id = orgs[0]["uuid"]
        print(f"Using organization: {orgs[0].get('name', 'Unknown')} ({org_id})", file=sys.stderr)

    except Exception as e:
        print(f"Failed to get organizations: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 2: Get usage data
    try:
        response = requests.get(
            f"https://claude.ai/api/organizations/{org_id}/usage",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        usage = response.json()

        return usage

    except Exception as e:
        print(f"Failed to get usage data: {e}", file=sys.stderr)
        sys.exit(1)

def format_usage(usage):
    """Format usage data for display"""
    output = {
        "current_period": {
            "message_count": usage.get("message_count", 0),
            "message_limit": usage.get("message_limit", 0),
            "remaining": usage.get("message_limit", 0) - usage.get("message_count", 0),
        },
        "reset_at": usage.get("reset_at"),
        "usage_type": usage.get("usage_type"),
    }

    # Add 7-day usage if available
    if "usage_7d" in usage:
        output["last_7_days"] = usage["usage_7d"]

    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_usage.py <cookie_file>", file=sys.stderr)
        print("Example: python get_usage.py ~/.config/openclaw/claude-session.json", file=sys.stderr)
        sys.exit(1)

    cookie_file = sys.argv[1]

    if not os.path.exists(cookie_file):
        print(f"Cookie file not found: {cookie_file}", file=sys.stderr)
        print("Run get_claude_cookie.py first", file=sys.stderr)
        sys.exit(1)

    try:
        with open(cookie_file) as f:
            cookies = json.load(f)

        usage = get_usage(cookies)
        formatted = format_usage(usage)

        print(json.dumps(formatted, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
