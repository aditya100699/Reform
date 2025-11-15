# Reform - Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- AWS Account (for S3 storage)

## Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   # On Windows
   py -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up PostgreSQL database:**
   ```sql
   CREATE DATABASE reform_db;
   CREATE USER reform_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE reform_db TO reform_user;
   ```

6. **Run migrations:**
   ```bash
   # On Windows
   py manage.py makemigrations
   py manage.py migrate
   
   # On macOS/Linux
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser:**
   ```bash
   # On Windows
   py manage.py createsuperuser
   
   # On macOS/Linux
   python manage.py createsuperuser
   ```

8. **Run development server:**
   ```bash
   # On Windows
   py manage.py runserver
   
   # On macOS/Linux
   python manage.py runserver
   ```

The backend API will be available at `http://localhost:8000`

## Mobile App Setup

1. **Navigate to mobile directory:**
   ```bash
   cd mobile
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **For iOS (macOS only):**
   ```bash
   cd ios
   pod install
   cd ..
   npm run ios
   ```

4. **For Android:**
   ```bash
   npm run android
   ```

5. **Update API URL:**
   Edit `mobile/src/services/api.js` and update `API_BASE_URL` if needed.

## Environment Variables

### Backend (.env)

Required variables:
- `SECRET_KEY`: Django secret key
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: PostgreSQL credentials
- `REDIS_URL`: Redis connection URL
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: AWS credentials
- `AWS_STORAGE_BUCKET_NAME`: S3 bucket name
- `UIDAI_LICENSE_KEY`, `UIDAI_AUA_CODE`: UIDAI credentials (for production)

### Mobile

Update `mobile/src/services/api.js`:
- `API_BASE_URL`: Backend API URL

## Testing

### Backend
```bash
cd backend
pytest
```

### Mobile
```bash
cd mobile
npm test
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Set up proper SSL certificates
3. Configure production database
4. Set up AWS S3 bucket with proper permissions
5. Configure UIDAI API credentials
6. Set up monitoring and logging
7. Configure CORS for production domains

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists

### Redis Connection Issues
- Ensure Redis is running
- Check Redis URL in `.env`

### AWS S3 Issues
- Verify AWS credentials
- Check bucket permissions
- Ensure bucket exists

### Mobile App Issues
- Clear cache: `npm start -- --reset-cache`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- For iOS: `cd ios && pod install && cd ..`

## Next Steps

1. Complete remaining screen implementations
2. Implement document upload functionality
3. Add OCR processing for documents
4. Implement AI health insights
5. Add push notifications
6. Set up CI/CD pipeline
7. Configure production infrastructure

