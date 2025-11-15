# Reform - Windows Setup Guide

## Quick Start for Windows

### Prerequisites Check

1. **Python** - Use `py` command (you have Python 3.12.1 ✅)
2. **Node.js** - Check with `node --version`
3. **PostgreSQL** - Download from https://www.postgresql.org/download/windows/
4. **Redis** - Download from https://github.com/microsoftarchive/redis/releases or use WSL

### Backend Setup (Windows)

1. **Navigate to backend directory:**
   ```powershell
   cd backend
   ```

2. **Create virtual environment:**
   ```powershell
   py -m venv venv
   ```

3. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   If you get an execution policy error, run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   ```powershell
   copy .env.example .env
   # Edit .env with your configuration (use Notepad or VS Code)
   ```

6. **Set up PostgreSQL database:**
   - Open pgAdmin or psql
   - Create database: `CREATE DATABASE reform_db;`
   - Or use: `psql -U postgres -c "CREATE DATABASE reform_db;"`

7. **Run migrations:**
   ```powershell
   py manage.py makemigrations
   py manage.py migrate
   ```

8. **Create superuser:**
   ```powershell
   py manage.py createsuperuser
   ```

9. **Run development server:**
   ```powershell
   py manage.py runserver
   ```

The backend API will be available at `http://localhost:8000`

### Mobile App Setup

1. **Navigate to mobile directory:**
   ```powershell
   cd mobile
   ```

2. **Install dependencies:**
   ```powershell
   npm install
   ```

3. **Start Expo:**
   ```powershell
   npm start
   ```

4. **For Android:**
   - Install Android Studio
   - Set up Android emulator
   - Run: `npm run android`

5. **For iOS (requires macOS):**
   - Not available on Windows

### Common Windows Issues

#### Issue: `python` command not found
**Solution:** Use `py` instead of `python`
- `py manage.py runserver`
- `py -m venv venv`
- `py manage.py migrate`

#### Issue: Execution Policy Error
**Solution:** Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Issue: PostgreSQL connection error
**Solution:** 
- Ensure PostgreSQL service is running: `services.msc` → PostgreSQL
- Check connection in `.env` file
- Default connection: `localhost:5432`

#### Issue: Redis not found
**Solution Options:**
1. Install Redis for Windows: https://github.com/microsoftarchive/redis/releases
2. Use WSL (Windows Subsystem for Linux)
3. Use Docker: `docker run -d -p 6379:6379 redis`
4. For development, you can temporarily disable Redis caching

### Environment Variables (.env)

Create `backend/.env` file with:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=reform_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/1

# AWS S3 (optional for development)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=reform-documents
AWS_S3_REGION_NAME=ap-south-1

# UIDAI (optional for development - uses mock)
UIDAI_LICENSE_KEY=
UIDAI_AUA_CODE=
UIDAI_SUB_AUA_CODE=
AADHAAR_PEPPER=change-this-secret-pepper
```

### Quick Commands Reference

```powershell
# Backend
cd backend
.\venv\Scripts\Activate.ps1
py manage.py runserver
py manage.py makemigrations
py manage.py migrate
py manage.py createsuperuser

# Mobile
cd mobile
npm install
npm start
npm run android
```

### Testing the Setup

1. **Test Backend:**
   ```powershell
   py manage.py runserver
   # Visit http://localhost:8000/api-docs/ for API documentation
   ```

2. **Test API:**
   ```powershell
   # In another terminal
   curl http://localhost:8000/api/v1/providers/
   ```

3. **Test Mobile:**
   ```powershell
   cd mobile
   npm start
   # Scan QR code with Expo Go app on your phone
   ```

### Next Steps

1. Complete environment setup
2. Run initial migrations
3. Create a test user
4. Start developing features!

For more details, see the main `SETUP.md` file.


