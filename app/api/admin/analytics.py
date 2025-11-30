from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.assignment import Assignment
from app.schemas.admin import AnalyticsOverview
from app.utils.dependencies import check_permission

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def get_analytics_overview(
    current_user: User = Depends(check_permission("can_view_analytics")),
    db: Session = Depends(get_db)
):
    """Общая статистика платформы"""

    # Подсчёт пользователей
    total_users = db.query(User).count()
    total_teachers = db.query(User).filter(User.role == UserRole.teacher).count()
    total_students = db.query(User).filter(User.role == UserRole.student).count()

    total_courses = db.query(func.count(Course.id)).scalar() or 0
    total_assignments = db.query(func.count(Assignment.id)).scalar() or 0

    one_month_ago = datetime.utcnow() - timedelta(days=30)
    active_users = db.query(func.count(User.id)).filter(
        User.last_login >= one_month_ago
    ).scalar() or 0

    return {
        "total_users": total_users,
        "total_teachers": total_teachers,
        "total_students": total_students,
        "total_courses": total_courses,
        "total_assignments": total_assignments,
        "active_users_last_month": active_users
    }


@router.get("/top-courses")
def get_top_courses(
    limit: int = 10,
    current_user: User = Depends(check_permission("can_view_analytics")),
    db: Session = Depends(get_db)
):
    """Топ курсов по количеству студентов"""
    from app.models.course import course_students

    courses_data = db.query(
        Course.id,
        Course.title,
        Course.is_published,
        User.full_name.label('teacher_name'),
        func.count(course_students.c.student_id).label('students_count')
    ).join(User, Course.teacher_id == User.id)\
        .outerjoin(course_students, course_students.c.course_id == Course.id)\
        .group_by(Course.id, Course.title, Course.is_published, User.full_name)\
        .order_by(func.count(course_students.c.student_id).desc())\
        .limit(limit)\
        .all()

    result = []
    for course_id, title, is_published, teacher_name, students_count in courses_data:
        result.append({
            "course_id": course_id,
            "title": title,
            "teacher_name": teacher_name,
            "students_count": students_count,
            "is_published": is_published
        })

    return result


@router.get("/teachers-stats")
def get_teachers_stats(
    current_user: User = Depends(check_permission("can_view_analytics")),
    db: Session = Depends(get_db)
):
    """Статистика преподавателей"""
    from app.models.course import course_students

    teachers_data = db.query(
        User.id,
        User.full_name,
        User.email,
        func.count(func.distinct(Course.id)).label('courses_count'),
        func.count(func.distinct(course_students.c.student_id)).label('total_students')
    ).filter(User.role == UserRole.teacher)\
        .outerjoin(Course, Course.teacher_id == User.id)\
        .outerjoin(course_students, course_students.c.course_id == Course.id)\
        .group_by(User.id, User.full_name, User.email)\
        .all()

    result = []
    for teacher_id, teacher_name, email, courses_count, total_students in teachers_data:
        result.append({
            "teacher_id": teacher_id,
            "teacher_name": teacher_name,
            "email": email,
            "courses_count": courses_count,
            "total_students": total_students
        })

    return result
