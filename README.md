# Reform - Centralized Healthcare Document Management

A unified platform for managing healthcare documents with AI-powered predictive health insights.

## 🎯 Project Overview

Reform (HealthConnect India) is a centralized application that allows users to securely store, manage, and access all their healthcare documents in one place. The platform enables seamless collaboration among doctors, specialists, pathologists, radiologists, and insurance companies.

## 🏗️ Architecture

### Technology Stack

- **Frontend (Mobile)**: React Native
- **Backend**: Django (Python)
- **Database**: PostgreSQL
- **Cloud Storage**: AWS S3
- **Cache**: Redis
- **Search**: Elasticsearch

### Project Structure

```
reform/
├── backend/              # Django backend application
│   ├── reform/          # Main Django project
│   ├── api/             # API endpoints
│   ├── core/            # Core models and utilities
│   ├── authentication/  # Auth system (Aadhaar-based)
│   └── storage/         # File storage integration
├── mobile/              # React Native mobile app
│   ├── src/
│   │   ├── screens/     # App screens
│   │   ├── components/  # Reusable components
│   │   ├── navigation/  # Navigation setup
│   │   └── services/    # API services
├── docs/                # Documentation
└── scripts/             # Deployment and utility scripts
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- AWS Account (for S3)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Mobile App Setup

```bash
cd mobile
npm install
# For iOS
cd ios && pod install && cd ..
npm run ios
# For Android
npm run android
```

## 📋 Core Features

- ✅ Aadhaar-based authentication
- ✅ Document upload and management
- ✅ Health records timeline
- ✅ Document sharing with providers
- ✅ Insurance policy management
- ✅ AI-powered health insights
- ✅ Real-time notifications
- ✅ Multi-user support (family members)

## 🔒 Security

- AES-256 encryption for sensitive data
- TLS 1.3 for all communications
- Aadhaar tokenization (never store raw Aadhaar)
- JWT-based authentication
- Role-based access control (RBAC)
- Comprehensive audit logging

## 📚 Documentation

See `/docs` directory for complete documentation:
- Technical Specifications
- API Documentation
- Security Implementation Guide
- Database Schema
- Testing Strategy

## 👥 Team

- **Pratham**: Technical Foundation
- **Rishab Shah**: ML Support
- **UI/UX Designer**: To be hired

## 📅 Development Timeline

- **Phase 1 (MVP)**: 4-6 months
- **Phase 2 (Provider Integration)**: 3-4 months
- **Phase 3 (Insurance Integration)**: 3-4 months
- **Phase 4 (Advanced Features)**: Ongoing

## 📞 Contact

For questions or support, please contact the development team.

## 📄 License

Proprietary - All rights reserved

