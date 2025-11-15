# Fix Database Connection

## Issue
Database connection is failing because the password in `.env` doesn't match your PostgreSQL password.

## Solution

### Step 1: Update .env file with your PostgreSQL password

1. Open the `.env` file:
   ```powershell
   cd backend
   notepad .env
   ```

2. Find this line:
   ```env
   DB_PASSWORD=postgres
   ```

3. Change it to your actual PostgreSQL password:
   ```env
   DB_PASSWORD=your_actual_password_here
   ```

4. Save and close the file.

### Step 2: Create the database (if not already created)

**Option A: Using pgAdmin (Easiest)**
1. Open **pgAdmin**
2. Connect to PostgreSQL server
3. Right-click on **"Databases"** → **Create** → **Database**
4. Name: `reform_db`
5. Click **Save**

**Option B: Using Command Line**
```powershell
# Add PostgreSQL to PATH temporarily
$env:PATH += ";C:\Program Files\PostgreSQL\18\bin"

# Create database (replace '18' with your PostgreSQL version)
psql -U postgres -c "CREATE DATABASE reform_db;"
```

### Step 3: Run migrations

```powershell
cd backend
.\venv\Scripts\Activate.ps1
py manage.py migrate
```

### Step 4: Start the server

```powershell
py manage.py runserver
```

## Verify Everything Works

1. Open browser: http://localhost:8000/api-docs/
2. You should see API documentation
3. AI endpoints should be available at: http://localhost:8000/api/v1/ai/

## Troubleshooting

### If password still doesn't work:
- Check PostgreSQL service is running: `services.msc` → Find "postgresql"
- Verify password: Try connecting with pgAdmin first
- Test connection manually:
  ```powershell
  psql -U postgres -h localhost
  ```

### If database already exists:
- You can skip Step 2
- Just run migrations: `py manage.py migrate`

## Quick Commands

```powershell
# Update .env file
notepad backend\.env

# Run migrations
cd backend
.\venv\Scripts\Activate.ps1
py manage.py migrate

# Start server
py manage.py runserver
```

