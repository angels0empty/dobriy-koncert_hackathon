from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class GradeCreate(BaseModel):
    score: int
    comment: Optional[str] = None


class GradeUpdate(BaseModel):
    score: Optional[int] = None
    comment: Optional[str] = None


class GradeResponse(BaseModel):
    id: UUID
    submission_id: UUID
    teacher_id: Optional[UUID]
    score: int
    comment: Optional[str]
    graded_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
