def router_node(state):
    high, medium, low = [], [], []

    for job in state["jobs"]:
        if job["category"] == "HIGH":
            high.append(job)
        elif job["category"] == "MEDIUM":
            medium.append(job)
        else:
            low.append(job)

    if high:
        next_pipeline = "full_pipeline"
    elif medium:
        next_pipeline = "quick_pipeline"
    else:
        next_pipeline = "skip"

    return {
        "jobs": state["jobs"],
        "high_jobs": high,
        "medium_jobs": medium,
        "low_jobs": low,
        "next_pipeline": next_pipeline
    }