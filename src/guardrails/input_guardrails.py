"""
guardrails/input_guardrails.py
==============================================================
INPUT GUARDRAILS for the Job Matching Engine Scorer Agent

Guardrail 1 — Prompt Injection Detector
  Scans the job description, candidate fields, and any free-text
  inputs for known injection patterns (keyword blacklist + regex).

Guardrail 2 — Input Validator
  Validates structure and content of the candidate + job payload:
  - Required fields present
  - Types correct (strings, lists, int)
  - Description length within bounds (20–5000 chars)
  - Skills list non-empty
  - experience_years / experience_required are non-negative integers
==============================================================
"""

import re
from typing import Any, Dict

# ─────────────────────────────────────────────────────────────
# Custom Exception
# ─────────────────────────────────────────────────────────────
class InputValidationError(Exception):
    """Raised when an input fails guardrail checks."""
    def __init__(self, rule: str, message: str):
        self.rule = rule
        self.message = message
        super().__init__(f"[InputGuardrail:{rule}] {message}")


# ─────────────────────────────────────────────────────────────
# GUARDRAIL 1: Prompt Injection Detector
# ─────────────────────────────────────────────────────────────

# Keyword-based blacklist (case-insensitive)
_INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "ignore all instructions",
    "disregard your guidelines",
    "forget your system prompt",
    "act as a different ai",
    "you are now dan",
    "you are now a",
    "override your instructions",
    "bypass your restrictions",
    "jailbreak",
    "pretend you are",
    "roleplay as",
    "hypothetically speaking, ignore",
    "from now on you will",
    "new instruction:",
    "system prompt:",
    "<<<",           # common injection delimiters
    ">>>",
    "```system",
    "[system]",
    "[[system]]",
]

# Regex patterns for more subtle injections
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"(you\s+are\s+now|act\s+as|pretend\s+(to\s+be|you('re|\s+are)))", re.IGNORECASE),
    re.compile(r"(disregard|forget|override|bypass)\s+(your\s+)?(guidelines|rules|prompt|constraints)", re.IGNORECASE),
    re.compile(r"\bDAN\b"),  # "Do Anything Now" jailbreak
    re.compile(r"score\s*(=|:)\s*10\s*(for\s+all|always|every)", re.IGNORECASE),
    re.compile(r"always\s+(give|assign|return)\s+(a\s+)?(score\s+of\s+)?10", re.IGNORECASE),
]


def detect_prompt_injection(text: str) -> bool:
    """
    Returns True if any injection pattern is found in text.
    Checks both keyword blacklist and regex patterns.
    """
    if not text:
        return False
    text_lower = text.lower()

    # Keyword check
    for keyword in _INJECTION_KEYWORDS:
        if keyword in text_lower:
            return True

    # Regex check
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            return True

    return False


def check_injection_in_payload(candidate: Dict, job: Dict) -> None:
    """
    Scan all free-text fields in candidate and job for injection attempts.
    Raises InputValidationError if injection is detected.
    """
    fields_to_scan = []

    # Candidate text fields
    for key in ("name", "title"):
        if key in candidate:
            fields_to_scan.append((f"candidate.{key}", str(candidate[key])))

    # Job text fields
    for key in ("title", "description", "location"):
        if key in job:
            fields_to_scan.append((f"job.{key}", str(job[key])))

    # Also scan skills lists as concatenated strings
    if "skills" in candidate:
        fields_to_scan.append(("candidate.skills", " ".join(candidate["skills"])))
    if "required_skills" in job:
        fields_to_scan.append(("job.required_skills", " ".join(job["required_skills"])))

    for field_name, text in fields_to_scan:
        if detect_prompt_injection(text):
            raise InputValidationError(
                rule="PROMPT_INJECTION",
                message=f"Injection pattern detected in field '{field_name}'. Request blocked."
            )


# ─────────────────────────────────────────────────────────────
# GUARDRAIL 2: Input Structure & Content Validator
# ─────────────────────────────────────────────────────────────

_MIN_DESCRIPTION_LENGTH = 20     # chars
_MAX_DESCRIPTION_LENGTH = 5000   # chars
_MAX_SKILLS_COUNT = 100


def validate_candidate(candidate: Any) -> None:
    """Validate candidate profile structure and content."""
    if not isinstance(candidate, dict):
        raise InputValidationError("INVALID_TYPE", "Candidate must be a dict/object.")

    required_fields = ["name", "title", "experience_years", "skills"]
    for field in required_fields:
        if field not in candidate:
            raise InputValidationError("MISSING_FIELD", f"Candidate missing required field: '{field}'")

    if not isinstance(candidate["name"], str) or len(candidate["name"].strip()) == 0:
        raise InputValidationError("INVALID_FIELD", "Candidate 'name' must be a non-empty string.")

    if not isinstance(candidate["experience_years"], (int, float)) or candidate["experience_years"] < 0:
        raise InputValidationError("INVALID_FIELD", "Candidate 'experience_years' must be a non-negative number.")

    if not isinstance(candidate["skills"], list):
        raise InputValidationError("INVALID_FIELD", "Candidate 'skills' must be a list.")

    if len(candidate["skills"]) > _MAX_SKILLS_COUNT:
        raise InputValidationError("INVALID_FIELD", f"Candidate skills list exceeds maximum of {_MAX_SKILLS_COUNT} items.")


def validate_job(job: Any) -> None:
    """Validate job posting structure and content."""
    if not isinstance(job, dict):
        raise InputValidationError("INVALID_TYPE", "Job must be a dict/object.")

    required_fields = ["job_id", "title", "description", "required_skills"]
    for field in required_fields:
        if field not in job:
            raise InputValidationError("MISSING_FIELD", f"Job missing required field: '{field}'")

    desc = job.get("description", "")
    if not isinstance(desc, str):
        raise InputValidationError("INVALID_FIELD", "Job 'description' must be a string.")

    if len(desc) > _MAX_DESCRIPTION_LENGTH:
        raise InputValidationError(
            "INPUT_TOO_LONG",
            f"Job description is {len(desc)} chars, exceeding the maximum of {_MAX_DESCRIPTION_LENGTH}. "
            "Please truncate or summarize the description before processing."
        )

    if not isinstance(job["required_skills"], list):
        raise InputValidationError("INVALID_FIELD", "Job 'required_skills' must be a list.")

    exp = job.get("experience_required", 0)
    if not isinstance(exp, (int, float)) or exp < 0:
        raise InputValidationError("INVALID_FIELD", "Job 'experience_required' must be a non-negative number.")


def validate_input(candidate: Any, job: Any) -> None:
    """
    Master input validation function — runs all guardrails in order.
    Raises InputValidationError on first failure.

    Usage:
        from guardrails.input_guardrails import validate_input, InputValidationError
        try:
            validate_input(candidate, job)
        except InputValidationError as e:
            print(f"Blocked: {e}")
    """
    # Step 1: Structure validation
    validate_candidate(candidate)
    validate_job(job)

    # Step 2: Injection detection (after structure validated)
    check_injection_in_payload(candidate, job)
