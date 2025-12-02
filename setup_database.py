"""
StudentTrackerDB - Database Setup with Sample Data
Run this script to create tables and populate with realistic data
"""

#import pyodbc
from datetime import datetime, timedelta
import random

# MySQL Connection Configuration (Change these to your actual credentials)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'StudentTrackerDB'
}

def get_connection():
    """Create MySQL connection"""
    import mysql.connector
    return mysql.connector.connect(**DB_CONFIG)

def create_tables():
    """Create all database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("Creating tables...")
        
        # Drop existing tables
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        tables = ['Attendance', 'Enrollments', 'Courses', 'Teachers', 'Students', 'Users']
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        # Create Users table
        cursor.execute("""
        CREATE TABLE Users (
            id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            role ENUM('admin', 'teacher', 'student') NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            INDEX idx_email (email),
            INDEX idx_role (role)
        );
        """)
        
        # Create Students table
        cursor.execute("""
        CREATE TABLE Students (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) UNIQUE NOT NULL,
            roll_number VARCHAR(50) UNIQUE NOT NULL,
            department VARCHAR(100),
            semester INT CHECK (semester BETWEEN 1 AND 8),
            year_of_admission INT,
            phone_number VARCHAR(20),
            address VARCHAR(500),
            date_of_birth DATE,
            guardian_name VARCHAR(200),
            guardian_phone VARCHAR(20),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
            INDEX idx_roll_number (roll_number),
            INDEX idx_department (department)
        );
        """)
        
        # Create Teachers table
        cursor.execute("""
        CREATE TABLE Teachers (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) UNIQUE NOT NULL,
            employee_id VARCHAR(50) UNIQUE NOT NULL,
            department VARCHAR(100),
            designation VARCHAR(100),
            qualification VARCHAR(200),
            phone_number VARCHAR(20),
            office_location VARCHAR(200),
            specialization VARCHAR(500),
            years_of_experience INT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
            INDEX idx_employee_id (employee_id)
        );
        """)
        
        # Create Courses table
        cursor.execute("""
        CREATE TABLE Courses (
            id VARCHAR(36) PRIMARY KEY,
            course_code VARCHAR(20) UNIQUE NOT NULL,
            course_name VARCHAR(200) NOT NULL,
            description TEXT,
            teacher_id VARCHAR(36) NOT NULL,
            credits INT DEFAULT 3 CHECK (credits BETWEEN 1 AND 6),
            semester VARCHAR(20),
            department VARCHAR(100),
            max_students INT DEFAULT 50,
            schedule_days VARCHAR(100),
            schedule_time VARCHAR(100),
            classroom VARCHAR(50),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES Teachers(id),
            INDEX idx_course_code (course_code)
        );
        """)
        
        # Create Enrollments table
        cursor.execute("""
        CREATE TABLE Enrollments (
            id VARCHAR(36) PRIMARY KEY,
            student_id VARCHAR(36) NOT NULL,
            course_id VARCHAR(36) NOT NULL,
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            grade VARCHAR(5) NULL,
            status ENUM('active', 'completed', 'dropped', 'failed') DEFAULT 'active',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Students(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES Courses(id) ON DELETE CASCADE,
            UNIQUE KEY unique_enrollment (student_id, course_id)
        );
        """)
        
        # Create Attendance table
        cursor.execute("""
        CREATE TABLE Attendance (
            id VARCHAR(36) PRIMARY KEY,
            student_id VARCHAR(36) NOT NULL,
            course_id VARCHAR(36) NOT NULL,
            attendance_date DATE NOT NULL,
            status ENUM('present', 'absent', 'late', 'excused') NOT NULL,
            marked_by VARCHAR(36) NOT NULL,
            remarks VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Students(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES Courses(id) ON DELETE CASCADE,
            FOREIGN KEY (marked_by) REFERENCES Teachers(id),
            UNIQUE KEY unique_attendance (student_id, course_id, attendance_date),
            INDEX idx_date (attendance_date)
        );
        """)
        
        conn.commit()
        print("✓ Tables created successfully!")
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def generate_uuid():
    """Generate a simple UUID"""
    import uuid
    return str(uuid.uuid4())

def insert_sample_data():
    """Insert realistic sample data"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("\nInserting sample data...")
        
        # Password hash for "password123" (in production, use bcrypt)
        password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYo/PlT3ZP8oTXvIQQvzfPxEsJQKqGrS"
        
        # Insert Admin User
        admin_id = generate_uuid()
        cursor.execute("""
        INSERT INTO Users (id, email, password_hash, first_name, last_name, role)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (admin_id, 'admin@studenttracker.com', password_hash, 'System', 'Administrator', 'admin'))
        
        # Insert Teachers
        teachers_data = [
            ('Dr. Sarah Johnson', 'sarah.johnson@college.edu', 'T001', 'Computer Science', 'Professor', 'Ph.D. in Computer Science', '555-0101', 'CS-301', 'Artificial Intelligence, Machine Learning', 15),
            ('Dr. Michael Chen', 'michael.chen@college.edu', 'T002', 'Computer Science', 'Associate Professor', 'Ph.D. in Software Engineering', '555-0102', 'CS-302', 'Software Engineering, Databases', 12),
            ('Prof. Emily Davis', 'emily.davis@college.edu', 'T003', 'Mathematics', 'Professor', 'Ph.D. in Mathematics', '555-0103', 'MATH-201', 'Applied Mathematics, Statistics', 18),
            ('Dr. Robert Williams', 'robert.williams@college.edu', 'T004', 'Physics', 'Assistant Professor', 'Ph.D. in Physics', '555-0104', 'PHY-101', 'Quantum Physics, Thermodynamics', 8),
            ('Dr. Amanda Martinez', 'amanda.martinez@college.edu', 'T005', 'Computer Science', 'Associate Professor', 'Ph.D. in Data Science', '555-0105', 'CS-303', 'Data Science, Analytics', 10),
        ]
        
        teacher_ids = []
        for name, email, emp_id, dept, designation, qualification, phone, office, specialization, experience in teachers_data:
            user_id = generate_uuid()
            teacher_id = generate_uuid()
            first_name, last_name = name.replace('Dr. ', '').replace('Prof. ', '').rsplit(' ', 1)
            
            cursor.execute("""
            INSERT INTO Users (id, email, password_hash, first_name, last_name, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, email, password_hash, first_name, last_name, 'teacher'))
            
            cursor.execute("""
            INSERT INTO Teachers (id, user_id, employee_id, department, designation, qualification, 
                                phone_number, office_location, specialization, years_of_experience)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (teacher_id, user_id, emp_id, dept, designation, qualification, phone, office, specialization, experience))
            
            teacher_ids.append({'id': teacher_id, 'name': name, 'dept': dept})
        
        print(f"✓ Inserted {len(teachers_data)} teachers")
        
        # Insert Students
        students_data = [
            ('John Smith', 'john.smith@student.edu', 'CS2021001', 'Computer Science', 6, 2021, '555-1001', '123 Oak St', '2003-05-15', 'James Smith', '555-2001'),
            ('Emma Wilson', 'emma.wilson@student.edu', 'CS2021002', 'Computer Science', 6, 2021, '555-1002', '456 Pine Ave', '2003-07-22', 'Mary Wilson', '555-2002'),
            ('Michael Brown', 'michael.brown@student.edu', 'CS2022001', 'Computer Science', 4, 2022, '555-1003', '789 Elm St', '2004-03-10', 'David Brown', '555-2003'),
            ('Sophia Davis', 'sophia.davis@student.edu', 'CS2022002', 'Computer Science', 4, 2022, '555-1004', '321 Maple Dr', '2004-09-18', 'Linda Davis', '555-2004'),
            ('James Martinez', 'james.martinez@student.edu', 'CS2023001', 'Computer Science', 2, 2023, '555-1005', '654 Cedar Ln', '2005-01-25', 'Carlos Martinez', '555-2005'),
            ('Olivia Anderson', 'olivia.anderson@student.edu', 'CS2023002', 'Computer Science', 2, 2023, '555-1006', '987 Birch Rd', '2005-06-30', 'Patricia Anderson', '555-2006'),
            ('William Taylor', 'william.taylor@student.edu', 'MATH2022001', 'Mathematics', 4, 2022, '555-1007', '147 Spruce St', '2004-04-12', 'Robert Taylor', '555-2007'),
            ('Ava Thomas', 'ava.thomas@student.edu', 'MATH2023001', 'Mathematics', 2, 2023, '555-1008', '258 Willow Ave', '2005-08-20', 'Jennifer Thomas', '555-2008'),
            ('Ethan Jackson', 'ethan.jackson@student.edu', 'PHY2022001', 'Physics', 4, 2022, '555-1009', '369 Ash Blvd', '2004-11-05', 'Michael Jackson', '555-2009'),
            ('Isabella White', 'isabella.white@student.edu', 'CS2021003', 'Computer Science', 6, 2021, '555-1010', '741 Oak Park', '2003-02-28', 'Susan White', '555-2010'),
            ('Mason Harris', 'mason.harris@student.edu', 'CS2022003', 'Computer Science', 4, 2022, '555-1011', '852 Pine Court', '2004-12-14', 'Thomas Harris', '555-2011'),
            ('Charlotte Clark', 'charlotte.clark@student.edu', 'CS2023003', 'Computer Science', 2, 2023, '555-1012', '963 Elm Place', '2005-05-09', 'Nancy Clark', '555-2012'),
            ('Liam Lewis', 'liam.lewis@student.edu', 'MATH2023002', 'Mathematics', 2, 2023, '555-1013', '159 Maple Lane', '2005-10-17', 'Richard Lewis', '555-2013'),
            ('Amelia Walker', 'amelia.walker@student.edu', 'CS2021004', 'Computer Science', 6, 2021, '555-1014', '357 Cedar Ave', '2003-09-23', 'Elizabeth Walker', '555-2014'),
            ('Noah Robinson', 'noah.robinson@student.edu', 'PHY2023001', 'Physics', 2, 2023, '555-1015', '486 Birch St', '2005-03-07', 'William Robinson', '555-2015'),
        ]
        
        student_ids = []
        for name, email, roll, dept, sem, year, phone, address, dob, guardian, g_phone in students_data:
            user_id = generate_uuid()
            student_id = generate_uuid()
            first_name, last_name = name.split(' ', 1)
            
            cursor.execute("""
            INSERT INTO Users (id, email, password_hash, first_name, last_name, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, email, password_hash, first_name, last_name, 'student'))
            
            cursor.execute("""
            INSERT INTO Students (id, user_id, roll_number, department, semester, year_of_admission,
                                phone_number, address, date_of_birth, guardian_name, guardian_phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (student_id, user_id, roll, dept, sem, year, phone, address, dob, guardian, g_phone))
            
            student_ids.append({'id': student_id, 'name': name, 'dept': dept, 'sem': sem})
        
        print(f"✓ Inserted {len(students_data)} students")
        
        # Insert Courses
        courses_data = [
            ('CS101', 'Introduction to Programming', 'Fundamentals of programming using Python', 'Computer Science', 1, 4, 'Mon, Wed, Fri', '10:00-11:00 AM', 'CS-Lab-1'),
            ('CS201', 'Data Structures and Algorithms', 'Study of data structures and algorithm design', 'Computer Science', 2, 4, 'Tue, Thu', '09:00-10:30 AM', 'CS-201'),
            ('CS301', 'Database Management Systems', 'Design and implementation of databases', 'Computer Science', 3, 4, 'Mon, Wed', '02:00-03:30 PM', 'CS-301'),
            ('CS401', 'Artificial Intelligence', 'Introduction to AI concepts and applications', 'Computer Science', 4, 4, 'Tue, Thu', '11:00 AM-12:30 PM', 'CS-401'),
            ('CS402', 'Machine Learning', 'Supervised and unsupervised learning algorithms', 'Computer Science', 4, 3, 'Wed, Fri', '01:00-02:15 PM', 'CS-Lab-2'),
            ('MATH201', 'Linear Algebra', 'Vectors, matrices, and linear transformations', 'Mathematics', 2, 3, 'Mon, Wed, Fri', '09:00-10:00 AM', 'MATH-201'),
            ('MATH301', 'Probability and Statistics', 'Probability theory and statistical methods', 'Mathematics', 3, 4, 'Tue, Thu', '02:00-03:30 PM', 'MATH-301'),
            ('PHY101', 'Physics I', 'Mechanics and thermodynamics', 'Physics', 1, 4, 'Mon, Wed', '11:00 AM-12:30 PM', 'PHY-101'),
            ('PHY201', 'Quantum Mechanics', 'Introduction to quantum physics', 'Physics', 2, 3, 'Tue, Thu', '03:00-04:15 PM', 'PHY-201'),
            ('CS501', 'Software Engineering', 'Software development methodologies', 'Computer Science', 5, 3, 'Mon, Fri', '10:00-11:15 AM', 'CS-501'),
        ]
        
        course_ids = []
        for code, name, desc, dept, sem, credits, days, time, classroom in courses_data:
            course_id = generate_uuid()
            # Assign teacher based on department
            teacher = next((t for t in teacher_ids if t['dept'] == dept), teacher_ids[0])
            
            cursor.execute("""
            INSERT INTO Courses (id, course_code, course_name, description, teacher_id, credits,
                               semester, department, schedule_days, schedule_time, classroom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (course_id, code, name, desc, teacher['id'], credits, str(sem), dept, days, time, classroom))
            
            course_ids.append({'id': course_id, 'code': code, 'dept': dept, 'sem': sem})
        
        print(f"✓ Inserted {len(courses_data)} courses")
        
        # Insert Enrollments
        enrollment_count = 0
        for student in student_ids:
            # Enroll students in courses matching their department and semester
            relevant_courses = [c for c in course_ids if c['dept'] == student['dept'] and c['sem'] <= student['sem']]
            
            for course in relevant_courses[:min(5, len(relevant_courses))]:  # Enroll in up to 5 courses
                enrollment_id = generate_uuid()
                cursor.execute("""
                INSERT INTO Enrollments (id, student_id, course_id, status)
                VALUES (%s, %s, %s, %s)
                """, (enrollment_id, student['id'], course['id'], 'active'))
                enrollment_count += 1
        
        print(f"✓ Inserted {enrollment_count} enrollments")
        
        # Insert Attendance Records (last 30 days)
        attendance_count = 0
        today = datetime.now()
        
        cursor.execute("SELECT id, student_id, course_id FROM Enrollments WHERE is_active = TRUE")
        enrollments = cursor.fetchall()
        
        for enrollment_id, student_id, course_id in enrollments:
            # Get teacher for this course
            cursor.execute("SELECT teacher_id FROM Courses WHERE id = %s", (course_id,))
            teacher_id = cursor.fetchone()[0]
            
            # Generate attendance for last 30 days (skip weekends)
            for day_offset in range(30):
                date = today - timedelta(days=day_offset)
                # Skip weekends
                if date.weekday() < 5:  # Monday = 0, Friday = 4
                    attendance_id = generate_uuid()
                    # 85% present, 10% absent, 5% late
                    rand = random.random()
                    if rand < 0.85:
                        status = 'present'
                    elif rand < 0.95:
                        status = 'absent'
                    else:
                        status = 'late'
                    
                    cursor.execute("""
                    INSERT INTO Attendance (id, student_id, course_id, attendance_date, status, marked_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """, (attendance_id, student_id, course_id, date.date(), status, teacher_id))
                    attendance_count += 1
        
        print(f"✓ Inserted {attendance_count} attendance records")
        
        conn.commit()
        print("\n✓ All sample data inserted successfully!")
        print("\n" + "="*60)
        print("LOGIN CREDENTIALS (password for all: password123)")
        print("="*60)
        print("Admin:    admin@studenttracker.com")
        print("Teacher:  sarah.johnson@college.edu")
        print("Student:  john.smith@student.edu")
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error inserting data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("="*60)
    print("StudentTrackerDB - Database Setup Script")
    print("="*60)
    
    create_tables()
    insert_sample_data()
    
    print("\n✓ Database setup complete!")
    print("\nYou can now start your Flask application.")