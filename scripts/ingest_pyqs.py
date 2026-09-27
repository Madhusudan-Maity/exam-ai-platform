import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.schema import DifficultyLevel, Exam, Question, Subject, Subtopic, Topic
from app.schemas.question import QuestionBase
from app.ingestion.jev_verifier import JEVVerifier


async def get_or_create_taxonomy(
    session,
    subject_code: str,
    topic_name: str,
    subtopic_name: str
) -> Subtopic:
    """Finds or creates the Subject -> Topic -> Subtopic hierarchy in SQLite."""
    # 1. Subject
    stmt = select(Subject).where(Subject.code == subject_code)
    result = await session.execute(stmt)
    subject = result.scalars().first()
    if not subject:
        subject = Subject(code=subject_code, name=subject_code.replace("_", " ").title(), is_common_core=True)
        session.add(subject)
        await session.flush()

    # 2. Topic
    stmt = select(Topic).where((Topic.subject_id == subject.id) & (Topic.name == topic_name))
    result = await session.execute(stmt)
    topic = result.scalars().first()
    if not topic:
        topic = Topic(subject_id=subject.id, name=topic_name, yield_score=1.0, difficulty_quadrant=1)
        session.add(topic)
        await session.flush()

    # 3. Subtopic
    stmt = select(Subtopic).where((Subtopic.topic_id == topic.id) & (Subtopic.name == subtopic_name))
    result = await session.execute(stmt)
    subtopic = result.scalars().first()
    if not subtopic:
        slug = subtopic_name.lower().replace(" ", "_").replace("&", "and")
        subtopic = Subtopic(topic_id=topic.id, name=subtopic_name, concept_slug=slug)
        session.add(subtopic)
        await session.flush()

    return subtopic


async def ingest_questions(
    questions_data: List[Dict[str, Any]],
    verify_with_jev: bool = True
) -> Dict[str, int]:
    """Ingests, validates with JEV, and writes questions to the SQLite database."""
    verifier = JEVVerifier()
    stats = {"total": len(questions_data), "verified": 0, "inserted": 0, "failed": 0}

    print(f"📥 Processing {len(questions_data)} questions for ingestion...")

    async with AsyncSessionLocal() as session:
        for idx, q_dict in enumerate(questions_data, 1):
            try:
                # Extract taxonomy fields
                subject_code = q_dict.get("subject_code", "quant")
                topic_name = q_dict.get("topic_name", "Arithmetic")
                subtopic_name = q_dict.get("subtopic_name", "General")

                # Parse and validate with Pydantic
                q_base = QuestionBase(
                    question_text=q_dict["question_text"],
                    option_a=q_dict["option_a"],
                    option_b=q_dict["option_b"],
                    option_c=q_dict["option_c"],
                    option_d=q_dict["option_d"],
                    correct_option=q_dict["correct_option"].upper(),
                    explanation=q_dict["explanation"],
                    difficulty_level=q_dict.get("difficulty_level", DifficultyLevel.LEVEL_2.value),
                    target_time_seconds=q_dict.get("target_time_seconds", 45),
                    language=q_dict.get("language", "en"),
                    exam_tags=q_dict.get("exam_tags", "ssc_cpo,ssc_je,wbp_si"),
                    source_info=q_dict.get("source_info", "Official PYQ")
                )

                # Optional JEV Verification
                is_verified = False
                if verify_with_jev:
                    jev_result = await verifier.verify_question(q_base)
                    if jev_result.official_key_verified:
                        is_verified = True
                        stats["verified"] += 1
                        print(f"  [Q{idx}] ✅ JEV Verified: {q_base.question_text[:40]}...")
                    else:
                        print(f"  [Q{idx}] ⚠️ JEV Discrepancy: Official={q_base.correct_option}, JEV={jev_result.verified_correct_option}. Notes: {jev_result.critique_notes[:60]}")

                # Get Subtopic ID
                subtopic = await get_or_create_taxonomy(session, subject_code, topic_name, subtopic_name)

                # Create DB Model
                db_question = Question(
                    subtopic_id=subtopic.id,
                    question_text=q_base.question_text,
                    option_a=q_base.option_a,
                    option_b=q_base.option_b,
                    option_c=q_base.option_c,
                    option_d=q_base.option_d,
                    correct_option=q_base.correct_option,
                    explanation=q_base.explanation,
                    difficulty_level=q_base.difficulty_level,
                    target_time_seconds=q_base.target_time_seconds,
                    language=q_base.language,
                    exam_tags=q_base.exam_tags,
                    source_info=q_base.source_info,
                    is_verified=is_verified
                )

                session.add(db_question)
                stats["inserted"] += 1

            except Exception as e:
                stats["failed"] += 1
                print(f"  [Q{idx}] ❌ Error ingesting question: {e}")

        await session.commit()

    print(f"\n📊 Ingestion Complete! Total: {stats['total']}, Inserted: {stats['inserted']}, Verified: {stats['verified']}, Failed: {stats['failed']}")
    return stats


async def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest_pyqs.py <path_to_questions.json>")
        print("Example: python scripts/ingest_pyqs.py scripts/sample_pyqs.json")
        return

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "questions" in data:
        data = data["questions"]

    await ingest_questions(data, verify_with_jev=True)


if __name__ == "__main__":
    asyncio.run(main())
