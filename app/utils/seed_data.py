"""
Скрипт для генерации тестовых данных
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.course import Course, course_students
from app.models.assignment import Assignment
from app.utils.auth import get_password_hash
from datetime import datetime, timedelta
import random


def seed_data():
    """Генерация тестовых данных для демо"""
    db = SessionLocal()

    try:
        print("[?] creating test data..")
 
        teacher = User(
            email="teacher@test.com",
            hashed_password=get_password_hash("teacher123"),
            full_name="Лебедев Денис",
            role=UserRole.teacher
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        print(f"[+] teacher created: {teacher.email}")

        students = []
        student_names = [
            "Иван Сидоров",
            "Мария Козлова",
            "Петр Васильев",
            "Елена Смирнова",
            "Дмитрий Новиков"
        ]

        for i, name in enumerate(student_names, 1):
            student = User(
                email=f"student{i}@test.com",
                hashed_password=get_password_hash("student123"),
                full_name=name,
                role=UserRole.student
            )
            db.add(student)
            students.append(student)

        db.commit()
        print(f"created {len(students)} students")

        courses_data = [
            {
                "title": "Основы Python",
                "description": "Курс для начинающих программистов"
            },
            {
                "title": "Web-разработка",
                "description": "HTML, CSS, JavaScript и React"
            },
            {
                "title": "Базы данных",
                "description": "SQL и работа с PostgreSQL"
            }
        ]

        courses = []
        for course_data in courses_data:
            course = Course(
                title=course_data["title"],
                description=course_data["description"],
                teacher_id=teacher.id,
                is_published=True
            )
            db.add(course)
            courses.append(course)

        db.commit()
        print(f"[+] created {len(courses)} courses")

        for course in courses:
            enrolled = random.sample(students, k=random.randint(3, 4))
            for student in enrolled:
                stmt = course_students.insert().values(
                    course_id=course.id,
                    student_id=student.id
                )
                db.execute(stmt)

        db.commit()
        print("[+] students enrolled")

        for course in courses:
            for i in range(3):
                assignment = Assignment(
                    course_id=course.id,
                    title=f"Задание {i+1}: {course.title}",
                    description=f"Практическое задание по теме курса",
                    max_score=100,
                    deadline=datetime.utcnow() + timedelta(days=random.randint(7, 30))
                )
                db.add(assignment)

        db.commit()
        print(f"Преподаватель: teacher@test.com / teacher123")
        print(f"Студенты: student1@test.com - student5@test.com / student123")

    except Exception as e:
        print(f"❌ Ошибка при создании данных: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
