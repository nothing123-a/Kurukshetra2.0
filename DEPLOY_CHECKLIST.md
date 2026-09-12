# 🚀 Deployment Checklist

## ✅ Pre-Deployment

- [x] Git conflicts resolved
- [x] All changes committed to GitHub
- [x] Large files added to .gitignore
- [x] Environment files created
- [x] Deployment configs added

## 📦 Backend Deployment (Render)

### Step 1: Create Account
- [ ] Go to https://render.com
- [ ] Sign up with GitHub account

### Step 2: Create Web Service
- [ ] Click "New +" → "Web Service"
- [ ] Select repository: `Darshan1814/Project-Bhishma's-2.0`
- [ ] Configure settings:
  ```
  Name: bhishma's-backend
  Region: Oregon (US West)
  Branch: main
  Root Directory: backend
  Runtime: Python 3
  Build Command: pip install -r requirements.txt
  Start Command: gunicorn app:app
  ```

### Step 3: Environment Variables
Copy these to Render dashboard:
```
SECRET_KEY=bhishma's-clinical-trial-secret-key-production-2024
GEMINI_API_KEY=AIzaSyCUD3MXSMK6Z9Klkt-D1volQBh6MLhzEEM
SERPER_API_KEY=7231a391c4e79eb950150f896a6949fad801e8e2
DATABASE_URL=sqlite:///app.db
FLASK_DEBUG=False
PORT=10000
HOST=0.0.0.0
UPLOAD_FOLDER=uploads
CORS_ORIGINS=https://your-frontend-url.vercel.app,http://localhost:3000
```

### Step 4: Deploy
- [ ] Click "Create Web Service"
- [ ] Wait 5-10 minutes
- [ ] Copy backend URL: `https://bhishma's-backend-XXXX.onrender.com`

### Step 5: Test Backend
```bash
curl https://your-backend-url.onrender.com/health
```
Should return: `{"status": "healthy"}`

---

## 🌐 Frontend Deployment (Vercel)

### Step 1: Create Account
- [ ] Go to https://vercel.com
- [ ] Sign up with GitHub account

### Step 2: Import Project
- [ ] Click "Add New..." → "Project"
- [ ] Select repository: `Darshan1814/Project-Bhishma's-2.0`
- [ ] Configure settings:
  ```
  Framework Preset: Vite
  Root Directory: frontend
  Build Command: npm run build
  Output Directory: dist
  Install Command: npm install
  ```

### Step 3: Environment Variables
Add these in Vercel dashboard:
```
VITE_APP_NAME=Bhishma's Clinical Trial System
VITE_APP_VERSION=2.0.0
VITE_API_BASE_URL=https://your-backend-url.onrender.com
VITE_APP_DESCRIPTION=Clinical Trial Outcome Prediction System
```

### Step 4: Deploy
- [ ] Click "Deploy"
- [ ] Wait 2-3 minutes
- [ ] Copy frontend URL: `https://your-project.vercel.app`

### Step 5: Test Frontend
- [ ] Open frontend URL in browser
- [ ] Try to register/login
- [ ] Check browser console for errors

---

## 🔄 Post-Deployment Updates

### Update Backend CORS
- [ ] Go to Render dashboard
- [ ] Update `CORS_ORIGINS` with actual Vercel URL
- [ ] Redeploy backend

### Update Frontend API URL
- [ ] Go to Vercel dashboard
- [ ] Update `VITE_API_BASE_URL` with actual Render URL
- [ ] Vercel will auto-redeploy

---

## ✅ Final Verification

### Backend Tests
- [ ] Health endpoint: `https://backend-url/health`
- [ ] API endpoint: `https://backend-url/api/auth/me`
- [ ] No CORS errors in browser console

### Frontend Tests
- [ ] Homepage loads
- [ ] Registration works
- [ ] Login works
- [ ] Dashboard loads
- [ ] API calls succeed

### Integration Tests
- [ ] Frontend can connect to backend
- [ ] Authentication works end-to-end
- [ ] File uploads work
- [ ] Data processing works

---

## 📊 URLs to Save

```
Backend URL: https://_____________________.onrender.com
Frontend URL: https://_____________________.vercel.app
GitHub Repo: https://github.com/Darshan1814/Project-Bhishma's-2.0
```

---

## 🐛 Common Issues

### Backend Issues
- **503 Error:** Wait 2-3 minutes, Render is starting
- **CORS Error:** Update CORS_ORIGINS with correct frontend URL
- **Build Failed:** Check requirements.txt and Python version

### Frontend Issues
- **Build Failed:** Check package.json dependencies
- **API Connection Failed:** Verify VITE_API_BASE_URL
- **404 on Routes:** Vercel handles SPA routing automatically

---

## 🎉 Success Criteria

- ✅ Backend health check returns 200
- ✅ Frontend loads without errors
- ✅ Can register new user
- ✅ Can login successfully
- ✅ Dashboard displays correctly
- ✅ No CORS errors
- ✅ API calls work

---

## 📞 Support

If you encounter issues:
1. Check Render logs: Dashboard → Logs
2. Check Vercel logs: Dashboard → Deployments → View Logs
3. Check browser console for errors
4. Verify environment variables are set correctly

---

**Deployment Date:** _______________
**Deployed By:** _______________
**Status:** ⬜ In Progress | ⬜ Completed | ⬜ Failed
