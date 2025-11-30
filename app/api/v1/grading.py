from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.submission import Submission, SubmissionStatus
from app.models.grade import Grade
from app.models.assignment import Assignment
from app.models.course import Course
from app.schemas.grade import GradeCreate, GradeUpdate, GradeResponse
from app.utils.dependencies import get_current_teacher

router = APIRouter(prefix="/grading", tags=["grading"])


@router.post("/submissions/{submission_id}/grade", response_model=GradeResponse)
def grade_submission(
    submission_id: UUID,
    grade_data: GradeCreate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Выставить оценку за работу"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # проверка прав
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
    course = db.query(Course).filter(Course.id == assignment.course_id).first()

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    if grade_data.score > assignment.max_score:
        raise HTTPException(
            status_code=400,
            detail=f"Score cannot exceed max_score ({assignment.max_score})"
        )

    # есть ли уже оценка
    existing_grade = db.query(Grade).filter(Grade.submission_id == submission_id).first()

    if existing_grade:
        # Обновляем существующую
        existing_grade.score = grade_data.score
        existing_grade.comment = grade_data.comment
        db.commit()
        db.refresh(existing_grade)
        grade = existing_grade
    else:
        # Создаем новую
        grade = Grade(
            submission_id=submission_id,
            teacher_id=current_user.id,
            score=grade_data.score,
            comment=grade_data.comment
        )
        db.add(grade)
        db.commit()
        db.refresh(grade)

    # Обновляем статус submission
    submission.status = SubmissionStatus.reviewed
    db.commit()

    return grade


@router.put("/grades/{grade_id}", response_model=GradeResponse)
def update_grade(
    grade_id: UUID,
    grade_data: GradeUpdate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Обновить оценку"""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()

    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    # Проверка прав (через submission -> assignment -> course)
    submission = db.query(Submission).filter(Submission.id == grade.submission_id).first()
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
    course = db.query(Course).filter(Course.id == assignment.course_id).first()

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    if grade_data.score is not None:
        if grade_data.score > assignment.max_score:
            raise HTTPException(
                status_code=400,
                detail=f"Score cannot exceed max_score ({assignment.max_score})"
            )
        grade.score = grade_data.score

    if grade_data.comment is not None:
        grade.comment = grade_data.comment

    db.commit()
    db.refresh(grade)

    return grade


@router.delete("/grades/{grade_id}")
def delete_grade(
    grade_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Удалить оценку"""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()

    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    # Проверка прав
    submission = db.query(Submission).filter(Submission.id == grade.submission_id).first()
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
    course = db.query(Course).filter(Course.id == assignment.course_id).first()

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Обновляем статус submission обратно
    submission.status = SubmissionStatus.pending

    db.delete(grade)
    db.commit()

    return {"message": "Grade deleted"}
