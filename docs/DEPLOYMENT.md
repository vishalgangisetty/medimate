# Deployment Guide for Medi-Mate

This guide covers deploying Medi-Mate to various cloud platforms.

---

## Option 1: Streamlit Cloud (Easiest & Free)

### Prerequisites
- GitHub account
- Push your code to a GitHub repository

### Steps

1. **Push code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/medi-mate.git
   git push -u origin main
   ```

2. **Sign up at Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Sign in with GitHub

3. **Deploy:**
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

4. **Add Secrets:**
   - In your app dashboard, go to Settings → Secrets
   - Add your environment variables:
   ```toml
   GOOGLE_API_KEY = "your_api_key_here"
   PINECONE_API_KEY = "your_pinecone_key_here"
   MONGO_URI = "your_mongodb_uri_here"
   ```

5. **Done!** Your app will be live at `https://share.streamlit.io/yourusername/medi-mate/main/app.py`

---

## Option 2: Render (Free Tier Available)

### Prerequisites
- Render account (free at [render.com](https://render.com))

### Steps

1. **Create `render.yaml`** in your project root:
   ```yaml
   services:
     - type: web
       name: medi-mate
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
       envVars:
         - key: GOOGLE_API_KEY
           sync: false
         - key: PINECONE_API_KEY
           sync: false
         - key: MONGO_URI
           sync: false
   ```

2. **Push to GitHub** (same as Option 1, step 1)

3. **Deploy on Render:**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically
   - Click "Create Web Service"

4. **Add Environment Variables:**
   - In the dashboard, go to Environment
   - Add your API keys

5. **Done!** Your app will be live at `https://your-app-name.onrender.com`

---

## Option 3: Railway ($5/month)

### Prerequisites
- Railway account at [railway.app](https://railway.app)

### Steps

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Initialize project:**
   ```bash
   railway init
   ```

4. **Add environment variables:**
   ```bash
   railway variables set GOOGLE_API_KEY=your_key_here
   railway variables set PINECONE_API_KEY=your_key_here
   railway variables set MONGO_URI=your_uri_here
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

6. **Generate domain:**
   ```bash
   railway domain
   ```

7. **Done!** Your app is live!

---

## Option 4: Docker + Any Cloud Platform

### Prerequisites
- Docker installed locally

### Steps

1. **Create `Dockerfile`:**
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Create `.dockerignore`:**
   ```
   __pycache__
   *.pyc
   .env
   .git
   .gitignore
   venv/
   .venv/
   data/input/*
   data/processed/*
   ```

3. **Build Docker image:**
   ```bash
   docker build -t medi-mate .
   ```

4. **Test locally:**
   ```bash
   docker run -p 8501:8501 \
     -e GOOGLE_API_KEY=your_key \
     -e PINECONE_API_KEY=your_key \
     -e MONGO_URI=your_uri \
     medi-mate
   ```

5. **Deploy to:**
   - **Google Cloud Run**
   - **AWS ECS**
   - **Azure Container Instances**
   - **DigitalOcean App Platform**

---

## Option 5: Heroku (Deprecated but still works)

### Steps

1. **Create `Procfile`:**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Create `setup.sh`:**
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   headless = true\n\
   port = $PORT\n\
   enableCORS = false\n\
   \n\
   " > ~/.streamlit/config.toml
   ```

3. **Deploy:**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   heroku config:set GOOGLE_API_KEY=your_key
   heroku config:set PINECONE_API_KEY=your_key
   heroku config:set MONGO_URI=your_uri
   ```

---

## Environment Variables

**Required for all platforms:**

```env
GOOGLE_API_KEY=your_google_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/medimate
```

---

## Post-Deployment Checklist

- ✅ Test user registration/login
- ✅ Test prescription upload
- ✅ Test OTC medicine checker
- ✅ Test medicine reminders
- ✅ Test pharmacy locator
- ✅ Test language switching
- ✅ Monitor MongoDB for data persistence
- ✅ Check Pinecone index for vector storage

---

## Troubleshooting

### Issue: App crashes on startup
**Solution:** Check if all environment variables are set correctly

### Issue: MongoDB connection fails
**Solution:** 
- Verify MongoDB Atlas IP whitelist (add 0.0.0.0/0 for all IPs)
- Check connection string format

### Issue: Pharmacy locator doesn't work
**Solution:** Ensure Google API key has Places API enabled

### Issue: Translation not working
**Solution:** Install `googletrans==4.0.0rc1` (specific version)

---

## Cost Estimates

| Platform | Free Tier | Paid |
|----------|-----------|------|
| **Streamlit Cloud** | ✅ 1 app, unlimited visitors | N/A |
| **Render** | ✅ 750 hours/month | $7/month for always-on |
| **Railway** | $5 credit/month | $5/month minimum |
| **Docker + Cloud Run** | Some free usage | Pay per request |

---

## Recommended: Streamlit Cloud

**Best for beginners:**
- Free forever
- Easy GitHub integration
- Auto-deploys on push
- Built-in secrets management
- No server management needed

**Start here:** [share.streamlit.io](https://share.streamlit.io)
