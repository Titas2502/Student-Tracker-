"""
Database initialization and setup script for StudentTracker
"""
import os
import sys
from pathlib import Path
import io

# Add the server directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set UTF-8 encoding for stdout
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

def setup_database():
    """Initialize the database with all tables and seed data"""
    
    print("=" * 60)
    print("StudentTracker Database Setup")
    print("=" * 60)
    
    try:
        # Import after adding to path
        from app import create_app
        from models import db, User, Student, Teacher, Course, UserRole
        from auth import hash_password
        
        print("\n[1/4] Creating Flask app context...")
        app = create_app('development')
        
        with app.app_context():
            print("[2/4] Creating database tables...")
            db.create_all()
            print("      Database tables created successfully!")
            
            print("\n[3/4] Checking for existing data...")
            existing_users = User.query.count()
            
            if existing_users == 0:
                print("      No existing users found. Creating seed data...")
                
                # Create admin user
                admin = User(
                    email='admin@test.com',
                    password_hash=hash_password('Admin123!'),
                    first_name='Admin',
                    last_name='User',
                    role=UserRole.ADMIN.value,
                    is_active=True
                )
                db.session.add(admin)
                db.session.flush()
                print("      - Admin user created: admin@test.com")
                
                # Create teacher user
                teacher_user = User(
                    email='teacher@test.com',
                    password_hash=hash_password('Teacher123!'),
                    first_name='Jane',
                    last_name='Smith',
                    role=UserRole.TEACHER.value,
                    is_active=True
                )
                db.session.add(teacher_user)
                db.session.flush()
                
                teacher = Teacher(
                    user_id=teacher_user.id,
                    employee_id='EMP001',
                    specialization='Computer Science',
                    phone='555-0001'
                )
                db.session.add(teacher)
                print("      - Teacher user created: teacher@test.com")
                
                # Create student user
                student_user = User(
                    email='student@test.com',
                    password_hash=hash_password('Student123!'),
                    first_name='John',
                    last_name='Doe',
                    role=UserRole.STUDENT.value,
                    is_active=True
                )
                db.session.add(student_user)
                db.session.flush()
                
                student = Student(
                    user_id=student_user.id,
                    roll_number='STU001',
                    phone='555-0002'
                )
                db.session.add(student)
                print("      - Student user created: student@test.com")
                
                db.session.commit()
                print("\n      Seed data committed to database!")
            else:
                print(f"      Found {existing_users} existing user(s). Skipping seed data.")
            
            print("\n[4/4] Database Setup Summary")
            print("=" * 60)
            
            # Show statistics
            user_count = User.query.count()
            student_count = Student.query.count()
            teacher_count = Teacher.query.count()
            course_count = Course.query.count()
            
            print(f"  Users:      {user_count}")
            print(f"  Students:   {student_count}")
            print(f"  Teachers:   {teacher_count}")
            print(f"  Courses:    {course_count}")
            
            print("\n" + "=" * 60)
            print("Database setup completed successfully!")
            print("=" * 60)
            
            if existing_users == 0:
                print("\nDefault Test Credentials:")
                print("  Admin:    admin@test.com / Admin123!")
                print("  Teacher:  teacher@test.com / Teacher123!")
                print("  Student:  student@test.com / Student123!")
            
            print("\nNext steps:")
            print("  1. Run: python app.py")
            print("  2. Open: http://localhost:5000")
            print("  3. Login with any of the test credentials above")
            print("\n")
            
            return True
            
    except Exception as e:
        print(f"\nError during database setup: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = setup_database()
    sys.exit(0 if success else 1)
