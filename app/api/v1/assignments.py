from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.models.assignment import Assignment
from app.models.submission import Submission
from app.models.grade import Grade
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentResponse,
    SubmissionResponse,
    SubmissionWithGrade
)
from app.utils.dependencies import get_current_user, get_current_teacher

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/courses/{course_id}/assignments", response_model=AssignmentResponse)
def create_assignment(
    course_id: UUID,
    assignment_data: AssignmentCreate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Создание задания для курса"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    new_assignment = Assignment(
        course_id=course_id,
        title=assignment_data.title,
        description=assignment_data.description,
        max_score=assignment_data.max_score,
        deadline=assignment_data.deadline
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return new_assignment


@router.get("/courses/{course_id}/assignments", response_model=List[AssignmentResponse])
def get_course_assignments(
    course_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Получить все задания курса"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    assignments = db.query(Assignment).filter(Assignment.course_id == course_id).all()
    return assignments


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(
    assignment_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Получить детали задания"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    return assignment


@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: UUID,
    assignment_data: AssignmentUpdate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Обновление задания"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Обновляем
    if assignment_data.title:
        assignment.title = assignment_data.title
    if assignment_data.description:
        assignment.description = assignment_data.description
    if assignment_data.max_score:
        assignment.max_score = assignment_data.max_score
    if assignment_data.deadline:
        assignment.deadline = assignment_data.deadline

    db.commit()
    db.refresh(assignment)

    return assignment


@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Удаление задания"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(assignment)
    db.commit()

    return {"message": "Assignment deleted"}


@router.get("/{assignment_id}/submissions", response_model=List[SubmissionWithGrade])
def get_assignment_submissions(
    assignment_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Получить все сданные работы по заданию"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    submissions = db.query(Submission)\
        .join(User, Submission.student_id == User.id)\
        .outerjoin(Grade, Grade.submission_id == Submission.id)\
        .filter(Submission.assignment_id == assignment_id)\
        .add_columns(User.full_name, Grade.score, Grade.comment)\
        .all()

    result = []
    for sub, student_name, grade_score, grade_comment in submissions:
        result.append({
            "id": sub.id,
            "assignment_id": sub.assignment_id,
            "student_id": sub.student_id,
            "student_name": student_name,
            "content": sub.content,
            "file_url": sub.file_url,
            "status": sub.status,
            "submitted_at": sub.submitted_at,
            "grade": grade_score,
            "grade_comment": grade_comment
        })

    return result
