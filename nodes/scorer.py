def score_single_job(job):
    title = job["title"]

    if "AI" in title:
        score = 9
    elif "Full Stack" in title:
        score = 6
    else:
        score = 3

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

    # simulate parallel fan-out
    updated_jobs = [score_single_job(job) for job in jobs]

    return {"jobs": updated_jobs}