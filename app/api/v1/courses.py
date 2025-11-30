from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models.user import User
from app.models.course import Course, course_students
from app.models.assignment import Assignment
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseDetailResponse
from app.utils.dependencies import get_current_user, get_current_teacher

router = APIRouter(prefix="/courses", tags=["courses"])


class AddStudentByEmail(BaseModel):
    email: EmailStr


class StudentResponse(BaseModel):
    id: UUID
    email: str
    full_name: str

    class Config:
        from_attributes = True


@router.post("/", response_model=CourseResponse)
def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Создание нового курса (только для преподавателей)"""
    new_course = Course(
        title=course_data.title,
        description=course_data.description,
        teacher_id=current_user.id
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course


@router.get("/", response_model=List[CourseResponse])
def get_my_courses(
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Получить все курсы преподавателя"""
    courses = db.query(Course).filter(Course.teacher_id == current_user.id).all()
    return courses


@router.get("/{course_id}", response_model=CourseDetailResponse)
def get_course(
    course_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Получить детали курса"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Проверяем что это курс текущего преподавателя
    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    students_count = db.query(func.count(course_students.c.student_id)).filter(
        course_students.c.course_id == course_id
    ).scalar() or 0

    assignments_count = db.query(func.count(Assignment.id)).filter(
        Assignment.course_id == course_id
    ).scalar() or 0

    return {
        **course.__dict__,
        "students_count": students_count,
        "assignments_count": assignments_count
    }


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: UUID,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Обновление курса"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = course_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)

    return course


@router.delete("/{course_id}")
def delete_course(
    course_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Удаление курса"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(course)
    db.commit()

    return {"message": "Course deleted successfully"}


@router.post("/{course_id}/students/{student_id}")
def add_student_to_course(
    course_id: UUID,
    student_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Добавить студента на курс по ID"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = db.query(course_students).filter(
        course_students.c.course_id == course_id,
        course_students.c.student_id == student_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled")

    stmt = course_students.insert().values(course_id=course_id, student_id=student_id)
    db.execute(stmt)
    db.commit()

    return {"message": "Student added successfully"}


@router.post("/{course_id}/students", response_model=dict)
def add_student_by_email(
    course_id: UUID,
    student_data: AddStudentByEmail,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Добавить студента на курс по email"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    student = db.query(User).filter(User.email == student_data.email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = db.query(course_students).filter(
        course_students.c.course_id == course_id,
        course_students.c.student_id == student.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled")

    stmt = course_students.insert().values(course_id=course_id, student_id=student.id)
    db.execute(stmt)
    db.commit()

    return {"message": "Student added successfully", "student": StudentResponse.model_validate(student)}


@router.get("/{course_id}/students", response_model=List[StudentResponse])
def get_course_students(
    course_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Получить список студентов на курсе"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    students = db.query(User).join(
        course_students,
        course_students.c.student_id == User.id
    ).filter(
        course_students.c.course_id == course_id
    ).all()

    return students


@router.delete("/{course_id}/students/{student_id}")
def remove_student_from_course(
    course_id: UUID,
    student_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Удалить студента с курса"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    existing = db.query(course_students).filter(
        course_students.c.course_id == course_id,
        course_students.c.student_id == student_id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Student not enrolled in this course")

    stmt = course_students.delete().where(
        course_students.c.course_id == course_id,
        course_students.c.student_id == student_id
    )
    db.execute(stmt)
    db.commit()

    return {"message": "Student removed successfully"}


@router.get("/all-students", response_model=List[StudentResponse])
def get_all_students(
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Получить список всех студентов"""
    students = db.query(User).filter(User.role == "student").all()
    return students

@router.get("/my-courses", response_model=List[CourseResponse])
def get_my_courses_as_student(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить курсы на которых записан студент"""
    courses = db.query(Course).join(
        course_students,
        course_students.c.course_id == Course.id
    ).filter(
        course_students.c.student_id == current_user.id
    ).all()

    return courses