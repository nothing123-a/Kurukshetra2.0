# Admin Page Test Guide

## Prerequisites
1. Backend server running on `http://localhost:5000`
2. Frontend running on `http://localhost:5173`
3. At least one admin user account created

## Test Steps

### 1. Access Admin Dashboard
- [ ] Login with admin account
- [ ] Navigate to `/admin` or click admin link
- [ ] Verify admin dashboard loads without errors

### 2. Check Statistics Display
- [ ] Users count displays correctly
- [ ] Datasets count displays correctly  
- [ ] Runs count displays correctly
- [ ] Reports count displays correctly

### 3. Test Latest Uploads Table
- [ ] Table shows uploaded datasets
- [ ] File names display correctly
- [ ] Row and column counts show
- [ ] Owner information displays
- [ ] Upload timestamps are formatted correctly

### 4. Test Recent Runs Table
- [ ] Table shows processing runs
- [ ] Dataset IDs display correctly
- [ ] User IDs display correctly
- [ ] Success/fail status shows with proper badges
- [ ] Plots count displays
- [ ] Timestamps are formatted correctly
- [ ] Filter by dataset works

### 5. Test User Management
- [ ] User list displays all users
- [ ] Usernames and emails show correctly
- [ ] Role badges display properly (admin/user)
- [ ] Role dropdown works for each user
- [ ] Role updates work without errors
- [ ] Success/error messages appear

### 6. Error Handling
- [ ] Non-admin users get access denied
- [ ] Network errors show proper error messages
- [ ] Loading spinner displays during data fetch
- [ ] Error messages clear when retrying

## Expected Console Logs
When admin page loads successfully, you should see:
```
Admin dashboard data: {
  stats: { users: X, datasets: Y, runs: Z, reports: W },
  latest_datasets: [...],
  latest_runs: [...],
  users: [...]
}
```

## Common Issues

### Access Denied (403)
- User is not an admin
- Session expired
- Backend admin_required decorator not working

### Empty Data
- No users/datasets/runs in database
- Database connection issues
- Backend not returning proper data structure

### Role Update Fails
- User doesn't have admin permissions
- Backend role update endpoint not working
- Network connectivity issues

## Debug Steps

1. **Check Browser Console**
   - Look for any JavaScript errors
   - Check network requests to `/api/admin/dashboard`
   - Verify response data structure

2. **Check Backend Logs**
   - Look for any Python errors
   - Verify admin_required decorator is working
   - Check database queries

3. **Verify Database**
   - Ensure users exist with admin role
   - Check if datasets and runs exist
   - Verify relationships between tables

## Expected API Responses

### GET /api/admin/dashboard
```json
{
  "stats": {
    "users": 5,
    "datasets": 10,
    "runs": 15,
    "reports": 8
  },
  "latest_datasets": [
    {
      "id": 1,
      "filename": "data.csv",
      "rows": 1000,
      "columns": 10,
      "uploaded_at": "2024-01-01T12:00:00",
      "owner": "admin"
    }
  ],
  "latest_runs": [
    {
      "id": 1,
      "dataset_id": 1,
      "user_id": 1,
      "success": true,
      "plots_count": 5,
      "created_at": "2024-01-01T12:30:00"
    }
  ],
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "created_at": "2024-01-01T10:00:00"
    }
  ]
}
```

### POST /api/admin/user/{id}/role
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "user1",
    "role": "admin"
  }
}
```
