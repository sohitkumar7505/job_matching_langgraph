"""
guardrails/output_guardrails.py
==============================================================
OUTPUT GUARDRAILS for the Job Matching Engine Scorer Agent

Guardrail 3 — PII Detector
  Scans LLM output text for personally identifiable information
  (emails, phone numbers, Aadhaar/SSN patterns, etc.) and
  redacts or blocks the response.

Guardrail 4 — Output Format Validator (Pydantic)
  Ensures the LLM's JSON output strictly conforms to the expected
  schema: score is int 1–10, category is a valid enum, reason is
  a non-empty string, and category matches the score range.
==============================================================
"""

import re
import json
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator


# ─────────────────────────────────────────────────────────────
# Custom Exception
# ─────────────────────────────────────────────────────────────
class OutputValidationError(Exception):
    """Raised when an LLM output fails guardrail checks."""
    def __init__(self, rule: str, message: str):
        self.rule = rule
        self.message = message
        super().__init__(f"[OutputGuardrail:{rule}] {message}")


# ─────────────────────────────────────────────────────────────
# GUARDRAIL 3: PII Detector
# ─────────────────────────────────────────────────────────────

_PII_PATTERNS = {
    "email":   re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
    "phone_in": re.compile(r"(\+91[\-\s]?)?[6-9]\d{9}"),           # Indian mobile
    "phone_intl": re.compile(r"\+?1?\s?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}"),  # US/intl
    "aadhaar": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),           # Aadhaar
    "ssn":     re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),               # US SSN
    "pan":     re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),              # PAN card
    "credit_card": re.compile(r"\b(?:\d{4}[\s\-]?){3}\d{4}\b"),   # credit card
}

_REDACT_PLACEHOLDER = "[REDACTED]"


def detect_pii(text: str) -> dict:
    """
    Scan text for PII. Returns a dict of {pii_type: [matches]} found.
    Empty dict means no PII detected.
    """
    found = {}
    for pii_type, pattern in _PII_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            found[pii_type] = matches
    return found


def redact_pii(text: str) -> str:
    """
    Replace any detected PII in text with [REDACTED].
    Returns the sanitized text.
    """
    for pattern in _PII_PATTERNS.values():
        text = pattern.sub(_REDACT_PLACEHOLDER, text)
    return text


def check_output_for_pii(output_text: str, raise_on_detect: bool = False) -> str:
    """
    Checks output for PII. By default, redacts and returns clean text.
    If raise_on_detect=True, raises OutputValidationError instead.

    Returns:
        Sanitized output text (with PII redacted).
    """
    pii_found = detect_pii(output_text)
    if pii_found:
        if raise_on_detect:
            types_found = list(pii_found.keys())
            raise OutputValidationError(
                rule="PII_DETECTED",
                message=f"LLM output contains PII ({', '.join(types_found)}). Response blocked."
            )
        # Default: redact and return
        return redact_pii(output_text)
    return output_text


# ─────────────────────────────────────────────────────────────
# GUARDRAIL 4: Output Format Validator (Pydantic)
# ─────────────────────────────────────────────────────────────

class ScoreCategory(str, Enum):
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"


class ScoredJobOutput(BaseModel):
    """
    Strict Pydantic model for the Scorer Agent's JSON output.
    Validates:
    - score: integer 1–10
    - category: HIGH | MEDIUM | LOW (must match score range)
    - reason: non-empty string, no PII
    """
    score: int
    category: ScoreCategory
    reason: str

    @field_validator("score")
    @classmethod
    def score_must_be_in_range(cls, v: int) -> int:
        if not (1 <= v <= 10):
            raise ValueError(f"score must be between 1 and 10, got {v}")
        return v

    @field_validator("reason")
    @classmethod
    def reason_must_be_non_empty(cls, v: str) -> str:
        if not v or len(v.strip()) < 10:
            raise ValueError("reason must be a meaningful non-empty string (≥ 10 chars)")
        # Auto-redact any PII in the reason field
        return redact_pii(v.strip())

    @model_validator(mode="after")
    def category_must_match_score(self) -> "ScoredJobOutput":
        score = self.score
        category = self.category
        if score >= 8 and category != ScoreCategory.HIGH:
            raise ValueError(f"score={score} requires category=HIGH, got {category}")
        if 5 <= score <= 7 and category != ScoreCategory.MEDIUM:
            raise ValueError(f"score={score} requires category=MEDIUM, got {category}")
        if score <= 4 and category != ScoreCategory.LOW:
            raise ValueError(f"score={score} requires category=LOW, got {category}")
        return self


def validate_output(raw_output: str) -> ScoredJobOutput:
    """
    Master output validation function — runs all output guardrails.

    Args:
        raw_output: Raw string from the LLM.

    Returns:
        Validated ScoredJobOutput Pydantic model.

    Raises:
        OutputValidationError on any guardrail failure.

    Usage:
        from guardrails.output_guardrails import validate_output, OutputValidationError
        try:
            result = validate_output(llm_raw_response)
        except OutputValidationError as e:
            print(f"Output blocked: {e}")
    """
    # Step 1: PII scan and redact (non-blocking — redacts in place)
    clean_output = check_output_for_pii(raw_output, raise_on_detect=False)

    # Step 2: Extract JSON from the output (handle extra whitespace/text)
    try:
        # Try direct parse first
        data = json.loads(clean_output.strip())
    except json.JSONDecodeError:
        # Try to extract JSON object using regex
        json_match = re.search(r'\{[^{}]*\}', clean_output, re.DOTALL)
        if not json_match:
            raise OutputValidationError(
                rule="INVALID_JSON",
                message=f"LLM output is not valid JSON: {clean_output[:200]}"
            )
        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError as e:
            raise OutputValidationError(
                rule="INVALID_JSON",
                message=f"Could not parse JSON from output: {e}"
            )

    # Step 3: Enforce integer type for score (regression bug fix)
    if "score" in data and isinstance(data["score"], str):
        try:
            data["score"] = int(data["score"])
        except ValueError:
            raise OutputValidationError(
                rule="INVALID_SCORE_TYPE",
                message=f"'score' field must be an integer, got string: '{data['score']}'"
            )

    # Step 4: Pydantic schema validation + business rules
    try:
        validated = ScoredJobOutput(**data)
    except Exception as e:
        raise OutputValidationError(
            rule="SCHEMA_VALIDATION",
            message=str(e)
        )

    return validated
