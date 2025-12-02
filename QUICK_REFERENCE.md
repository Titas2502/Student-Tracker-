# 🚀 StudentTracker - Quick Reference & Commands

## File Structure at a Glance

```
d:\StudentTracker\server\
│
├── 📱 FRONTEND (User Interface)
│   └── static/
│       ├── index.html          # Main web page
│       ├── styles.css          # Responsive styling
│       ├── api.js              # API communication layer
│       └── app.js              # Frontend application logic
│
├── 🔧 BACKEND (Flask Application)
│   ├── app.py                  # Application entry point
│   ├── config.py               # Configuration settings
│   ├── models.py               # Database models
│   ├── auth.py                 # Authentication logic
│   ├── utils.py                # Helper functions
│   │
│   └── routes/                 # API endpoints
│       ├── auth.py             # Login/Register APIs
│       ├── admin.py            # Admin management APIs
│       ├── course.py           # Course management APIs
│       └── attendance.py       # Attendance tracking APIs
│
├── 🔐 CONFIGURATION
│   ├── config.py               # App configuration
│   ├── .env.example            # Environment template
│   └── requirements.txt        # Python dependencies
│
├── 🐳 DEPLOYMENT
│   ├── Dockerfile              # Docker image definition
│   ├── docker-compose.yml      # Multi-container setup
│   ├── web.config              # Azure IIS configuration
│   ├── startup.sh              # Azure startup script
│   └── build.ps1               # Build automation script
│
└── 📚 DOCUMENTATION
    ├── README.md               # Main documentation
    ├── BUILD_AND_DEPLOYMENT.md # Build & deployment guide
    ├── PROJECT_SUMMARY.md      # Project overview
    └── QUICK_REFERENCE.md      # This file!
```

## Quick Start Commands

### 1️⃣ Development Setup (5 minutes)

```powershell
# Navigate to project
cd d:\StudentTracker\server

# Run with automatic setup
.\build.ps1 dev

# Or manually:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

**Access**: http://localhost:5000

### 2️⃣ Production Setup

```powershell
# Using Gunicorn
.\build.ps1 prod

# Or manually:
.\venv\Scripts\Activate.ps1
gunicorn --bind 0.0.0.0:8000 --workers 4 app:app
```

**Access**: http://localhost:8000

### 3️⃣ Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access**: http://localhost:8000

## Key Files & Their Purposes

| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | Flask application factory | 339 |
| `models.py` | Database models (Users, Students, Teachers, Courses, Attendance) | 371 |
| `routes/auth.py` | Authentication endpoints | 119 |
| `routes/admin.py` | Admin management endpoints | 239 |
| `routes/course.py` | Course management endpoints | 252 |
| `routes/attendance.py` | Attendance tracking endpoints | 338 |
| `static/index.html` | Main user interface | 340 |
| `static/styles.css` | Responsive styling | 690 |
| `static/api.js` | API client wrapper | 374 |
| `static/app.js` | Frontend logic | 752 |

## Environment Variables Setup

### Create `.env` file:

```env
# Flask
FLASK_ENV=development
DEBUG=True

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production

# Database
DB_SERVER=localhost
DB_NAME=StudentTrackerDB
DB_USER=sa
DB_PASSWORD=YourPassword123!
DB_DRIVER=ODBC Driver 17 for SQL Server

# CORS
CORS_ORIGINS=http://localhost:5000
```

## Test Credentials

### Create Admin User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Admin123!",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin"
  }'
```

### Create Student User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@test.com",
    "password": "Student123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "roll_number": "STU001"
  }'
```

### Create Teacher User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@test.com",
    "password": "Teacher123!",
    "first_name": "Jane",
    "last_name": "Smith",
    "role": "teacher",
    "employee_id": "EMP001",
    "specialization": "Computer Science"
  }'
```

## API Endpoints Quick Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create new user |
| POST | `/api/auth/login` | Login user |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/refresh` | Refresh token |

### Admin Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | List all users |
| GET | `/api/admin/users/<id>` | Get user details |
| PUT | `/api/admin/users/<id>` | Update user |
| DELETE | `/api/admin/users/<id>` | Deactivate user |
| GET | `/api/admin/dashboard` | Get dashboard stats |

### Courses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/courses` | List courses |
| POST | `/api/courses` | Create course (teacher) |
| GET | `/api/courses/<id>` | Get course details |
| POST | `/api/courses/<id>/enroll` | Enroll student |
| POST | `/api/courses/<id>/unenroll` | Unenroll student |

### Attendance
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/attendance` | Mark attendance |
| GET | `/api/attendance/course/<id>` | Get course attendance |
| GET | `/api/attendance/student/<id>` | Get student attendance |
| GET | `/api/attendance/course/<id>/summary` | Get attendance summary |

## Database Tables

### Users
- Stores all user accounts
- Roles: admin, teacher, student
- JWT authentication

### Students
- Student-specific information
- Linked to Users table
- Tracks enrollment

### Teachers
- Teacher-specific information
- Linked to Users table
- Specialization & contact info

### Courses
- Course details
- Linked to Teachers
- Enrollment capacity

### Enrollment
- Student-Course relationships
- Tracks who's enrolled in what

### Attendance
- Daily attendance records
- Status: present, absent, late
- Linked to Student, Course, Teacher

## Troubleshooting

### Port in Use
```powershell
# Find process
netstat -ano | findstr :5000

# Kill process
taskkill /PID <PID> /F
```

### Database Connection Failed
```powershell
# Check ODBC driver
Get-OdbcDriver | Where-Object { $_.Name -like "*SQL*" }

# Test connection with osql
osql -S localhost -U sa -P YourPassword123!
```

### Virtual Environment Issues
```powershell
# Remove and recreate
Remove-Item -Recurse venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Module Not Found
```powershell
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Verify installation
pip list
```

## Performance Tips

### Development
- Use Flask development server for hot reload
- Enable DEBUG mode for detailed errors
- Use browser DevTools for frontend debugging

### Production
- Use Gunicorn with multiple workers: `gunicorn --workers 4 app:app`
- Enable database connection pooling (already configured)
- Consider adding Redis for caching
- Monitor with Azure Application Insights

## Security Checklist

- ✅ JWT authentication enabled
- ✅ Password hashing with PBKDF2
- ✅ Role-based access control
- ✅ SQL injection prevention (parameterized queries)
- ✅ CORS configuration
- ✅ Input validation
- ⚠️  Change JWT_SECRET_KEY in production
- ⚠️  Use strong database password
- ⚠️  Enable HTTPS/SSL
- ⚠️  Configure firewall rules

## Azure Deployment Quick Steps

```bash
# 1. Create resource group
az group create --name StudentTrackerRG --location eastus

# 2. Create SQL Server
az sql server create --resource-group StudentTrackerRG --name studenttracker-sql \
  --admin-user sqladmin --admin-password YourPassword123!

# 3. Create App Service
az appservice plan create --name StudentTrackerPlan --resource-group StudentTrackerRG --sku B2 --is-linux
az webapp create --resource-group StudentTrackerRG --plan StudentTrackerPlan \
  --name studenttracker-api --runtime "PYTHON|3.11"

# 4. Deploy code (ZIP method)
Compress-Archive -Path * -DestinationPath deploy.zip
az webapp deployment source config-zip --resource-group StudentTrackerRG \
  --name studenttracker-api --src deploy.zip

# 5. Set startup command
az webapp config set --resource-group StudentTrackerRG --name studenttracker-api \
  --startup-file "gunicorn --bind 0.0.0.0 app:app"
```

## Common Commands

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Deactivate virtual environment
deactivate

# Install packages
pip install package_name

# List installed packages
pip list

# Run Flask app
python app.py

# Run with Gunicorn
gunicorn --bind 0.0.0.0:8000 app:app

# Run tests
pytest

# Database initialization
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

## File Size Summary

| Component | Files | Total Size |
|-----------|-------|------------|
| Backend Python | 9 | ~1,829 LOC |
| Frontend | 4 | ~2,156 LOC |
| Configuration | 8 | ~150 LOC |
| Documentation | 4 | ~500+ LOC |
| **TOTAL** | **25+** | **~4,635+ LOC** |

## Getting Help

### Documentation Files
- 📖 `README.md` - Main documentation
- 📖 `BUILD_AND_DEPLOYMENT.md` - Detailed build guide
- 📖 `PROJECT_SUMMARY.md` - Project overview

### Online Resources
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Azure: https://docs.microsoft.com/azure/
- JWT: https://pyjwt.readthedocs.io/

## What's Included ✅

✅ Complete Flask backend with 4 API modules
✅ Responsive HTML5/CSS3/JavaScript frontend
✅ SQLAlchemy ORM with 6 database models
✅ JWT authentication system
✅ Role-based access control (Admin, Teacher, Student)
✅ Course management system
✅ Daily attendance tracking
✅ Admin dashboard
✅ Docker containerization
✅ Azure deployment configuration
✅ Comprehensive documentation
✅ Build automation scripts
✅ Environment configuration template
✅ Security best practices implemented
✅ Database connection pooling
✅ Error handling and logging
✅ CORS support
✅ Pagination support

## Next Actions

1. **Local Testing**: Run `.\build.ps1 dev` to test locally
2. **Configuration**: Update `.env` file with your settings
3. **Database**: Ensure SQL Server is running
4. **Deployment**: Follow Azure deployment steps in BUILD_AND_DEPLOYMENT.md
5. **Customization**: Modify frontend and backend as needed

---

**Version**: 1.0.0
**Created**: December 2, 2025
**Status**: ✅ Production Ready

**Happy Building! 🚀**
