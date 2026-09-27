import pytest
from sqlalchemy import select
from app.database import AsyncSessionLocal, engine, Base
from app.models.schema import Question
from scripts.ingest_pyqs import ingest_questions


@pytest.mark.asyncio
async def test_database_tables_creation():
    """Verify all SQLite database tables are created cleanly."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    assert engine is not None


@pytest.mark.asyncio
async def test_ingest_sample_questions():
    """Verify ingestion of multilingual questions and taxonomy mapping."""
    sample_data = [
        {
            "subject_code": "quant",
            "topic_name": "Test Percentage",
            "subtopic_name": "Fraction Conversion",
            "question_text": "What is 20% expressed as a fraction?",
            "option_a": "1/4",
            "option_b": "1/5",
            "option_c": "1/6",
            "option_d": "1/3",
            "correct_option": "B",
            "explanation": "20% = 20/100 = 1/5.",
            "difficulty_level": 1,
            "target_time_seconds": 20,
            "language": "en",
            "exam_tags": "ssc_cpo,wbp_si"
        },
        {
            "subject_code": "bengali",
            "topic_name": "Bengali Grammar",
            "subtopic_name": "Sandhi",
            "question_text": "'বিদ্যালয়' শব্দটির সঠিক সন্ধি বিচ্ছেদ কোনটি?",
            "option_a": "বিদ্যা + লয়",
            "option_b": "বিদ্যা + আলয়",
            "option_c": "বিদ + আলয়",
            "option_d": "বিদ্যা + আলয়ঃ",
            "correct_option": "B",
            "explanation": "বিদ্যা + আলয় = বিদ্যালয় (আ + আ = আ)।",
            "difficulty_level": 1,
            "target_time_seconds": 25,
            "language": "bn",
            "exam_tags": "wbp_si,wbp_constable"
        }
    ]

    stats = await ingest_questions(sample_data, verify_with_jev=False)
    assert stats["inserted"] == 2
    assert stats["failed"] == 0

    # Verify presence of the newly inserted Bengali question in database
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Question).where(Question.question_text.contains("বিদ্যালয়"))
        )
        bn_question = result.scalars().first()
        assert bn_question is not None
        assert "বিদ্যা + আলয়" in bn_question.option_b
        assert bn_question.correct_option == "B"
        assert bn_question.language == "bn"
