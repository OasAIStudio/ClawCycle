#!/bin/bash
# Quick test script for MoltMarket cookie functionality

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COOKIE_FILE="${HOME}/.config/openclaw/claude-session.json"

echo "🧪 MoltMarket Quick Test"
echo "========================"
echo ""

# Check dependencies
echo "📦 Checking dependencies..."
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "❌ playwright not installed"
    echo "   Run: pip install playwright && playwright install chromium"
    exit 1
fi

if ! python3 -c "import requests" 2>/dev/null; then
    echo "❌ requests not installed"
    echo "   Run: pip install requests"
    exit 1
fi

echo "✅ Dependencies OK"
echo ""

# Test 1: Cookie extraction
echo "🔑 Test 1: Cookie Extraction"
echo "----------------------------"

if [ -f "${COOKIE_FILE}" ]; then
    echo "📁 Found cached cookie: ${COOKIE_FILE}"
    echo "   Cookie file size: $(du -h "${COOKIE_FILE}" | cut -f1)"
    echo "   Last modified: $(stat -f "%Sm" "${COOKIE_FILE}")"

    # Count cookies
    COOKIE_COUNT=$(python3 -c "import json; print(len(json.load(open('${COOKIE_FILE}'))))")
    echo "   Number of cookies: ${COOKIE_COUNT}"

    # Check for sessionKey
    HAS_SESSION=$(python3 -c "import json; cookies = json.load(open('${COOKIE_FILE}')); print('yes' if any(c['name'] == 'sessionKey' for c in cookies) else 'no')")

    if [ "${HAS_SESSION}" = "yes" ]; then
        echo "   ✅ sessionKey present"
    else
        echo "   ❌ sessionKey missing!"
        exit 1
    fi
else
    echo "⚠️  No cached cookie found"
    echo ""
    echo "Choose cookie extraction method:"
    echo "  [1] Persistent (recommended) - Uses real browser profile, keeps login"
    echo "  [2] Interactive - Most reliable, incognito mode"
    echo "  [3] Auto-detect - Fully automated (may have CSP issues)"
    echo "  [q] Skip test"
    echo ""
    read -p "Select method [1-3, q]: " -n 1 -r
    echo ""

    case $REPLY in
        1)
            echo "Using persistent mode..."
            python3 "${SCRIPT_DIR}/get_claude_cookie_persistent.py" > /tmp/cookies.json
            ;;
        2)
            echo "Using interactive mode..."
            python3 "${SCRIPT_DIR}/get_claude_cookie_interactive.py" > /tmp/cookies.json
            ;;
        3)
            echo "Using auto-detect mode..."
            python3 "${SCRIPT_DIR}/get_claude_cookie.py" > /tmp/cookies.json
            ;;
        q|Q)
            echo "❌ Skipping test"
            exit 1
            ;;
        *)
            echo "❌ Invalid selection"
            exit 1
            ;;
    esac

    if [ $? -eq 0 ]; then
        echo "✅ Cookie extracted"
    else
        echo "❌ Cookie extraction failed"
        exit 1
    fi
fi

echo ""

# Test 2: Cookie validation
echo "✅ Test 2: Cookie Validation"
echo "-----------------------------"

python3 -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}')
from get_claude_cookie import validate_cookie
import json

with open('${COOKIE_FILE}') as f:
    cookies = json.load(f)

if validate_cookie(cookies):
    print('✅ Cookie is valid!')
    sys.exit(0)
else:
    print('❌ Cookie is invalid or expired')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "   API connection successful"
else
    echo "   ⚠️  Cookie needs refresh"
    exit 1
fi

echo ""

# Test 3: Usage API
echo "📊 Test 3: Usage API"
echo "--------------------"

python3 "${SCRIPT_DIR}/get_usage.py" "${COOKIE_FILE}" > /tmp/usage.json

if [ $? -eq 0 ]; then
    echo "✅ Usage data retrieved"
    echo ""
    python3 -c "
import json
with open('/tmp/usage.json') as f:
    usage = json.load(f)

current = usage.get('current_period', {})
print(f\"   Messages: {current.get('message_count', 0)}/{current.get('message_limit', 0)}\")
print(f\"   Remaining: {current.get('remaining', 0)}\")
print(f\"   Type: {usage.get('usage_type', 'unknown')}\")

if 'last_7_days' in usage:
    days = usage['last_7_days']
    print(f\"   7-day usage: {days.get('total_minutes', 0)}/{days.get('limit_minutes', 0)} minutes\")
"
else
    echo "❌ Failed to get usage data"
    exit 1
fi

echo ""

# Test 4: Minimal cookie test
echo "🔬 Test 4: Minimal Cookie Test"
echo "-------------------------------"

python3 -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}')
from get_claude_cookie import validate_cookie
import json

with open('${COOKIE_FILE}') as f:
    full_cookies = json.load(f)

# Extract only sessionKey
session_key = next((c for c in full_cookies if c['name'] == 'sessionKey'), None)

if not session_key:
    print('❌ No sessionKey found')
    sys.exit(1)

minimal = [session_key]

print('Testing with only sessionKey...')
if validate_cookie(minimal):
    print('✅ Only sessionKey is sufficient!')
    print('   💡 Could optimize to extract only sessionKey')
else:
    print('⚠️  Full cookie set is required')
    print('   Current implementation is correct')
"

echo ""
echo "========================"
echo "✅ All tests completed!"
echo ""
echo "Next steps:"
echo "  - Test isolated execution: bash scripts/execute_isolated.sh \"echo test\""
echo "  - View full test: python scripts/test_cookie.py"
