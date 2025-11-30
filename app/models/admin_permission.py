from sqlalchemy import Column, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class AdminPermission(Base):
    __tablename__ = "admin_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    can_manage_users = Column(Boolean, default=False)
    can_manage_courses = Column(Boolean, default=False)
    can_manage_tests = Column(Boolean, default=False)
    can_view_analytics = Column(Boolean, default=False)
    can_manage_permissions = Column(Boolean, default=False)  # супер-админ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
