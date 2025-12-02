# StudentTracker - Build & Deployment Guide

## Project Structure

```
StudentTracker/
├── server/
│   ├── app.py                    # Flask application entry point
│   ├── config.py                 # Configuration management
│   ├── models.py                 # Database models
│   ├── auth.py                   # Authentication utilities
│   ├── utils.py                  # Helper utilities
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── admin.py             # Admin management endpoints
│   │   ├── course.py            # Course management endpoints
│   │   └── attendance.py        # Attendance tracking endpoints
│   ├── static/
│   │   ├── index.html           # Main HTML file
│   │   ├── styles.css           # Styling
│   │   ├── api.js               # API client
│   │   └── app.js               # Frontend logic
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example             # Environment variables template
│   ├── .gitignore               # Git ignore rules
│   ├── web.config               # Azure deployment config
│   ├── Dockerfile               # Docker configuration
│   ├── docker-compose.yml       # Docker Compose setup
│   ├── build.ps1                # PowerShell build script
│   ├── startup.sh               # Azure startup script
│   └── README.md                # Documentation
```

## Quick Start

### Option 1: Local Development (Windows PowerShell)

```powershell
# Navigate to project directory
cd d:\StudentTracker\server

# Run the build script
.\build.ps1 dev

# The application will start at http://localhost:5000
```

### Option 2: Production Build with Gunicorn

```powershell
# Navigate to project directory
cd d:\StudentTracker\server

# Run production build
.\build.ps1 prod

# The application will start at http://localhost:8000
```

### Option 3: Docker Deployment

```bash
# Navigate to project directory
cd d:\StudentTracker\server

# Run Docker Compose
docker-compose up -d

# Access the application at http://localhost:8000
# Database available at localhost:1433
```

## Step-by-Step Build Instructions

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Git (optional, for version control)
- Docker (for containerized deployment)
- SQL Server or Azure SQL Database

### 1. Environment Setup

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip
```

### 2. Install Dependencies

```powershell
# Install all required packages
pip install -r requirements.txt
```

Dependencies include:
- Flask 2.3.2
- Flask-SQLAlchemy 3.0.5
- Flask-JWT-Extended 4.5.2
- flask-cors 4.0.0
- SQLAlchemy 2.0.20
- pyodbc 4.0.39
- python-dotenv 1.0.0
- gunicorn 21.2.0

### 3. Configure Environment Variables

Create `.env` file in the `server` directory:

```env
# Flask Configuration
FLASK_ENV=development
DEBUG=True

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production

# Database Configuration (SQL Server or Azure SQL)
DB_SERVER=localhost
DB_NAME=StudentTrackerDB
DB_USER=sa
DB_PASSWORD=YourPassword123!
DB_DRIVER=ODBC Driver 17 for SQL Server

# CORS Configuration
CORS_ORIGINS=http://localhost:5000

# Optional: Application Port
PORT=5000
```

**For Azure SQL Database:**
```env
DB_SERVER=your-server.database.windows.net
DB_NAME=StudentTrackerDB
DB_USER=yourusername
DB_PASSWORD=YourPassword123!
DB_DRIVER=ODBC Driver 17 for SQL Server
```

### 4. Initialize Database

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run database initialization
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"
```

### 5. Run Application

#### Development Mode (with auto-reload)
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run Flask development server
python app.py

# Access at http://localhost:5000
```

#### Production Mode (with Gunicorn)
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run with Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 60 app:app

# Access at http://localhost:8000
```

## Azure App Service Deployment

### 1. Create Azure Resources

```bash
# Set variables
$resourceGroup = "StudentTrackerRG"
$location = "eastus"
$sqlServer = "studenttracker-sql"
$appName = "studenttracker-api"

# Create resource group
az group create --name $resourceGroup --location $location

# Create SQL Server
az sql server create `
  --resource-group $resourceGroup `
  --name $sqlServer `
  --admin-user sqladmin `
  --admin-password YourPassword123! `
  --location $location

# Create SQL Database
az sql db create `
  --resource-group $resourceGroup `
  --server $sqlServer `
  --name StudentTrackerDB `
  --edition Standard

# Create App Service Plan (Linux)
az appservice plan create `
  --name StudentTrackerPlan `
  --resource-group $resourceGroup `
  --sku B2 `
  --is-linux

# Create Web App
az webapp create `
  --resource-group $resourceGroup `
  --plan StudentTrackerPlan `
  --name $appName `
  --runtime "PYTHON|3.11"
```

### 2. Configure Application Settings

```bash
az webapp config appsettings set `
  --resource-group $resourceGroup `
  --name $appName `
  --settings `
    FLASK_ENV=production `
    DEBUG=False `
    JWT_SECRET_KEY=your-production-secret-key `
    DB_SERVER=studenttracker-sql.database.windows.net `
    DB_NAME=StudentTrackerDB `
    DB_USER=sqladmin `
    DB_PASSWORD=YourPassword123! `
    CORS_ORIGINS=https://studenttracker-api.azurewebsites.net
```

### 3. Configure Startup Command

```bash
az webapp config set `
  --resource-group $resourceGroup `
  --name $appName `
  --startup-file "gunicorn --bind 0.0.0.0 --timeout 600 app:app"
```

### 4. Deploy Code

#### Option A: Git Deployment
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Configure deployment
az webapp deployment source config-local-git `
  --resource-group $resourceGroup `
  --name $appName

# Get deployment credentials and push
git remote add azure <deployment-url>
git push azure master
```

#### Option B: ZIP Deployment
```bash
# Create deployment package
Compress-Archive -Path * -DestinationPath deploy.zip

# Deploy
az webapp deployment source config-zip `
  --resource-group $resourceGroup `
  --name $appName `
  --src deploy.zip
```

## Docker Deployment

### Build and Run Locally

```bash
# Build Docker image
docker build -t studenttracker:latest .

# Run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop containers
docker-compose down
```

### Push to Azure Container Registry

```bash
# Create container registry
az acr create `
  --resource-group $resourceGroup `
  --name studenttrackerregistry `
  --sku Basic

# Build and push image
az acr build `
  --registry studenttrackerregistry `
  --image studenttracker:latest .

# Deploy to App Service
az webapp create `
  --resource-group $resourceGroup `
  --plan StudentTrackerPlan `
  --name $appName `
  --deployment-container-image-name `
    studenttrackerregistry.azurecr.io/studenttracker:latest
```

## Testing the Application

### 1. Register a Test User

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

### 2. Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Admin123!"
  }'
```

### 3. Access Dashboard

Open browser and navigate to: `http://localhost:5000`

### 4. Test API Endpoints

```bash
# Get current user (replace TOKEN with actual token)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5000/api/auth/me

# List users (admin only)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5000/api/admin/users

# Get dashboard stats (admin only)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5000/api/admin/dashboard
```

## Troubleshooting

### Database Connection Issues

**Problem**: Cannot connect to database
**Solution**:
```powershell
# Test database connection
$connectionString = "Driver=ODBC Driver 17 for SQL Server;Server=localhost;Database=StudentTrackerDB;UID=sa;PWD=YourPassword123!"

# Try to connect with osql
osql -S localhost -U sa -P YourPassword123! -d StudentTrackerDB

# Verify ODBC driver is installed
Get-OdbcDriver | Where-Object { $_.Name -like "*SQL Server*" }
```

### Port Already in Use

**Problem**: Address already in use (port 5000/8000)
**Solution**:
```powershell
# Find process using port
netstat -ano | findstr :5000

# Kill process
taskkill /PID <PID> /F

# Or use different port
$env:PORT=5001
python app.py
```

### Module Import Errors

**Problem**: ImportError for Flask modules
**Solution**:
```powershell
# Verify virtual environment is activated
# (should see (venv) in command prompt)

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check installed packages
pip list
```

### JWT Token Issues

**Problem**: Invalid token error
**Solution**:
```powershell
# Ensure JWT_SECRET_KEY is set
$env:JWT_SECRET_KEY="your-secret-key"

# Verify token in browser console
# Check token expiration: jwt_decode(token)
```

## Performance Optimization

### 1. Database Connection Pooling
Already configured in `config.py`:
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

### 2. Gunicorn Workers
For production, adjust worker count based on CPU cores:
```bash
gunicorn --workers $(nproc) app:app
```

### 3. Enable Caching
Add Redis for session and query caching:
```python
pip install flask-caching redis
```

### 4. Database Indexes
Indexes are created automatically for foreign keys and unique constraints.

## Security Best Practices

### 1. Change Default Credentials
- JWT_SECRET_KEY
- Database password
- Admin user password

### 2. Enable HTTPS
```bash
# In Azure Portal:
# App Service > TLS/SSL settings > Private Key Certificates
# Upload your certificate
```

### 3. Configure Firewall
```bash
# Azure SQL Firewall rules
az sql server firewall-rule create `
  --resource-group $resourceGroup `
  --server $sqlServer `
  --name AllowAppService `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 0.0.0.0
```

### 4. Use Environment Variables
Store sensitive data in:
- `.env` files (development)
- Azure Key Vault (production)

### 5. Enable Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Monitoring and Logs

### Local Development
Logs appear in console output.

### Azure App Service
```bash
# View logs
az webapp log tail --resource-group $resourceGroup --name $appName

# Download logs
az webapp log download --resource-group $resourceGroup --name $appName
```

## Continuous Integration/Deployment

### GitHub Actions Example
```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r server/requirements.txt
    - name: Deploy to Azure
      run: |
        az login --service-principal -u ${{ secrets.AZURE_CLIENT_ID }} -p ${{ secrets.AZURE_CLIENT_SECRET }} --tenant ${{ secrets.AZURE_TENANT_ID }}
        az webapp deployment source config-zip --resource-group ${{ secrets.AZURE_RESOURCE_GROUP }} --name ${{ secrets.AZURE_APP_NAME }} --src deploy.zip
```

## Scaling Considerations

### Horizontal Scaling
- Use Azure App Service with multiple instances
- Load balance with Azure Application Gateway

### Vertical Scaling
- Increase App Service Plan tier (B2, B3, S1, S2, etc.)
- Increase database compute resources

### Database Optimization
- Add read replicas for read-heavy operations
- Implement query caching
- Use Connection Pooling

## Support & Resources

- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Azure**: https://docs.microsoft.com/azure/
- **Docker**: https://docs.docker.com/

---

**Last Updated**: December 2, 2025
**Version**: 1.0.0
