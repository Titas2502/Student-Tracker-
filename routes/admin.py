"""
Administrator routes for managing users, students, and teachers
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Student, Teacher, UserRole
from auth import hash_password, require_admin
from utils import api_response, handle_exceptions, validate_email, paginate

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# ==================== USER MANAGEMENT ====================

@admin_bp.route('/users', methods=['GET'])
@require_admin
@handle_exceptions
def list_users():
    """List all users with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role', None, type=str)
    
    query = User.query
    
    if role:
        valid_roles = [r.value for r in UserRole]
        if role not in valid_roles:
            return api_response('Invalid role', status_code=400)
        query = query.filter_by(role=role)
    
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return api_response(
        'Users retrieved',
        {
            'users': [user.to_dict() for user in users],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        },
        status_code=200
    )

@admin_bp.route('/users/<user_id>', methods=['GET'])
@require_admin
@handle_exceptions
def get_user(user_id):
    """Get user details"""
    user = User.query.get(user_id)
    
    if not user:
        return api_response('User not found', status_code=404)
    
    user_data = user.to_dict()
    if user.role == UserRole.STUDENT.value and user.student:
        user_data['student'] = user.student.to_dict()
    elif user.role == UserRole.TEACHER.value and user.teacher:
        user_data['teacher'] = user.teacher.to_dict()
    
    return api_response('User retrieved', user_data, status_code=200)

@admin_bp.route('/users/<user_id>', methods=['PUT'])
@require_admin
@handle_exceptions
def update_user(user_id):
    """Update user information"""
    user = User.query.get(user_id)
    
    if not user:
        return api_response('User not found', status_code=404)
    
    data = request.get_json()
    
    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'password' in data:
        user.password_hash = hash_password(data['password'])
    
    db.session.commit()
    
    return api_response('User updated', user.to_dict(), status_code=200)

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@require_admin
@handle_exceptions
def delete_user(user_id):
    """Soft delete a user"""
    user = User.query.get(user_id)
    
    if not user:
        return api_response('User not found', status_code=404)
    
    user.is_active = False
    db.session.commit()
    
    return api_response('User deactivated', status_code=200)

# ==================== STUDENT MANAGEMENT ====================

@admin_bp.route('/students', methods=['GET'])
@require_admin
@handle_exceptions
def list_students():
    """List all students"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    total = Student.query.count()
    students = Student.query.offset((page - 1) * per_page).limit(per_page).all()
    
    return api_response(
        'Students retrieved',
        {
            'students': [student.to_dict() for student in students],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        },
        status_code=200
    )

@admin_bp.route('/students/<student_id>', methods=['GET'])
@require_admin
@handle_exceptions
def get_student(student_id):
    """Get student details"""
    student = Student.query.get(student_id)
    
    if not student:
        return api_response('Student not found', status_code=404)
    
    return api_response('Student retrieved', student.to_dict(), status_code=200)

@admin_bp.route('/students/<student_id>', methods=['PUT'])
@require_admin
@handle_exceptions
def update_student(student_id):
    """Update student information"""
    student = Student.query.get(student_id)
    
    if not student:
        return api_response('Student not found', status_code=404)
    
    data = request.get_json()
    
    if 'phone' in data:
        student.phone = data['phone']
    if 'address' in data:
        student.address = data['address']
    if 'is_active' in data:
        student.is_active = data['is_active']
    
    db.session.commit()
    
    return api_response('Student updated', student.to_dict(), status_code=200)

@admin_bp.route('/students/<student_id>', methods=['DELETE'])
@require_admin
@handle_exceptions
def delete_student(student_id):
    """Soft delete a student"""
    student = Student.query.get(student_id)
    
    if not student:
        return api_response('Student not found', status_code=404)
    
    student.is_active = False
    db.session.commit()
    
    return api_response('Student deactivated', status_code=200)

# ==================== TEACHER MANAGEMENT ====================

@admin_bp.route('/teachers', methods=['GET'])
@require_admin
@handle_exceptions
def list_teachers():
    """List all teachers"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    total = Teacher.query.count()
    teachers = Teacher.query.offset((page - 1) * per_page).limit(per_page).all()
    
    return api_response(
        'Teachers retrieved',
        {
            'teachers': [teacher.to_dict() for teacher in teachers],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        },
        status_code=200
    )

@admin_bp.route('/teachers/<teacher_id>', methods=['GET'])
@require_admin
@handle_exceptions
def get_teacher(teacher_id):
    """Get teacher details"""
    teacher = Teacher.query.get(teacher_id)
    
    if not teacher:
        return api_response('Teacher not found', status_code=404)
    
    return api_response('Teacher retrieved', teacher.to_dict(), status_code=200)

@admin_bp.route('/teachers/<teacher_id>', methods=['PUT'])
@require_admin
@handle_exceptions
def update_teacher(teacher_id):
    """Update teacher information"""
    teacher = Teacher.query.get(teacher_id)
    
    if not teacher:
        return api_response('Teacher not found', status_code=404)
    
    data = request.get_json()
    
    if 'specialization' in data:
        teacher.specialization = data['specialization']
    if 'phone' in data:
        teacher.phone = data['phone']
    if 'office_number' in data:
        teacher.office_number = data['office_number']
    if 'is_active' in data:
        teacher.is_active = data['is_active']
    
    db.session.commit()
    
    return api_response('Teacher updated', teacher.to_dict(), status_code=200)

@admin_bp.route('/teachers/<teacher_id>', methods=['DELETE'])
@require_admin
@handle_exceptions
def delete_teacher(teacher_id):
    """Soft delete a teacher"""
    teacher = Teacher.query.get(teacher_id)
    
    if not teacher:
        return api_response('Teacher not found', status_code=404)
    
    teacher.is_active = False
    db.session.commit()
    
    return api_response('Teacher deactivated', status_code=200)

# ==================== DASHBOARD ====================

@admin_bp.route('/dashboard', methods=['GET'])
@require_admin
@handle_exceptions
def dashboard():
    """Get admin dashboard statistics"""
    total_users = User.query.count()
    total_students = Student.query.filter_by(is_active=True).count()
    total_teachers = Teacher.query.filter_by(is_active=True).count()
    total_courses = db.session.query(db.func.count('*')).select_from(db.Table('courses')).scalar()
    
    stats = {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses or 0
    }
    
    return api_response('Dashboard stats', stats, status_code=200)
