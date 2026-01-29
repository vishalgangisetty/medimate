# Google Calendar Integration Setup

This guide helps you set up Google Calendar integration for medicine reminders.

## Quick Setup (5 minutes)

### 1. Enable Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Go to **APIs & Services** > **Library**
4. Search for **Google Calendar API**
5. Click **Enable**

### 2. Create OAuth Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure OAuth consent screen:
   - User Type: **External**
   - App name: **Medi Mate**
   - User support email: Your email
   - Developer contact: Your email
   - Click **Save and Continue** (skip scopes, test users)
4. Back to Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: **Medi Mate Desktop**
   - Click **Create**
5. **Download JSON** file (button appears after creation)
6. Rename to `credentials.json`
7. Place in project root: `medi.mate/credentials.json`

### 3. First Run

When you add a reminder with "Add to Google Calendar" checked:
- Browser will open for Google account authorization
- Sign in and click **Allow**
- Token saved as `token.pickle` (don't share this file)
- Future reminders won't need re-authorization

## Features

✅ Automatic event creation for all reminder times  
✅ Recurring events for multi-day medications  
✅ Pop-up notifications 30 minutes before dose  
✅ Color-coded events (purple for medicine reminders)  
✅ Includes dosage and instructions in event description

## Troubleshooting

**Error: "credentials.json not found"**
- Download credentials from Google Cloud Console
- Place in project root as `credentials.json`

**Error: "invalid_grant"**
- Delete `token.pickle` file
- Re-authorize when prompted

**No browser opens**
- Check firewall/antivirus settings
- Try different browser as default

## Security Notes

- ⚠️ Never commit `credentials.json` or `token.pickle` to git
- ✅ Already added to `.gitignore`
- 🔒 Tokens are encrypted and stored locally
- 📱 Only your calendar is accessed (read/write events)

## Optional: Add Google Places API

For pharmacy locator to work:

1. Go to **APIs & Services** > **Library**
2. Search **Places API**
3. Click **Enable**
4. No credentials needed (uses GOOGLE_API_KEY from .env)
