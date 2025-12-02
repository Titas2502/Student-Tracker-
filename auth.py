"""
Authentication utilities for JWT token handling
"""
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

def hash_password(password):
    """Hash a password for storage"""
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(password_hash, password):
    """Verify a password against its hash"""
    return check_password_hash(password_hash, password)

def generate_tokens(user_id, user_role):
    """Generate access and refresh tokens"""
    access_token = create_access_token(
        identity=user_id,
        additional_claims={'role': user_role},
        expires_delta=timedelta(hours=24)
    )
    refresh_token = create_refresh_token(
        identity=user_id,
        additional_claims={'role': user_role},
        expires_delta=timedelta(days=30)
    )
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }

def require_role(*roles):
    """Decorator to require specific roles"""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            from models import User
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or user.role not in roles:
                return jsonify({'message': 'Insufficient permissions'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def require_admin(fn):
    """Decorator to require admin role"""
    return require_role('admin')(fn)

def require_teacher(fn):
    """Decorator to require teacher role"""
    return require_role('teacher', 'admin')(fn)

def require_student(fn):
    """Decorator to require student role"""
    return require_role('student', 'admin')(fn)
