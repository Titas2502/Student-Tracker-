#!/usr/bin/env pwsh
# Build and run script for StudentTracker

param(
    [string]$Command = "run",
    [string]$Environment = "development"
)

function Show-Banner {
    Write-Host @"
╔════════════════════════════════════════════╗
║        StudentTracker Build System         ║
╚════════════════════════════════════════════╝
"@ -ForegroundColor Cyan
}

function Install-Dependencies {
    Write-Host "`n[*] Installing Python dependencies..." -ForegroundColor Yellow
    
    if (-not (Test-Path "venv")) {
        Write-Host "[*] Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
    }
    
    & ".\venv\Scripts\Activate.ps1"
    pip install -r requirements.txt
    
    Write-Host "[+] Dependencies installed successfully!" -ForegroundColor Green
}

function Initialize-Database {
    Write-Host "`n[*] Initializing database..." -ForegroundColor Yellow
    
    & ".\venv\Scripts\Activate.ps1"
    python -c "
from app import create_app, db
app = create_app('$Environment')
with app.app_context():
    db.create_all()
    print('[+] Database initialized successfully!')
"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[+] Database ready!" -ForegroundColor Green
    } else {
        Write-Host "[!] Database initialization failed!" -ForegroundColor Red
        exit 1
    }
}

function Run-Development {
    Write-Host "`n[*] Starting development server..." -ForegroundColor Yellow
    Write-Host "[*] Server will be available at http://localhost:5000" -ForegroundColor Cyan
    
    & ".\venv\Scripts\Activate.ps1"
    $env:FLASK_ENV = "development"
    $env:DEBUG = "True"
    
    python app.py
}

function Run-Production {
    Write-Host "`n[*] Starting production server with Gunicorn..." -ForegroundColor Yellow
    Write-Host "[*] Server will be available at http://localhost:8000" -ForegroundColor Cyan
    
    & ".\venv\Scripts\Activate.ps1"
    $env:FLASK_ENV = "production"
    $env:DEBUG = "False"
    
    gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 60 app:app
}

function Run-Docker {
    Write-Host "`n[*] Building Docker image..." -ForegroundColor Yellow
    docker build -t studenttracker:latest .
    
    Write-Host "`n[*] Starting Docker containers..." -ForegroundColor Yellow
    docker-compose up -d
    
    Write-Host "[+] Docker containers started!" -ForegroundColor Green
    Write-Host "[*] API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "[*] Database: localhost:1433" -ForegroundColor Cyan
}

function Show-Help {
    Write-Host @"
Usage: .\build.ps1 [Command] [Environment]

Commands:
  run         - Install dependencies and run the application (default)
  install     - Only install dependencies
  init-db     - Initialize the database
  dev         - Run in development mode
  prod        - Run in production mode with Gunicorn
  docker      - Run with Docker Compose
  help        - Show this help message

Environment:
  development - Use development configuration (default)
  production  - Use production configuration

Examples:
  .\build.ps1                          # Run in development mode
  .\build.ps1 dev                      # Run in development mode
  .\build.ps1 prod production          # Run in production mode
  .\build.ps1 docker                   # Run with Docker
  .\build.ps1 install                  # Only install dependencies
"@ -ForegroundColor Cyan
}

# Main execution
Show-Banner

switch ($Command.ToLower()) {
    "run" {
        Install-Dependencies
        Initialize-Database
        Run-Development
    }
    "install" {
        Install-Dependencies
    }
    "init-db" {
        Initialize-Database
    }
    "dev" {
        Install-Dependencies
        Initialize-Database
        Run-Development
    }
    "prod" {
        Install-Dependencies
        Initialize-Database
        Run-Production
    }
    "docker" {
        Run-Docker
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "[!] Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}
