# Troubleshooting Guide

## Common Issues and Solutions

### Pharmacy Locator Issues

#### Error: "REQUEST_DENIED" when searching pharmacies

**Cause:** Google Places API is not enabled for your API key.

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** > **Library**
4. Search for **"Places API"**
5. Click **Enable**
6. Wait 1-2 minutes for activation
7. Try searching again

**Note:** The same `GOOGLE_API_KEY` used for Gemini works for Places API once enabled.

---

#### Error: "Could not find location" when entering address

**Cause:** Invalid address format or Geocoding API not enabled.

**Solutions:**
1. **Try more specific addresses:**
   - ✅ Good: "Connaught Place, New Delhi"
   - ❌ Bad: "near park"

2. **Enable Geocoding API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to **APIs & Services** > **Library**
   - Search for **"Geocoding API"**
   - Click **Enable**

3. **Use Coordinates Tab:**
   - Get coordinates from Google Maps (right-click location → click coordinates)
   - Enter in "By Coordinates" tab

---

#### No pharmacies found

**Possible Causes:**
- Search radius too small
- Remote location with few pharmacies
- Places API quota exceeded

**Solutions:**
- Increase search radius (try 10-20 km)
- Check different location
- Verify Places API is enabled
- Check Google Cloud Console for quota limits

---

### Google Calendar Integration Issues

#### Error: "credentials.json not found"

**Solution:**
1. Follow setup in [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md)
2. Download OAuth credentials from Google Cloud Console
3. Save as `credentials.json` in project root

---

#### Browser doesn't open for authorization

**Solutions:**
- Check if default browser is set
- Temporarily disable firewall/antivirus
- Copy authorization URL from terminal and paste in browser
- Try different browser

---

#### Error: "invalid_grant" or "Token has been expired or revoked"

**Solution:**
1. Delete `token.pickle` file from project root
2. Re-run the application
3. Complete authorization again

---

### Reminder Issues

#### Reminders not showing in "Today's Schedule"

**Possible Causes:**
- Start date is in the future
- Reminder duration has expired
- Time zone mismatch

**Solutions:**
- Check start date (should be today or earlier)
- Verify current date/time on your system
- Add new reminder if duration expired

---

### Login/Authentication Issues

#### Can't login after registration

**Solutions:**
- Ensure username/password match exactly (case-sensitive)
- Check MongoDB connection in `.env`
- Verify MongoDB Atlas IP whitelist includes your IP
- Check terminal for error messages

---

#### Error: "MongoDB connection failed"

**Solutions:**
1. Verify `MONGO_URI` in `.env` file
2. Check internet connection
3. Verify MongoDB Atlas cluster is running
4. Update IP whitelist in MongoDB Atlas (allow 0.0.0.0/0 for testing)

---

### Prescription Upload Issues

#### OCR extraction failed or returns empty

**Possible Causes:**
- Image too blurry/low quality
- Handwriting too unclear
- PDF is scanned image without text layer

**Solutions:**
- Use high-resolution images (min 1200px width)
- Ensure good lighting when taking photos
- Try different file format (PDF vs JPG/PNG)
- Type prescription manually if OCR fails

---

#### Error: "Invalid file type"

**Solution:**
- Only PDF, JPG, JPEG, PNG supported
- Check file extension
- Re-save image in supported format

---

### Language/Translation Issues

#### Translation not working

**Solutions:**
- Check internet connection (googletrans requires online access)
- Try switching back to English and then to desired language
- Restart application if language gets stuck

---

### Performance Issues

#### App is slow or freezing

**Solutions:**
- Clear browser cache
- Restart Streamlit server
- Check system resources (RAM/CPU)
- Reduce number of concurrent operations
- Close other browser tabs

---

### API Quota/Rate Limits

#### Error: "Quota exceeded" or "Rate limit"

**Solutions:**

**Google Gemini:**
- Free tier: 15 RPM (requests per minute)
- Upgrade to paid tier or wait

**Pinecone:**
- Free tier: Limited queries/month
- Monitor usage in Pinecone dashboard

**Google Places API:**
- Free tier: $200 credit/month
- Check billing in Google Cloud Console

---

## Getting Help

If issues persist:

1. Check terminal/console for detailed error messages
2. Verify all API keys in `.env` file
3. Ensure all APIs are enabled in respective consoles
4. Check internet connectivity
5. Review logs in terminal for stack traces

## Enable Debug Mode

Add to `.env` file:
```env
DEBUG=True
```

This will show more detailed error messages in the terminal.
