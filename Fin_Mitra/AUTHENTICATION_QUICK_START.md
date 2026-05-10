# KPMG Authentication System - Quick Start Guide

## 🚀 Setup Instructions

### Step 1: Install Required Package

```powershell
& C:\Users\virendra\Projects\agents\.venv\Scripts\Activate.ps1
cd KPMG_v2
python -m pip install bcrypt
```

### Step 2: Initialize Database

```powershell
python setup_auth.py
```

This will:
- Create the database `App_Login_DB.db`
- Create 3 tables: UserDetails, AccessLogs, FailedLoginAttempts
- Create default admin user (username: admin, password: sheep123)
- Create sample test user (username: testuser, password: test123)

### Step 3: Run the Application

```powershell
python app_kpmg.py
```

Access at: `http://127.0.0.1:8060/`

## 🔐 Default Login Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `sheep123`
- **Privileges**: Full access + User Management

### Test User Account
- **Username**: `testuser`
- **Password**: `test123`
- **Privileges**: Dashboard access only

⚠️ **IMPORTANT**: Change the admin password after first login!

## 📋 Features Implemented

### ✅ Secure Authentication
- Bcrypt password encryption with automatic salt
- Database-backed user verification
- Failed login attempt logging
- IP address tracking

### ✅ Session Management
- Unique UUID session ID per login
- 30-minute automatic timeout
- Session duration tracking
- Logout with cleanup

### ✅ Role-Based Access Control (RBAC)
- **Admin**: Full access + User Management
- **User**: Dashboard access only
- Dynamic sidebar based on role

### ✅ User Management Page (Admin Only)
Access via sidebar: 👥 User Management

Features:
- Create new users
- View all users
- View access logs
- Monitor active sessions
- Encrypted password storage

### ✅ State Preservation
- No page refresh when switching tabs
- Dashboard states preserved
- Filters and data retained
- Smooth navigation

### ✅ Access Logging
Every login creates a record with:
- Session ID (UUID)
- User ID and Username
- IP Address
- Browser/System Info
- Login timestamp
- Logout timestamp (when applicable)
- Access duration in seconds

## 🎯 How to Use

### For Admins

1. **Login** with admin credentials
2. Navigate to **👥 User Management** (sidebar)
3. **Create New User**:
   - Enter username (unique)
   - Enter email (unique)
   - Set password (min 6 characters)
   - Select role (Admin or User)
   - Click "Create User"
4. **Monitor Users**: Click "Refresh User List"
5. **View Access Logs**: Click "Refresh Access Logs"

### For Regular Users

1. **Login** with user credentials
2. Access available dashboards:
   - 📊 CFaR Calculator
   - 📈 CT Exposure Dashboard
   - 🎲 MonteCarlo Simulator
   - 📉 Distribution Plot
   - 💰 Cashflow Projection
3. **Navigate freely** - states are preserved
4. **Logout** when done

## 🔧 Database Management

### View Database (SQLite Browser)

```powershell
# Install DB Browser for SQLite (optional)
# Or use command line:
sqlite3 App_Login_DB.db
```

### Common Queries

```sql
-- View all users
SELECT * FROM UserDetails;

-- View active sessions
SELECT * FROM AccessLogs WHERE Is_Active = 1;

-- View recent failed logins
SELECT * FROM FailedLoginAttempts ORDER BY Attempt_Timestamp DESC LIMIT 10;

-- Count users by role
SELECT Role, COUNT(*) FROM UserDetails WHERE Is_Active = 1 GROUP BY Role;
```

### Manual User Creation (via SQL)

```python
from auth_database import get_auth_db

db = get_auth_db()
success, message = db.create_user(
    username="newuser",
    password="password123",
    email="newuser@kpmg.com",
    role="User"
)
print(message)
```

### Change Password

```python
from auth_database import get_auth_db

db = get_auth_db()
success, message = db.change_password(user_id=1, new_password="newpassword123")
print(message)
```

## 🛡️ Security Recommendations

1. **Change default admin password** immediately
2. Use **strong passwords**:
   - Minimum 8 characters
   - Mix of letters, numbers, symbols
   - No common words or patterns

3. **Regular monitoring**:
   - Review access logs weekly
   - Check failed login attempts
   - Deactivate unused accounts

4. **Database security**:
   - Keep database file secure
   - Regular backups
   - Restrict file access

5. **Network security**:
   - Use HTTPS in production
   - Implement rate limiting
   - Monitor unusual IP patterns

## 📊 Session Timeout Behavior

- **Timeout duration**: 30 minutes (1800 seconds)
- **Check frequency**: Every 60 seconds
- **On timeout**:
  1. Session marked inactive
  2. Access duration logged
  3. User redirected to login
  4. No data loss (can login again)

## 🐛 Troubleshooting

### "Module 'auth_database' not found"
- Ensure `auth_database.py` is in KPMG_v2 directory
- Check Python path
- Run from KPMG_v2 directory

### "No module named 'bcrypt'"
```powershell
pip install bcrypt
```

### "User Management not visible"
- Only Admin users can see this button
- Check user role in database
- Regular users don't have access

### "Database locked" error
- Close any SQLite browser connections
- Only one write operation at a time
- Wait and retry

### Login not working after database creation
- Verify default admin was created
- Check `UserDetails` table has entries
- Try running `setup_auth.py` again

## 📝 Notes

- Database auto-creates on first import
- Default admin auto-creates if not exists
- Session storage uses browser session storage
- All timestamps in ISO format
- UUIDs used for session IDs (v4)

## 🎨 UI Integration

The authentication system integrates seamlessly with:
- KPMG blue color scheme
- Card-based design
- Professional tables
- Consistent button styling
- Responsive layout

---

**Created**: November 2025  
**Version**: 1.0  
**Author**: KPMG Development Team

