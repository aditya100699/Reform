# 🚀 START HERE - Complete Setup Guide

Follow these steps **in order** to get your Reform project up and running.

## Step 1: Check What You Have Installed

Run the verification script to see what's installed:

```powershell
.\check_setup.ps1
```

This will show you:
- ✅ What's already installed
- ❌ What needs to be installed
- ⚠️ What's optional

## Step 2: Install Missing Prerequisites

Based on the check, install what's missing:

### Required:
1. **Python 3.9+** - https://www.python.org/downloads/
   - ✅ You already have Python 3.12.1!

2. **Node.js 18+** - https://nodejs.org/
   - Download and install the LTS version

3. **PostgreSQL 14+** - https://www.postgresql.org/download/windows/
   - During installation, remember the password you set for the `postgres` user
   - Make sure to add PostgreSQL to PATH during installation

### Optional (for development):
4. **Redis** - https://github.com/microsoftarchive/redis/releases
   - Or use Docker: `docker run -d -p 6379:6379 redis`

5. **Git** - https://git-scm.com/download/win
   - If you don't have it already

## Step 3: Set Up Backend

### Option A: Automated Setup (Recommended)

```powershell
cd backend
.\setup_windows.ps1
```

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Option B: Manual Setup

```powershell
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
py -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 4. Install Python packages
pip install -r requirements.txt

# 5. Create environment file
copy .env.example .env

# 6. Edit .env file (use Notepad or VS Code)
notepad .env
```

**Update .env file with:**
```env
SECRET_KEY=your-secret-key-here-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=reform_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/1
```

## Step 4: Set Up Database

### Create PostgreSQL Database

**Option A: Using pgAdmin (GUI)**
1. Open pgAdmin
2. Connect to PostgreSQL server
3. Right-click "Databases" → Create → Database
4. Name: `reform_db`
5. Click Save

**Option B: Using Command Line**
```powershell
# Open PowerShell and run:
psql -U postgres

# In psql, run:
CREATE DATABASE reform_db;
\q
```

### Run Database Migrations

```powershell
# Make sure you're in backend directory and venv is activated
cd backend
.\venv\Scripts\Activate.ps1

# Create database tables
py manage.py makemigrations
py manage.py migrate

# Create admin user (optional)
py manage.py createsuperuser
```

## Step 5: Start Backend Server

```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Start server
py manage.py runserver
```

✅ **Backend is running!** 
- API: http://localhost:8000
- Admin: http://localhost:8000/admin
- API Docs: http://localhost:8000/api-docs/

## Step 6: Set Up Mobile App

Open a **new PowerShell window** (keep backend server running):

```powershell
# Navigate to mobile directory
cd mobile

# Install dependencies (first time only)
npm install

# Start Expo
npm start
```

✅ **Mobile app is running!**
- Scan QR code with Expo Go app on your phone
- Or press `a` for Android emulator
- Or press `i` for iOS simulator (Mac only)

## Step 7: Verify Everything Works

### Test Backend API:
1. Open browser: http://localhost:8000/api-docs/
2. You should see Swagger API documentation

### Test Mobile App:
1. Install "Expo Go" app on your phone
2. Scan the QR code from the terminal
3. App should load on your phone

## 🎉 You're Ready to Code!

### Quick Command Reference

**Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1          # Activate venv
py manage.py runserver               # Start server
py manage.py makemigrations          # Create migrations
py manage.py migrate                 # Apply migrations
py manage.py createsuperuser         # Create admin
```

**Mobile:**
```powershell
cd mobile
npm start                            # Start Expo
npm run android                      # Run on Android
npm install                          # Install packages
```

## Common Issues & Solutions

### Issue: `python` command not found
**Solution:** Always use `py` instead of `python` on Windows

### Issue: Execution Policy Error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: PostgreSQL connection error
- Check if PostgreSQL service is running: `services.msc`
- Verify password in `.env` file
- Test connection: `psql -U postgres -h localhost`

### Issue: Virtual environment not activating
```powershell
# Try this:
& .\venv\Scripts\Activate.ps1
```

### Issue: Port 8000 already in use
```powershell
# Use a different port:
py manage.py runserver 8001
```

## Next Steps

1. ✅ Backend running
2. ✅ Mobile app running
3. 📝 Start coding features!
4. 📚 Read `PROJECT_SUMMARY.md` for project overview
5. 🔍 Check `docs/` folder for detailed documentation

## Need Help?

- Check `QUICKSTART_WINDOWS.md` for quick reference
- Check `SETUP_WINDOWS.md` for detailed Windows guide
- Check `PROJECT_SUMMARY.md` for project overview

---

**Happy Coding! 🚀**

