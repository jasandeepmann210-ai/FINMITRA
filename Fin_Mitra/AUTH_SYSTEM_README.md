# KPMG Authentication & User Management System

## Overview

A comprehensive authentication system with encrypted password storage, session tracking, and role-based access control (RBAC).

## Database Schema

### Database Name: `App_Login_DB.db`

Located in the KPMG_v2 directory.

### Tables

#### 1. UserDetails
Stores user account information with encrypted passwords.

| Column | Type | Description |
|--------|------|-------------|
| User_ID | INTEGER (PK) | Auto-incrementing primary key |
| Username | VARCHAR(255) | Unique username (UNIQUE, NOT NULL) |
| Password_Encrypted | VARCHAR(255) | Bcrypt-hashed password (NOT NULL) |
| Email | VARCHAR(255) | Unique email address (UNIQUE, NOT NULL) |
| Role | VARCHAR(50) | User role: 'Admin' or 'User' |
| Created_At | DATETIME | Account creation timestamp |
| Updated_At | DATETIME | Last update timestamp |
| Is_Active | BOOLEAN | Account status (1=active, 0=disabled) |

#### 2. AccessLogs
Tracks all login sessions and access duration.

| Column | Type | Description |
|--------|------|-------------|
| Session_ID | VARCHAR(255) (PK) | UUID session identifier |
| User_ID | INTEGER (FK) | References UserDetails.User_ID |
| Username | VARCHAR(255) | Username for quick reference |
| User_IP | VARCHAR(100) | IP address of user |
| System_Info | TEXT | Browser/device information |
| Login_Timestamp | DATETIME | When user logged in |
| Logout_Timestamp | DATETIME | When user logged out (NULL if active) |
| Access_Duration | INTEGER | Session duration in seconds |
| Is_Active | BOOLEAN | Session status (1=active, 0=ended) |

#### 3. FailedLoginAttempts
Security log of failed login attempts.

| Column | Type | Description |
|--------|------|-------------|
| Attempt_ID | INTEGER (PK) | Auto-incrementing primary key |
| Username | VARCHAR(255) | Attempted username |
| User_IP | VARCHAR(100) | IP address of attempt |
| Attempt_Timestamp | DATETIME | When attempt occurred |
| Reason | VARCHAR(255) | Reason for failure |

## Security Features

### Password Encryption
- **Algorithm**: bcrypt with automatic salt generation
- **Process**: 
  - Registration: Password → bcrypt.hashpw() → Stored hash
  - Login: Input password → bcrypt.checkpw() → Verification
- **No plain text**: Passwords are NEVER stored in plain text
- **Salt**: Each password has a unique, automatically generated salt

### SQL Injection Prevention
- All queries use **parameterized statements**
- No string concatenation for SQL queries
- Safe from SQL injection attacks

### Session Security
- **UUID-based session IDs**: Unpredictable and unique
- **Session timeout**: Automatic logout after 30 minutes of inactivity
- **Session tracking**: All sessions logged with IP and system info

## Default Credentials

**Username**: `admin`  
**Password**: `sheep123`  
**Role**: Admin

*Note: Change this password immediately after first login!*

## User Roles

### Admin
- Full access to all dashboards
- Can create new users
- Can view all users and access logs
- Can manage user accounts
- Access to User Management page

### User
- Access to all dashboards (CFaR, CT Exposure, MonteCarlo, etc.)
- Cannot create or manage users
- Cannot view access logs
- No access to User Management page

## Features

### 1. Secure Authentication
- Database-backed user verification
- Encrypted password storage
- Failed login attempt tracking
- IP address logging

### 2. Session Management
- Unique session ID per login
- Session duration tracking
- Automatic timeout after 30 minutes
- Manual logout with session cleanup

### 3. User Management (Admin Only)
- Create new users with encrypted passwords
- View all users in system
- View access logs
- Monitor active sessions
- Role-based access control

### 4. Access Logging
- Records every login attempt
- Tracks session duration
- Logs IP addresses and system info
- Maintains audit trail

### 5. State Preservation
- No page refresh when navigating between modules
- All dashboard states preserved when switching tabs
- Smooth navigation without data loss

## File Structure

```
KPMG_v2/
├── auth_database.py          # Database operations & encryption
├── User_Management.py        # Admin user management page
├── Login_Page.py             # Login interface
├── app_kpmg.py              # Main application with authentication
├── App_Login_DB.db          # SQLite database (auto-created)
└── AUTH_SYSTEM_README.md    # This file
```

## API Reference

### AuthDatabase Class

#### `authenticate_user(username, password)`
Authenticates user credentials.
- **Returns**: (success: bool, user_data: dict, message: str)

#### `create_user(username, password, email, role)`
Creates a new user with encrypted password.
- **Returns**: (success: bool, message: str)

#### `log_login(user_id, username, user_ip, system_info)`
Logs a successful login.
- **Returns**: session_id (str)

#### `log_logout(session_id)`
Updates logout timestamp and calculates session duration.

#### `log_failed_login(username, user_ip, reason)`
Records failed login attempt.

#### `get_all_users()`
Retrieves all users (admin only).
- **Returns**: List[Dict]

#### `get_access_logs(user_id, limit)`
Retrieves access logs.
- **Returns**: List[Dict]

#### `change_password(user_id, new_password)`
Changes user password with re-encryption.
- **Returns**: (success: bool, message: str)

#### `delete_user(user_id)`
Soft deletes user (sets Is_Active = 0).
- **Returns**: (success: bool, message: str)

## Usage

### Creating a New User (Admin Only)

1. Login as admin
2. Navigate to "User Management" (sidebar)
3. Fill in the create user form:
   - Username (unique)
   - Email (unique)
   - Password (min 6 characters)
   - Role (Admin or User)
4. Click "Create User"
5. New user credentials are generated with encrypted password

### Viewing Access Logs

1. Login as admin
2. Navigate to "User Management"
3. Scroll to "Recent Access Logs" section
4. Click "Refresh Access Logs" to update

### Monitoring Active Sessions

Active sessions show "Active" in the Logout Time column.

## Security Best Practices

1. **Change default admin password** immediately
2. Use **strong passwords** (min 8 characters recommended)
3. **Review access logs** regularly
4. **Monitor failed login attempts** for security threats
5. **Deactivate unused accounts** (set Is_Active = 0)
6. Keep the database file **secure and backed up**

## Session Timeout

- **Duration**: 30 minutes from login
- **Check interval**: Every 60 seconds
- **Auto-logout**: Automatic when timeout reached
- **Grace period**: None (hard timeout)

## Troubleshooting

### Database not found
- Database auto-creates on first run
- Default admin user auto-creates
- Check file: `KPMG_v2/App_Login_DB.db`

### Cannot login
- Verify username/password
- Check Is_Active status in database
- Review failed login logs

### User Management not visible
- Only available to Admin role users
- Check user role in database
- Non-admin users see "Access Denied"

## Future Enhancements

- Password complexity requirements
- Account lockout after N failed attempts
- Email verification for new accounts
- Two-factor authentication (2FA)
- Password reset via email
- Session activity refresh on interaction
- Audit trail for all user management actions

## Technical Notes

- Database: SQLite (single-file, no server required)
- Encryption: bcrypt (industry-standard)
- Session storage: Dash dcc.Store (session type)
- Session timeout: Client-side interval check
- Password hashing: Automatic salt generation

---
*KPMG Risk & Valuation Dashboard - User Authentication System*

