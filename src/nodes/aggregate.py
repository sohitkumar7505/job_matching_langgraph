def aggregate_node(state):
    jobs = state["jobs"]
    processed = []
    skipped = []
    
    for job in jobs:
        if job["category"] in ["HIGH", "MEDIUM"]:
            processed.append(job)
        else:
            skipped.append(job)

    return {
        "processed_jobs": processed,
        "skipped_jobs": skipped
    }