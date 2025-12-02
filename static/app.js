/**
 * StudentTracker Main Application
 */

document.addEventListener('DOMContentLoaded', function () {
    initializeApp();
});

// ==================== Initialization ====================

async function initializeApp() {
    console.log('App initializing...');
    console.log('Is authenticated?', isAuthenticated());
    console.log('Current user:', api.currentUser);
    console.log('Access token:', api.accessToken);
    
    if (isAuthenticated()) {
        console.log('Showing dashboard');
        showDashboard();
    } else {
        console.log('Showing auth section');
        showAuthSection();
    }
    closeModal();
}

function showAuthSection() {
    document.getElementById('auth-section').classList.add('active');
    document.getElementById('dashboard-section').classList.remove('active');

    document.getElementById('modal-backdrop').classList.add('hidden');
    document.getElementById('modal-container').classList.add('hidden');
}

async function showDashboard() {
    document.getElementById('auth-section').classList.remove('active');
    document.getElementById('dashboard-section').classList.add('active');

    // Update navigation based on role
    updateNavigation();

    // Load dashboard
    loadDashboard();
}

function updateNavigation() {
    const adminBtn = document.getElementById('nav-admin');
    const attendanceBtn = document.getElementById('nav-attendance');
    const studentsBtn = document.getElementById('nav-students');
    const teachersBtn = document.getElementById('nav-teachers');

    // Hide all role-specific buttons
    [adminBtn, attendanceBtn, studentsBtn, teachersBtn].forEach(btn => {
        if (btn) btn.classList.add('hidden');
    });

    // Show based on role
    if (hasRole('admin')) {
        if (adminBtn) adminBtn.classList.remove('hidden');
        if (studentsBtn) studentsBtn.classList.remove('hidden');
        if (teachersBtn) teachersBtn.classList.remove('hidden');
    } else if (hasRole('teacher')) {
        if (attendanceBtn) attendanceBtn.classList.remove('hidden');
    }
}

// ==================== Authentication ====================

async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');

    try {
        const response = await api.login(email, password);

        if (response.success) {
            const { user, tokens } = response.data;
            api.setAuth(tokens.access_token, tokens.refresh_token, user);
            showToast('Login successful!');
            showDashboard();
        } else {
            errorDiv.textContent = response.message || 'Login failed';
        }
    } catch (error) {
        errorDiv.textContent = 'An error occurred during login';
        console.error(error);
    }
}

function updateRegisterFields() {
    const role = document.getElementById('register-role').value;
    const fieldsDiv = document.getElementById('register-role-fields');
    fieldsDiv.innerHTML = '';

    if (role === 'student') {
        fieldsDiv.innerHTML = `
            <div class="form-group">
                <label for="register-roll-number">Roll Number</label>
                <input type="text" id="register-roll-number" required>
            </div>
        `;
    } else if (role === 'teacher') {
        fieldsDiv.innerHTML = `
            <div class="form-group">
                <label for="register-employee-id">Employee ID</label>
                <input type="text" id="register-employee-id" required>
            </div>
            <div class="form-group">
                <label for="register-specialization">Specialization</label>
                <input type="text" id="register-specialization">
            </div>
        `;
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const email = document.getElementById('register-email').value;
    const firstName = document.getElementById('register-first-name').value;
    const lastName = document.getElementById('register-last-name').value;
    const password = document.getElementById('register-password').value;
    const role = document.getElementById('register-role').value;
    const errorDiv = document.getElementById('register-error');

    const data = {
        email,
        first_name: firstName,
        last_name: lastName,
        password,
        role
    };

    if (role === 'student') {
        data.roll_number = document.getElementById('register-roll-number').value;
    } else if (role === 'teacher') {
        data.employee_id = document.getElementById('register-employee-id').value;
        data.specialization = document.getElementById('register-specialization').value;
    }

    try {
        const response = await api.register(data);

        if (response.success) {
            const { user, tokens } = response.data;
            api.setAuth(tokens.access_token, tokens.refresh_token, user);
            showToast('Registration successful!');
            showDashboard();
        } else {
            errorDiv.textContent = response.message || 'Registration failed';
        }
    } catch (error) {
        errorDiv.textContent = 'An error occurred during registration';
        console.error(error);
    }
}

async function handleLogout() {
    api.clearAuth();
    document.getElementById('dashboard-section').classList.remove('active');
    showAuthSection();
    showToast('Logged out successfully');
}

// ==================== Tab Switching ====================

function switchTab(tabName) {
    // Hide all forms
    document.querySelectorAll('.auth-form').forEach(form => {
        form.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.auth-tabs .tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected form
    if (tabName === 'login') {
        document.getElementById('login-form').classList.add('active');
    } else if (tabName === 'register') {
        document.getElementById('register-form').classList.add('active');
    }

    // Add active class to clicked button
    event.target.classList.add('active');
}

function switchAdminTab(tabName) {
    // Hide all panels
    document.querySelectorAll('.admin-panel').forEach(panel => {
        panel.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.admin-tabs .tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected panel
    document.getElementById(tabName).classList.add('active');

    // Add active class to clicked button
    event.target.classList.add('active');
}

// ==================== Section Navigation ====================

function showSection(sectionName) {
    // Hide all content sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });

    // Show selected section
    const section = document.getElementById(sectionName + '-view');
    if (section) {
        section.classList.add('active');

        // Load section-specific data
        if (sectionName === 'admin') {
            loadUsers();
        } else if (sectionName === 'courses') {
            loadCourses();
        } else if (sectionName === 'attendance') {
            loadTeacherCourses();
        } else if (sectionName === 'students') {
            loadStudents();
        } else if (sectionName === 'teachers') {
            loadTeachers();
        } else if (sectionName === 'profile') {
            loadProfile();
        }
    }
}

// ==================== Dashboard ====================

async function loadDashboard() {
    const greeting = document.getElementById('user-greeting');
    const statsGrid = document.getElementById('dashboard-stats');

    greeting.innerHTML = `Welcome back, <strong>${getUserName()}</strong>!`;

    if (hasRole('admin')) {
        const response = await api.getDashboard();
        if (response && response.success) {
            const stats = response.data;
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <h3>Total Users</h3>
                    <div class="stat-value">${stats.total_users}</div>
                </div>
                <div class="stat-card">
                    <h3>Active Students</h3>
                    <div class="stat-value">${stats.total_students}</div>
                </div>
                <div class="stat-card">
                    <h3>Active Teachers</h3>
                    <div class="stat-value">${stats.total_teachers}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Courses</h3>
                    <div class="stat-value">${stats.total_courses}</div>
                </div>
            `;
        }
    } else {
        statsGrid.innerHTML = '<p>Select a section from the menu to get started.</p>';
    }
}

// ==================== Profile ====================

async function loadProfile() {
    const profileInfo = document.getElementById('profile-info');
    const user = api.currentUser;

    let html = `
        <div class="profile-info">
            <label>Full Name</label>
            <p>${user.first_name} ${user.last_name}</p>
        </div>
        <div class="profile-info">
            <label>Email</label>
            <p>${user.email}</p>
        </div>
        <div class="profile-info">
            <label>Role</label>
            <p>${user.role.toUpperCase()}</p>
        </div>
    `;

    if (user.student) {
        html += `
            <div class="profile-info">
                <label>Roll Number</label>
                <p>${user.student.roll_number}</p>
            </div>
            <div class="profile-info">
                <label>Enrollment Date</label>
                <p>${formatDate(user.student.enrollment_date)}</p>
            </div>
        `;
    }

    if (user.teacher) {
        html += `
            <div class="profile-info">
                <label>Employee ID</label>
                <p>${user.teacher.employee_id}</p>
            </div>
            <div class="profile-info">
                <label>Specialization</label>
                <p>${user.teacher.specialization || 'N/A'}</p>
            </div>
        `;
    }

    profileInfo.innerHTML = html;
}

// ==================== Admin Users ====================

async function loadUsers(page = 1) {
    const response = await api.listUsers(page);
    const table = document.getElementById('users-table');

    if (response && response.success) {
        const users = response.data.users;
        table.innerHTML = users.map(user => `
            <tr>
                <td>${user.email}</td>
                <td>${user.first_name} ${user.last_name}</td>
                <td>${user.role}</td>
                <td><span class="status ${user.is_active ? 'active' : 'inactive'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-warning" onclick="showUserEditModal('${user.id}')">Edit</button>
                        <button class="btn btn-danger" onclick="deleteUserConfirm('${user.id}')">Delete</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
}

function searchUsers() {
    const search = document.getElementById('user-search').value.toLowerCase();
    // Implement search logic
}

async function deleteUserConfirm(userId) {
    if (confirm('Are you sure you want to deactivate this user?')) {
        const response = await api.deleteUser(userId);
        if (response && response.success) {
            showToast('User deactivated successfully');
            loadUsers();
        }
    }
}

function showUserModal() {
    const modalBody = document.getElementById('modal-body');
    modalBody.innerHTML = `
        <h2>Add New User</h2>
        <div class="form-group">
            <label for="modal-email">Email</label>
            <input type="email" id="modal-email" required>
        </div>
        <div class="form-group">
            <label for="modal-first-name">First Name</label>
            <input type="text" id="modal-first-name" required>
        </div>
        <div class="form-group">
            <label for="modal-last-name">Last Name</label>
            <input type="text" id="modal-last-name" required>
        </div>
        <div class="form-group">
            <label for="modal-password">Password</label>
            <input type="password" id="modal-password" required>
        </div>
        <div class="form-group">
            <label for="modal-role">Role</label>
            <select id="modal-role" required>
                <option value="">Select Role</option>
                <option value="admin">Admin</option>
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="saveNewUser()">Save</button>
    `;

    openModal();
}

async function saveNewUser() {
    const data = {
        email: document.getElementById('modal-email').value,
        first_name: document.getElementById('modal-first-name').value,
        last_name: document.getElementById('modal-last-name').value,
        password: document.getElementById('modal-password').value,
        role: document.getElementById('modal-role').value,
    };

    const response = await api.register(data);
    if (response && response.success) {
        showToast('User created successfully');
        closeModal();
        loadUsers();
    } else {
        showToast(response?.message || 'Error creating user', 'error');
    }
}

function showUserEditModal(userId) {
    // Implement edit modal
}

// ==================== Admin Students ====================

async function loadStudents(page = 1) {
    const response = await api.listStudents(page);
    const table = document.getElementById('students-table');

    if (response && response.success) {
        const students = response.data.students;
        table.innerHTML = students.map(student => `
            <tr>
                <td>${student.roll_number}</td>
                <td>${student.first_name} ${student.last_name}</td>
                <td>${student.email}</td>
                <td>${student.phone || 'N/A'}</td>
                <td><span class="status ${student.is_active ? 'active' : 'inactive'}">${student.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-warning" onclick="editStudent('${student.id}')">Edit</button>
                        <button class="btn btn-danger" onclick="deleteStudent('${student.id}')">Delete</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
}

function searchStudents() {
    // Implement search
}

function showStudentModal() {
    // Implement student creation modal
}

async function deleteStudent(studentId) {
    if (confirm('Delete this student?')) {
        const response = await api.deleteStudent(studentId);
        if (response && response.success) {
            showToast('Student deleted');
            loadStudents();
        }
    }
}

function editStudent(studentId) {
    // Implement edit
}

// ==================== Admin Teachers ====================

async function loadTeachers(page = 1) {
    const response = await api.listTeachers(page);
    const table = document.getElementById('teachers-table');

    if (response && response.success) {
        const teachers = response.data.teachers;
        table.innerHTML = teachers.map(teacher => `
            <tr>
                <td>${teacher.employee_id}</td>
                <td>${teacher.first_name} ${teacher.last_name}</td>
                <td>${teacher.email}</td>
                <td>${teacher.specialization || 'N/A'}</td>
                <td><span class="status ${teacher.is_active ? 'active' : 'inactive'}">${teacher.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-warning" onclick="editTeacher('${teacher.id}')">Edit</button>
                        <button class="btn btn-danger" onclick="deleteTeacher('${teacher.id}')">Delete</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
}

function searchTeachers() {
    // Implement search
}

function showTeacherModal() {
    // Implement teacher creation modal
}

async function deleteTeacher(teacherId) {
    if (confirm('Delete this teacher?')) {
        const response = await api.deleteTeacher(teacherId);
        if (response && response.success) {
            showToast('Teacher deleted');
            loadTeachers();
        }
    }
}

function editTeacher(teacherId) {
    // Implement edit
}

// ==================== Courses ====================

async function loadCourses(page = 1) {
    let teacherId = null;
    if (hasRole('teacher')) {
        const teacher = api.currentUser.teacher;
        if (teacher) teacherId = teacher.id;
    }

    const response = await api.listCourses(page, 20, teacherId);
    const coursesGrid = document.getElementById('courses-grid');

    if (response && response.success) {
        const courses = response.data.courses;
        coursesGrid.innerHTML = courses.map(course => `
            <div class="course-card">
                <div class="course-card-header">
                    <h3>${course.course_name}</h3>
                    <div class="course-code">${course.course_code}</div>
                </div>
                <div class="course-card-body">
                    <div class="course-info">
                        <label>Instructor</label>
                        <p>${course.teacher_name}</p>
                    </div>
                    <div class="course-info">
                        <label>Credits</label>
                        <p>${course.credits}</p>
                    </div>
                    <div class="course-info">
                        <label>Enrolled Students</label>
                        <p>${course.enrolled_students} / ${course.max_students}</p>
                    </div>
                    <div class="course-info">
                        <label>Semester</label>
                        <p>${course.semester || 'N/A'}</p>
                    </div>
                </div>
                <div class="course-card-footer">
                    ${hasRole('student') ? `
                        <button class="btn btn-primary" onclick="enrollInCourse('${course.id}')">Enroll</button>
                    ` : hasRole('teacher') ? `
                        <button class="btn btn-warning" onclick="editCourse('${course.id}')">Edit</button>
                        <button class="btn btn-danger" onclick="deleteCourse('${course.id}')">Delete</button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }
}

function searchCourses() {
    // Implement search
}

async function enrollInCourse(courseId) {
    const response = await api.enrollInCourse(courseId);
    if (response && response.success) {
        showToast('Enrolled successfully');
        loadCourses();
    } else {
        showToast(response?.message || 'Enrollment failed', 'error');
    }
}

async function deleteCourse(courseId) {
    if (confirm('Delete this course?')) {
        const response = await api.deleteCourse(courseId);
        if (response && response.success) {
            showToast('Course deleted');
            loadCourses();
        }
    }
}

function showCourseModal() {
    // Implement course creation modal
}

function editCourse(courseId) {
    // Implement edit
}

// ==================== Attendance ====================

async function loadTeacherCourses() {
    const teacher = api.currentUser.teacher;
    if (!teacher) return;

    const response = await api.listCourses(1, 100, teacher.id);
    const select = document.getElementById('attendance-course');

    if (response && response.success) {
        const courses = response.data.courses;
        select.innerHTML = '<option value="">-- Select Course --</option>' +
            courses.map(course => `
                <option value="${course.id}">${course.course_name}</option>
            `).join('');
    }
}

async function loadCourseAttendance() {
    const courseId = document.getElementById('attendance-course').value;
    if (!courseId) return;

    const response = await api.getAttendanceSummary(courseId);
    const summary = document.getElementById('attendance-summary');

    if (response && response.success) {
        const records = response.data;
        summary.innerHTML = `
            <h3>Attendance Summary</h3>
            <table class="attendance-summary">
                <thead>
                    <tr>
                        <th>Roll Number</th>
                        <th>Student Name</th>
                        <th>Present</th>
                        <th>Absent</th>
                        <th>Late</th>
                        <th>Total Classes</th>
                        <th>Attendance %</th>
                    </tr>
                </thead>
                <tbody>
                    ${records.map(record => `
                        <tr>
                            <td>${record.roll_number}</td>
                            <td>${record.student_name}</td>
                            <td>${record.present}</td>
                            <td>${record.absent}</td>
                            <td>${record.late}</td>
                            <td>${record.total_classes}</td>
                            <td><span class="percentage ${record.attendance_percentage < 75 ? 'low' : ''}">${record.attendance_percentage}%</span></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
}

function showAttendanceForm() {
    const courseId = document.getElementById('attendance-course').value;
    if (!courseId) {
        showToast('Please select a course', 'warning');
        return;
    }

    const modalBody = document.getElementById('modal-body');
    modalBody.innerHTML = `
        <h2>Mark Attendance</h2>
        <div id="attendance-form"></div>
        <button class="btn btn-primary" onclick="submitAttendance()">Submit</button>
    `;

    openModal();
    loadAttendanceForm(courseId);
}

async function loadAttendanceForm(courseId) {
    const response = await api.getCourse(courseId);
    const formDiv = document.getElementById('attendance-form');

    if (response && response.success) {
        const enrolledStudents = response.data.enrolled_students;
        formDiv.innerHTML = enrolledStudents.map((student, index) => `
            <div class="attendance-row">
                <input type="hidden" value="${student.student_id}" class="student-id-${index}">
                <span>${student.student_name}</span>
                <select class="status-${index}">
                    <option value="present">Present</option>
                    <option value="absent">Absent</option>
                    <option value="late">Late</option>
                </select>
                <input type="text" placeholder="Remarks" class="remarks-${index}">
            </div>
        `).join('');
    }
}

async function submitAttendance() {
    const courseId = document.getElementById('attendance-course').value;
    const attendanceRecords = [];

    // Collect all attendance records from the form
    const rows = document.querySelectorAll('.attendance-row');
    rows.forEach((row, index) => {
        const studentId = row.querySelector(`input[type="hidden"]`).value;
        const status = row.querySelector(`.status-${index}`).value;
        const remarks = row.querySelector(`.remarks-${index}`).value;

        attendanceRecords.push({
            student_id: studentId,
            status,
            remarks,
            attendance_date: new Date().toISOString()
        });
    });

    const response = await api.markAttendance({
        course_id: courseId,
        attendance_records: attendanceRecords
    });

    if (response && response.success) {
        showToast(`Attendance marked for ${response.data.marked_count} students`);
        closeModal();
        loadCourseAttendance();
    } else {
        showToast(response?.message || 'Error marking attendance', 'error');
    }
}

// ==================== Modal Utilities ====================

function openModal() {
    document.getElementById('modal-backdrop').classList.remove('hidden');
    document.getElementById('modal-container').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal-backdrop').classList.add('hidden');
    document.getElementById('modal-container').classList.add('hidden');
}
