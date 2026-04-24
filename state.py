from typing import TypedDict, List, Optional

class JobState(TypedDict):
    job_id: str
    title: str
    description: str
    score: Optional[int]
    category: Optional[str]
    tailored_resume: Optional[str]
    cover_letter: Optional[str]
    summary: Optional[str]
    quality_score: Optional[int]
    retries: int
    status: Optional[str]

class GraphState(TypedDict):
    candidate: dict
    jobs: List[JobState]

    high_jobs: List[JobState]
    medium_jobs: List[JobState]
    low_jobs: List[JobState]

    processed_jobs: List[JobState]
    skipped_jobs: List[JobState]
    approved_jobs: List[JobState]
    final_output: Optional[dict]