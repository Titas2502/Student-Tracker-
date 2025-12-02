"""
Attendance tracking routes (Teacher only)
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from models import db, Attendance, Student, Course, Teacher, Enrollment, User, UserRole
from auth import require_teacher
from utils import api_response, handle_exceptions

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

@attendance_bp.route('', methods=['POST'])
@require_teacher
@handle_exceptions
def mark_attendance():
    """Mark attendance for students in a course"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    teacher = Teacher.query.filter_by(user_id=current_user_id).first()
    
    if not teacher:
        return api_response('Teacher profile not found', status_code=404)
    
    data = request.get_json()
    
    # Validate input
    required_fields = ['course_id', 'attendance_records']
    if not all(field in data for field in required_fields):
        return api_response('Missing required fields', status_code=400)
    
    course = Course.query.get(data['course_id'])
    
    if not course:
        return api_response('Course not found', status_code=404)
    
    # Check if teacher owns the course
    if course.teacher_id != teacher.id:
        return api_response('Unauthorized to mark attendance for this course', status_code=403)
    
    attendance_records = []
    errors = []
    
    for record in data['attendance_records']:
        try:
            # Validate record
            if not all(field in record for field in ['student_id', 'status']):
                errors.append(f"Invalid record: missing fields")
                continue
            
            student = Student.query.get(record['student_id'])
            if not student:
                errors.append(f"Student {record['student_id']} not found")
                continue
            
            # Check if student is enrolled
            enrollment = Enrollment.query.filter_by(
                student_id=record['student_id'],
                course_id=data['course_id'],
                is_active=True
            ).first()
            
            if not enrollment:
                errors.append(f"Student {record['student_id']} not enrolled in this course")
                continue
            
            # Validate status
            valid_statuses = ['present', 'absent', 'late']
            if record['status'] not in valid_statuses:
                errors.append(f"Invalid status: {record['status']}")
                continue
            
            # Check if attendance already exists for this date
            attendance_date = datetime.fromisoformat(record.get('attendance_date', datetime.now().isoformat())).date()
            
            existing = Attendance.query.filter_by(
                student_id=record['student_id'],
                course_id=data['course_id'],
                attendance_date=attendance_date
            ).first()
            
            if existing:
                # Update existing record
                existing.status = record['status']
                existing.remarks = record.get('remarks', '')
                attendance_records.append(existing)
            else:
                # Create new record
                attendance = Attendance(
                    student_id=record['student_id'],
                    course_id=data['course_id'],
                    teacher_id=teacher.id,
                    attendance_date=attendance_date,
                    status=record['status'],
                    remarks=record.get('remarks', '')
                )
                db.session.add(attendance)
                attendance_records.append(attendance)
        
        except Exception as e:
            errors.append(f"Error processing record: {str(e)}")
    
    db.session.commit()
    
    response_data = {
        'marked_count': len(attendance_records),
        'records': [record.to_dict() for record in attendance_records],
    }
    
    if errors:
        response_data['errors'] = errors
    
    return api_response(
        'Attendance marked',
        response_data,
        status_code=201 if not errors else 207
    )

@attendance_bp.route('/course/<course_id>', methods=['GET'])
@require_teacher
@handle_exceptions
def get_course_attendance(course_id):
    """Get attendance records for a course"""
    current_user_id = get_jwt_identity()
    teacher = Teacher.query.filter_by(user_id=current_user_id).first()
    
    course = Course.query.get(course_id)
    
    if not course:
        return api_response('Course not found', status_code=404)
    
    # Check authorization
    if course.teacher_id != teacher.id:
        return api_response('Unauthorized to view attendance', status_code=403)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    from_date = request.args.get('from_date', None, type=str)
    to_date = request.args.get('to_date', None, type=str)
    
    query = Attendance.query.filter_by(course_id=course_id)
    
    if from_date:
        from_date_obj = datetime.fromisoformat(from_date).date()
        query = query.filter(Attendance.attendance_date >= from_date_obj)
    
    if to_date:
        to_date_obj = datetime.fromisoformat(to_date).date()
        query = query.filter(Attendance.attendance_date <= to_date_obj)
    
    total = query.count()
    records = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return api_response(
        'Attendance records retrieved',
        {
            'records': [record.to_dict() for record in records],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        },
        status_code=200
    )


@attendance_bp.route('/course/<course_id>/today', methods=['GET'])
@require_teacher
@handle_exceptions
def get_course_today_attendance(course_id):
    """Get list of enrolled students for a course and attendance for a given date (defaults to today)"""
    current_user_id = get_jwt_identity()
    teacher = Teacher.query.filter_by(user_id=current_user_id).first()

    course = Course.query.get(course_id)
    if not course:
        return api_response('Course not found', status_code=404)

    if course.teacher_id != teacher.id:
        return api_response('Unauthorized to view attendance', status_code=403)

    # allow optional `date` query param in ISO format (YYYY-MM-DD)
    date_str = request.args.get('date', None, type=str)
    if date_str:
        try:
            today = datetime.fromisoformat(date_str).date()
        except Exception:
            return api_response('Invalid date format, expected YYYY-MM-DD', status_code=400)
    else:
        today = date.today()
    
    # Pagination support
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    enrollments = Enrollment.query.filter_by(course_id=course_id, is_active=True).all()
    total = len(enrollments)
    paginated_enrollments = enrollments[(page-1)*per_page:page*per_page]
    
    students = []
    for enrollment in paginated_enrollments:
        student = enrollment.student
        existing = Attendance.query.filter_by(
            student_id=student.id,
            course_id=course_id,
            attendance_date=today
        ).first()
        students.append({
            'student_id': student.id,
            'roll_number': student.roll_number,
            'name': f"{student.user.first_name} {student.user.last_name}",
            'status': existing.status if existing else 'not_marked',
            'attendance_id': existing.id if existing else None,
        })

    return api_response(
        'Today attendance fetched',
        {
            'date': today.isoformat(),
            'students': students,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        },
        status_code=200
    )

@attendance_bp.route('/student/<student_id>', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_student_attendance(student_id):
    """Get attendance records for a student"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    student = Student.query.get(student_id)
    
    if not student:
        return api_response('Student not found', status_code=404)
    
    # Check authorization - student can only see their own records
    if user.role == UserRole.STUDENT.value and student.user_id != current_user_id:
        return api_response('Unauthorized to view attendance', status_code=403)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    course_id = request.args.get('course_id', None, type=str)
    
    query = Attendance.query.filter_by(student_id=student_id)
    
    if course_id:
        query = query.filter_by(course_id=course_id)
    
    total = query.count()
    records = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Calculate statistics
    present_count = Attendance.query.filter_by(student_id=student_id, status='present').count()
    absent_count = Attendance.query.filter_by(student_id=student_id, status='absent').count()
    late_count = Attendance.query.filter_by(student_id=student_id, status='late').count()
    total_classes = present_count + absent_count + late_count
    
    attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
    
    return api_response(
        'Student attendance retrieved',
        {
            'records': [record.to_dict() for record in records],
            'statistics': {
                'total_classes': total_classes,
                'present': present_count,
                'absent': absent_count,
                'late': late_count,
                'attendance_percentage': round(attendance_percentage, 2)
            },
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        },
        status_code=200
    )


@attendance_bp.route('/student/<student_id>/monthly', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_student_monthly(student_id):
    """Return attendance status per day for a given month for histogram/charting

    Query params: year (int), month (1-12)
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    student = Student.query.get(student_id)
    if not student:
        return api_response('Student not found', status_code=404)

    # Authorization: student can view own, teachers/admins can view
    if user.role == UserRole.STUDENT.value and student.user_id != current_user_id:
        return api_response('Unauthorized to view attendance', status_code=403)

    # Parse year/month
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    # determine number of days in month
    from calendar import monthrange
    _, num_days = monthrange(year, month)

    days = []
    values = []
    raw = []
    for d in range(1, num_days + 1):
        day_date = date(year, month, d)
        rec = Attendance.query.filter_by(student_id=student_id, attendance_date=day_date).first()
        if rec:
            status = rec.status
        else:
            status = 'not_marked'

        # numeric mapping for histogram: present=1, late=0.5, absent=0, not_marked=0
        mapping = {'present': 1, 'late': 0.5, 'absent': 0, 'not_marked': 0}
        value = mapping.get(status, 0)

        days.append(d)
        values.append(value)
        raw.append({'date': day_date.isoformat(), 'status': status})

    return api_response('Monthly attendance', {'year': year, 'month': month, 'days': days, 'values': values, 'raw': raw}, status_code=200)

@attendance_bp.route('/<attendance_id>', methods=['PUT'])
@require_teacher
@handle_exceptions
def update_attendance(attendance_id):
    """Update an attendance record"""
    current_user_id = get_jwt_identity()
    teacher = Teacher.query.filter_by(user_id=current_user_id).first()
    
    attendance = Attendance.query.get(attendance_id)
    
    if not attendance:
        return api_response('Attendance record not found', status_code=404)
    
    # Check authorization
    if attendance.teacher_id != teacher.id:
        return api_response('Unauthorized to update this record', status_code=403)
    
    data = request.get_json()
    
    if 'status' in data:
        valid_statuses = ['present', 'absent', 'late']
        if data['status'] not in valid_statuses:
            return api_response('Invalid status', status_code=400)
        attendance.status = data['status']
    
    if 'remarks' in data:
        attendance.remarks = data['remarks']
    
    db.session.commit()
    
    return api_response('Attendance updated', attendance.to_dict(), status_code=200)

@attendance_bp.route('/<attendance_id>', methods=['DELETE'])
@require_teacher
@handle_exceptions
def delete_attendance(attendance_id):
    """Delete an attendance record"""
    current_user_id = get_jwt_identity()
    teacher = Teacher.query.filter_by(user_id=current_user_id).first()
    
    attendance = Attendance.query.get(attendance_id)
    
    if not attendance:
        return api_response('Attendance record not found', status_code=404)
    
    # Check authorization
    if attendance.teacher_id != teacher.id:
        return api_response('Unauthorized to delete this record', status_code=403)
    
    db.session.delete(attendance)
    db.session.commit()
    
    return api_response('Attendance record deleted', status_code=200)

@attendance_bp.route('/course/<course_id>/summary', methods=['GET'])
@require_teacher
@handle_exceptions
def get_attendance_summary(course_id):
    """Get attendance summary for a course"""
    current_user_id = get_jwt_identity()
    teacher = Teacher.query.filter_by(user_id=current_user_id).first()
    
    course = Course.query.get(course_id)
    
    if not course:
        return api_response('Course not found', status_code=404)
    
    # Check authorization
    if course.teacher_id != teacher.id:
        return api_response('Unauthorized to view attendance', status_code=403)
    
    # Get all enrolled students
    enrollments = Enrollment.query.filter_by(course_id=course_id, is_active=True).all()
    
    summary = []
    for enrollment in enrollments:
        student = enrollment.student
        
        total_classes = Attendance.query.filter_by(
            student_id=student.id,
            course_id=course_id
        ).count()
        
        present = Attendance.query.filter_by(
            student_id=student.id,
            course_id=course_id,
            status='present'
        ).count()
        
        absent = Attendance.query.filter_by(
            student_id=student.id,
            course_id=course_id,
            status='absent'
        ).count()
        
        late = Attendance.query.filter_by(
            student_id=student.id,
            course_id=course_id,
            status='late'
        ).count()
        
        percentage = (present / total_classes * 100) if total_classes > 0 else 0
        
        summary.append({
            'student_id': student.id,
            'student_name': f"{student.user.first_name} {student.user.last_name}",
            'roll_number': student.roll_number,
            'total_classes': total_classes,
            'present': present,
            'absent': absent,
            'late': late,
            'attendance_percentage': round(percentage, 2)
        })
    
    return api_response('Attendance summary', summary, status_code=200)
