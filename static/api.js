/**
 * API Client for StudentTracker
 * Handles all API calls to the backend
 */

const API_BASE_URL = 'http://localhost:5000/api';

class APIClient {
    constructor() {
        this.accessToken = localStorage.getItem('accessToken');
        this.refreshToken = localStorage.getItem('refreshToken');
        this.currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;
    }

    /**
     * Set tokens and user data
     */
    setAuth(accessToken, refreshToken, user) {
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;
        this.currentUser = user;
        
        localStorage.setItem('accessToken', accessToken);
        localStorage.setItem('refreshToken', refreshToken);
        localStorage.setItem('currentUser', JSON.stringify(user));
    }

    /**
     * Clear authentication data
     */
    clearAuth() {
        this.accessToken = null;
        this.refreshToken = null;
        this.currentUser = null;
        
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('currentUser');
    }

    /**
     * Generic HTTP request method
     */
    async request(method, endpoint, data = null) {
        const url = `${API_BASE_URL}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (this.accessToken) {
            options.headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            
            // Handle token expiration
            if (response.status === 401) {
                showToast('Session expired. Please login again.', 'error');
                this.clearAuth();
                window.location.reload();
                return null;
            }

            const json = await response.json();
            
            if (!response.ok) {
                console.error('API Error:', json);
                return json;
            }

            return json;
        } catch (error) {
            console.error('Request failed:', error);
            showToast('Network error. Please try again.', 'error');
            return null;
        }
    }

    // ==================== Authentication ====================

    async login(email, password) {
        return this.request('POST', '/auth/login', { email, password });
    }

    async register(userData) {
        return this.request('POST', '/auth/register', userData);
    }

    async getCurrentUser() {
        return this.request('GET', '/auth/me');
    }

    async refreshAccessToken() {
        const response = await this.request('POST', '/auth/refresh', {});
        if (response && response.data) {
            this.setAuth(response.data.access_token, response.data.refresh_token, this.currentUser);
        }
        return response;
    }

    // ==================== Admin Endpoints ====================

    // Users
    async listUsers(page = 1, perPage = 20, role = null) {
        let url = `/admin/users?page=${page}&per_page=${perPage}`;
        if (role) url += `&role=${role}`;
        return this.request('GET', url);
    }

    async getUser(userId) {
        return this.request('GET', `/admin/users/${userId}`);
    }

    async updateUser(userId, userData) {
        return this.request('PUT', `/admin/users/${userId}`, userData);
    }

    async deleteUser(userId) {
        return this.request('DELETE', `/admin/users/${userId}`);
    }

    // Students
    async listStudents(page = 1, perPage = 20) {
        return this.request('GET', `/admin/students?page=${page}&per_page=${perPage}`);
    }

    async getStudent(studentId) {
        return this.request('GET', `/admin/students/${studentId}`);
    }

    async updateStudent(studentId, data) {
        return this.request('PUT', `/admin/students/${studentId}`, data);
    }

    async deleteStudent(studentId) {
        return this.request('DELETE', `/admin/students/${studentId}`);
    }

    // Teachers
    async listTeachers(page = 1, perPage = 20) {
        return this.request('GET', `/admin/teachers?page=${page}&per_page=${perPage}`);
    }

    async getTeacher(teacherId) {
        return this.request('GET', `/admin/teachers/${teacherId}`);
    }

    async updateTeacher(teacherId, data) {
        return this.request('PUT', `/admin/teachers/${teacherId}`, data);
    }

    async deleteTeacher(teacherId) {
        return this.request('DELETE', `/admin/teachers/${teacherId}`);
    }

    // Dashboard
    async getDashboard() {
        return this.request('GET', '/admin/dashboard');
    }

    // ==================== Courses ====================

    async listCourses(page = 1, perPage = 20, teacherId = null) {
        let url = `/courses?page=${page}&per_page=${perPage}`;
        if (teacherId) url += `&teacher_id=${teacherId}`;
        return this.request('GET', url);
    }

    async getCourse(courseId) {
        return this.request('GET', `/courses/${courseId}`);
    }

    async createCourse(data) {
        return this.request('POST', '/courses', data);
    }

    async updateCourse(courseId, data) {
        return this.request('PUT', `/courses/${courseId}`, data);
    }

    async deleteCourse(courseId) {
        return this.request('DELETE', `/courses/${courseId}`);
    }

    async enrollInCourse(courseId) {
        return this.request('POST', `/courses/${courseId}/enroll`, {});
    }

    async unenrollFromCourse(courseId) {
        return this.request('POST', `/courses/${courseId}/unenroll`, {});
    }

    // ==================== Attendance ====================

    async markAttendance(data) {
        return this.request('POST', '/attendance', data);
    }

    async getCourseAttendance(courseId, page = 1, perPage = 50, fromDate = null, toDate = null) {
        let url = `/attendance/course/${courseId}?page=${page}&per_page=${perPage}`;
        if (fromDate) url += `&from_date=${fromDate}`;
        if (toDate) url += `&to_date=${toDate}`;
        return this.request('GET', url);
    }

    async getStudentAttendance(studentId, page = 1, perPage = 50, courseId = null) {
        let url = `/attendance/student/${studentId}?page=${page}&per_page=${perPage}`;
        if (courseId) url += `&course_id=${courseId}`;
        return this.request('GET', url);
    }

    async updateAttendance(attendanceId, data) {
        return this.request('PUT', `/attendance/${attendanceId}`, data);
    }

    async deleteAttendance(attendanceId) {
        return this.request('DELETE', `/attendance/${attendanceId}`);
    }

    async getAttendanceSummary(courseId) {
        return this.request('GET', `/attendance/course/${courseId}/summary`);
    }
}

// Create global API client instance
const api = new APIClient();

/**
 * Utility function to show toast notifications
 */
function showToast(message, type = 'success', duration = 3000) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

/**
 * Format date to YYYY-MM-DD
 */
function formatDate(date) {
    if (typeof date === 'string') {
        return date.split('T')[0];
    }
    const d = new Date(date);
    return d.toISOString().split('T')[0];
}

/**
 * Format datetime
 */
function formatDateTime(datetime) {
    const d = new Date(datetime);
    return d.toLocaleString();
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return !!api.accessToken && !!api.currentUser;
}

/**
 * Check user role
 */
function hasRole(role) {
    if (!api.currentUser) return false;
    if (Array.isArray(role)) {
        return role.includes(api.currentUser.role);
    }
    return api.currentUser.role === role;
}

/**
 * Get user full name
 */
function getUserName() {
    if (!api.currentUser) return '';
    return `${api.currentUser.first_name} ${api.currentUser.last_name}`;
}
