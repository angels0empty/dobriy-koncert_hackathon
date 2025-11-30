from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserAdminResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    is_blocked: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_blocked: Optional[bool] = None


class AdminPermissionUpdate(BaseModel):
    can_manage_users: bool = False
    can_manage_courses: bool = False
    can_manage_tests: bool = False
    can_view_analytics: bool = False
    can_manage_permissions: bool = False


class AdminPermissionResponse(BaseModel):
    id: UUID
    user_id: UUID
    can_manage_users: bool
    can_manage_courses: bool
    can_manage_tests: bool
    can_view_analytics: bool
    can_manage_permissions: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MockStatisticCreate(BaseModel):
    student_id: UUID
    course_id: UUID
    assignment_id: Optional[UUID] = None
    test_id: Optional[UUID] = None
    score: int
    completion_percentage: float = 0.0
    time_spent_minutes: int = 0


class TestAdminResponse(BaseModel):
    id: UUID
    title: str
    course_name: str
    questions_count: int
    completions_count: int

    class Config:
        from_attributes = True


class AnalyticsOverview(BaseModel):
    total_users: int
    total_teachers: int
    total_students: int
    total_courses: int
    total_assignments: int
    active_users_last_month: int
