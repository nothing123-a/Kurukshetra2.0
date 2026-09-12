# 🚀 Deployment Checklist - Refinify Backend

## 📋 Pre-Deployment

### Local Development
- [ ] Test app locally: `python backend/app.py`
- [ ] Verify all endpoints work
- [ ] Check database migrations
- [ ] Test file uploads
- [ ] Verify CORS configuration

### Environment Variables
- [ ] Generate strong SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] Set GEMINI_API_KEY in Render dashboard
- [ ] Set SERPER_API_KEY in Render dashboard
- [ ] Configure CORS_ORIGINS with production URLs
- [ ] Set FLASK_ENV=production
- [ ] Set FLASK_DEBUG=False

---

## 🌐 Render Deployment (Non-Docker)

### 1. Initial Setup
```bash
# Ensure render.yaml is in project root
# Push to GitHub/GitLab
git add .
git commit -m "Production-ready configuration"
git push origin main
```

### 2. Render Dashboard Configuration
1. Create new Web Service
2. Connect your repository
3. Select branch: `main`
4. Root Directory: `backend`
5. Environment: `Python`
6. Build Command: `pip install --upgrade pip && pip install -r requirements.txt`
7. Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 app:app`

### 3. Environment Variables (Set in Render Dashboard)
```
SECRET_KEY=<generate-strong-key>
GEMINI_API_KEY=<your-key>
SERPER_API_KEY=<your-key>
FLASK_ENV=production
FLASK_DEBUG=False
SQLALCHEMY_DATABASE_URI=sqlite:///app.db
CORS_ORIGINS=https://refinify.vercel.app,https://refinify-frontend.vercel.app
```

### 4. Health Check
- Path: `/health`
- Expected Response: `{"status": "healthy"}`

---

## 🐘 PostgreSQL Migration (Recommended for Production)

### Why PostgreSQL?
- ✅ Better concurrency than SQLite
- ✅ ACID compliance
- ✅ Better for multi-user applications
- ✅ Render provides free PostgreSQL

### Setup Steps

#### 1. Create PostgreSQL Database on Render
1. Go to Render Dashboard → New → PostgreSQL
2. Name: `refinify-db`
3. Plan: Free
4. Copy the **Internal Database URL**

#### 2. Update Environment Variable
```
SQLALCHEMY_DATABASE_URI=<internal-database-url>
```

#### 3. Database Migration (One-time)
```bash
# Install PostgreSQL locally for testing
pip install psycopg2-binary

# Test connection
python -c "from sqlalchemy import create_engine; engine = create_engine('your-db-url'); print('Connected!')"
```

#### 4. Auto-Migration
Your app already handles database initialization automatically on startup!

---

## 📦 AWS S3 Integration (Optional - For File Uploads)

### Why S3?
- ✅ Persistent storage (Render's filesystem is ephemeral)
- ✅ Scalable
- ✅ CDN integration

### Setup Steps

#### 1. Create S3 Bucket
```bash
# AWS CLI
aws s3 mb s3://refinify-uploads --region us-east-1
```

#### 2. Install boto3
```bash
pip install boto3
```

#### 3. Update requirements.txt
```
boto3==1.34.0
```

#### 4. Add Environment Variables
```
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_S3_BUCKET=refinify-uploads
AWS_REGION=us-east-1
```

#### 5. Update app.py (Add S3 Upload Function)
```python
import boto3
from botocore.exceptions import ClientError

def upload_to_s3(file_path, bucket_name, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_path)
    
    s3_client = boto3.client('s3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )
    
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
    except ClientError as e:
        print(f"S3 upload error: {e}")
        return None
```

---

## 🔒 Security Best Practices

### 1. Secret Management
- ✅ Never commit `.env` to git
- ✅ Use Render's environment variables dashboard
- ✅ Rotate API keys every 90 days
- ✅ Use different keys for dev/staging/prod

### 2. CORS Configuration
```python
# Production CORS (Strict)
CORS_ORIGINS = "https://refinify.vercel.app,https://refinify-frontend.vercel.app"

# Development CORS (Permissive)
CORS_ORIGINS = "http://localhost:3000,http://localhost:5173"
```

### 3. Database Security
- ✅ Use PostgreSQL in production (not SQLite)
- ✅ Enable SSL for database connections
- ✅ Use connection pooling
- ✅ Regular backups

### 4. Rate Limiting (Optional)
```bash
pip install Flask-Limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

---

## 📊 Monitoring & Logging

### 1. Render Logs
```bash
# View logs in Render Dashboard
# Or use Render CLI
render logs -s refinify-backend
```

### 2. Health Monitoring
- Endpoint: `https://your-app.onrender.com/health`
- Use UptimeRobot or Pingdom for monitoring

### 3. Error Tracking (Optional)
```bash
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

---

## 🧪 Testing Deployment

### 1. Local Testing
```bash
# Test with production settings
export FLASK_ENV=production
export FLASK_DEBUG=False
gunicorn --bind 0.0.0.0:8000 --workers 2 app:app
```

### 2. Smoke Tests
```bash
# Health check
curl https://your-app.onrender.com/health

# API test
curl https://your-app.onrender.com/api/dashboard

# CORS test
curl -H "Origin: https://refinify.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS https://your-app.onrender.com/upload
```

---

## 🔄 Continuous Deployment

### GitHub Actions (Optional)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Trigger Render Deploy
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

---

## 📈 Scaling Considerations

### Free Tier Limitations
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ 512 MB RAM
- ⚠️ Shared CPU

### Upgrade Path
1. **Starter Plan ($7/month)**
   - Always on
   - 512 MB RAM
   - Dedicated CPU

2. **Standard Plan ($25/month)**
   - 2 GB RAM
   - Better performance

### Performance Optimization
```python
# Enable gzip compression
from flask_compress import Compress
Compress(app)

# Cache static responses
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

---

## ✅ Post-Deployment Verification

- [ ] Health endpoint returns 200
- [ ] Database initialized correctly
- [ ] File uploads work
- [ ] CORS configured properly
- [ ] All API endpoints functional
- [ ] Frontend can connect
- [ ] Error logging working
- [ ] Performance acceptable

---

## 🆘 Troubleshooting

### Issue: App won't start
**Solution:** Check Render logs for errors
```bash
render logs -s refinify-backend --tail
```

### Issue: Database connection fails
**Solution:** Verify DATABASE_URL format
```python
# Should be: postgresql://user:pass@host:port/db
# NOT: postgres://user:pass@host:port/db
```

### Issue: CORS errors
**Solution:** Add frontend URL to CORS_ORIGINS
```
CORS_ORIGINS=https://your-frontend.vercel.app
```

### Issue: File uploads fail
**Solution:** Check UPLOAD_FOLDER permissions or migrate to S3

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Flask Production Best Practices](https://flask.palletsprojects.com/en/3.0.x/deploying/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)
- [PostgreSQL on Render](https://render.com/docs/databases)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)

---

## 🎯 Quick Commands Reference

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Test locally with production settings
FLASK_ENV=production gunicorn app:app

# Freeze dependencies
pip freeze > requirements.txt

# Database migration
flask db upgrade

# View Render logs
render logs -s refinify-backend

# Test health endpoint
curl https://your-app.onrender.com/health
```

---

**Last Updated:** 2024
**Maintainer:** Refinify Team
