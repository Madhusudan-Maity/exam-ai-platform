import pytest
from app.engines.pareto import ParetoYieldEngine
from app.engines.student_model import IRTBKTEngine


def test_pareto_yield_calculation():
    """Verify Pareto Yield = (Frequency * Marks) / Effort."""
    engine = ParetoYieldEngine()
    # Topic A: 20 past questions, 2.0 marks avg, 4.0 hours effort -> Yield = 10.0
    yield_a = engine.calculate_yield_score(20, 2.0, 4.0)
    assert yield_a == 10.0

    # Topic B: 2 past questions, 1.0 marks avg, 8.0 hours effort -> Yield = 0.25
    yield_b = engine.calculate_yield_score(2, 1.0, 8.0)
    assert yield_b == 0.25


def test_pareto_quadrant_classification():
    """Verify classification into 4 quadrants."""
    engine = ParetoYieldEngine()
    # High Marks (>= 4.0), Low Effort (<= 6.0) -> Q1 (Must Master)
    result_q1 = engine.analyze_topic("Syllogisms", "reasoning", 15, 2.0, 3.0)
    assert result_q1.quadrant == 1
    assert "MUST MASTER" in result_q1.recommendation

    # Low Marks (< 4.0), High Effort (> 6.0) -> Q4 (Low Priority)
    result_q4 = engine.analyze_topic("Ancient Genealogies", "general_studies", 2, 1.0, 10.0)
    assert result_q4.quadrant == 4
    assert "LOW PRIORITY" in result_q4.recommendation


def test_bkt_mastery_updates():
    """Verify Bayesian Knowledge Tracing increases on correct and decreases on incorrect."""
    initial_p = 0.20
    # Correct response increases mastery
    p_after_correct = IRTBKTEngine.update_bkt_mastery(initial_p, is_correct=True)
    assert p_after_correct > initial_p

    # Incorrect response decreases mastery
    p_after_wrong = IRTBKTEngine.update_bkt_mastery(p_after_correct, is_correct=False)
    assert p_after_wrong < p_after_correct


def test_irt_theta_difficulty_scaling():
    """Verify IRT ability parameter theta scales according to question difficulty level."""
    initial_theta = 0.0
    # Answering a Level 3 (Advanced SSC CPO) question correctly gives a significant boost
    theta_cpo = IRTBKTEngine.update_theta(initial_theta, is_correct=True, difficulty_level=3)
    assert theta_cpo > initial_theta

    # Answering a Level 1 (WBP Constable) question incorrectly drops theta
    theta_wbp_slip = IRTBKTEngine.update_theta(initial_theta, is_correct=False, difficulty_level=1)
    assert theta_wbp_slip < initial_theta


def test_multi_exam_readiness_projection():
    """Verify multi-exam readiness reflects relative exam difficulty benchmarks."""
    # A student with strong theta (+1.2) should be 90%+ ready for WBP Constable, but approaching for SSC CPO
    thetas = {"quant": 1.2, "reasoning": 1.4, "general_studies": 1.0, "english": 1.2}
    mastery = {"Arithmetic": 0.85, "Polity": 0.75}

    readiness = IRTBKTEngine.compute_exam_readiness(thetas, mastery)
    assert len(readiness) == 4

    wbp_constable = next(r for r in readiness if r.exam_code == "wbp_constable")
    ssc_cpo = next(r for r in readiness if r.exam_code == "ssc_cpo")

    # WBP Constable readiness should be strictly higher than SSC CPO for the same theta
    assert wbp_constable.readiness_percentage >= ssc_cpo.readiness_percentage
    assert "🟢" in wbp_constable.status_badge
