if (!api.isAuthenticated()) {
    window.location.href = 'form.html';
}

// Получаем ID курса из URL
const urlParams = new URLSearchParams(window.location.search);
const courseId = urlParams.get('id');

if (!courseId) {
    alert('ID курса не указан');
    window.location.href = 'lkp.html';
}

let currentCourse = null;
let currentEditingMaterialId = null;
let currentEditingAssignmentId = null;

async function init() {
    try {
        currentCourse = await api.getCourse(courseId);
        document.getElementById('courseTitle').textContent = currentCourse.title;

        await loadMaterials();
        await loadAssignments();

        // Загружаем данные при переходе на вкладки
        document.querySelector('[data-tab="stats"]').addEventListener('click', loadStats);
        document.querySelector('[data-tab="students"]').addEventListener('click', loadStudents);
    } catch (error) {
        console.error('Ошибка загрузки курса:', error);
        alert('Не удалось загрузить курс');
        window.location.href = 'lkp.html';
    }
}

// === МАТЕРИАЛЫ ===

async function loadMaterials() {
    try {
        const materials = await api.getMaterials(courseId);
        renderMaterials(materials);
    } catch (error) {
        console.error('Ошибка загрузки материалов:', error);
    }
}

function renderMaterials(materials) {
    const list = document.getElementById('materials-list');

    if (!materials || materials.length === 0) {
        list.innerHTML = '<p style="padding: 20px; color: #666;">Материалов пока нет</p>';
        return;
    }

    list.innerHTML = materials.map(m => `
        <div class="material-item">
            <h3>${m.title}</h3>
            <p>${m.content || 'Нет описания'}</p>
            ${m.file_url ? `<p><a href="${m.file_url}" target="_blank">Открыть файл</a></p>` : ''}
            <div class="item-actions">
                <button onclick="editMaterial('${m.id}')">Редактировать</button>
                <button class="danger" onclick="deleteMaterial('${m.id}')">Удалить</button>
            </div>
        </div>
    `).join('');
}

function showAddMaterial() {
    currentEditingMaterialId = null;
    document.getElementById('materialModalTitle').textContent = 'Добавить материал';
    document.getElementById('materialForm').reset();
    document.getElementById('materialModal').classList.add('active');
}

async function editMaterial(materialId) {
    // Находим материал
    const materials = await api.getMaterials(courseId);
    const material = materials.find(m => m.id === materialId);

    if (!material) return;

    currentEditingMaterialId = materialId;
    document.getElementById('materialModalTitle').textContent = 'Редактировать материал';
    document.getElementById('materialTitle').value = material.title;
    document.getElementById('materialContent').value = material.content || '';
    document.getElementById('materialFileUrl').value = material.file_url || '';
    document.getElementById('materialOrder').value = material.order_number || 1;
    document.getElementById('materialModal').classList.add('active');
}

async function deleteMaterial(materialId) {
    if (!confirm('Удалить материал?')) return;

    try {
        await api.deleteMaterial(materialId);
        await loadMaterials();
    } catch (error) {
        alert('Ошибка удаления: ' + error.message);
    }
}

// Обработка формы материала
document.getElementById('materialForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const data = {
        title: document.getElementById('materialTitle').value,
        content: document.getElementById('materialContent').value,
        file_url: document.getElementById('materialFileUrl').value || null,
        order_number: parseInt(document.getElementById('materialOrder').value) || 1
    };

    try {
        if (currentEditingMaterialId) {
            await api.updateMaterial(currentEditingMaterialId, data);
        } else {
            await api.createMaterial(courseId, data);
        }

        closeModal('materialModal');
        await loadMaterials();
    } catch (error) {
        alert('Ошибка сохранения: ' + error.message);
    }
});

// === ЗАДАНИЯ ===

async function loadAssignments() {
    try {
        const assignments = await api.getAssignments(courseId);
        renderAssignments(assignments);
    } catch (error) {
        console.error('Ошибка загрузки заданий:', error);
    }
}

function renderAssignments(assignments) {
    const list = document.getElementById('assignments-list');

    if (!assignments || assignments.length === 0) {
        list.innerHTML = '<p style="padding: 20px; color: #666;">Заданий пока нет</p>';
        return;
    }

    list.innerHTML = assignments.map(a => {
        const deadline = a.deadline ? new Date(a.deadline).toLocaleString('ru-RU') : 'Не указан';
        return `
            <div class="assignment-item">
                <h3>${a.title}</h3>
                <p>${a.description || 'Нет описания'}</p>
                <p><strong>Макс. балл:</strong> ${a.max_score}</p>
                <p><strong>Дедлайн:</strong> ${deadline}</p>
                <div class="item-actions">
                    <button class="primary" onclick="viewSubmissions('${a.id}')">Проверить работы</button>
                    <button onclick="editAssignment('${a.id}')">Редактировать</button>
                    <button class="danger" onclick="deleteAssignment('${a.id}')">Удалить</button>
                </div>
            </div>
        `;
    }).join('');
}

function showAddAssignment() {
    currentEditingAssignmentId = null;
    document.getElementById('assignmentModalTitle').textContent = 'Добавить задание';
    document.getElementById('assignmentForm').reset();
    document.getElementById('assignmentModal').classList.add('active');
}

async function editAssignment(assignmentId) {
    const assignments = await api.getAssignments(courseId);
    const assignment = assignments.find(a => a.id === assignmentId);

    if (!assignment) return;

    currentEditingAssignmentId = assignmentId;
    document.getElementById('assignmentModalTitle').textContent = 'Редактировать задание';
    document.getElementById('assignmentTitle').value = assignment.title;
    document.getElementById('assignmentDescription').value = assignment.description || '';
    document.getElementById('assignmentMaxScore').value = assignment.max_score;

    if (assignment.deadline) {
        const dt = new Date(assignment.deadline);
        document.getElementById('assignmentDeadline').value = dt.toISOString().slice(0, 16);
    }

    document.getElementById('assignmentModal').classList.add('active');
}

async function deleteAssignment(assignmentId) {
    if (!confirm('Удалить задание?')) return;

    try {
        await api.deleteAssignment(assignmentId);
        await loadAssignments();
    } catch (error) {
        alert('Ошибка удаления: ' + error.message);
    }
}

// Обработка формы задания
document.getElementById('assignmentForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const deadlineValue = document.getElementById('assignmentDeadline').value;

    const data = {
        title: document.getElementById('assignmentTitle').value,
        description: document.getElementById('assignmentDescription').value,
        max_score: parseInt(document.getElementById('assignmentMaxScore').value),
        deadline: deadlineValue ? new Date(deadlineValue).toISOString() : null
    };

    try {
        if (currentEditingAssignmentId) {
            await api.updateAssignment(currentEditingAssignmentId, data);
        } else {
            await api.createAssignment(courseId, data);
        }

        closeModal('assignmentModal');
        await loadAssignments();
    } catch (error) {
        alert('Ошибка сохранения: ' + error.message);
    }
});

// === ПРОВЕРКА РАБОТ ===

async function viewSubmissions(assignmentId) {
    try {
        const submissions = await api.getSubmissions(assignmentId);
        renderSubmissions(submissions, assignmentId);
        document.getElementById('submissionsModal').classList.add('active');
    } catch (error) {
        alert('Ошибка загрузки работ: ' + error.message);
    }
}

function renderSubmissions(submissions, assignmentId) {
    const list = document.getElementById('submissions-list');

    if (!submissions || submissions.length === 0) {
        list.innerHTML = '<p style="padding: 20px;">Работ пока не сдано</p>';
        return;
    }

    list.innerHTML = submissions.map(s => {
        const hasGrade = s.grade !== null && s.grade !== undefined;

        return `
            <div class="submission-item">
                <h4>Студент: ${s.student_name}</h4>
                <p><strong>Статус:</strong> ${s.status}</p>
                <p><strong>Дата сдачи:</strong> ${new Date(s.submitted_at).toLocaleString('ru-RU')}</p>

                <div class="submission-content">
                    <strong>Ответ студента:</strong><br>
                    ${s.content || 'Нет текстового ответа'}
                    ${s.file_url ? `<br><br><a href="${s.file_url}" target="_blank">Открыть прикрепленный файл</a>` : ''}
                </div>

                ${hasGrade ? `
                    <div class="grade-display">
                        <strong>Оценка:</strong> ${s.grade}<br>
                        <strong>Комментарий:</strong> ${s.grade_comment || 'Нет комментария'}
                    </div>
                ` : ''}

                <div class="grading-form">
                    <input type="number" id="score_${s.id}" placeholder="Балл" value="${s.grade || ''}" min="0" required>
                    <textarea id="comment_${s.id}" placeholder="Комментарий преподавателя" rows="3">${s.grade_comment || ''}</textarea>
                    <button onclick="gradeSubmission('${s.id}', '${assignmentId}')">
                        ${hasGrade ? 'Обновить оценку' : 'Выставить оценку'}
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

async function gradeSubmission(submissionId, assignmentId) {
    const score = parseInt(document.getElementById(`score_${submissionId}`).value);
    const comment = document.getElementById(`comment_${submissionId}`).value;

    if (isNaN(score)) {
        alert('Введите балл');
        return;
    }

    try {
        await api.gradeSubmission(submissionId, score, comment);
        // Перезагружаем работы
        await viewSubmissions(assignmentId);
    } catch (error) {
        alert('Ошибка выставления оценки: ' + error.message);
    }
}

// === СТУДЕНТЫ ===

async function loadStudents() {
    try {
        const students = await api.getCourseStudents(courseId);
        renderStudents(students);
    } catch (error) {
        console.error('Ошибка загрузки студентов:', error);
    }
}

function renderStudents(students) {
    const list = document.getElementById('students-list');

    if (!students || students.length === 0) {
        list.innerHTML = '<p style="padding: 20px; color: #666;">Студентов пока нет</p>';
        return;
    }

    list.innerHTML = students.map(s => `
        <div class="material-item">
            <h3>${s.full_name}</h3>
            <p>Email: ${s.email}</p>
            <div class="item-actions">
                <button class="danger" onclick="removeStudent('${s.id}')">Удалить с курса</button>
            </div>
        </div>
    `).join('');
}

function showAddStudent() {
    document.getElementById('studentForm').reset();
    document.getElementById('studentModal').classList.add('active');
}

async function removeStudent(studentId) {
    if (!confirm('Удалить студента с курса?')) return;

    try {
        await api.removeStudent(courseId, studentId);
        await loadStudents();
    } catch (error) {
        alert('Ошибка удаления: ' + error.message);
    }
}

// Обработка формы добавления студента
document.getElementById('studentForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const email = document.getElementById('studentEmail').value;

    try {
        await api.addStudentByEmail(courseId, email);
        closeModal('studentModal');
        await loadStudents();
    } catch (error) {
        alert('Ошибка добавления студента: ' + error.message);
    }
});

// === СТАТИСТИКА ===

async function loadStats() {
    try {
        const stats = await api.getCourseStats(courseId);
        const progress = await api.getStudentProgress(courseId);
        renderStats(stats, progress);
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

function renderStats(stats, progress) {
    const content = document.getElementById('stats-content');

    content.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Студентов</h3>
                <div class="stat-value">${stats.students_count}</div>
            </div>
            <div class="stat-card">
                <h3>Заданий</h3>
                <div class="stat-value">${stats.assignments_count}</div>
            </div>
            <div class="stat-card">
                <h3>Сдано работ</h3>
                <div class="stat-value">${stats.total_submissions}</div>
            </div>
            <div class="stat-card">
                <h3>Средний балл</h3>
                <div class="stat-value">${stats.average_score}</div>
            </div>
        </div>

        <div class="students-table">
            <table>
                <thead>
                    <tr>
                        <th>Студент</th>
                        <th>Сдано работ</th>
                        <th>Проверено</th>
                        <th>Средний балл</th>
                        <th>Прогресс</th>
                    </tr>
                </thead>
                <tbody>
                    ${progress.map(p => `
                        <tr>
                            <td>${p.student_name}</td>
                            <td>${p.submissions_count}</td>
                            <td>${p.graded_count}</td>
                            <td>${p.average_score}</td>
                            <td>${p.completion_percentage}%</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Переключение вкладок
document.querySelectorAll('.tab-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();

        const tab = this.dataset.tab;

        // Убираем active у всех
        document.querySelectorAll('.tab-link').forEach(l => l.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        // Добавляем active к нужным
        this.classList.add('active');
        document.getElementById(tab).classList.add('active');
    });
});

// Выход
document.getElementById('logoutBtn').addEventListener('click', function() {
    api.removeToken();
    window.location.href = 'form.html';
});

// Закрытие модального окна при клике вне его
window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
});

// Инициализация
init();
