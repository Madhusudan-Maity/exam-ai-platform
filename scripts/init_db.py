import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.database import Base, engine, AsyncSessionLocal
from app.models.schema import Exam, Subject, StudentProfile
from sqlalchemy import select


async def seed_database():
    print("🚀 Initializing SQLite Database & Seeding Standard Exam Taxonomies...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(Exam))
        if result.scalars().first():
            print("✅ Database already initialized and seeded.")
            return

        # 1. Seed Exams
        exams = [
            Exam(
                code="ssc_cpo",
                name="SSC CPO (Sub-Inspector in Delhi Police & CAPFs)",
                total_marks=200.0,
                duration_minutes=120,
                negative_mark_ratio=0.25,
                languages="en,hi"
            ),
            Exam(
                code="ssc_je_cs",
                name="SSC JE (Junior Engineer - CS/IT)",
                total_marks=200.0,
                duration_minutes=120,
                negative_mark_ratio=0.33,
                languages="en,hi"
            ),
            Exam(
                code="wbp_si",
                name="WBP / Kolkata Police Sub-Inspector (Prelims)",
                total_marks=200.0,
                duration_minutes=90,
                negative_mark_ratio=0.25,
                languages="bn,en,hi"
            ),
            Exam(
                code="wbp_constable",
                name="WBP / Kolkata Police Constable (Prelims)",
                total_marks=100.0,
                duration_minutes=60,
                negative_mark_ratio=0.25,
                languages="bn,en,hi"
            ),
        ]
        session.add_all(exams)

        # 2. Seed Common Core & Specialized Subjects
        subjects = [
            Subject(code="quant", name="Quantitative Aptitude (Mathematics)", is_common_core=True),
            Subject(code="reasoning", name="General Intelligence & Reasoning", is_common_core=True),
            Subject(code="general_studies", name="General Studies & Static GK", is_common_core=True),
            Subject(code="english", name="English Language & Comprehension", is_common_core=True),
            Subject(code="bengali", name="Bengali Language & Regional Grammar", is_common_core=False),
            Subject(code="technical_cs", name="Computer Science & IT Technical (SSC JE)", is_common_core=False),
        ]
        session.add_all(subjects)

        # 3. Seed Default Student Profile
        student = StudentProfile(name="Aspirant", current_exam_focus="all")
        session.add(student)

        await session.commit()
        print("✅ Successfully seeded 4 standard exams, 6 subjects, and student profile!")


if __name__ == "__main__":
    asyncio.run(seed_database())
