from typing import Dict, List, Tuple
from pydantic import BaseModel, Field


class TopicYieldResult(BaseModel):
    topic_name: str
    subject_code: str
    historical_frequency: int
    avg_marks_weight: float
    cognitive_effort_hours: float
    yield_score: float
    quadrant: int = Field(..., ge=1, le=4, description="1: Must Master, 2: Deep Drill, 3: Quick Rev, 4: Skip/Low Priority")
    quadrant_label: str
    recommendation: str


class ParetoYieldEngine:
    """Computes the 80/20 Pareto Yield Score and classifies topics into actionable quadrants."""

    @staticmethod
    def calculate_yield_score(
        historical_frequency: int,
        avg_marks_weight: float,
        cognitive_effort_hours: float
    ) -> float:
        """Yield = (Historical Frequency * Average Marks) / Cognitive Effort Hours."""
        if cognitive_effort_hours <= 0:
            cognitive_effort_hours = 1.0
        return round((historical_frequency * avg_marks_weight) / cognitive_effort_hours, 2)

    @staticmethod
    def classify_quadrant(
        marks_density: float,
        cognitive_effort_hours: float,
        median_marks: float = 4.0,
        median_effort: float = 6.0
    ) -> Tuple[int, str, str]:
        """
        Classifies topic into 4 Quadrants:
        - Q1 (High Marks, Low Effort): MUST MASTER FIRST
        - Q2 (High Marks, High Effort): STRUCTURED DRILLS
        - Q3 (Low Marks, Low Effort): QUICK REVISION
        - Q4 (Low Marks, High Effort): LOW PRIORITY / SKIP IF TIME SHORT
        """
        is_high_marks = marks_density >= median_marks
        is_low_effort = cognitive_effort_hours <= median_effort

        if is_high_marks and is_low_effort:
            return (
                1,
                "Quadrant 1: High Yield / High ROI",
                "MUST MASTER FIRST: Maximum scoring potential with minimum study hours."
            )
        elif is_high_marks and not is_low_effort:
            return (
                2,
                "Quadrant 2: High Yield / Deep Drill",
                "STRUCTURED DRILLS: High exam weightage; allocate dedicated practice blocks."
            )
        elif not is_high_marks and is_low_effort:
            return (
                3,
                "Quadrant 3: Moderate Yield / Quick Recall",
                "QUICK REVISION: Low effort formulas & static facts for rapid last-minute recall."
            )
        else:
            return (
                4,
                "Quadrant 4: Low Yield / High Effort",
                "LOW PRIORITY: Deprioritize or skip if exam is within 45 days."
            )

    def analyze_topic(
        self,
        topic_name: str,
        subject_code: str,
        historical_frequency: int,
        avg_marks_weight: float,
        cognitive_effort_hours: float,
        median_marks: float = 4.0,
        median_effort: float = 6.0
    ) -> TopicYieldResult:
        yield_score = self.calculate_yield_score(
            historical_frequency,
            avg_marks_weight,
            cognitive_effort_hours
        )
        quadrant, label, recommendation = self.classify_quadrant(
            marks_density=avg_marks_weight * historical_frequency / 5.0,  # normalized per shift
            cognitive_effort_hours=cognitive_effort_hours,
            median_marks=median_marks,
            median_effort=median_effort
        )
        return TopicYieldResult(
            topic_name=topic_name,
            subject_code=subject_code,
            historical_frequency=historical_frequency,
            avg_marks_weight=avg_marks_weight,
            cognitive_effort_hours=cognitive_effort_hours,
            yield_score=yield_score,
            quadrant=quadrant,
            quadrant_label=label,
            recommendation=recommendation
        )
