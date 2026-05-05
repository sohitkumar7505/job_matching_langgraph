import json
import os
import threading
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parents[0] / "logs" / "agent_runs.jsonl"
_log_lock = threading.Lock()


def _ensure_log_file_exists():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("")


def log_agent_run(input_text: str, output_text: str, latency_seconds: float, success: bool) -> None:
    """Append a structured JSON line to the agent monitoring log."""
    _ensure_log_file_exists()
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "input_summary": input_text[:1024],
        "output_summary": output_text[:1024],
        "latency_seconds": round(latency_seconds, 4),
        "success": success,
        "input_length": len(input_text),
        "output_length": len(output_text),
    }
    with _log_lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


def read_recent_runs(limit: int = 20):
    """Read the most recent log entries from the monitoring file."""
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
    return [json.loads(line) for line in lines]
