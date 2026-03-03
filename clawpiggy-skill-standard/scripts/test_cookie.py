#!/usr/bin/env python3
"""
Test script for cookie extraction and validation
"""

import json
import sys
import os

# Add current directory to path to import get_claude_cookie
sys.path.insert(0, os.path.dirname(__file__))

from get_claude_cookie import get_claude_cookie, validate_cookie, COOKIE_PATH

def test_cookie_structure():
    """Test 1: Check cookie structure"""
    print("=" * 60)
    print("Test 1: Cookie Structure Analysis")
    print("=" * 60)

    try:
        cookies = get_claude_cookie()

        print(f"\n✅ Successfully extracted {len(cookies)} cookies\n")

        # Analyze cookies
        cookie_names = [c['name'] for c in cookies]
        print("Cookie names:")
        for name in cookie_names:
            print(f"  - {name}")

        # Check for sessionKey
        has_session_key = 'sessionKey' in cookie_names
        print(f"\n{'✅' if has_session_key else '❌'} sessionKey present: {has_session_key}")

        # Show sessionKey details if present
        if has_session_key:
            session_cookie = next(c for c in cookies if c['name'] == 'sessionKey')
            print(f"\nsessionKey details:")
            print(f"  Domain: {session_cookie.get('domain')}")
            print(f"  Path: {session_cookie.get('path')}")
            print(f"  Secure: {session_cookie.get('secure')}")
            print(f"  HttpOnly: {session_cookie.get('httpOnly')}")
            print(f"  Value (first 20 chars): {session_cookie.get('value', '')[:20]}...")

        return cookies

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_minimal_cookie():
    """Test 2: Check if only sessionKey is sufficient"""
    print("\n" + "=" * 60)
    print("Test 2: Minimal Cookie Validation")
    print("=" * 60)

    try:
        # Load full cookies
        with open(COOKIE_PATH) as f:
            full_cookies = json.load(f)

        # Extract only sessionKey
        session_key = next((c for c in full_cookies if c['name'] == 'sessionKey'), None)

        if not session_key:
            print("❌ No sessionKey found in cookies")
            return

        minimal_cookies = [session_key]

        print("\nTesting with only sessionKey cookie...")
        is_valid = validate_cookie(minimal_cookies)

        print(f"{'✅' if is_valid else '❌'} Minimal cookie valid: {is_valid}")

        if is_valid:
            print("\n💡 Insight: Only sessionKey is needed!")
            print("   We could optimize to only extract sessionKey")
        else:
            print("\n💡 Insight: Full cookie set is required")
            print("   Current implementation is correct")

        return is_valid

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cookie_validation():
    """Test 3: Validate cookie with actual API call"""
    print("\n" + "=" * 60)
    print("Test 3: API Validation Test")
    print("=" * 60)

    try:
        with open(COOKIE_PATH) as f:
            cookies = json.load(f)

        print("\nValidating cookies against Claude.ai API...")
        is_valid = validate_cookie(cookies)

        print(f"{'✅' if is_valid else '❌'} Cookie validation: {is_valid}")

        if is_valid:
            print("\n✅ Cookies are working correctly!")
            print(f"   Cached at: {COOKIE_PATH}")
        else:
            print("\n❌ Cookies are invalid or expired")
            print("   Need to re-authenticate")

        return is_valid

    except FileNotFoundError:
        print(f"❌ No cached cookies found at {COOKIE_PATH}")
        print("   Run get_claude_cookie.py first")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_usage_api():
    """Test 4: Full workflow test (cookie → usage API)"""
    print("\n" + "=" * 60)
    print("Test 4: Full Workflow Test")
    print("=" * 60)

    try:
        # Import get_usage
        sys.path.insert(0, os.path.dirname(__file__))
        from get_usage import get_usage

        with open(COOKIE_PATH) as f:
            cookies = json.load(f)

        print("\nFetching usage data from Claude.ai...")
        usage = get_usage(cookies)

        print("\n✅ Usage data retrieved successfully!\n")
        print("Current usage:")
        print(f"  Messages: {usage.get('message_count', 0)}/{usage.get('message_limit', 0)}")
        print(f"  Remaining: {usage.get('message_limit', 0) - usage.get('message_count', 0)}")
        print(f"  Type: {usage.get('usage_type', 'unknown')}")

        if 'usage_7d' in usage:
            print(f"\n7-day usage:")
            print(f"  Minutes: {usage['usage_7d'].get('total_minutes', 0)}/{usage['usage_7d'].get('limit_minutes', 0)}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🧪 MoltMarket Cookie Extraction Test Suite\n")

    results = {}

    # Test 1: Extract and analyze cookie structure
    cookies = test_cookie_structure()
    results['structure'] = cookies is not None

    if not cookies:
        print("\n❌ Cookie extraction failed. Cannot proceed with other tests.")
        return

    # Test 2: Check if minimal cookie works
    results['minimal'] = test_minimal_cookie()

    # Test 3: Validate cookies
    results['validation'] = test_cookie_validation()

    # Test 4: Full workflow
    results['workflow'] = test_usage_api()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Cookie Structure:    {'✅ PASS' if results['structure'] else '❌ FAIL'}")
    print(f"Minimal Cookie:      {'✅ PASS' if results['minimal'] else '❌ FAIL'}")
    print(f"Cookie Validation:   {'✅ PASS' if results['validation'] else '❌ FAIL'}")
    print(f"Full Workflow:       {'✅ PASS' if results['workflow'] else '❌ FAIL'}")

    all_passed = all(results.values())
    print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️  Some tests failed'}")

    if results['minimal']:
        print("\n💡 Optimization opportunity: Consider extracting only sessionKey")
    else:
        print("\n💡 Current implementation (full cookies) is necessary")

if __name__ == "__main__":
    main()
