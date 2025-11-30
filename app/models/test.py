from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class Test(Base):
    __tablename__ = "tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    time_limit_minutes = Column(Integer, nullable=True)  # лимит времени на тест
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID(as_uuid=True), ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, default="multiple_choice")  # multiple_choice, text, etc
    options = Column(JSON, nullable=True)  # варианты ответов для multiple choice
    correct_answer = Column(Text, nullable=True)
    points = Column(Integer, default=1)
    order_number = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID(as_uuid=True), ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    answers = Column(JSON, nullable=True)  # сохранённые ответы
    completed_at = Column(DateTime, default=datetime.utcnow)
