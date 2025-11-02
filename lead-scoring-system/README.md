# Lead Scoring System

AI-powered lead scoring and prioritization system for car dealerships with multi-user collaboration features.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Status](https://img.shields.io/badge/status-production--ready-green)

---

## 🎯 Features

### Core Features
- ✅ **AI-Powered Scoring** - Automated lead scoring based on activities and engagement
- ✅ **Lead Management** - Complete CRUD operations for leads
- ✅ **Activity Tracking** - Track all interactions with leads
- ✅ **Score Breakdown** - Detailed scoring analysis

### Authentication & Security
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **Role-Based Access Control** - Admin, Manager, Sales Rep roles
- ✅ **Password Security** - bcrypt password hashing
- ✅ **Protected Routes** - Frontend route guards

### Collaboration Features
- ✅ **Lead Assignment** - Assign leads to sales representatives
- ✅ **Notes System** - Add notes and comments to leads
- ✅ **Activity Timeline** - View complete interaction history
- ✅ **Status Tracking** - Track lead progression (New → Won/Lost)
- ✅ **Notifications** - In-app and email notifications
- ✅ **My Leads Dashboard** - Personal dashboard for sales reps

### User Experience
- ✅ **Responsive Design** - Mobile-friendly interface
- ✅ **Real-time Updates** - Live notification system
- ✅ **Error Handling** - Graceful error recovery
- ✅ **Loading States** - Skeleton loaders and smooth transitions

---

## 📋 Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **JWT** - Authentication tokens

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **TanStack Query** - Data fetching
- **React Router** - Routing

### Infrastructure
- **Docker Compose** - Local development
- **Nginx** - Production web server (recommended)
- **Systemd** - Service management (Linux)

---

## 🚀 Quick Start

See [QUICK_START.md](./QUICK_START.md) for detailed setup instructions.

```bash
# 1. Start infrastructure
docker-compose up -d

# 2. Backend
cd backend
./start.sh

# 3. Frontend
cd frontend
./start.sh

# 4. Create users (after backend starts)
cd backend
./create_users_via_api.sh
```

**Default Credentials:**
- Admin: `admin` / `admin123`
- Manager: `manager` / `manager123`
- Sales Rep: `rep1` / `rep123`

---

## 📁 Project Structure

```
lead-scoring-system/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints
│   │   ├── models/          # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── utils/            # Utilities (auth, etc.)
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Database migrations
│   ├── tests/                # Test suite
│   ├── migrate.sh            # Migration helper
│   └── start.sh              # Startup script
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Page components
│   │   ├── contexts/        # React contexts
│   │   ├── services/        # API client
│   │   └── types/           # TypeScript types
│   └── start.sh             # Startup script
├── docker-compose.yml        # Local infrastructure
└── docs/                    # Documentation
```

---

## 📚 Documentation

- **[QUICK_START.md](./QUICK_START.md)** - Get started in 5 minutes
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment guide
- **[FINAL_LAUNCH_GUIDE.md](./FINAL_LAUNCH_GUIDE.md)** - Complete verification & launch guide
- **[LAUNCH_CHECKLIST.md](./LAUNCH_CHECKLIST.md)** - Pre-launch checklist
- **[SYSTEM_STATUS.md](./SYSTEM_STATUS.md)** - Current system status
- **[SETUP_COMPLETE.md](./SETUP_COMPLETE.md)** - Setup completion summary

### API Documentation

When running the backend, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧪 Testing

```bash
# Verify system
./verify_system.sh

# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🔧 Development

### Backend Commands

```bash
# Migrations
./migrate.sh phase4       # Phase 4 migration
./migrate.sh create "msg" # New migration
./migrate.sh upgrade      # Apply migrations
./migrate.sh status       # Check status

# Development
./start.sh                # Start with checks
uvicorn app.main:app --reload  # Manual start

# Create users
./create_users_via_api.sh  # Create test users
```

### Frontend Commands

```bash
./start.sh                # Start dev server
npm run build             # Production build
npm run preview           # Preview build
npm run lint              # Lint code
```

---

## 🔒 Security

### Production Checklist
- [x] SECRET_KEY from environment
- [x] CORS configuration
- [x] Password hashing (bcrypt)
- [x] JWT token expiration
- [x] Rate limiting (optional)
- [x] Environment-based config

### Environment Variables

See `backend/.env.example` for all required variables.

**Critical for Production:**
- `SECRET_KEY` - Must be changed!
- `DATABASE_URL` - Production database
- `CORS_ORIGINS` - Your domain(s)
- `ENVIRONMENT=production`

---

## 📊 Database Schema

### Core Tables
- `users` - User accounts and authentication
- `leads` - Lead information and scoring
- `lead_activities` - Activity tracking
- `lead_scores_history` - Score change history
- `lead_assignments` - Lead-to-user assignments
- `lead_notes` - Notes and comments
- `notifications` - User notifications

---

## 🚀 Deployment

### Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete guide.

**Quick Steps:**
1. Set up production server
2. Configure environment variables
3. Run database migrations
4. Deploy backend (systemd/Docker)
5. Build and deploy frontend (Nginx)
6. Configure SSL
7. Set up monitoring

---

## 📈 Roadmap

### Completed (v2.0.0)
- ✅ Core scoring engine
- ✅ User authentication
- ✅ Lead assignment
- ✅ Notes and notifications
- ✅ Status tracking
- ✅ Mobile responsive design
- ✅ Security hardening
- ✅ Error handling & logging
- ✅ Performance optimization

### Future Enhancements
- [ ] Automated lead distribution (round-robin)
- [ ] Advanced analytics dashboard
- [ ] CSV import/export
- [ ] SMS notifications
- [ ] Calendar integration
- [ ] API rate limiting dashboard
- [ ] Audit logging
- [ ] Multi-tenant support

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📝 License

[Add your license here]

---

## 🆘 Support

- **Documentation**: Check `/docs` folder
- **Issues**: GitHub Issues
- **Email**: [your-email]

---

## 🎉 Acknowledgments

Built with:
- FastAPI
- React
- PostgreSQL
- Tailwind CSS

---

**Version**: 2.0.0  
**Last Updated**: November 2024  
**Status**: Production Ready

---

## 🚀 Launch Checklist

Before going live, complete:
1. ✅ [FINAL_LAUNCH_GUIDE.md](./FINAL_LAUNCH_GUIDE.md) - Comprehensive testing
2. ✅ [LAUNCH_CHECKLIST.md](./LAUNCH_CHECKLIST.md) - Pre-launch items
3. ✅ Run `./verify_system.sh` - System verification

**Ready to launch!** 🎉
