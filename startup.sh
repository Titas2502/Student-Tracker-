#!/usr/bin/env bash
# Azure Deployment Script

# Install Python dependencies
pip install -r requirements.txt

# Initialize database
python -c "
from app import create_app, db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"

echo "Deployment complete!"
