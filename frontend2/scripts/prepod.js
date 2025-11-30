if (!api.isAuthenticated()) {
    window.location.href = 'form.html';
}

let currentCourseId = null;
let currentUser = null;

// Загружаем данные пользователя и курсы при загрузке страницы
async function init() {
    try {
        currentUser = await api.getCurrentUser();
        document.getElementById('userName').textContent = currentUser.full_name || currentUser.email;
        await loadCourses();
    } catch (error) {
        console.error('Ошибка инициализации:', error);
        api.removeToken();
        window.location.href = 'form.html';
    }
}

// Загрузка курсов
async function loadCourses() {
    try {
        const courses = await api.getCourses();
        renderCourses(courses);
    } catch (error) {
        console.error('Ошибка загрузки курсов:', error);
    }
}

// Отрисовка курсов
function renderCourses(courses) {
    const coursesList = document.getElementById('courses-list');

    if (!courses || courses.length === 0) {
        coursesList.innerHTML = '<p style="padding: 20px; color: #666;">У вас пока нет курсов. Создайте первый!</p>';
        return;
    }

    const images = [
        './img/course-1.svg',
        './img/course-2.svg',
        './img/course-3.svg'
    ];

    coursesList.innerHTML = courses.map((course, index) => `
        <div class="courses-item" data-course-id="${course.id}">
            <div class="item-img">
                <img src="${images[index % images.length]}" alt="">
            </div>
            <div class="item-info">
                <div class="item-describtion">
                    <h1>${course.title}</h1>
                    <span>${course.description || 'Описание отсутствует'}</span>
                </div>
                <div class="item-nav">
                    <button onclick="openCourse('${course.id}')">
                        <img src="./img/open.svg" alt="" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 4px;">
                        Открыть
                    </button>
                    <button onclick="editCourse('${course.id}')">
                        <img src="./img/edit.svg" alt="" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 4px;">
                        Редактировать
                    </button>
                    <button onclick="deleteCourse('${course.id}')">
                        <img src="./img/delete.svg" alt="" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 4px;">
                        Удалить
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Открыть курс (переход на страницу курса)
function openCourse(courseId) {
    window.location.href = `course.html?id=${courseId}`;
}

// Редактировать курс
async function editCourse(courseId) {
    try {
        const course = await api.getCourse(courseId);
        currentCourseId = courseId;

        document.getElementById('formTitle').textContent = 'Редактирование курса';
        document.getElementById('name').value = course.title;
        document.getElementById('descr').value = course.description || '';

        showView('coursescreate');
    } catch (error) {
        alert('Ошибка загрузки курса: ' + error.message);
    }
}

// Удалить курс
async function deleteCourse(courseId) {
    if (!confirm('Вы уверены что хотите удалить этот курс?')) {
        return;
    }

    try {
        await api.deleteCourse(courseId);
        await loadCourses();
    } catch (error) {
        alert('Ошибка удаления курса: ' + error.message);
    }
}

// Показать определенный view
function showView(viewId) {
    document.getElementById('courses').style.display = 'none';
    document.getElementById('stat').style.display = 'none';
    document.getElementById('coursescreate').style.display = 'none';

    document.getElementById(viewId).style.display = viewId === 'courses' ? 'flex' : 'block';
    if (viewId === 'coursescreate') {
        document.getElementById(viewId).style.display = 'flex';
    }
}

// Навигация - Создание курса
document.querySelector("a.c").addEventListener('click', function(e) {
    e.preventDefault();
    currentCourseId = null;
    document.getElementById('formTitle').textContent = 'Создание курса';
    document.getElementById('name').value = '';
    document.getElementById('descr').value = '';
    showView('coursescreate');
});

// Навигация - Мои курсы
document.querySelector("a.ch").addEventListener('click', function(e) {
    e.preventDefault();
    loadCourses();
    showView('courses');
});

// Навигация - Статистика
document.querySelector("a.s").addEventListener('click', async function(e) {
    e.preventDefault();
    showView('stat');
});

// Сохранение курса (создание или обновление)
document.getElementById('saveCourse').addEventListener('click', async function() {
    const title = document.getElementById('name').value.trim();
    const description = document.getElementById('descr').value.trim();

    if (!title) {
        alert('Введите название курса');
        return;
    }

    try {
        if (currentCourseId) {
            // Обновление
            await api.updateCourse(currentCourseId, title, description);
        } else {
            // Создание
            await api.createCourse(title, description);
        }

        await loadCourses();
        showView('courses');
    } catch (error) {
        alert('Ошибка сохранения курса: ' + error.message);
    }
});

document.getElementById('cancelEdit').addEventListener('click', function() {
    showView('courses');
});

document.getElementById('logoutBtn').addEventListener('click', function() {
    api.removeToken();
    window.location.href = 'form.html';
});

init();
