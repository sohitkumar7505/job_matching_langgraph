def score_single_job(job, candidate):
    candidate_skills = set(candidate["skills"])
    required_skills = set(job["required_skills"])
    preferred_skills = set(job.get("preferred_skills", []))

    # Required skills match ratio
    required_match = len(candidate_skills & required_skills) / len(required_skills) if required_skills else 0

    # Preferred skills match ratio
    preferred_match = len(candidate_skills & preferred_skills) / len(preferred_skills) if preferred_skills else 0

    # Experience match
    experience_match = 1 if candidate["experience_years"] >= job["experience_required"] else 0

    # Location match
    candidate_location_pref = candidate["preferences"]["location"]
    location_match = 1 if job["location"] in candidate_location_pref or "Remote" in candidate_location_pref else 0

    # Role match
    candidate_role_pref = candidate["preferences"]["role_type"].lower()
    role_match = 1 if candidate_role_pref in job["title"].lower() else 0

    # Calculate total score (out of 10)
    score = (required_match * 6) + (preferred_match * 2) + experience_match + location_match + role_match
    score = min(10, score)

    if score >= 8:
        category = "HIGH"
    elif score >= 5:
        category = "MEDIUM"
    else:
        category = "LOW"

    job["score"] = score
    job["category"] = category

    return job


def scorer_node(state):
    jobs = state["jobs"]
    candidate = state["candidate"]

    # simulate parallel fan-out
    updated_jobs = [score_single_job(job, candidate) for job in jobs]

    return {"jobs": updated_jobs}