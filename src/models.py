from pydantic import BaseModel
from typing import List

class JobScore(BaseModel):
    score: int
    category: str
    reason: str

class ApplicationStrategy(BaseModel):
    candidate_name: str
    total_jobs_analyzed: int
    approved_jobs: List[dict]
    skipped_jobs: List[dict]
    recommended_apply_order: List[str]