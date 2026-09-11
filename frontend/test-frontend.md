# Frontend Test Guide

## Prerequisites
1. Backend server running on `http://localhost:5000`
2. Frontend dependencies installed: `npm install`

## Starting the Frontend
```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

## Test Scenarios

### 1. Basic Navigation
- [ ] Home page loads without errors
- [ ] Navigation between pages works
- [ ] Navbar displays correctly

### 2. Authentication
- [ ] Register page loads
- [ ] Can create a new account
- [ ] Login page loads
- [ ] Can login with created account
- [ ] Logout works
- [ ] Profile page loads and displays user info

### 3. File Upload
- [ ] Upload area is visible
- [ ] Can drag and drop files
- [ ] Can select files via file picker
- [ ] Upload progress is shown
- [ ] Success message appears after upload
- [ ] Data summary is displayed after upload

### 4. Data Processing
- [ ] Configuration options are available
- [ ] Can select processing options
- [ ] Processing starts when button is clicked
- [ ] Results are displayed after processing
- [ ] Download options work

### 5. Admin Features (if admin user)
- [ ] Admin dashboard loads
- [ ] User statistics are displayed
- [ ] Can view user list
- [ ] Can change user roles

## Common Issues and Solutions

### CORS Errors
- Ensure backend CORS is configured for `http://localhost:5173`
- Check that backend is running on port 5000

### 404 Errors
- Verify all API endpoints are properly configured
- Check Vite proxy configuration

### Authentication Issues
- Clear browser cookies and try again
- Check that backend session management is working

### File Upload Issues
- Ensure file size is under 16MB
- Check file format (CSV, Excel)
- Verify upload directory exists on backend

## Browser Console
Check browser console for any JavaScript errors:
- Open Developer Tools (F12)
- Go to Console tab
- Look for any red error messages

## Network Tab
Check network requests:
- Open Developer Tools (F12)
- Go to Network tab
- Monitor API calls to ensure they're successful

## Expected API Calls
When using the application, you should see these API calls:
- `GET /api/auth/me` - Check authentication status
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/data/upload` - File upload
- `POST /api/data/clean` - Data processing
- `POST /api/data/report` - Generate reports
- `POST /api/data/download` - Download data
