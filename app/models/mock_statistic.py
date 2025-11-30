from sqlalchemy import Column, DateTime, ForeignKey, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class MockStatistic(Base):
    __tablename__ = "mock_statistics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id", ondelete="CASCADE"), nullable=True)
    test_id = Column(UUID(as_uuid=True), ForeignKey("tests.id", ondelete="CASCADE"), nullable=True)
    score = Column(Integer, nullable=False)
    completion_percentage = Column(Float, default=0.0)
    time_spent_minutes = Column(Integer, default=0)
    is_mock = Column(Boolean, default=True)  # маркер тестовых данных
    created_at = Column(DateTime, default=datetime.utcnow)
