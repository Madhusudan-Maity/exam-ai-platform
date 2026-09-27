from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schema import Question
from app.schemas.question import QuestionOut

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("/", response_model=List[QuestionOut])
async def list_questions(
    exam_code: Optional[str] = Query(None, description="Filter by exam e.g. ssc_cpo, wbp_si"),
    difficulty: Optional[int] = Query(None, ge=1, le=3),
    language: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Question)
    if difficulty:
        stmt = stmt.where(Question.difficulty_level == difficulty)
    if language:
        stmt = stmt.where(Question.language == language)
    if exam_code:
        stmt = stmt.where(Question.exam_tags.contains(exam_code))

    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{question_id}", response_model=QuestionOut)
async def get_question(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalars().first()
    if not question:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Question not found")
    return question
