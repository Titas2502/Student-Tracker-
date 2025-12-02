"""
Authentication routes for user login and token refresh
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Student, Teacher, UserRole
from auth import hash_password, verify_password, generate_tokens
from utils import api_response, handle_exceptions, validate_email

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
@handle_exceptions
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate input
    required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
    if not all(field in data for field in required_fields):
        return api_response('Missing required fields', status_code=400)
    
    if not validate_email(data['email']):
        return api_response('Invalid email format', status_code=400)
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return api_response('Email already registered', status_code=409)
    
    # Validate role
    valid_roles = [role.value for role in UserRole]
    if data['role'] not in valid_roles:
        return api_response('Invalid role', status_code=400)
    
    # Create user
    user = User(
        email=data['email'],
        password_hash=hash_password(data['password']),
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=data['role']
    )
    
    db.session.add(user)
    db.session.flush()  # Flush to get the user ID
    
    # Create role-specific profile
    if data['role'] == UserRole.STUDENT.value:
        if 'roll_number' not in data:
            return api_response('Roll number required for student', status_code=400)
        
        student = Student(
            user_id=user.id,
            roll_number=data['roll_number']
        )
        db.session.add(student)
    
    elif data['role'] == UserRole.TEACHER.value:
        if 'employee_id' not in data:
            return api_response('Employee ID required for teacher', status_code=400)
        
        teacher = Teacher(
            user_id=user.id,
            employee_id=data['employee_id'],
            specialization=data.get('specialization', '')
        )
        db.session.add(teacher)
    
    db.session.commit()
    
    tokens = generate_tokens(user.id, user.role)
    return api_response(
        'User registered successfully',
        {'user': user.to_dict(), 'tokens': tokens},
        status_code=201
    )

@auth_bp.route('/login', methods=['POST'])
@handle_exceptions
def login():
    """Login user and return tokens"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return api_response('Email and password required', status_code=400)
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not verify_password(user.password_hash, data['password']):
        return api_response('Invalid email or password', status_code=401)
    
    if not user.is_active:
        return api_response('User account is inactive', status_code=403)
    
    tokens = generate_tokens(user.id, user.role)
    return api_response(
        'Login successful',
        {'user': user.to_dict(), 'tokens': tokens},
        status_code=200
    )

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_current_user():
    """Get current user information"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return api_response('User not found', status_code=404)
    
    user_data = user.to_dict()
    
    # Add role-specific data
    if user.role == UserRole.STUDENT.value and user.student:
        user_data['student'] = user.student.to_dict()
    elif user.role == UserRole.TEACHER.value and user.teacher:
        user_data['teacher'] = user.teacher.to_dict()
    
    return api_response('Current user', user_data, status_code=200)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@handle_exceptions
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return api_response('User not found', status_code=404)
    
    tokens = generate_tokens(user.id, user.role)
    return api_response('Token refreshed', tokens, status_code=200)
