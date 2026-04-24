from models import JobScore
from utility import get_llm_response

def score_single_job(job, candidate):
    prompt = f"""
You are an expert HR recruiter. Score this job for the candidate on a scale of 1-10.

Candidate Profile:
- Name: {candidate['name']}
- Title: {candidate['title']}
- Experience: {candidate['experience_years']} years
- Skills: {', '.join(candidate['skills'])}
- Preferences: Role: {candidate['preferences']['role_type']}, Location: {candidate['preferences']['location']}

Job Details:
- Title: {job['title']}
- Location: {job['location']}
- Description: {job['description']}
- Required Skills: {', '.join(job['required_skills'])}
- Preferred Skills: {', '.join(job.get('preferred_skills', []))}
- Experience Required: {job['experience_required']} years

Provide a JSON response with:
- score: integer 1-10
- category: "HIGH" (8-10), "MEDIUM" (5-7), "LOW" (1-4)
- reason: brief explanation

Response format: {{"score": 8, "category": "HIGH", "reason": "Strong match in skills and experience"}}
"""

    result = get_llm_response(prompt)
    # Parse JSON
    import json
    try:
        score_data = json.loads(result)
        job_score = JobScore(**score_data)
    except:
        # Fallback
        job_score = JobScore(score=5, category="MEDIUM", reason="LLM parsing failed")

    job["score"] = job_score.score
    job["category"] = job_score.category

    return job


def scorer_node(state):
    jobs = state["jobs"]
    candidate = state["candidate"]

    # simulate parallel fan-out
    updated_jobs = [score_single_job(job, candidate) for job in jobs]

    return {"jobs": updated_jobs}