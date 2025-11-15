# 📋 Step-by-Step Setup Guide

Follow these steps **exactly in order** to set up your Reform project.

## 🔍 STEP 1: Check Your Current Setup

Run this command in PowerShell (from the project root):

```powershell
.\check_setup.ps1
```

This will tell you what's installed and what you need to install.

---

## 📦 STEP 2: Install Prerequisites

### 2.1 Install Node.js (if not installed)

1. Go to: https://nodejs.org/
2. Download the **LTS version** (recommended)
3. Run the installer
4. Verify installation:
   ```powershell
   node --version
   npm --version
   ```

### 2.2 Install PostgreSQL (if not installed)

1. Go to: https://www.postgresql.org/download/windows/
2. Download the installer
3. During installation:
   - **Remember the password** you set for `postgres` user
   - Check "Add PostgreSQL to PATH"
4. Verify installation:
   ```powershell
   psql --version
   ```

### 2.3 (Optional) Install Redis

For development, Redis is optional. You can skip this for now.

---

## 🐍 STEP 3: Set Up Python Virtual Environment

```powershell
# Navigate to backend folder
cd backend

# Create virtual environment
py -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**You should see `(venv)` in your prompt now!**

If you get an error about execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📚 STEP 4: Install Python Dependencies

```powershell
# Make sure venv is activated (you should see (venv) in prompt)
pip install -r requirements.txt
```

This will install:
- Django
- Django REST Framework
- PostgreSQL driver
- All other required packages

**Wait for installation to complete** (may take a few minutes)

---

## ⚙️ STEP 5: Configure Environment Variables

```powershell
# Copy the example environment file
copy .env.example .env

# Open .env file in Notepad
notepad .env
```

**Update these values in .env:**

```env
# Change this to a random string
SECRET_KEY=your-secret-key-here-change-this-in-production

# Database settings (use the password you set during PostgreSQL installation)
DB_NAME=reform_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
DB_HOST=localhost
DB_PORT=5432
```

**Save and close the file.**

---

## 🗄️ STEP 6: Create Database

### Option A: Using pgAdmin (Easier)

1. Open **pgAdmin** (installed with PostgreSQL)
2. Connect to PostgreSQL server (use the password you set)
3. Right-click on **"Databases"** → **Create** → **Database**
4. Name: `reform_db`
5. Click **Save**

### Option B: Using Command Line

```powershell
# Connect to PostgreSQL
psql -U postgres

# Enter your password when prompted
# Then run:
CREATE DATABASE reform_db;
\q
```

---

## 🔄 STEP 7: Run Database Migrations

```powershell
# Make sure you're in backend folder and venv is activated
cd backend
.\venv\Scripts\Activate.ps1

# Create migration files
py manage.py makemigrations

# Apply migrations to database
py manage.py migrate
```

You should see output like:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, ...
Running migrations:
  Applying contenttypes.0001_initial... OK
  ...
```

---

## 👤 STEP 8: Create Admin User (Optional)

```powershell
# Make sure venv is activated
py manage.py createsuperuser
```

Enter:
- Username: (choose one)
- Email: (your email)
- Password: (choose a strong password)

---

## 🚀 STEP 9: Start Backend Server

```powershell
# Make sure venv is activated
py manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

✅ **Backend is running!**

**Test it:**
- Open browser: http://localhost:8000/api-docs/
- You should see API documentation

**Keep this terminal window open!**

---

## 📱 STEP 10: Set Up Mobile App

Open a **NEW PowerShell window** (keep backend running):

```powershell
# Navigate to mobile folder
cd mobile

# Install Node.js packages (first time only, takes a few minutes)
npm install
```

Wait for installation to complete...

---

## 📱 STEP 11: Start Mobile App

```powershell
# Still in mobile folder
npm start
```

You should see:
- A QR code in the terminal
- Options to press `a` for Android, `i` for iOS

**To test on your phone:**
1. Install **"Expo Go"** app from App Store/Play Store
2. Scan the QR code with Expo Go
3. App will load on your phone!

---

## ✅ STEP 12: Verify Everything Works

### Test Backend:
1. Open: http://localhost:8000/api-docs/
2. You should see Swagger API documentation
3. Try clicking "GET /api/v1/providers/" → "Try it out" → "Execute"

### Test Mobile:
1. App should be running on your phone/emulator
2. You should see the onboarding screens

---

## 🎉 You're Ready!

### Quick Reference Commands

**Backend (in backend folder):**
```powershell
.\venv\Scripts\Activate.ps1    # Activate venv
py manage.py runserver         # Start server
py manage.py migrate           # Update database
```

**Mobile (in mobile folder):**
```powershell
npm start                      # Start Expo
npm run android                # Run on Android
```

---

## 🆘 Troubleshooting

### Problem: "python" command not found
**Solution:** Use `py` instead of `python`

### Problem: Virtual environment won't activate
**Solution:** 
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: PostgreSQL connection error
**Solution:**
1. Check if PostgreSQL service is running: `services.msc`
2. Verify password in `.env` file
3. Test: `psql -U postgres -h localhost`

### Problem: Port 8000 already in use
**Solution:**
```powershell
py manage.py runserver 8001
```

### Problem: npm install fails
**Solution:**
```powershell
npm cache clean --force
npm install
```

---

## 📚 Next Steps

1. ✅ Everything is set up!
2. 📖 Read `PROJECT_SUMMARY.md` to understand the project
3. 💻 Start coding features!
4. 📝 Check `docs/` folder for detailed documentation

---

**Need help?** Check:
- `START_HERE.md` - Quick overview
- `QUICKSTART_WINDOWS.md` - Quick reference
- `SETUP_WINDOWS.md` - Detailed Windows guide

