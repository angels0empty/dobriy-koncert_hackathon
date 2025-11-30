const API_BASE_URL = 'http://64.188.78.85:8000/api/v1';

class API {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    getToken() {
        return localStorage.getItem('access_token');
    }

    setToken(token) {
        localStorage.setItem('access_token', token);
    }

    removeToken() {
        localStorage.removeItem('access_token');
    }

    isAuthenticated() {
        return !!this.getToken();
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Добавляем токен если есть
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);

            // Если 401 - токен невалиден, разлогиниваем
            if (response.status === 401) {
                this.removeToken();
                window.location.href = 'form.html';
                return null;
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Ошибка запроса');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async get(endpoint) {
        return this.request(endpoint, {
            method: 'GET'
        });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }

    // === AUTH ENDPOINTS ===

    async login(email, password) {
        const data = await this.post('/auth/login', { email, password });
        if (data && data.access_token) {
            this.setToken(data.access_token);
        }
        return data;
    }

    async register(email, password, full_name, role = 'teacher') {
        return this.post('/auth/register', { email, password, full_name, role });
    }

    async getCurrentUser() {
        return this.get('/auth/me');
    }

    // === COURSES ENDPOINTS ===

    async getCourses() {
        return this.get('/courses/');
    }

    async getCourse(courseId) {
        return this.get(`/courses/${courseId}`);
    }

    async createCourse(title, description) {
        return this.post('/courses/', { title, description });
    }

    async updateCourse(courseId, title, description) {
        return this.put(`/courses/${courseId}`, { title, description });
    }

    async deleteCourse(courseId) {
        return this.delete(`/courses/${courseId}`);
    }

    // === STUDENTS ENDPOINTS ===

    async getCourseStudents(courseId) {
        return this.get(`/courses/${courseId}/students`);
    }

    async addStudentByEmail(courseId, email) {
        return this.post(`/courses/${courseId}/students`, { email });
    }

    async removeStudent(courseId, studentId) {
        return this.delete(`/courses/${courseId}/students/${studentId}`);
    }

    async getAllStudents() {
        return this.get('/courses/all-students');
    }

    // === ASSIGNMENTS ENDPOINTS ===

    async getAssignments(courseId) {
        return this.get(`/assignments/courses/${courseId}/assignments`);
    }

    async createAssignment(courseId, data) {
        return this.post(`/assignments/courses/${courseId}/assignments`, data);
    }

    async updateAssignment(assignmentId, data) {
        return this.put(`/assignments/${assignmentId}`, data);
    }

    async deleteAssignment(assignmentId) {
        return this.delete(`/assignments/${assignmentId}`);
    }

    async getSubmissions(assignmentId) {
        return this.get(`/assignments/${assignmentId}/submissions`);
    }

    // === GRADING ENDPOINTS ===

    async gradeSubmission(submissionId, score, comment) {
        return this.post(`/grading/submissions/${submissionId}/grade`, { score, comment });
    }

    async updateGrade(gradeId, score, comment) {
        return this.put(`/grading/grades/${gradeId}`, { score, comment });
    }

    // === MATERIALS ENDPOINTS ===

    async getMaterials(courseId) {
        return this.get(`/materials/courses/${courseId}/materials`);
    }

    async createMaterial(courseId, data) {
        return this.post(`/materials/courses/${courseId}/materials`, data);
    }

    async updateMaterial(materialId, data) {
        return this.put(`/materials/${materialId}`, data);
    }

    async deleteMaterial(materialId) {
        return this.delete(`/materials/${materialId}`);
    }

    // === ANALYTICS ENDPOINTS ===

    async getCourseStats(courseId) {
        return this.get(`/analytics/courses/${courseId}/stats`);
    }

    async getStudentProgress(courseId) {
        return this.get(`/analytics/courses/${courseId}/student-progress`);
    }

    // === ADMIN ENDPOINTS ===

    async generateMockData(courseId, numRecords = 20) {
        return this.post(`/admin/mock-data/generate?course_id=${courseId}&num_records=${numRecords}`);
    }

    async getMockStats(courseId = null) {
        const url = courseId ? `/admin/mock-data/statistics?course_id=${courseId}` : '/admin/mock-data/statistics';
        return this.get(url);
    }
}

const api = new API();
