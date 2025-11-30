from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_published: Optional[bool] = None


class CourseResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    teacher_id: UUID
    is_published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CourseDetailResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    teacher_id: UUID
    is_published: bool
    created_at: datetime
    students_count: int = 0
    assignments_count: int = 0

    class Config:
        from_attributes = True


# Для админки
class CourseAdminResponse(BaseModel):
    id: UUID
    title: str
    teacher_name: str
    students_count: int
    created_at: datetime
    is_published: bool

    class Config:
        from_attributes = True
