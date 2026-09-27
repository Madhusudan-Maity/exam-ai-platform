import json
from typing import Optional
from google import genai
from google.genai import types

from app.config import settings
from app.schemas.question import JEVVerificationResult, QuestionBase


class JEVVerifier:
    """Judge-Evaluator-Verifier harness to validate questions, verify answer keys, and detect traps."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    async def verify_question(self, question: QuestionBase) -> JEVVerificationResult:
        """Independently solves the question, checks the answer key, and extracts traps."""
        if not self.client:
            # Fallback deterministic pass-through when API key is not configured locally yet
            return JEVVerificationResult(
                is_mathematically_sound=True,
                official_key_verified=True,
                confidence_score=1.0,
                verified_correct_option=question.correct_option,
                critique_notes="Pass-through verification (Gemini API key not set).",
                extracted_trap_pattern=None
            )

        prompt = f"""
You are an expert exam referee and psychometric judge for Indian competitive exams (SSC CPO, SSC JE, WBP Police).
Independently solve this question step-by-step from scratch WITHOUT looking at the provided answer first.
Then, compare your derived answer with the given Official Option ({question.correct_option}).

QUESTION:
{question.question_text}

OPTIONS:
(A) {question.option_a}
(B) {question.option_b}
(C) {question.option_c}
(D) {question.option_d}

GIVEN OFFICIAL OPTION: {question.correct_option}
GIVEN EXPLANATION: {question.explanation}
LANGUAGE: {question.language}

OUTPUT REQUIREMENTS:
Output strict JSON matching the schema:
- is_mathematically_sound (boolean)
- official_key_verified (boolean: true if official key matches your solution)
- confidence_score (float 0.0 to 1.0)
- verified_correct_option (string: A, B, C, or D)
- critique_notes (string: concise step-by-step proof)
- extracted_trap_pattern (string or null: common trick/unit conversion trap that students fall for)
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JEVVerificationResult,
                temperature=0.1
            )
        )

        result_dict = json.loads(response.text)
        return JEVVerificationResult(**result_dict)
