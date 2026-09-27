import math
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ExamReadiness(BaseModel):
    exam_code: str
    exam_name: str
    target_cutoff_marks: float
    projected_marks: float
    readiness_percentage: float
    status_badge: str  # "Ready 🟢", "Approaching 🟡", "Critical Gap 🔴"
    strong_topics: List[str]
    critical_gap_topics: List[str]


class StudentKnowledgeState(BaseModel):
    student_id: int
    overall_theta: float = Field(0.0, description="Latent ability parameter from -3.0 to +3.0")
    subject_thetas: Dict[str, float] = Field(default_factory=dict)
    topic_masteries: Dict[str, float] = Field(default_factory=dict, description="P(L) probability 0.0 to 1.0")
    multi_exam_readiness: List[ExamReadiness] = Field(default_factory=list)


class IRTBKTEngine:
    """Dynamic Student Profiler using Bayesian Knowledge Tracing & Item Response Theory."""

    # BKT Default Hyperparameters
    P_INIT = 0.20   # Prior probability of knowing the concept
    P_TRANS = 0.15  # Probability of learning concept after an opportunity
    P_SLIP = 0.10   # Probability of making a slip despite knowing concept
    P_GUESS = 0.25  # Probability of guessing correctly (1 in 4 options)

    @classmethod
    def update_bkt_mastery(
        cls,
        current_p_l: float,
        is_correct: bool,
        p_slip: float = P_SLIP,
        p_guess: float = P_GUESS,
        p_trans: float = P_TRANS
    ) -> float:
        """
        Updates Bayesian Knowledge Tracing mastery probability based on response evidence.
        """
        if is_correct:
            numerator = current_p_l * (1 - p_slip)
            denominator = numerator + (1 - current_p_l) * p_guess
        else:
            numerator = current_p_l * p_slip
            denominator = numerator + (1 - current_p_l) * (1 - p_guess)

        posterior_p_l = numerator / (denominator if denominator > 0 else 1e-6)
        # Apply learning transition
        new_p_l = posterior_p_l + (1 - posterior_p_l) * p_trans
        return round(min(max(new_p_l, 0.01), 0.99), 4)

    @classmethod
    def calculate_irt_probability(cls, theta: float, difficulty_b: float, discrimination_a: float = 1.0) -> float:
        """
        2-Parameter Logistic IRT Model:
        P(Correct | theta) = 1 / (1 + exp(-a * (theta - b)))
        """
        exponent = -discrimination_a * (theta - difficulty_b)
        # Prevent math overflow
        if exponent > 20:
            return 0.0
        elif exponent < -20:
            return 1.0
        return 1.0 / (1.0 + math.exp(exponent))

    @classmethod
    def update_theta(cls, current_theta: float, is_correct: bool, difficulty_level: int, learning_rate: float = 0.25) -> float:
        """
        Updates ability parameter theta based on question difficulty level:
        - Level 1: b = -1.0 (Basic / WBP Constable)
        - Level 2: b = 0.0 (Applied / SSC JE / WBP SI)
        - Level 3: b = +1.2 (Advanced / SSC CPO)
        """
        difficulty_b_map = {1: -1.0, 2: 0.0, 3: 1.2}
        b = difficulty_b_map.get(difficulty_level, 0.0)
        p_expected = cls.calculate_irt_probability(current_theta, b)
        outcome = 1.0 if is_correct else 0.0
        new_theta = current_theta + learning_rate * (outcome - p_expected)
        return round(min(max(new_theta, -3.0), 3.0), 3)

    @classmethod
    def compute_exam_readiness(
        cls,
        subject_thetas: Dict[str, float],
        topic_masteries: Dict[str, float]
    ) -> List[ExamReadiness]:
        """
        Maps subject ability thetas against target exam cutoffs and benchmarks.
        """
        avg_theta = sum(subject_thetas.values()) / len(subject_thetas) if subject_thetas else 0.0

        # Exam difficulty & cutoff profiles
        exam_profiles = [
            {
                "code": "wbp_constable",
                "name": "WBP / Kolkata Police Constable",
                "target_cutoff": 65.0,
                "total_marks": 100.0,
                "required_theta": -0.2,
            },
            {
                "code": "wbp_si",
                "name": "WBP / Kolkata Police Sub-Inspector",
                "target_cutoff": 135.0,
                "total_marks": 200.0,
                "required_theta": 0.4,
            },
            {
                "code": "ssc_je_cs",
                "name": "SSC JE (CS/IT Technical)",
                "target_cutoff": 130.0,
                "total_marks": 200.0,
                "required_theta": 0.5,
            },
            {
                "code": "ssc_cpo",
                "name": "SSC CPO (Sub-Inspector)",
                "target_cutoff": 145.0,
                "total_marks": 200.0,
                "required_theta": 0.8,
            },
        ]

        readiness_list = []
        for profile in exam_profiles:
            # Projected marks based on logistic mastery curve
            z = (avg_theta - profile["required_theta"]) * 1.5
            p_score = 1.0 / (1.0 + math.exp(-z)) if abs(z) < 20 else (1.0 if z > 0 else 0.0)
            projected_marks = round(p_score * profile["total_marks"], 1)
            readiness_pct = round(min(max((projected_marks / profile["target_cutoff"]) * 100, 0), 100), 1)

            if readiness_pct >= 90:
                badge = "Ready 🟢"
            elif readiness_pct >= 70:
                badge = "Approaching 🟡"
            else:
                badge = "Critical Gap 🔴"

            # Filter strong vs gap topics
            strong = [t for t, p in topic_masteries.items() if p >= 0.70]
            gaps = [t for t, p in topic_masteries.items() if p < 0.50]

            readiness_list.append(
                ExamReadiness(
                    exam_code=profile["code"],
                    exam_name=profile["name"],
                    target_cutoff_marks=profile["target_cutoff"],
                    projected_marks=projected_marks,
                    readiness_percentage=readiness_pct,
                    status_badge=badge,
                    strong_topics=strong[:5],
                    critical_gap_topics=gaps[:5]
                )
            )

        return readiness_list
