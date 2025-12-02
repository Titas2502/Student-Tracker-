# Database Setup Guide for StudentTracker

## Current Status
✓ Python environment configured (Python 3.12)
✓ All dependencies installed
✓ Code is ready to run

## Database Connection Error
**Error**: `[IM002] Data source name not found and no default driver specified`

This means SQL Server (or the connection string) is not properly configured.

## Step 1: Choose Your Database Option

### Option A: Local SQL Server (Recommended for Development)
- **Easiest to set up**
- **Good for testing locally**
- **Free: SQL Server Express Edition**

### Option B: Azure SQL Database (Production)
- **Cloud-based**
- **Pay-as-you-go**
- **Best for Azure App Service deployment**

### Option C: SQLite (Quick Testing Only)
- **No setup needed**
- **Single file database**
- **Not for production**

---

## Database Setup Instructions

### Option A: Using Local SQL Server Express

#### Step 1: Download & Install SQL Server Express
1. Go to: https://www.microsoft.com/en-us/sql-server/sql-server-editions/express
2. Download "SQL Server 2022 Express"
3. Run installer and select "Basic" installation
4. Follow the wizard (accept defaults)
5. Note: No configuration needed

#### Step 2: Configure Your .env File

Create `.env` file in `d:\StudentTracker\server\` with:

```env
FLASK_ENV=development
DEBUG=True
JWT_SECRET_KEY=dev-secret-key-change-in-production
DB_SERVER=localhost
DB_NAME=StudentTrackerDB
DB_USER=sa
DB_PASSWORD=YourPassword123!
DB_DRIVER=ODBC Driver 17 for SQL Server
CORS_ORIGINS=http://localhost:5000
```

#### Step 3: Verify ODBC Driver

```powershell
# Check if ODBC driver is installed
Get-OdbcDriver | Where-Object { $_.Name -like "*SQL*" }
```

If no drivers show up, download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

#### Step 4: Create Database via SQL Server Management Studio

1. Download: https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms
2. Install SSMS
3. Connect to: `localhost` or `(local)`
4. Right-click "Databases" → "New Database"
5. Name: `StudentTrackerDB`
6. Click OK

#### Step 5: Run Database Setup

```powershell
cd d:\StudentTracker\server
.\venv312\Scripts\python.exe setup_db.py
```

---

### Option B: Using Azure SQL Database

#### Step 1: Create Azure Resources

```bash
# Install Azure CLI
# From: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login to Azure
az login

# Create Resource Group
az group create --name StudentTrackerRG --location eastus

# Create SQL Server
az sql server create \
  --resource-group StudentTrackerRG \
  --name studenttracker-sql \
  --admin-user sqladmin \
  --admin-password YourPassword123! \
  --location eastus

# Create Database
az sql db create \
  --resource-group StudentTrackerRG \
  --server studenttracker-sql \
  --name StudentTrackerDB \
  --edition Standard
```

#### Step 2: Configure Firewall

```bash
# Allow your IP to connect
az sql server firewall-rule create \
  --resource-group StudentTrackerRG \
  --server studenttracker-sql \
  --name AllowMyIP \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP

# Or allow all (less secure)
az sql server firewall-rule create \
  --resource-group StudentTrackerRG \
  --server studenttracker-sql \
  --name AllowAllAzureIps \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

#### Step 3: Update .env File

```env
FLASK_ENV=development
DEBUG=False
JWT_SECRET_KEY=your-strong-secret-key
DB_SERVER=studenttracker-sql.database.windows.net
DB_NAME=StudentTrackerDB
DB_USER=sqladmin
DB_PASSWORD=YourPassword123!
DB_DRIVER=ODBC Driver 17 for SQL Server
CORS_ORIGINS=https://your-domain.azurewebsites.net
```

#### Step 4: Run Database Setup

```powershell
cd d:\StudentTracker\server
.\venv312\Scripts\python.exe setup_db.py
```

---

### Option C: Using SQLite (Quick Testing)

Edit `config.py`:

```python
# Replace this line:
SQLALCHEMY_DATABASE_URI = (
    f'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}'
    f'?driver={DB_DRIVER}&Encrypt=yes&TrustServerCertificate=no&Connection Timeout=30'
)

# With this line:
SQLALCHEMY_DATABASE_URI = 'sqlite:///studenttracker.db'
```

Then run:

```powershell
cd d:\StudentTracker\server
.\venv312\Scripts\python.exe setup_db.py
```

---

## Troubleshooting

### Error: "ODBC Driver 17 for SQL Server not found"

**Solution**: Download and install from Microsoft:
https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Error: "Cannot connect to server"

**Checklist**:
- [ ] SQL Server is running (check Services)
- [ ] Correct server name in .env
- [ ] Correct username/password
- [ ] Firewall allows connection
- [ ] Database exists

### Error: "pyodbc" module not found

**Solution**:
```powershell
.\venv312\Scripts\python.exe -m pip install --force-reinstall pyodbc
```

### Error: "Login failed for user 'sa'"

**Checklist**:
- [ ] Username is correct ('sa' for Express)
- [ ] Password is correct
- [ ] SQL Server allows SQL authentication

---

## Verify Database is Set Up

Run this command:

```powershell
cd d:\StudentTracker\server
.\venv312\Scripts\python.exe -c "
from app import create_app, db
app = create_app('development')
with app.app_context():
    print('Database connected!')
    print(f'Tables created: {len(db.metadata.tables)}')"
```

If you see:
```
Database connected!
Tables created: 6
```

Success! Your database is ready!

---

## Next Steps

Once database is set up:

### 1. Run the Application
```powershell
cd d:\StudentTracker\server
.\venv312\Scripts\python.exe app.py
```

### 2. Open in Browser
```
http://localhost:5000
```

### 3. Login with Test Credentials
- **Admin**: admin@test.com / Admin123!
- **Teacher**: teacher@test.com / Teacher123!
- **Student**: student@test.com / Student123!

---

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| FLASK_ENV | Environment mode | development, production |
| DEBUG | Enable debug mode | True, False |
| JWT_SECRET_KEY | Token signing key | any-secret-string |
| DB_SERVER | Database server | localhost, server.database.windows.net |
| DB_NAME | Database name | StudentTrackerDB |
| DB_USER | Database user | sa, sqladmin |
| DB_PASSWORD | Database password | YourPassword123! |
| DB_DRIVER | ODBC driver | ODBC Driver 17 for SQL Server |
| CORS_ORIGINS | Allowed domains | http://localhost:5000, * |

---

## Quick Setup Command (If Using Local SQL Server)

After installing SQL Server locally:

```powershell
# 1. Create .env file
Copy-Item .env.example .env

# 2. Edit .env with your database credentials
notepad .env

# 3. Create database in SQL Server (via SSMS or sqlcmd)
# Name: StudentTrackerDB

# 4. Run setup
.\venv312\Scripts\python.exe setup_db.py

# 5. Start application
.\venv312\Scripts\python.exe app.py
```

---

**Questions?** Check the documentation:
- README.md - Main documentation
- BUILD_AND_DEPLOYMENT.md - Full build guide
- QUICK_REFERENCE.md - Quick commands
