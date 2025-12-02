<<<<<<< HEAD
# Student-Tracker-
A scalable, cloud-ready student management system built using Flask, MySQL + SQLAlchemy ORM, HTML/CSS/JavaScript frontend, and Gunicorn for production deployment .  This application provides role-based dashboards for Administrators, Teachers, and Students, including attendance management, course management, and student/teacher CRUD operations.
=======
# StudentTracker API Documentation

## Overview
StudentTracker is a comprehensive student management system with attendance tracking, built with Flask backend and vanilla HTML/CSS/JavaScript frontend, ready for deployment on Azure App Service.

## Features
- **User Management**: Admin, Student, and Teacher roles
- **Student Management**: Add, update, remove student records
- **Teacher Management**: Manage teacher profiles and courses
- **Course Management**: Create and manage courses with enrollment
- **Attendance Tracking**: Daily attendance tracking with statistics
- **JWT Authentication**: Secure token-based authentication
- **Responsive UI**: Mobile-friendly interface

## Tech Stack
- **Backend**: Flask, SQLAlchemy, Flask-JWT-Extended
- **Database**: Azure SQL Server (pyodbc)
- **Server**: Gunicorn (production WSGI server)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Azure App Service

## Setup Instructions

### Prerequisites
- Python 3.9+
- pip package manager
- Azure SQL Database (for production)
- Azure App Service (for hosting)

### Local Development Setup

1. **Clone or extract the project**
   ```bash
   cd StudentTracker/server
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (create `.env` file)
   ```env
   FLASK_ENV=development
   DEBUG=True
   JWT_SECRET_KEY=your-secret-key-change-in-production
   DB_SERVER=localhost
   DB_NAME=StudentTrackerDB
   DB_USER=sa
   DB_PASSWORD=YourPassword123!
   DB_DRIVER=ODBC Driver 17 for SQL Server
   CORS_ORIGINS=http://localhost:5000
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

   The application will start at `http://localhost:5000`

## API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /me` - Get current user
- `POST /refresh` - Refresh access token

### Admin (`/api/admin`)
- `GET /users` - List all users
- `GET /users/<id>` - Get user details
- `PUT /users/<id>` - Update user
- `DELETE /users/<id>` - Deactivate user
- `GET /dashboard` - Admin dashboard statistics
- Student, Teacher management endpoints (similar structure)

### Courses (`/api/courses`)
- `GET /` - List all courses
- `POST /` - Create course (teacher only)
- `GET /<id>` - Get course details
- `PUT /<id>` - Update course
- `DELETE /<id>` - Delete course
- `POST /<id>/enroll` - Enroll student
- `POST /<id>/unenroll` - Unenroll student

### Attendance (`/api/attendance`)
- `POST /` - Mark attendance
- `GET /course/<id>` - Get course attendance
- `GET /student/<id>` - Get student attendance
- `PUT /<id>` - Update attendance record
- `DELETE /<id>` - Delete attendance record
- `GET /course/<id>/summary` - Get attendance summary

## Database Schema

### Users Table
- id (UUID)
- email (unique)
- password_hash
- first_name, last_name
- role (admin, teacher, student)
- is_active
- created_at, updated_at

### Students Table
- id (UUID)
- user_id (FK)
- roll_number (unique)
- phone, address
- enrollment_date
- is_active
- created_at, updated_at

### Teachers Table
- id (UUID)
- user_id (FK)
- employee_id (unique)
- specialization
- phone, office_number
- joining_date
- is_active
- created_at, updated_at

### Courses Table
- id (UUID)
- course_code (unique)
- course_name
- description
- teacher_id (FK)
- credits
- semester
- max_students
- is_active
- created_at, updated_at

### Enrollment Table
- id (UUID)
- student_id (FK)
- course_id (FK)
- enrollment_date
- is_active
- created_at

### Attendance Table
- id (UUID)
- student_id (FK)
- course_id (FK)
- teacher_id (FK)
- attendance_date
- status (present, absent, late)
- remarks
- created_at, updated_at

## Deployment to Azure App Service

### 1. Prepare Azure Resources
```bash
# Create resource group
az group create --name StudentTrackerRG --location eastus

# Create SQL Server and Database
az sql server create --resource-group StudentTrackerRG --name studenttracker-sql --admin-user sqladmin --admin-password YourPassword123!

az sql db create --resource-group StudentTrackerRG --server studenttracker-sql --name StudentTrackerDB --edition Standard

# Create App Service Plan
az appservice plan create --name StudentTrackerPlan --resource-group StudentTrackerRG --sku B2 --is-linux

# Create Web App
az webapp create --resource-group StudentTrackerRG --plan StudentTrackerPlan --name studenttracker-api --runtime "PYTHON|3.11"
```

### 2. Configure Application Settings
```bash
az webapp config appsettings set --resource-group StudentTrackerRG --name studenttracker-api --settings \
  FLASK_ENV=production \
  DEBUG=False \
  JWT_SECRET_KEY=your-production-secret-key \
  DB_SERVER=studenttracker-sql.database.windows.net \
  DB_NAME=StudentTrackerDB \
  DB_USER=sqladmin \
  DB_PASSWORD=YourPassword123! \
  CORS_ORIGINS=https://studenttracker-api.azurewebsites.net
```

### 3. Deploy Code
```bash
# Option 1: Using Azure CLI
az webapp deployment source config-zip --resource-group StudentTrackerRG --name studenttracker-api --src deploy.zip

# Option 2: Using Git
az webapp deployment source config-local-git --resource-group StudentTrackerRG --name studenttracker-api
git remote add azure https://username@studenttracker-api.scm.azurewebsites.net/studenttracker-api.git
git push azure master
```

### 4. Configure Startup Command
```bash
az webapp config set --resource-group StudentTrackerRG --name studenttracker-api --startup-file "gunicorn --bind 0.0.0.0 --timeout 600 app:app"
```

### 5. Enable SSL
```bash
az webapp config ssl bind --resource-group StudentTrackerRG --name studenttracker-api --certificate-thumbprint {thumbprint}
```

## Build Instructions

### Build locally
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Visit http://localhost:5000 in your browser
```

### Build for production with Gunicorn
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 60 app:app
```

## Testing

### Register Test User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@test.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "roll_number": "STU001"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@test.com",
    "password": "password123"
  }'
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| FLASK_ENV | Environment (development/production) | development |
| DEBUG | Debug mode | False |
| JWT_SECRET_KEY | Secret key for JWT signing | your-secret-key-change-in-production |
| DB_SERVER | Database server address | localhost |
| DB_NAME | Database name | StudentTrackerDB |
| DB_USER | Database user | sa |
| DB_PASSWORD | Database password | YourPassword123! |
| DB_DRIVER | ODBC driver | ODBC Driver 17 for SQL Server |
| CORS_ORIGINS | Allowed CORS origins | * |

## Security Considerations

1. **Change JWT_SECRET_KEY** in production
2. **Use strong passwords** for database
3. **Enable SSL/TLS** for all communications
4. **Implement rate limiting** for API endpoints
5. **Use Azure Key Vault** for secrets management
6. **Enable Azure SQL firewall** rules
7. **Implement request validation** and sanitization
8. **Use parameterized queries** (SQLAlchemy handles this)
9. **Keep dependencies updated**
10. **Monitor application logs** regularly

## Troubleshooting

### Database Connection Issues
- Verify connection string format
- Check database credentials
- Ensure ODBC driver is installed
- Verify firewall rules

### Authentication Errors
- Verify JWT_SECRET_KEY is set
- Check token expiration
- Ensure Authorization header is correct

### CORS Issues
- Check CORS_ORIGINS setting
- Verify preflight requests are handled
- Check browser console for CORS errors

## Support and Documentation

For more information:
- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Azure App Service: https://docs.microsoft.com/en-us/azure/app-service/
- JWT Documentation: https://pyjwt.readthedocs.io/

## License
MIT License

## Author
StudentTracker Development Team
>>>>>>> f70deee (initial commit)
