"""
Database models for StudentTracker application
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
import uuid

db = SQLAlchemy()

class UserRole(Enum):
    """User roles in the system"""
    ADMIN = 'admin'
    TEACHER = 'teacher'
    STUDENT = 'student'

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.STUDENT.value)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    teacher = db.relationship('Teacher', uselist=False, backref='user', cascade='all, delete-orphan')
    student = db.relationship('Student', uselist=False, backref='user', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }

class Student(db.Model):
    """Student model"""
    __tablename__ = 'students'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    roll_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='student', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'roll_number': self.roll_number,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'phone': self.phone,
            'address': self.address,
            'enrollment_date': self.enrollment_date.isoformat(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }

class Teacher(db.Model):
    """Teacher model"""
    __tablename__ = 'teachers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    specialization = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    office_number = db.Column(db.String(50))
    joining_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    courses = db.relationship('Course', backref='teacher', cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='teacher', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_id': self.employee_id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'specialization': self.specialization,
            'phone': self.phone,
            'office_number': self.office_number,
            'joining_date': self.joining_date.isoformat(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }

class Course(db.Model):
    """Course model"""
    __tablename__ = 'courses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    course_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.String(36), db.ForeignKey('teachers.id'), nullable=False, index=True)
    credits = db.Column(db.Integer, default=3)
    semester = db.Column(db.String(50))
    max_students = db.Column(db.Integer, default=50)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='course', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'teacher_name': f"{self.teacher.user.first_name} {self.teacher.user.last_name}",
            'credits': self.credits,
            'semester': self.semester,
            'max_students': self.max_students,
            'enrolled_students': len(self.enrollments),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }

class Enrollment(db.Model):
    """Student enrollment in courses"""
    __tablename__ = 'enrollments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False, index=True)
    course_id = db.Column(db.String(36), db.ForeignKey('courses.id'), nullable=False, index=True)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_student_course'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'course_name': self.course.course_name,
            'enrollment_date': self.enrollment_date.isoformat(),
            'is_active': self.is_active,
        }

class Attendance(db.Model):
    """Attendance tracking model"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False, index=True)
    course_id = db.Column(db.String(36), db.ForeignKey('courses.id'), nullable=False, index=True)
    teacher_id = db.Column(db.String(36), db.ForeignKey('teachers.id'), nullable=False, index=True)
    attendance_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), default='present', nullable=False)  # present, absent, late
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', 'attendance_date', name='unique_attendance'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': f"{self.student.user.first_name} {self.student.user.last_name}",
            'course_id': self.course_id,
            'course_name': self.course.course_name,
            'teacher_id': self.teacher_id,
            'attendance_date': self.attendance_date.isoformat(),
            'status': self.status,
            'remarks': self.remarks,
        }
