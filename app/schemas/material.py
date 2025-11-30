from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class MaterialCreate(BaseModel):
    title: str
    content: Optional[str] = None
    file_url: Optional[str] = None
    order_number: int = 0


class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    file_url: Optional[str] = None
    order_number: Optional[int] = None


class MaterialResponse(BaseModel):
    id: UUID
    course_id: UUID
    title: str
    content: Optional[str]
    file_url: Optional[str]
    order_number: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
