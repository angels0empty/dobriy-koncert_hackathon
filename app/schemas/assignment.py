from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    max_score: int = 100
    deadline: Optional[datetime] = None


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    max_score: Optional[int] = None
    deadline: Optional[datetime] = None


class AssignmentResponse(BaseModel):
    id: UUID
    course_id: UUID
    title: str
    description: Optional[str]
    max_score: int
    deadline: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    content: Optional[str] = None
    file_url: Optional[str] = None


class SubmissionResponse(BaseModel):
    id: UUID
    assignment_id: UUID
    student_id: UUID
    content: Optional[str]
    file_url: Optional[str]
    status: str
    submitted_at: datetime

    class Config:
        from_attributes = True


class SubmissionWithGrade(BaseModel):
    id: UUID
    assignment_id: UUID
    student_id: UUID
    student_name: str
    content: Optional[str]
    file_url: Optional[str]
    status: str
    submitted_at: datetime
    grade: Optional[int] = None
    grade_comment: Optional[str] = None

    class Config:
        from_attributes = True
