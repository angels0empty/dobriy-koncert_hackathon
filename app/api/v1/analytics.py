from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import List, Dict

from app.database import get_db
from app.models.user import User
from app.models.course import Course, course_students
from app.models.assignment import Assignment
from app.models.submission import Submission
from app.models.grade import Grade
from app.utils.dependencies import get_current_teacher

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/courses/{course_id}/stats")
def get_course_stats(
    course_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Получить статистику по курсу"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    students_count = db.query(func.count(course_students.c.student_id)).filter(
        course_students.c.course_id == course_id
    ).scalar() or 0

    assignments_count = db.query(func.count(Assignment.id)).filter(
        Assignment.course_id == course_id
    ).scalar() or 0

    total_submissions = db.query(func.count(Submission.id))\
        .join(Assignment, Submission.assignment_id == Assignment.id)\
        .filter(Assignment.course_id == course_id)\
        .scalar() or 0

    avg_score = db.query(func.avg(Grade.score))\
        .join(Submission, Grade.submission_id == Submission.id)\
        .join(Assignment, Submission.assignment_id == Assignment.id)\
        .filter(Assignment.course_id == course_id)\
        .scalar() or 0

    return {
        "course_id": course_id,
        "course_title": course.title,
        "students_count": students_count,
        "assignments_count": assignments_count,
        "total_submissions": total_submissions,
        "average_score": round(avg_score, 2)
    }


@router.get("/courses/{course_id}/student-progress")
def get_student_progress(
    course_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Получить прогресс студентов по курсу"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    assignments_count = db.query(func.count(Assignment.id)).filter(
        Assignment.course_id == course_id
    ).scalar() or 1

    progress_data = db.query(
        User.id,
        User.full_name,
        func.count(Submission.id).label('submissions_count'),
        func.count(Grade.id).label('graded_count'),
        func.avg(Grade.score).label('avg_score')
    ).select_from(course_students)\
        .join(User, course_students.c.student_id == User.id)\
        .outerjoin(Submission, (Submission.student_id == User.id) &
                   (Submission.assignment_id.in_(
                       db.query(Assignment.id).filter(Assignment.course_id == course_id)
                   )))\
        .outerjoin(Grade, Grade.submission_id == Submission.id)\
        .filter(course_students.c.course_id == course_id)\
        .group_by(User.id, User.full_name)\
        .all()

    result = []
    for student_id, student_name, submissions_count, graded_count, avg_score in progress_data:
        completion = (submissions_count / assignments_count * 100) if assignments_count > 0 else 0
        result.append({
            "student_id": student_id,
            "student_name": student_name,
            "submissions_count": submissions_count or 0,
            "graded_count": graded_count or 0,
            "average_score": round(float(avg_score), 2) if avg_score else 0,
            "completion_percentage": round(completion, 2)
        })

    return result
