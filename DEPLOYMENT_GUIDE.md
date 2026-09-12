# Bhishma's Deployment Guide - Vercel + Render

## 🚀 Quick Deployment Steps

### 1️⃣ Backend Deployment (Render)

**Step 1: Create Render Account**
- Go to https://render.com
- Sign up with GitHub

**Step 2: Create Web Service**
1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `Darshan1814/Project-Bhishma's-2.0`
3. Configure:
   - **Name:** `bhishma's-backend`
   - **Region:** Oregon (US West)
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

**Step 3: Add Environment Variables**
```
SECRET_KEY=bhishma's-clinical-trial-secret-key-2024-production
UPLOAD_FOLDER=uploads
DATABASE_URL=sqlite:///app.db
GEMINI_API_KEY=AIzaSyCUD3MXSMK6Z9Klkt-D1volQBh6MLhzEEM
SERPER_API_KEY=7231a391c4e79eb950150f896a6949fad801e8e2
FLASK_DEBUG=False
PORT=10000
HOST=0.0.0.0
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

**Step 4: Deploy**
- Click "Create Web Service"
- Wait 5-10 minutes for deployment
- Note your backend URL: `https://bhishma's-backend.onrender.com`

---

### 2️⃣ Frontend Deployment (Vercel)

**Step 1: Create Vercel Account**
- Go to https://vercel.com
- Sign up with GitHub

**Step 2: Import Project**
1. Click "Add New..." → "Project"
2. Import `Darshan1814/Project-Bhishma's-2.0`
3. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

**Step 3: Add Environment Variables**
```
VITE_APP_NAME=Bhishma's Clinical Trial System
VITE_APP_VERSION=2.0.0
VITE_API_BASE_URL=https://bhishma's-backend.onrender.com
VITE_APP_DESCRIPTION=Clinical Trial Outcome Prediction System
```

**Step 4: Deploy**
- Click "Deploy"
- Wait 2-3 minutes
- Note your frontend URL: `https://bhishma's-frontend.vercel.app`

---

## 📝 Environment Variables Reference

### Backend (Render)
| Variable | Value | Required |
|----------|-------|----------|
| SECRET_KEY | Random secret key | ✅ |
| GEMINI_API_KEY | Your Gemini API key | ✅ |
| SERPER_API_KEY | Your Serper API key | ✅ |
| DATABASE_URL | sqlite:///app.db | ✅ |
| FLASK_DEBUG | False | ✅ |
| PORT | 10000 | ✅ |
| HOST | 0.0.0.0 | ✅ |
| CORS_ORIGINS | Your Vercel URL | ✅ |

### Frontend (Vercel)
| Variable | Value | Required |
|----------|-------|----------|
| VITE_API_BASE_URL | Your Render backend URL | ✅ |
| VITE_APP_NAME | Bhishma's Clinical Trial System | ✅ |
| VITE_APP_VERSION | 2.0.0 | ✅ |

---

## 🔧 Post-Deployment Configuration

### Update Backend CORS
After deploying frontend, update backend environment variable:
```
CORS_ORIGINS=https://your-actual-frontend.vercel.app,http://localhost:3000
```

### Update Frontend API URL
Update frontend environment variable:
```
VITE_API_BASE_URL=https://your-actual-backend.onrender.com
```

### Redeploy Both Services
1. Render: Click "Manual Deploy" → "Deploy latest commit"
2. Vercel: Automatic redeploy on environment variable change

---

## ✅ Verification

### Test Backend
```bash
curl https://your-backend.onrender.com/health
```
Should return:
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

### Test Frontend
1. Open `https://your-frontend.vercel.app`
2. Try to register/login
3. Check browser console for errors

---

## 🐛 Troubleshooting

### Backend Issues
- **503 Error:** Service is starting (wait 2-3 minutes)
- **CORS Error:** Update CORS_ORIGINS with correct frontend URL
- **Database Error:** Render will create SQLite automatically

### Frontend Issues
- **API Connection Failed:** Check VITE_API_BASE_URL
- **Build Failed:** Check package.json and dependencies
- **404 on Routes:** Vercel handles SPA routing automatically

---

## 📊 Monitoring

### Render Dashboard
- View logs: Dashboard → Logs
- Check metrics: Dashboard → Metrics
- Restart service: Dashboard → Manual Deploy

### Vercel Dashboard
- View deployments: Dashboard → Deployments
- Check logs: Click on deployment → View Function Logs
- Redeploy: Dashboard → Redeploy

---

## 💰 Cost Estimate

### Render (Backend)
- **Free Tier:** 750 hours/month
- **Limitations:** Spins down after 15 min inactivity
- **Upgrade:** $7/month for always-on

### Vercel (Frontend)
- **Free Tier:** Unlimited deployments
- **Bandwidth:** 100GB/month
- **Upgrade:** $20/month for team features

---

## 🔐 Security Checklist

- ✅ Change SECRET_KEY to random value
- ✅ Set FLASK_DEBUG=False in production
- ✅ Use HTTPS URLs only
- ✅ Restrict CORS_ORIGINS to your domain
- ✅ Keep API keys in environment variables
- ✅ Enable Render's automatic HTTPS

---

## 🚀 Quick Commands

### Redeploy Backend
```bash
# From local machine
git push origin main
# Render auto-deploys on push
```

### Redeploy Frontend
```bash
# From local machine
git push origin main
# Vercel auto-deploys on push
```

### View Backend Logs
```bash
# In Render dashboard
Dashboard → Your Service → Logs
```

### View Frontend Logs
```bash
# In Vercel dashboard
Dashboard → Your Project → Deployments → Latest → View Function Logs
```
