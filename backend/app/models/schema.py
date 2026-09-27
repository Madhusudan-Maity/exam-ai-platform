from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


def utc_now():
    return datetime.now(timezone.utc)


class DifficultyLevel(int, enum.Enum):
    LEVEL_1 = 1  # Basic / Direct Fact (WBP Constable)
    LEVEL_2 = 2  # Applied Concept (SSC JE / WBP SI)
    LEVEL_3 = 3  # Advanced / Multi-Variable (SSC CPO)


class ErrorCategory(str, enum.Enum):
    CONCEPTUAL = "conceptual"
    CALCULATION = "calculation"
    TRAP = "trap"
    PANIC = "panic"


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    total_marks = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    negative_mark_ratio = Column(Float, default=0.25)
    languages = Column(String(100), default="en,hi,bn")
    is_active = Column(Boolean, default=True)


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_common_core = Column(Boolean, default=True)

    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    yield_score = Column(Float, default=0.0)
    difficulty_quadrant = Column(Integer, default=1)
    historical_frequency = Column(Integer, default=0)

    subject = relationship("Subject", back_populates="topics")
    subtopics = relationship("Subtopic", back_populates="topic", cascade="all, delete-orphan")


class Subtopic(Base):
    __tablename__ = "subtopics"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    name = Column(String(150), nullable=False)
    concept_slug = Column(String(150), index=True)

    topic = relationship("Topic", back_populates="subtopics")
    questions = relationship("Question", back_populates="subtopic")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_option = Column(String(1), nullable=False)
    explanation = Column(Text, nullable=False)
    difficulty_level = Column(Integer, default=DifficultyLevel.LEVEL_2.value)
    target_time_seconds = Column(Integer, default=45)
    language = Column(String(10), default="en")
    exam_tags = Column(String(200), default="ssc_cpo,ssc_je,wbp_si")
    source_info = Column(String(200), nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    subtopic = relationship("Subtopic", back_populates="questions")


class StudentProfile(Base):
    __tablename__ = "student_profile"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="Aspirant")
    current_exam_focus = Column(String(50), default="all")
    created_at = Column(DateTime, default=utc_now)


class TestSession(Base):
    __tablename__ = "test_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profile.id"), nullable=False)
    exam_code = Column(String(50), nullable=False)
    test_type = Column(String(50), default="full_mock")
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    skipped_count = Column(Integer, default=0)
    raw_score = Column(Float, default=0.0)
    penalty_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)
    total_duration_ms = Column(Integer, default=0)
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)

    attempts = relationship("QuestionAttempt", back_populates="session", cascade="all, delete-orphan")


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option = Column(String(1), nullable=True)
    is_correct = Column(Boolean, default=False)
    time_spent_ms = Column(Integer, default=0)
    hesitation_time_ms = Column(Integer, default=0)
    option_changes_count = Column(Integer, default=0)
    is_trap_violation = Column(Boolean, default=False)

    session = relationship("TestSession", back_populates="attempts")
    question = relationship("Question")


class MistakeEntry(Base):
    __tablename__ = "mistake_vault"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profile.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    error_category = Column(String(50), default=ErrorCategory.CONCEPTUAL.value)
    root_cause_note = Column(Text, nullable=True)
    review_count = Column(Integer, default=0)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    question = relationship("Question")


class FSRSCard(Base):
    __tablename__ = "fsrs_cards"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profile.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    card_type = Column(String(50), default="question_recall")
    state = Column(Integer, default=0)
    due_date = Column(DateTime, default=utc_now, index=True)
    stability = Column(Float, default=0.0)
    difficulty = Column(Float, default=0.0)
    elapsed_days = Column(Integer, default=0)
    scheduled_days = Column(Integer, default=0)
    reps = Column(Integer, default=0)
    lapses = Column(Integer, default=0)
    last_review = Column(DateTime, nullable=True)

    question = relationship("Question")
