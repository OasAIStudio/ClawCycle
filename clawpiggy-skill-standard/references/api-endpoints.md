# Claude.ai API Endpoints

This document describes the Claude.ai API endpoints used by ClawPiggy skill.

## Authentication

All API requests require authentication via cookie:

```http
Cookie: sessionKey=sk-ant-xxxxx; other_cookies=...
```

The `sessionKey` cookie is the primary authentication token.

## Base URL

```
https://claude.ai
```

## Endpoints

### 1. Get Organizations

**Endpoint:** `GET /api/organizations`

**Description:** List all organizations the authenticated user belongs to.

**Headers:**
```http
Cookie: sessionKey=sk-ant-xxxxx
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
```

**Response:** `200 OK`
```json
[
  {
    "uuid": "org-xxxxx",
    "name": "Personal",
    "created_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T00:00:00.000Z",
    "capabilities": ["chat", "api"],
    "active_flags": [],
    "settings": {}
  }
]
```

**Error Responses:**
- `401 Unauthorized` - Invalid or expired sessionKey
- `403 Forbidden` - Session expired, need re-authentication

### 2. Get Usage Data

**Endpoint:** `GET /api/organizations/{org_id}/usage`

**Description:** Get usage statistics for the specified organization.

**Path Parameters:**
- `org_id` (string) - Organization UUID from Get Organizations endpoint

**Headers:**
```http
Cookie: sessionKey=sk-ant-xxxxx
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
```

**Response:** `200 OK`
```json
{
  "message_count": 45,
  "message_limit": 50,
  "reset_at": "2024-02-10T00:00:00.000Z",
  "usage_type": "pro",
  "usage_7d": {
    "total_minutes": 180,
    "limit_minutes": 300,
    "reset_at": "2024-02-15T12:00:00.000Z"
  }
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `message_count` | integer | Number of messages sent in current 5-hour window |
| `message_limit` | integer | Maximum messages allowed in 5-hour window |
| `reset_at` | string (ISO 8601) | When the 5-hour window resets |
| `usage_type` | string | Subscription type: "free", "pro", "team" |
| `usage_7d` | object | 7-day rolling usage (Claude Pro only) |
| `usage_7d.total_minutes` | integer | Total minutes of Claude usage in last 7 days |
| `usage_7d.limit_minutes` | integer | Maximum minutes allowed in 7-day window |
| `usage_7d.reset_at` | string (ISO 8601) | When the oldest usage will expire |

**Error Responses:**
- `401 Unauthorized` - Invalid or expired sessionKey
- `404 Not Found` - Organization ID not found
- `403 Forbidden` - User not authorized to view organization usage

### 3. Get Account Information

**Endpoint:** `GET /api/account`

**Description:** Get authenticated user's account details.

**Headers:**
```http
Cookie: sessionKey=sk-ant-xxxxx
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
```

**Response:** `200 OK`
```json
{
  "uuid": "user-xxxxx",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-01-01T00:00:00.000Z",
  "subscription": {
    "type": "pro",
    "status": "active",
    "renewal_date": "2024-03-01T00:00:00.000Z"
  }
}
```

**Note:** This endpoint is not currently used by ClawPiggy but may be useful for future features.

## Usage Limits

### Free Tier
- **5-hour window:** ~15-20 messages
- **No 7-day limit**

### Claude Pro
- **5-hour window:** ~50 messages
- **7-day rolling:** ~5 hours of usage time
- Resets continuously (rolling window)

### Team Plan
- Higher limits (varies by plan)
- Shared across team members

## Rate Limiting

The API implements rate limiting:
- Max ~10 requests per second per user
- Excessive requests return `429 Too Many Requests`
- Recommended: Add 100ms delay between requests

## Error Handling

Common error patterns:

```json
{
  "error": {
    "type": "authentication_error",
    "message": "Invalid session key"
  }
}
```

**Error Types:**
- `authentication_error` - Invalid or expired session
- `rate_limit_error` - Too many requests
- `not_found_error` - Resource not found
- `server_error` - Internal server error

## Example Usage

### Python

```python
import requests
import json

# Load cookies
with open('cookies.json') as f:
    cookies = json.load(f)

cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
headers = {
    "Cookie": cookie_header,
    "User-Agent": "Mozilla/5.0..."
}

# Get organizations
resp = requests.get("https://claude.ai/api/organizations", headers=headers)
org_id = resp.json()[0]["uuid"]

# Get usage
resp = requests.get(f"https://claude.ai/api/organizations/{org_id}/usage", headers=headers)
usage = resp.json()

print(f"Used: {usage['message_count']}/{usage['message_limit']}")
```

### cURL

```bash
curl -H "Cookie: sessionKey=sk-ant-xxxxx" \
     -H "User-Agent: Mozilla/5.0..." \
     https://claude.ai/api/organizations

curl -H "Cookie: sessionKey=sk-ant-xxxxx" \
     -H "User-Agent: Mozilla/5.0..." \
     https://claude.ai/api/organizations/org-xxxxx/usage
```

## API Stability

**Warning:** These are undocumented internal APIs that may change without notice.

- Endpoints are reverse-engineered from web app traffic
- No official API documentation from Anthropic
- Breaking changes possible at any time
- Use for personal/educational purposes only

For production use, consider the official Anthropic API at https://api.anthropic.com instead.
