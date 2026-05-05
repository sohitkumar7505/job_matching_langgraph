"""
guardrails/action_guardrails.py
==============================================================
ACTION GUARDRAIL — Token Cost Limiter

Tracks cumulative token usage across the entire agent session.
Blocks further LLM calls once the configured token budget is
exhausted, preventing runaway API costs.

Estimated cost reference (Groq / gpt-oss-120b):
  ~$0.90 per 1M input tokens, ~$0.90 per 1M output tokens
  50,000 token budget ≈ $0.045 per session (configurable)
==============================================================
"""

import threading
from typing import Optional


# ─────────────────────────────────────────────────────────────
# Custom Exception
# ─────────────────────────────────────────────────────────────
class CostLimitExceededError(Exception):
    """Raised when the session token budget is exhausted."""
    def __init__(self, used: int, limit: int):
        self.used = used
        self.limit = limit
        super().__init__(
            f"[ActionGuardrail:COST_LIMIT] Token budget exceeded. "
            f"Used {used:,} of {limit:,} allowed tokens. "
            "Further LLM calls are blocked for this session."
        )


# ─────────────────────────────────────────────────────────────
# Token Cost Limiter
# ─────────────────────────────────────────────────────────────

class TokenCostLimiter:
    """
    Thread-safe token usage tracker with a hard budget cap.

    Usage:
        limiter = TokenCostLimiter(max_tokens=50_000)

        # Before each LLM call:
        limiter.check()                 # raises CostLimitExceededError if over budget

        # After each LLM call (report actual usage):
        limiter.record(input_tokens=320, output_tokens=85)

        # Get current stats:
        stats = limiter.stats()
    """

    DEFAULT_MAX_TOKENS = 50_000
    WARNING_THRESHOLD  = 0.80   # warn at 80% usage

    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS, session_id: Optional[str] = None):
        self.max_tokens   = max_tokens
        self.session_id   = session_id or "default"
        self._lock        = threading.Lock()
        self._total_input  = 0
        self._total_output = 0
        self._call_count   = 0
        self._blocked      = False

    @property
    def total_tokens(self) -> int:
        return self._total_input + self._total_output

    def check(self) -> None:
        """
        Check if the budget allows another LLM call.
        Raises CostLimitExceededError if the budget is exhausted.
        Call this BEFORE every LLM invocation.
        """
        with self._lock:
            if self._blocked or self.total_tokens >= self.max_tokens:
                self._blocked = True
                raise CostLimitExceededError(self.total_tokens, self.max_tokens)

            # Warn if approaching limit
            usage_pct = self.total_tokens / self.max_tokens
            if usage_pct >= self.WARNING_THRESHOLD:
                remaining = self.max_tokens - self.total_tokens
                print(
                    f"[ActionGuardrail:COST_WARNING] ⚠️  {usage_pct:.0%} of token budget used. "
                    f"{remaining:,} tokens remaining in session '{self.session_id}'."
                )

    def record(self, input_tokens: int = 0, output_tokens: int = 0) -> None:
        """
        Record token usage after an LLM call completes.
        Call this AFTER every LLM invocation.
        """
        with self._lock:
            self._total_input  += max(0, input_tokens)
            self._total_output += max(0, output_tokens)
            self._call_count   += 1

    def estimate_and_record(self, prompt: str, response: str) -> None:
        """
        Estimate token counts from text length (~4 chars per token)
        and record them. Use when actual token counts aren't available.
        """
        input_est  = len(prompt)  // 4
        output_est = len(response) // 4
        self.record(input_tokens=input_est, output_tokens=output_est)

    def reset(self) -> None:
        """Reset all counters (e.g., for a new session)."""
        with self._lock:
            self._total_input  = 0
            self._total_output = 0
            self._call_count   = 0
            self._blocked      = False

    def stats(self) -> dict:
        """Return current usage statistics."""
        with self._lock:
            return {
                "session_id":     self.session_id,
                "max_tokens":     self.max_tokens,
                "input_tokens":   self._total_input,
                "output_tokens":  self._total_output,
                "total_tokens":   self.total_tokens,
                "llm_calls":      self._call_count,
                "budget_used_pct": round(self.total_tokens / self.max_tokens * 100, 1),
                "is_blocked":     self._blocked,
                "remaining_tokens": max(0, self.max_tokens - self.total_tokens),
            }


# ─────────────────────────────────────────────────────────────
# Module-level default limiter (shared across the session)
# ─────────────────────────────────────────────────────────────
_default_limiter = TokenCostLimiter(max_tokens=50_000, session_id="global")


def get_default_limiter() -> TokenCostLimiter:
    """Return the module-level default cost limiter."""
    return _default_limiter
