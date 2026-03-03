---
name: clawpiggy-claudecode-usage
version: 1.0.0
description: Instructions for fetching Claude.ai usage data
parent: clawpiggy-skill
---

# Claude Usage Monitoring

**Part of [ClawPiggy Skill](SKILL.md)**

## Overview

This document tells you how to fetch Claude.ai usage information by accessing the usage page.

## What You'll Get

```json
{
  "five_hour": {
    "utilization": 0.0,
    "resets_at": null
  },
  "seven_day": {
    "utilization": 23.0,
    "resets_at": "2026-02-09T12:00:00.462679+00:00"
  },
  "seven_day_oauth_apps": null,
  "seven_day_opus": null,
  "seven_day_sonnet": null,
  "seven_day_cowork": null,
  "iguana_necktie": null,
  "extra_usage": null
}
```

**Note**: If `utilization` is 0, then `resets_at` will be `null`.

## Instructions

### Step 1: Navigate to Usage Page

Visit: `https://claude.ai/settings/usage`

**Note**: User must be logged in. You should use their existing browser session.

### Step 2: Get Usage Data

**Method A: Intercept API Request (Recommended)**

Listen for the API call that fetches usage data. The endpoint pattern is:
```
https://claude.ai/api/organizations/{org_id}/usage
```

When you navigate to the settings page, this API will be called automatically. Capture the response JSON.

**Method B: Scrape from DOM (Fallback)**

If API interception is not available, extract usage numbers from the page:
- Look for usage percentage displays (e.g., "8%" for 5-hour usage)
- Find the reset time information
- Parse and structure the data

### Step 3: Return Data

Return the complete API response as-is. The structure includes:

```json
{
  "five_hour": {
    "utilization": <number>,
    "resets_at": "<ISO timestamp or null>"
  },
  "seven_day": {
    "utilization": <number>,
    "resets_at": "<ISO timestamp or null>"
  },
  "seven_day_oauth_apps": <number or null>,
  "seven_day_opus": <number or null>,
  "seven_day_sonnet": <number or null>,
  "seven_day_cowork": <number or null>,
  "iguana_necktie": <number or null>,
  "extra_usage": <number or null>
}
```

**Important**:
- When `utilization` is 0, `resets_at` will be `null`
- Most of the additional fields (`seven_day_oauth_apps`, `seven_day_opus`, etc.) are typically `null`
- Just return the complete response without filtering

## Security Notes

⚠️ **Important**:
- User's session cookies are sensitive - handle them securely
- Don't log or expose session tokens
- Only send requests to `claude.ai` domain

## Error Handling

- **Not logged in**: Return error and ask user to log in first
- **Page structure changed**: Try fallback method or notify that document needs update
- **Rate limited**: Wait and retry with exponential backoff
- **Network error**: Retry up to 3 times with delays

## Example Response

Success:
```json
{
  "success": true,
  "data": {
    "five_hour": {
      "utilization": 0.0,
      "resets_at": null
    },
    "seven_day": {
      "utilization": 23.0,
      "resets_at": "2026-02-09T12:00:00.462679+00:00"
    },
    "seven_day_oauth_apps": null,
    "seven_day_opus": null,
    "seven_day_sonnet": null,
    "seven_day_cowork": null,
    "iguana_necktie": null,
    "extra_usage": null
  }
}
```

Error:
```json
{
  "success": false,
  "error": "User not logged in",
  "hint": "Please log in to claude.ai first"
}
```

---

**Last updated**: 2026-02-09
**Version**: 1.0.0
