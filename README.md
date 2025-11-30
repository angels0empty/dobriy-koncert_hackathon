# LMS - Система управления обучением

### Структура проекта
```
app/
├── api/                    # API endpoints (маршруты)
│   ├── v1/                # API версии 1
│   │   ├── auth.py        # Аутентификация и регистрация
│   │   ├── courses.py     # Управление курсами
│   │   ├── assignments.py # Задания для студентов
│   │   ├── materials.py   # Учебные материалы
│   │   ├── grading.py     # Выставление оценок
│   │   └── analytics.py   # Статистика и аналитика
│   └── admin/             # Админские endpoints
│       ├── users.py       # Управление пользователями
│       ├── analytics.py   # Общая статистика
│       └── mock_data.py   # Генерация тестовых данных
├── models/                # SQLAlchemy модели (БД схемы)
│   ├── user.py           # Модель пользователя
│   ├── course.py         # Модель курса
│   ├── assignment.py     # Модель задания
│   ├── submission.py     # Модель сданной работы
│   ├── grade.py          # Модель оценки
│   ├── material.py       # Модель учебного материала
│   ├── test.py           # Модель теста и вопросов
│   └── admin_permission.py # Права администратора
├── schemas/               # Pydantic схемы (валидация данных)
│   ├── auth.py           # Схемы для аутентификации
│   ├── course.py         # Схемы для курсов
│   ├── assignment.py     # Схемы для заданий
│   ├── grade.py          # Схемы для оценок
│   ├── material.py       # Схемы для материалов
│   └── admin.py          # Схемы для админки
├── utils/                 # Вспомогательные функции
│   ├── auth.py           # JWT токены, хэширование паролей
│   ├── dependencies.py   # Проверка прав
│   ├── create_admin.py   # Создание первого админа
│   └── seed_data.py      # Загрузка тестовых данных
├── middleware/            # Промежуточные обработчики
├── services/              # Под бизнес-логика (будущее расширение)
├── main.py               # Точка входа приложения
├── database.py           # Настройка подключения к БД
└── config.py             # Конфигурация (переменные окружения)
```
Структура Frontend'а описана в сооветствующем [readme.md](https://github.com/angels0empty/dobriy-koncert_hackathon/blob/main/frontend2/README.md) в папке Frontend'а.


## Технологии

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT Authentication

### Frontend
- Vanilla HTML/CSS/JavaScript
- Nginx

### Infrastructure
- Docker
- Docker Compose

## Запуск проекта

### С помощью Docker Compose
```bash
# Запустить все сервисы (БД, бэкенд, фронтенд)
docker-compose up -d

# Применить миграции
docker-compose exec backend alembic upgrade head

# Создать первого преподавателя
docker-compose exec backend python -c "from app.utils.create_admin import create_admin; create_admin()"

# Опционально: Загрузить тестовые данные
docker-compose exec backend python -m app.utils.seed_data
```

### Тестовые данные

ДЛЯ ХАКАТОНА: На указанном сервере уже создан профиль с созданными курсами и добавленными туда юзерами teacher@test.com / teacher123

После запуска можете зарегистрировать преподавателя через форму на http://localhost или использовать команду создания админа выше.

### Доступ к приложению

- **Фронтенд**: http://localhost (порт 80)
- **Backend API**: http://localhost:8000
- **API Документация (Swagger)**: http://localhost:8000/docs

## Функционал фронтенда

### Для преподавателя:

1. **Авторизация** (`form.html`)
   - Вход в систему с JWT токеном
   - Автоматическая проверка авторизации

2. **Главная страница** (`lkp.html`)
   - Просмотр всех своих курсов
   - Создание нового курса
   - Редактирование курса
   - Удаление курса

3. **Страница курса** (`course.html`)
   - **Материалы**: создание, редактирование, удаление учебных материалов
   - **Задания**: создание заданий, установка дедлайнов и максимальных баллов
   - **Проверка работ**: просмотр сданных работ студентов, выставление оценок и комментариев
   - **Статистика**: общая статистика по курсу и прогресс каждого студента

4. **Админ панель** (`admin.html`)
   - Генерация тестовых данных для демонстрации
   - Просмотр сгенерированных данных
   - Очистка тестовых данных

## Структура API

### Аутентификация
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `GET /api/v1/auth/me` - Информация о текущем пользователе

### Курсы (преподаватели)
- `POST /api/v1/courses/` - Создать курс
- `GET /api/v1/courses/` - Список моих курсов
- `GET /api/v1/courses/{id}` - Детали курса
- `PUT /api/v1/courses/{id}` - Обновить курс
- `DELETE /api/v1/courses/{id}` - Удалить курс
- `POST /api/v1/courses/{id}/students/{student_id}` - Добавить студента

### Курсы (студент)
- `GET /courses/my-courses` - получить курсы студента

### Задания (преподователь)
- `POST /api/v1/assignments/courses/{course_id}/assignments` - Создать задание
- `GET /api/v1/assignments/courses/{course_id}/assignments` - Список заданий
- `GET /api/v1/assignments/{id}/submissions` - Получить сданные работы

### Задания (студент)
- `POST /assignments/{assignment_id}/submit` - сдать работу по заданию
- `GET /assignments/my-assignments` - получить все задания студента
- `GET /assignments/{assignment_id}/my-submission` - получить свою сданную работу


### Оценки
- `POST /api/v1/grading/submissions/{id}/grade` - Выставить оценку
- `PUT /api/v1/grading/grades/{id}` - Обновить оценку

### Материалы
- `POST /api/v1/materials/courses/{course_id}/materials` - Добавить материал
- `GET /api/v1/materials/courses/{course_id}/materials` - Список материалов

### Аналитика
- `GET /api/v1/analytics/courses/{course_id}/stats` - Статистика курса
- `GET /api/v1/analytics/courses/{course_id}/student-progress` - Прогресс студентов

### Админка
- `GET /api/v1/admin/users` - Список пользователей
- `PUT /api/v1/admin/users/{id}` - Обновить пользователя
- `POST /api/v1/admin/users/{id}/block` - Заблокировать
- `GET /api/v1/admin/analytics/overview` - Общая статистика
- `POST /api/v1/admin/mock-data/generate` - Генерация тестовых данных

## База данных

Модели:
- User - Пользователи (студенты, преподаватели, админы)
- Course - Курсы
- Assignment - Задания
- Submission - Сданные работы
- Grade - Оценки
- Material - Учебные материалы
- Test - Тесты
- Question - Вопросы к тестам
- TestResult - Результаты тестов
- AdminPermission - Права администраторов
- MockStatistic - Тестовые данные для демо

## Примеры использования

### Регистрация преподавателя
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@example.com",
    "password": "password123",
    "full_name": "Иван Иванов",
    "role": "teacher"
  }'
```

### Вход
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@example.com",
    "password": "password123"
  }'
```

### Создание курса
```bash
curl -X POST http://localhost:8000/api/v1/courses/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Основы программирования",
    "description": "Курс для начинающих"
  }'
```
