from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schema import Exam, Subject
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/exams", tags=["Exams & Taxonomies"])


class ExamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    total_marks: float
    duration_minutes: int
    negative_mark_ratio: float
    languages: str
    is_active: bool


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    is_common_core: bool


@router.get("/", response_model=List[ExamOut])
async def list_exams(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exam).where(Exam.is_active == True))
    return result.scalars().all()


@router.get("/subjects", response_model=List[SubjectOut])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subject))
    return result.scalars().all()
