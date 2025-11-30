from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


course_students = Table(
    'course_students',
    Base.metadata,
    Column('course_id', UUID(as_uuid=True), ForeignKey('courses.id', ondelete="CASCADE")),
    Column('student_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE")),
    Column('enrolled_at', DateTime, default=datetime.utcnow)
)


class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    teacher = relationship("User", foreign_keys=[teacher_id])
    students = relationship("User", secondary=course_students)
