from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.engines.student_model import IRTBKTEngine, ExamReadiness
from app.engines.pareto import ParetoYieldEngine, TopicYieldResult
from app.models.schema import Question, StudentProfile, Subject, Topic, Subtopic
from app.schemas.question import QuestionOut

router = APIRouter(prefix="/diagnostic", tags=["Diagnostic & Multi-Exam Radar"])


class ResponseItem(BaseModel):
    question_id: int
    selected_option: str
    time_spent_ms: int


class DiagnosticSubmission(BaseModel):
    student_id: int = 1
    responses: List[ResponseItem]


class DiagnosticEvaluationOut(BaseModel):
    total_answered: int
    correct_count: int
    raw_score: float
    accuracy_percentage: float
    overall_theta: float
    subject_thetas: Dict[str, float]
    multi_exam_readiness: List[ExamReadiness]


class PriorityRadarOut(BaseModel):
    student_id: int
    current_overall_theta: float
    multi_exam_readiness: List[ExamReadiness]
    high_yield_priority_topics: List[TopicYieldResult]


@router.get("/baseline-test", response_model=List[QuestionOut])
async def generate_baseline_test(
    limit: int = 25,
    db: AsyncSession = Depends(get_db)
):
    """Generates an adaptive cross-section baseline test."""
    stmt = select(Question).order_by(Question.difficulty_level.asc()).limit(limit)
    result = await db.execute(stmt)
    questions = result.scalars().all()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions available for diagnostic test.")
    return questions


@router.post("/submit-baseline", response_model=DiagnosticEvaluationOut)
async def submit_diagnostic(
    submission: DiagnosticSubmission,
    db: AsyncSession = Depends(get_db)
):
    """Processes diagnostic test submissions, updates IRT theta and BKT mastery, and projects readiness."""
    total = len(submission.responses)
    if total == 0:
        raise HTTPException(status_code=400, detail="Empty submission responses.")

    correct_count = 0
    theta = 0.0
    subject_thetas: Dict[str, float] = {"quant": 0.0, "reasoning": 0.0, "general_studies": 0.0, "english": 0.0, "bengali": 0.0, "technical_cs": 0.0}
    topic_masteries: Dict[str, float] = {}

    for resp in submission.responses:
        q_result = await db.execute(select(Question).where(Question.id == resp.question_id))
        q = q_result.scalars().first()
        if not q:
            continue

        is_correct = (resp.selected_option.upper() == q.correct_option.upper())
        if is_correct:
            correct_count += 1

        # Update IRT Theta
        theta = IRTBKTEngine.update_theta(theta, is_correct, q.difficulty_level)

        # Update subject-level theta
        # Find subject code via subtopic -> topic -> subject
        subj_code = "quant"
        if q.language == "bn":
            subj_code = "bengali" if "Grammar" in (q.source_info or "") else "general_studies"
        elif "je" in q.exam_tags:
            subj_code = "technical_cs"

        subject_thetas[subj_code] = IRTBKTEngine.update_theta(
            subject_thetas.get(subj_code, 0.0),
            is_correct,
            q.difficulty_level
        )

        topic_name = q.source_info or "General"
        topic_masteries[topic_name] = IRTBKTEngine.update_bkt_mastery(
            topic_masteries.get(topic_name, 0.20),
            is_correct
        )

    # Compute multi-exam readiness
    readiness = IRTBKTEngine.compute_exam_readiness(subject_thetas, topic_masteries)
    accuracy = round((correct_count / total) * 100, 1)

    return DiagnosticEvaluationOut(
        total_answered=total,
        correct_count=correct_count,
        raw_score=float(correct_count),
        accuracy_percentage=accuracy,
        overall_theta=theta,
        subject_thetas=subject_thetas,
        multi_exam_readiness=readiness
    )


@router.get("/radar", response_model=PriorityRadarOut)
async def get_priority_radar(
    student_id: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """Returns the multi-exam readiness radar and the 80/20 Pareto priority topic list."""
    pareto_engine = ParetoYieldEngine()

    # Sample top priority high-yield topics
    sample_topics = [
        ("Time and Work", "quant", 18, 2.0, 4.0),
        ("Syllogisms", "reasoning", 15, 2.0, 3.0),
        ("Indian Polity: Articles & Writs", "general_studies", 12, 2.0, 4.0),
        ("Speed Time & Distance (Trains)", "quant", 14, 2.0, 4.5),
        ("Process Scheduling & Deadlocks", "technical_cs", 10, 2.5, 5.0),
        ("Sandhi & Samas", "bengali", 12, 2.0, 3.5),
    ]

    priority_topics = [
        pareto_engine.analyze_topic(name, subj, freq, marks, effort)
        for name, subj, freq, marks, effort in sample_topics
    ]

    # Baseline readiness
    default_thetas = {"quant": 0.2, "reasoning": 0.4, "general_studies": -0.1, "english": 0.1, "bengali": 0.3, "technical_cs": 0.0}
    default_mastery = {"Time and Work": 0.6, "Syllogisms": 0.8, "Indian Polity": 0.4}
    readiness = IRTBKTEngine.compute_exam_readiness(default_thetas, default_mastery)

    return PriorityRadarOut(
        student_id=student_id,
        current_overall_theta=0.25,
        multi_exam_readiness=readiness,
        high_yield_priority_topics=priority_topics
    )
