import json
import os
import time
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage

from guardrails.action_guardrails import get_default_limiter
from monitoring.agent_monitor import log_agent_run
from prompts import SCORER_SYSTEM_PROMPT_V1_1

load_dotenv()

llm = None


def get_groq_llm():
    global llm
    if llm is not None:
        return llm

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment. Please add it to your .env file.")
    llm = ChatGroq(
        api_key=api_key,
        model="openai/gpt-oss-120b",
        temperature=0.1
    )
    return llm


def get_system_prompt(version: str = "1.1") -> str:
    """Return the selected scorer system prompt version."""
    if version == "1.0":
        from prompts import SCORER_SYSTEM_PROMPT_V1_0
        return SCORER_SYSTEM_PROMPT_V1_0
    return SCORER_SYSTEM_PROMPT_V1_1


def _call_llm(prompt: str, stream: bool = False, show_prefix: str | None = None) -> str:
    """Invoke the LLM, monitor usage, and return its text."""
    limiter = get_default_limiter()
    limiter.check()

    start_ts = time.time()
    response_text = ""
    success = False

    try:
        if stream:
            if show_prefix:
                print(show_prefix, end="", flush=True)
            llm = get_groq_llm()
            for chunk in llm.stream([SystemMessage(content=prompt)]):
                if chunk.content:
                    print(chunk.content, end="", flush=True)
                    response_text += chunk.content
            print()
            success = bool(response_text)
        else:
            llm = get_groq_llm()
            response = llm.invoke([SystemMessage(content=prompt)])
            response_text = response.content.strip()
            success = bool(response_text)
    finally:
        duration = time.time() - start_ts
        limiter.estimate_and_record(prompt, response_text)
        log_agent_run(
            input_text=prompt,
            output_text=response_text,
            latency_seconds=duration,
            success=success,
        )

    return response_text


def stream_llm_response(prompt: str, show_prefix: str | None = None):
    """Stream LLM response with real-time output."""
    return _call_llm(prompt, stream=True, show_prefix=show_prefix)


def get_llm_response(prompt: str):
    """Get LLM response without streaming (for structured data like JSON)."""
    return _call_llm(prompt, stream=False)
