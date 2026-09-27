from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class QuestionBase(BaseModel):
    question_text: str = Field(..., description="Full text of the question with LaTeX math formatting if any")
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str = Field(..., pattern="^[A-D]$", description="Must be one of A, B, C, D")
    explanation: str = Field(..., description="Step-by-step mathematical or logical solution")
    difficulty_level: int = Field(2, ge=1, le=3, description="1: Basic (WBP), 2: Applied (JE/SI), 3: Advanced (CPO)")
    target_time_seconds: int = Field(45, ge=15, le=180)
    language: str = Field("en", description="en, bn, or hi")
    exam_tags: str = Field("ssc_cpo,ssc_je,wbp_si")
    source_info: Optional[str] = None


class QuestionCreate(QuestionBase):
    subtopic_id: Optional[int] = None
    is_verified: bool = False


class QuestionOut(QuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subtopic_id: Optional[int]
    is_verified: bool
    created_at: datetime


class JEVVerificationResult(BaseModel):
    is_mathematically_sound: bool = Field(..., description="Whether the solution is mathematically and logically correct")
    official_key_verified: bool = Field(..., description="Whether the given official correct_option matches independent solution")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    verified_correct_option: str = Field(..., pattern="^[A-D]$")
    critique_notes: str = Field(..., description="Detailed critique notes explaining any flaw or trap")
    extracted_trap_pattern: Optional[str] = Field(None, description="The specific trick or trap in this question")
