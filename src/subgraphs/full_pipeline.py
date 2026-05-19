from langgraph.graph import StateGraph
from utility import get_llm_response, stream_llm_response

def analyze_jd(state):
    jobs = state.get("jobs", [])
    for job in jobs:
        if job["category"] == "HIGH":
            prompt = f"Analyze this job description and extract key requirements, responsibilities, and company culture: {job['description']}"
            job["analysis"] = stream_llm_response(prompt, show_prefix=f"[ANALYSIS {job['job_id']}] ")
    return state

def tailor_resume(state):
    candidate = state["candidate"]
    jobs = state.get("jobs", [])
    for job in jobs:
        if job["category"] == "HIGH":
            prompt = f"""
Tailor this resume for the job: {job['title']}

Original Resume:
Name: {candidate['name']}
Title: {candidate['title']}
Experience: {candidate['experience_years']} years
Skills: {', '.join(candidate['skills'])}

Job Analysis: {job.get('analysis', '')}

Provide a tailored resume summary highlighting relevant skills and experience.
"""
            job["tailored_resume"] = stream_llm_response(prompt, show_prefix=f"[RESUME {job['job_id']}] ")
    return state

def cover_letter(state):
    candidate = state["candidate"]
    jobs = state.get("jobs", [])
    for job in jobs:
        if job["category"] == "HIGH":
            prompt = f"""
Write a professional cover letter for this job.

Candidate: {candidate['name']}, {candidate['title']}
Job: {job['title']} at {job['location']}
Job Description: {job['description']}

Tailored Resume: {job.get('tailored_resume', '')}

Make it compelling and personalized.
"""
            job["cover_letter"] = stream_llm_response(prompt, show_prefix=f"[COVER {job['job_id']}] ")
    return state

def quality_check(state):
    jobs = state.get("jobs", [])
    for job in jobs:
        if job["category"] == "HIGH":
            prompt = f"""
Rate the quality of this cover letter on a scale of 1-10.

Cover Letter:
{job.get('cover_letter', '')}

Provide a score and brief feedback.
"""
            content = get_llm_response(prompt)
            # Extract score
            import re
            score_match = re.search(r'(\d+)', content)
            score = int(score_match.group(1)) if score_match else 7
            job["quality_score"] = score
    return state


def quality_router(state):
    jobs = state.get("jobs", [])
    for job in jobs:
        if job["category"] == "HIGH" and job.get("quality_score", 10) < 7 and job.get("retries", 0) < 2:
            job["retries"] = job.get("retries", 0) + 1
            return "retry"
    return "done"


def build_full_pipeline():
    builder = StateGraph(dict)

    builder.add_node("analyze", analyze_jd)
    builder.add_node("tailor", tailor_resume)
    builder.add_node("cover", cover_letter)
    builder.add_node("quality", quality_check)

    builder.set_entry_point("analyze")

    builder.add_edge("analyze", "tailor")
    builder.add_edge("tailor", "cover")
    builder.add_edge("cover", "quality")

    builder.add_conditional_edges(
        "quality",
        quality_router,
        {
            "retry": "cover",
            "done": "__end__"
        }
    )

    return builder.compile()

   