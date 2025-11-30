from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.models.material import Material
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialResponse
from app.utils.dependencies import get_current_teacher

router = APIRouter(prefix="/materials", tags=["materials"])


@router.post("/courses/{course_id}/materials", response_model=MaterialResponse)
def create_material(
    course_id: UUID,
    material_data: MaterialCreate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Создать учебный материал для курса"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    material = Material(
        course_id=course_id,
        title=material_data.title,
        content=material_data.content,
        file_url=material_data.file_url,
        order_number=material_data.order_number
    )

    db.add(material)
    db.commit()
    db.refresh(material)

    return material


@router.get("/courses/{course_id}/materials", response_model=List[MaterialResponse])
def get_course_materials(
    course_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Получить все материалы курса"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    materials = db.query(Material).filter(
        Material.course_id == course_id
    ).order_by(Material.order_number).all()

    return materials


@router.put("/{material_id}", response_model=MaterialResponse)
def update_material(
    material_id: UUID,
    material_data: MaterialUpdate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Обновить материал"""
    material = db.query(Material).filter(Material.id == material_id).first()

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    course = db.query(Course).filter(Course.id == material.course_id).first()
    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Обновляем поля
    if material_data.title:
        material.title = material_data.title
    if material_data.content:
        material.content = material_data.content
    if material_data.file_url:
        material.file_url = material_data.file_url
    if material_data.order_number is not None:
        material.order_number = material_data.order_number

    db.commit()
    db.refresh(material)

    return material


@router.delete("/{material_id}")
def delete_material(
    material_id: UUID,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Удалить материал"""
    material = db.query(Material).filter(Material.id == material_id).first()

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    course = db.query(Course).filter(Course.id == material.course_id).first()
    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(material)
    db.commit()

    return {"message": "Material deleted"}
