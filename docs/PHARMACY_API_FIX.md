# Google Places API Fix

## Problem
The pharmacy locator is using the **legacy Places API** which is deprecated. You're seeing this error:
```
REQUEST_DENIED - You're calling a legacy API, which is not enabled for your project
```

## Solution

### Option 1: Enable the New Places API (Recommended)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to **APIs & Services** > **Library**
4. Search for **"Places API (New)"**
5. Click **Enable**
6. Make sure your API key has access to this API

### Option 2: Use Sample Data (For Testing)
If you don't want to set up Google Places API right now, the app already has sample pharmacy data built-in that works without an API key.

To use sample data temporarily, I can modify the pharmacy locator to fall back to sample data when the API fails.

## Which option do you prefer?
- **Option 1**: I'll help you enable the new Google Places API
- **Option 2**: Use sample data for now (no API key needed)
