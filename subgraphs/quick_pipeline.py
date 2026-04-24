from langgraph.graph import StateGraph
from utility import get_llm_response, stream_llm_response

def extract_reqs(state):
    jobs = state.get("jobs", [])
    for job in jobs:
        if job["category"] == "MEDIUM":
            prompt = f"Extract the key requirements from this job description: {job['description']}"
            job["requirements"] = stream_llm_response(prompt, show_prefix=f"[REQS {job['job_id']}] ")
    return state

def match_skills(state):
    candidate = state["candidate"]
    jobs = state.get("jobs", [])
    for job in jobs:
        if job["category"] == "MEDIUM":
            prompt = f"""
Match candidate skills to job requirements.

Candidate Skills: {', '.join(candidate['skills'])}
Job Requirements: {job.get('requirements', '')}

List matching skills and gaps.
"""
            job["matches"] = stream_llm_response(prompt, show_prefix=f"[MATCH {job['job_id']}] ")
    return state

def quick_summary(state):
    candidate = state["candidate"]
    jobs = state.get("jobs", [])
    for job in jobs:
        if job["category"] == "MEDIUM":
            prompt = f"""
Provide a quick summary of why this candidate is a good fit for the job.

Candidate: {candidate['name']}, {candidate['experience_years']} years experience
Job: {job['title']}
Matches: {job.get('matches', '')}

Keep it concise.
"""
            job["summary"] = stream_llm_response(prompt, show_prefix=f"[SUMMARY {job['job_id']}] ")
    return state

def build_quick_pipeline():
    builder = StateGraph(dict)

    builder.add_node("extract", extract_reqs)
    builder.add_node("match", match_skills)
    builder.add_node("summary", quick_summary)

    builder.set_entry_point("extract")

    builder.add_edge("extract", "match")
    builder.add_edge("match", "summary")

    return builder.compile()