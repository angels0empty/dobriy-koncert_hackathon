from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import random
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.models.assignment import Assignment
from app.models.test import Test
from app.models.mock_statistic import MockStatistic
from app.schemas.admin import MockStatisticCreate
from app.utils.dependencies import check_permission

router = APIRouter(prefix="/admin/mock-data", tags=["admin-mock-data"])


@router.post("/statistics")
def create_mock_statistic(
    data: MockStatisticCreate,
    current_user: User = Depends(check_permission("can_view_analytics")),
    db: Session = Depends(get_db)
):
    """Создать тестовую статистику вручную"""
    mock_stat = MockStatistic(
        student_id=data.student_id,
        course_id=data.course_id,
        assignment_id=data.assignment_id,
        test_id=data.test_id,
        score=data.score,
        completion_percentage=data.completion_percentage,
        time_spent_minutes=data.time_spent_minutes,
        is_mock=True
    )

    db.add(mock_stat)
    db.commit()
    db.refresh(mock_stat)

    return {"message": "Mock statistic created", "id": mock_stat.id}


@router.post("/generate")
def generate_mock_data(
    course_id: UUID,
    num_records: int = 20,
    current_user: User = Depends(check_permission("can_view_analytics")),
    db: Session = Depends(get_db)
):
    """Автогенерация тестовых данных для курса"""

    # Проверяем что курс существует
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Получаем студентов и задания
    from app.models.course import course_students
    student_ids = [row.student_id for row in db.query(course_students.c.student_id).filter(
        course_students.c.course_id == course_id
    ).all()]

    if not student_ids:
        raise HTTPException(status_code=400, detail="No students in this course")

    assignments = db.query(Assignment).filter(Assignment.course_id == course_id).all()
    tests = db.query(Test).filter(Test.course_id == course_id).all()

    # Генерируем данные
    created_count = 0
    for _ in range(num_records):
        student_id = random.choice(student_ids)

        # Случайно выбираем задание или тест
        assignment_id = None
        test_id = None
        if assignments and random.choice([True, False]):
            assignment_id = random.choice(assignments).id
        elif tests:
            test_id = random.choice(tests).id

        # Генерируем случайные метрики
        score = random.randint(50, 100)
        completion = random.uniform(60.0, 100.0)
        time_spent = random.randint(30, 180)

        mock_stat = MockStatistic(
            student_id=student_id,
            course_id=course_id,
            assignment_id=assignment_id,
            test_id=test_id,
            score=score,
            completion_percentage=completion,
            time_spent_minutes=time_spent,
            is_mock=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )

        db.add(mock_stat)
        created_count += 1

    db.commit()

    return {
        "message": f"Generated {created_count} mock statistics",
        "course_id": course_id
    }


@router.get("/statistics")
def get_mock_statistics(
    course_id: UUID = None,
    current_user: User = Depends(check_permission("can_view_analytics")),
    db: Session = Depends(get_db)
):
    """Получить все тестовые данные"""
    query = db.query(MockStatistic).filter(MockStatistic.is_mock == True)

    if course_id:
        query = query.filter(MockStatistic.course_id == course_id)

    stats = query.all()

    result = []
    for stat in stats:
        student = db.query(User).filter(User.id == stat.student_id).first()
        course = db.query(Course).filter(Course.id == stat.course_id).first()

        result.append({
            "id": stat.id,
            "student_name": student.full_name if student else "Unknown",
            "course_title": course.title if course else "Unknown",
            "score": stat.score,
            "completion_percentage": stat.completion_percentage,
            "time_spent_minutes": stat.time_spent_minutes,
            "created_at": stat.created_at
        })

    return result


@router.delete("/statistics")
def clear_mock_data(
    current_user: User = Depends(check_permission("can_view_analytics")),
    db: Session = Depends(get_db)
):
    """Очистить все тестовые данные"""
    deleted_count = db.query(MockStatistic).filter(MockStatistic.is_mock == True).delete()
    db.commit()

    return {"message": f"Deleted {deleted_count} mock statistics"}
