"""
Course management routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Course, Teacher, Enrollment, User, UserRole, Student
from auth import require_admin, require_teacher
from utils import api_response, handle_exceptions

course_bp = Blueprint('course', __name__, url_prefix='/api/courses')

@course_bp.route('', methods=['GET'])
@jwt_required()
@handle_exceptions
def list_courses():
    """List all active courses"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    teacher_id = request.args.get('teacher_id', None, type=str)
    
    query = Course.query.filter_by(is_active=True)
    
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)
    
    total = query.count()
    courses = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return api_response(
        'Courses retrieved',
        {
            'courses': [course.to_dict() for course in courses],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        },
        status_code=200
    )

@course_bp.route('/<course_id>', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_course(course_id):
    """Get course details with enrolled students"""
    course = Course.query.get(course_id)
    
    if not course:
        return api_response('Course not found', status_code=404)
    
    course_data = course.to_dict()
    
    # Add enrolled students
    enrollments = Enrollment.query.filter_by(course_id=course_id, is_active=True).all()
    course_data['enrolled_students'] = [
        {
            'student_id': enrollment.student_id,
            'student_name': f"{enrollment.student.user.first_name} {enrollment.student.user.last_name}",
            'roll_number': enrollment.student.roll_number,
            'enrollment_date': enrollment.enrollment_date.isoformat()
        }
        for enrollment in enrollments
    ]
    
    return api_response('Course retrieved', course_data, status_code=200)

@course_bp.route('', methods=['POST'])
@require_teacher
@handle_exceptions
def create_course():
    """Create a new course (teacher only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != UserRole.TEACHER.value:
        return api_response('Only teachers can create courses', status_code=403)
    
    teacher = Teacher.query.filter_by(user_id=current_user_id).first()
    if not teacher:
        return api_response('Teacher profile not found', status_code=404)
    
    data = request.get_json()
    
    # Validate input
    required_fields = ['course_code', 'course_name']
    if not all(field in data for field in required_fields):
        return api_response('Missing required fields', status_code=400)
    
    # Check if course code already exists
    if Course.query.filter_by(course_code=data['course_code']).first():
        return api_response('Course code already exists', status_code=409)
    
    course = Course(
        course_code=data['course_code'],
        course_name=data['course_name'],
        description=data.get('description', ''),
        teacher_id=teacher.id,
        credits=data.get('credits', 3),
        semester=data.get('semester', ''),
        max_students=data.get('max_students', 50)
    )
    
    db.session.add(course)
    db.session.commit()
    
    return api_response(
        'Course created',
        course.to_dict(),
        status_code=201
    )

@course_bp.route('/<course_id>', methods=['PUT'])
@require_teacher
@handle_exceptions
def update_course(course_id):
    """Update course (teacher can only update their own courses)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    course = Course.query.get(course_id)
    
    if not course:
        return api_response('Course not found', status_code=404)
    
    # Check authorization
    if user.role == UserRole.TEACHER.value:
        teacher = Teacher.query.filter_by(user_id=current_user_id).first()
        if course.teacher_id != teacher.id:
            return api_response('Unauthorized to update this course', status_code=403)
    elif user.role != UserRole.ADMIN.value:
        return api_response('Insufficient permissions', status_code=403)
    
    data = request.get_json()
    
    if 'course_name' in data:
        course.course_name = data['course_name']
    if 'description' in data:
        course.description = data['description']
    if 'credits' in data:
        course.credits = data['credits']
    if 'semester' in data:
        course.semester = data['semester']
    if 'max_students' in data:
        course.max_students = data['max_students']
    if 'is_active' in data:
        course.is_active = data['is_active']
    
    db.session.commit()
    
    return api_response('Course updated', course.to_dict(), status_code=200)

@course_bp.route('/<course_id>', methods=['DELETE'])
@require_teacher
@handle_exceptions
def delete_course(course_id):
    """Soft delete course"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    course = Course.query.get(course_id)
    
    if not course:
        return api_response('Course not found', status_code=404)
    
    # Check authorization
    if user.role == UserRole.TEACHER.value:
        teacher = Teacher.query.filter_by(user_id=current_user_id).first()
        if course.teacher_id != teacher.id:
            return api_response('Unauthorized to delete this course', status_code=403)
    elif user.role != UserRole.ADMIN.value:
        return api_response('Insufficient permissions', status_code=403)
    
    course.is_active = False
    db.session.commit()
    
    return api_response('Course deleted', status_code=200)

@course_bp.route('/<course_id>/enroll', methods=['POST'])
@jwt_required()
@handle_exceptions
def enroll_student(course_id):
    """Enroll student in a course"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != UserRole.STUDENT.value:
        return api_response('Only students can enroll', status_code=403)
    
    course = Course.query.get(course_id)
    
    if not course:
        return api_response('Course not found', status_code=404)
    
    if not course.is_active:
        return api_response('Course is not active', status_code=400)
    
    student = Student.query.filter_by(user_id=current_user_id).first()
    
    # Check if already enrolled
    existing = Enrollment.query.filter_by(
        student_id=student.id,
        course_id=course_id
    ).first()
    
    if existing:
        if existing.is_active:
            return api_response('Already enrolled in this course', status_code=409)
        else:
            # Re-activate enrollment
            existing.is_active = True
            db.session.commit()
            return api_response('Re-enrolled in course', existing.to_dict(), status_code=200)
    
    # Check capacity
    active_enrollments = Enrollment.query.filter_by(
        course_id=course_id,
        is_active=True
    ).count()
    
    if active_enrollments >= course.max_students:
        return api_response('Course is at full capacity', status_code=400)
    
    enrollment = Enrollment(
        student_id=student.id,
        course_id=course_id
    )
    
    db.session.add(enrollment)
    db.session.commit()
    
    return api_response(
        'Enrolled successfully',
        enrollment.to_dict(),
        status_code=201
    )

@course_bp.route('/<course_id>/unenroll', methods=['POST'])
@jwt_required()
@handle_exceptions
def unenroll_student(course_id):
    """Unenroll student from a course"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != UserRole.STUDENT.value:
        return api_response('Only students can unenroll', status_code=403)
    
    student = Student.query.filter_by(user_id=current_user_id).first()
    
    enrollment = Enrollment.query.filter_by(
        student_id=student.id,
        course_id=course_id,
        is_active=True
    ).first()
    
    if not enrollment:
        return api_response('Not enrolled in this course', status_code=404)
    
    enrollment.is_active = False
    db.session.commit()
    
    return api_response('Unenrolled from course', status_code=200)
