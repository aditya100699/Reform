# Quick Start Guide - Windows

## Step 1: Install Prerequisites

1. **Python 3.9+** ✅ (You have Python 3.12.1)
2. **Node.js** - Download from https://nodejs.org/
3. **PostgreSQL** - Download from https://www.postgresql.org/download/windows/
4. **Git** - Download from https://git-scm.com/download/win

## Step 2: Set Up Backend

### Option A: Use the Setup Script (Recommended)

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
# Navigate to backend
cd backend

# Create virtual environment
py -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
# Edit .env with your settings (use Notepad or VS Code)
```

## Step 3: Configure Database

1. **Start PostgreSQL** (if not running)
   - Open Services: `services.msc`
   - Find "postgresql" service and start it

2. **Create Database**
   ```powershell
   # Using psql (if in PATH)
   psql -U postgres
   CREATE DATABASE reform_db;
   \q
   
   # Or use pgAdmin GUI
   ```

3. **Update .env file** with your database credentials:
   ```env
   DB_NAME=reform_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

## Step 4: Run Migrations

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Create migrations
py manage.py makemigrations

# Apply migrations
py manage.py migrate

# Create superuser (optional)
py manage.py createsuperuser
```

## Step 5: Start the Server

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Start Django server
py manage.py runserver
```

The API will be available at: **http://localhost:8000**

API Documentation: **http://localhost:8000/api-docs/**

## Step 6: Set Up Mobile App

```powershell
# Navigate to mobile directory
cd ..\mobile

# Install dependencies
npm install

# Start Expo
npm start
```

## Common Commands Reference

### Backend Commands (use `py` instead of `python`)

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run server
py manage.py runserver

# Create migrations
py manage.py makemigrations

# Apply migrations
py manage.py migrate

# Create superuser
py manage.py createsuperuser

# Django shell
py manage.py shell

# Run tests
py manage.py test
```

### Mobile Commands

```powershell
# Install dependencies
npm install

# Start Expo
npm start

# Run on Android
npm run android

# Clear cache
npm start -- --reset-cache
```

## Troubleshooting

### Issue: `python` command not found
**Solution:** Always use `py` on Windows instead of `python`

### Issue: Execution Policy Error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Virtual environment not activating
```powershell
# Try this instead
& .\venv\Scripts\Activate.ps1
```

### Issue: PostgreSQL connection error
- Check if PostgreSQL service is running
- Verify credentials in `.env` file
- Test connection: `psql -U postgres -h localhost`

### Issue: Module not found after activation
- Make sure virtual environment is activated (you should see `(venv)` in prompt)
- Reinstall: `pip install -r requirements.txt`

## Next Steps

1. ✅ Backend is running
2. ✅ Mobile app is running
3. Test the API at http://localhost:8000/api-docs/
4. Start developing features!

For detailed documentation, see:
- `SETUP.md` - Full setup guide
- `SETUP_WINDOWS.md` - Windows-specific guide
- `PROJECT_SUMMARY.md` - Project overview


