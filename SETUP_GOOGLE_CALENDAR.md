# Setting Up Google Calendar Integration

The error `credentials.json not found` indicates that the application is missing the **OAuth 2.0 Client Secrets** file required to communicate with the Google Calendar API.

To fix this, you need to generate a `credentials.json` file from the Google Cloud Console and place it in your application directory.

## Step-by-Step Instructions

### 1. Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project drop-down at the top and select **New Project**.
3. Name it `Medical App` (or similar) and click **Create**.

### 2. Enable Google Calendar API
1. In the sidebar, go to **APIs & Services > Library**.
2. Search for **"Google Calendar API"**.
3. Click on it and select **Enable**.

### 3. Configure OAuth Consent Screen
1. Go to **APIs & Services > OAuth consent screen**.
2. Select **External** (or Internal if you have a Google Workspace) and click **Create**.
3. Fill in the required fields:
   - **App name**: Medication Reminder
   - **User support email**: Your email
   - **Developer contact information**: Your email
4. Click **Save and Continue**.
5. **Scopes**: Click **Add or Remove Scopes**, search for `calendar.events`, select it, and click **Update**.
6. **Test Users**: Add your own email address as a test user.
7. Save and continue.

### 4. Create Credentials
1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials** > **OAuth client ID**.
3. Select **Desktop app** as the Application type.
4. Name it `Desktop Client`.
5. Click **Create**.

### 5. Download credentials.json
1. You will see a popup with "OAuth client created".
2. Click the **Download JSON** button (icon with a down arrow).
3. Save the file as `credentials.json`.

### 6. Place the File
1. Move the downloaded `credentials.json` file into your application folder:
   ```
   c:\Users\visha\Desktop\sdc\medical upgraded\medi.mate\credentials.json
   ```
   (Verify this is the folder containing `app.py`)

## Verification
1. Restart the application.
2. Try adding a medication with "Add to Google Calendar" checked.
3. A browser window should open asking you to log in to your Google account.
4. Allow access to the application.
5. The event should successfully coordinate with your calendar.
