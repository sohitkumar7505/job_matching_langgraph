def aggregate_node(state):
    processed = state["high_jobs"] + state["medium_jobs"]

    return {
        "processed_jobs": processed,
        "skipped_jobs": state["low_jobs"]
    }